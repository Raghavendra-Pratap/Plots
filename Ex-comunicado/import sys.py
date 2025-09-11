import sys
import os
import subprocess
import pandas as pd

from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QTextEdit, QListWidget,
    QListWidgetItem, QPushButton, QComboBox,
    QFileDialog, QScrollArea, QLineEdit, QAbstractItemView,
    QInputDialog
)

def ensure_package(pkg_name):
    """
    Try to import pkg_name; if that fails, pip-install it.
    """
    try:
        __import__(pkg_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])

# Ensure cross-platform dependencies
for pkg in ("PyQt5", "pandas", "openpyxl"):
    ensure_package(pkg)


class DropArea(QLabel):
    """
    A simple drag-&-drop area for CSV/XLSX files.
    Now handles dragMoveEvent, checks for real files,
    and wraps calls to load_file() in a try/except.
    """
    def __init__(self, parent=None):
        super().__init__("Drag & drop CSV/XLSX files here", parent)
        self.setFixedHeight(100)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border:2px dashed #aaa;")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        # required to continue accepting drop after dragEnter
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        # Loop through all dropped URLs
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if not os.path.isfile(path):
                # skip directories or invalid paths
                print(f"Ignored non-file drop: {path}")
                continue

            # Safely invoke load_file on the main window
            try:
                # self.window() returns the top-level QWidget (PlaygroundPage)
                mw = self.window()
                if hasattr(mw, "load_file"):
                    mw.load_file(path)
                else:
                    print(f"No load_file() method on {mw}")
            except Exception as e:
                # catch any C-extension crash point or logic error
                print(f"Error loading dropped file {path}: {e}")

        event.acceptProposedAction()


class PlaygroundPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Playground")

        # -------------------------------------------------------------------
        # Data structures:
        #  - loaded_files: list of CSV/XLSX paths
        #  - loaded_prompts: list of (path, content) tuples
        #  - actions: list of prompt-builder steps
        #  - redo_stack: for undo/redo
        #  - ref_mode: 'column' or 'sheet'
        # -------------------------------------------------------------------
        self.loaded_files    = []
        self.loaded_prompts  = []
        self.actions         = []
        self.redo_stack      = []
        self.ref_mode        = "column"
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 1) Toolbar — define the buttons *before* using them
        self.undo_btn  = QPushButton("Undo")
        self.redo_btn  = QPushButton("Redo")
        self.break_btn = QPushButton("Break")
        self.clear_btn = QPushButton("Clear")
        self.save_and_select_btn = QPushButton("Save & Select")

        tb = QHBoxLayout()
        for btn in (self.undo_btn, self.redo_btn,
                    self.break_btn, self.clear_btn, self.save_and_select_btn
                    ):
            tb.addWidget(btn)
        main_layout.addLayout(tb)

               # Connect button signals to their functions
        self.undo_btn.clicked.connect(self.undo_action)
        self.redo_btn.clicked.connect(self.redo_action)
        self.break_btn.clicked.connect(self.break_action)
        self.clear_btn.clicked.connect(self.clear_prompt) 
        self.save_and_select_btn.clicked.connect(self.save_and_select)

        # 2) Relation Builder
        relation_box = QGroupBox("Relation Builder")
        rel_v       = QVBoxLayout(relation_box)

        # 2a) Prompt Builder
        # define the five buttons before laying out
        self.new_file_btn         = QPushButton("New File")
        self.custom_btn           = QPushButton("Custom")
        self.add_col_btn          = QPushButton("Add Column")
        self.save_prompt_btn      = QPushButton("Save Prompt")
        self.start_processing_btn = QPushButton("Start Processing")

        prompt_box = QGroupBox("Prompt Builder")
        pb_layout  = QVBoxLayout(prompt_box)

        # prompt display area
        pb_layout.addWidget(QLabel("Prompt:"))
        self.prompt_area = QTextEdit()
        self.prompt_area.setReadOnly(True)
        pb_layout.addWidget(self.prompt_area)

        # hidden custom‐text input & Add button (already configured)
        self.custom_input   = QLineEdit()
        self.custom_input.setPlaceholderText("Enter custom text…")
        self.custom_input.hide()
        pb_layout.addWidget(self.custom_input)

        self.custom_add_btn = QPushButton("Add")
        self.custom_add_btn.hide()
        pb_layout.addWidget(self.custom_add_btn)

        self.custom_add_btn.clicked.connect(self.add_custom_text)
        self.custom_input.returnPressed.connect(self.add_custom_text)

        # ── Bottom row: left buttons ─ stretch ─ right buttons ──
        bottom_h = QHBoxLayout()
        # left group
        bottom_h.addWidget(self.new_file_btn)
        bottom_h.addWidget(self.custom_btn)
        bottom_h.addWidget(self.add_col_btn)
        bottom_h.addStretch()
        # right group
        bottom_h.addWidget(self.save_prompt_btn)
        bottom_h.addWidget(self.start_processing_btn)
        pb_layout.addLayout(bottom_h)
        # ────────────────────────────────────────────────────────

        # connect signals
        self.new_file_btn.clicked.connect(self.create_new_file)
        self.custom_btn.clicked.connect(self.prompt_custom_value)
        self.add_col_btn.clicked.connect(self.prompt_new_column)
        self.save_prompt_btn.clicked.connect(self.save_prompt)
        self.start_processing_btn.clicked.connect(self.start_processing)

        # add the Prompt Builder into the Relation Builder layout
        rel_v.addWidget(prompt_box, 3)

        # 2b) Formula dropdown
        fv = QVBoxLayout()
        fv.addWidget(QLabel("Formula:"))
        self.formula_combo = QComboBox()
        self.formula_combo.addItems(
            ["SUM","AVERAGE","COUNT","IF","VLOOKUP","CUSTOM…"]
        )
        fv.addWidget(self.formula_combo)
        fv.addStretch()

        # assemble Relation Builder
        rel_h = QHBoxLayout()
        rel_h.addWidget(prompt_box, 3)
        rel_h.addLayout(fv, 1)
        rel_v.addLayout(rel_h)
        main_layout.addWidget(relation_box)

        # 3) Preview & Import
        preview_box = QGroupBox("Preview & Import")
        pv2        = QVBoxLayout(preview_box)

        # 3a) File history + Import button under it
        top_h2  = QHBoxLayout()
        hist_box = QGroupBox("File History")
        hv       = QVBoxLayout(hist_box)
        self.file_list_widget = QListWidget()
        hv.addWidget(self.file_list_widget)
        self.import_btn = QPushButton("Import File")
        self.import_btn.clicked.connect(self.open_file_dialog)
        hv.addWidget(self.import_btn)
        top_h2.addWidget(hist_box, 1)

        drop_box = QGroupBox("Import & Recent Actions")
        dv       = QVBoxLayout(drop_box)
        self.drop_area = DropArea(self)
        dv.addWidget(self.drop_area)
        dv.addWidget(QLabel("Recent Actions:"))
        self.actions_list_widget = QListWidget()
        dv.addWidget(self.actions_list_widget)
        top_h2.addWidget(drop_box, 1)

        pv2.addLayout(top_h2)

        # 3b) Columns area
        self.columns_area      = QScrollArea()
        self.columns_area.setWidgetResizable(True)
        self.columns_container = QWidget()
        self.columns_layout    = QHBoxLayout(self.columns_container)
        self.columns_area.setWidget(self.columns_container)
        pv2.addWidget(self.columns_area)
        main_layout.addWidget(preview_box)

    # -- file import / history ------------------------------------------------

    def open_file_dialog(self):
        """
        Allow selecting multiple CSV/XLSX files at once.
        """
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open CSV/Excel Files",
            "",
            "All Supported (*.csv *.xls *.xlsx);;"
            "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)"
        )
        if not paths:
            return
        for path in paths:
            self.load_file(path)

    def load_file(self, path):
        """Add a file to history & refresh."""
        if path in self.loaded_files:
            return
        self.loaded_files.append(path)
        item = QListWidgetItem(self.file_list_widget)
        w    = QWidget(); hl = QHBoxLayout(w)
        hl.setContentsMargins(4,2,4,2)
        hl.addWidget(QLabel(os.path.basename(path)))
        hl.addStretch()
        btn = QPushButton("✕"); btn.setFixedSize(16,16)
        btn.setStyleSheet("border:none;color:red;")
        hl.addWidget(btn)
        item.setSizeHint(w.sizeHint())
        self.file_list_widget.setItemWidget(item, w)
        btn.clicked.connect(lambda *_,
                            it=item, p=path: self.remove_file(it, p))
        self.add_action_history(f"Imported: {os.path.basename(path)}")
        self.update_columns()

    def remove_file(self, item, path):
        self.loaded_files.remove(path)
        self.file_list_widget.takeItem(
            self.file_list_widget.row(item)
        )
        self.update_columns()

    # -- prompt-builder actions ------------------------------------------------

    def toggle_mode(self):
        if self.ref_mode == "column":
            self.ref_mode = "sheet"
            self.mode_btn.setText("Mode: Sheet")
        else:
            self.ref_mode = "column"
            self.mode_btn.setText("Mode: Column")

    def show_custom_input(self):
        vis = not self.custom_input.isVisible()
        self.custom_input.setVisible(vis)
        self.custom_add_btn.setVisible(vis)
        if vis:
            self.custom_input.setFocus()

    def add_custom_text(self):
        txt = self.custom_input.text().strip()
        if not txt:
            return
        self._add_action(("text", txt))
        self.custom_input.clear()

    def break_action(self):
        if not self.actions or self.actions[-1][0] == "break":
            return
        self._add_action(("break", None))

    def clear_prompt(self):
        self.actions.clear()
        self.redo_stack.clear()
        self._update_prompt_area()

    def save_and_select(self):
        """
        Process current prompt actions into a CSV or Excel, then
        add the saved file into history & preview it.
        Now uses only the plain column name for headers.
        """
        # split actions into segments by 'break'
        segments, curr = [], []
        for t, v in self.actions:
            if t == "break":
                segments.append(curr); curr = []
            else:
                curr.append(v)
        segments.append(curr)

        if self.ref_mode == "column":
            # === CSV mode ===
            out_path, _ = QFileDialog.getSaveFileName(
                self, "Save CSV", "", "CSV Files (*.csv)"
            )
            if not out_path:
                return

            df_out = pd.DataFrame()
            for seg in segments:
                for val in seg:
                    parts = val.split(" ▸ ")
                    fname, col = parts[0], parts[-1]
                    sheet = parts[1] if len(parts) == 3 else None

                    # find the original file path
                    fpath = next(
                        (p for p in self.loaded_files
                         if os.path.basename(p) == fname),
                        None
                    )
                    if not fpath:
                        continue

                    try:
                        src = (pd.read_csv if fpath.lower().endswith(".csv")
                               else lambda p: pd.read_excel(p, sheet_name=sheet))
                        df_src = src(fpath)
                        # Use only the column name as header
                        df_out[col] = df_src[col]
                    except Exception as e:
                        df_out[col] = f"Error: {e}"

            df_out.to_csv(out_path, index=False)

        else:
            # === SHEET mode ===
            out_path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel", "", "Excel Files (*.xlsx)"
            )
            if not out_path:
                return

            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                for idx, seg in enumerate(segments, start=1):
                    df_sheet = pd.DataFrame()
                    for val in seg:
                        parts = val.split(" ▸ ")
                        fname, col = parts[0], parts[-1]
                        sheet = parts[1] if len(parts) == 3 else None

                        fpath = next(
                            (p for p in self.loaded_files
                             if os.path.basename(p) == fname),
                            None
                        )
                        if not fpath:
                            continue

                        try:
                            src = (pd.read_csv if fpath.lower().endswith(".csv")
                                   else lambda p: pd.read_excel(p, sheet_name=sheet))
                            df_src = src(fpath)
                            # Use only the column name as header
                            df_sheet[col] = df_src[col]
                        except Exception as e:
                            df_sheet[col] = f"Error: {e}"

                    sheet_name = f"Prompt{idx}"
                    df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

        # add newly created file to history & refresh preview
        self.load_file(out_path)
        self.add_action_history(f"Saved&Selected: {os.path.basename(out_path)}")

    def save_prompt(self):
        """Only save the current prompt text to a file."""
        txt = self.prompt_area.toPlainText().strip()
        if not txt:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Prompt", "", "Prompt (*.prompt);;Text (*.txt)"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)
        self.add_action_history(f"Prompt saved: {os.path.basename(path)}")

    def start_processing(self):
        """
        Process current prompt into a CSV or Excel.
        Uses only plain column names as headers for both modes.
        """
        # split actions into segments by 'break'
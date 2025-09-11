import sys
import os
import subprocess
import pandas as pd
import re
from datetime import datetime
import numpy as np
import shutil
import tempfile
import time
import threading
import pyarrow

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
for pkg in ("PyQt5", "pandas", "openpyxl", "polars", "pyarrow"):
    ensure_package(pkg)

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

print(pyarrow.__version__)

class FormulaProcessor:
    """Handles formula operations on dataframe columns"""
    
    def __init__(self):
        self.available_formulas = {
            'CONCATENATE': self.concatenate,
            'SPLIT': self.split,
            'IF': self.if_condition,
            'PIVOT': self.pivot,
            'DEPIVOT': self.depivot,
            'SUM': self.sum,
            'COUNT': self.count,
            'UNIQUE_COUNT': self.unique_count,
            'DATE': self.date_format,
            'UPPER': self.upper,
            'LOWER': self.lower,
            'PROPER': self.proper,
            'TEXT': self.to_text,
            # --- Added from FormulaEngine ---
            'ADD': self.add,
            'SUBTRACT': self.subtract,
            'MULTIPLY': self.multiply,
            'DIVIDE': self.divide,
            'TITLE_CASE': self.title_case,
            'TEXT_LENGTH': self.text_length,
            'FIND_TEXT': self.find_text,
            'DAYS_SINCE': self.days_since,
            'EXTRACT_YEAR': self.extract_year,
            'EXTRACT_MONTH': self.extract_month,
            'EXTRACT_DAY': self.extract_day,
            'SUMIF': self.sumif,
            'COUNTIF': self.countif,
            'AVERAGEIF': self.averageif,
            'VLOOKUP': self.vlookup,
            'PIVOT_TABLE': self.pivot_table,
            'UNPIVOT': self.unpivot,
            'REMOVE_DUPLICATES': self.remove_duplicates,
            'COUNT_UNIQUE': self.count_unique,
            'MARK_DUPLICATES': self.mark_duplicates,
            'FILLNA': self.fillna,
            'IFERROR_DIVIDE': self.iferror_divide,
            'ROW_SUM': self.row_sum,
            'MEDIAN': self.median,
            'MODE': self.mode,
            'STDDEV': self.stddev,
            'VARIANCE': self.variance,
            'RANK': self.rank,
            'PERCENTILE': self.percentile,
            'TRANSPOSE': self.transpose,
            'ROUND_COLUMN': self.round_column,
            'CEIL_COLUMN': self.ceil_column,
            'FLOOR_COLUMN': self.floor_column,
            'ROLLING_MEAN': self.rolling_mean,
        }

    def parse_formula(self, formula_str):
        """Parse formula string into operation and arguments (supports both old and new formats)"""
        # New format: OPERATION [arg1 -> arg2 -> ...]
        match_bracket = re.match(r'(\w+) \[(.*)\]', formula_str)
        if match_bracket:
            operation = match_bracket.group(1).upper()
            # Split by '->', strip whitespace
            args = [arg.strip() for arg in match_bracket.group(2).split('->')]
            return operation, args
        # Old format: OPERATION(arg1, arg2, ...)
        match_paren = re.match(r'(\w+)\((.*)\)', formula_str)
        if match_paren:
            operation = match_paren.group(1).upper()
            args = [arg.strip() for arg in match_paren.group(2).split(',')]
            return operation, args
        raise ValueError("Invalid formula format")

    def apply_formula(self, df, formula_str):
        """Apply formula to dataframe"""
        operation, args = self.parse_formula(formula_str)
        if operation not in self.available_formulas:
            raise ValueError(f"Unknown operation: {operation}")
        
        return self.available_formulas[operation](df, *args)

    def concatenate(self, df, *args):
        """Concatenate columns and/or custom values row-wise, step by step."""
        # args can be column references (e.g., 'Store Master.csv ▸ Shop Name') or custom values (e.g., 'custom <101>')
        result = None
        for arg in args:
            arg = arg.strip()
            if arg.startswith('custom <') and arg.endswith('>'):
                # Extract the custom value
                value = arg[len('custom <'):-1]
                series = pd.Series([value] * len(df), index=df.index)
            elif arg.startswith('add column <') and arg.endswith('>'):
                # Ignore add column in concatenation
                continue
            elif arg in df.columns:
                series = df[arg].astype(str)
            else:
                # Try to match column by suffix (for 'file ▸ col' style)
                colname = arg.split('▸')[-1].strip()
                if colname in df.columns:
                    series = df[colname].astype(str)
                else:
                    # Fallback: treat as literal
                    series = pd.Series([arg] * len(df), index=df.index)
            if result is None:
                result = series
            else:
                result = result.astype(str) + series.astype(str)
        return result if result is not None else pd.Series([''] * len(df), index=df.index)

    def split(self, df, column, separator, index):
        """Split column by separator and get index"""
        return df[column].str.split(separator).str[int(index)]

    def if_condition(self, df, column, condition, true_value, false_value):
        """IF condition on column"""
        mask = eval(f"df['{column}'] {condition}")
        return pd.Series(np.where(mask, true_value, false_value), index=df.index)

    def pivot(self, df, index_col, value_col):
        """Pivot table on index_col with value_col"""
        return pd.pivot_table(df, values=value_col, index=index_col)

    def depivot(self, df, id_vars):
        """Melt/Unpivot dataframe"""
        id_vars = [col.strip() for col in id_vars.split('|')]
        return pd.melt(df, id_vars=id_vars)

    def sum(self, df, *columns):
        """Sum multiple columns"""
        return df[list(columns)].sum(axis=1)

    def count(self, df, column):
        """Count non-null values in column"""
        return df[column].count()

    def unique_count(self, df, column):
        """Count unique values in column"""
        return df[column].nunique()

    def date_format(self, df, column, format_str):
        """Format date column"""
        return pd.to_datetime(df[column]).dt.strftime(format_str)

    def upper(self, df, column):
        """Convert to uppercase"""
        return df[column].str.upper()

    def lower(self, df, column):
        """Convert to lowercase"""
        return df[column].str.lower()

    def proper(self, df, column):
        """Convert to proper case"""
        return df[column].str.title()

    def to_text(self, df, column):
        """Convert to text"""
        return df[column].astype(str)

    def add(self, var1, var2=None):
        return self.df.select([pl.col(var1).sum(axis=1) + (pl.col(var2).sum(axis=1) if var2 else 0)]).to_series()

    def subtract(self, var1, var2):
        return self.df.select([pl.col(var1).sum(axis=1) - pl.col(var2).sum(axis=1)]).to_series()

    def multiply(self, var1, var2=None):
        return self.df.select([pl.col(var1).product(axis=1) * (pl.col(var2).product(axis=1) if var2 else 1)]).to_series()

    def divide(self, var1, var2):
        return self.df.select([pl.col(var1).sum(axis=1) / pl.col(var2).sum(axis=1)]).to_series()

    def title_case(self, column):
        return self.df[column].str.to_titlecase()

    def text_length(self, column):
        return self.df[column].str.lengths()

    def find_text(self, column, substring):
        return self.df[column].str.find(substring)

    def days_since(self, column):
        return (pl.lit(datetime.now()) - pl.col(column).str.strptime(pl.Datetime)).dt.days()

    def extract_year(self, column):
        return self.df[column].str.strptime(pl.Datetime).dt.year()

    def extract_month(self, column):
        return self.df[column].str.strptime(pl.Datetime).dt.month()

    def extract_day(self, column):
        return self.df[column].str.strptime(pl.Datetime).dt.day()

    def sumif(self, condition_col, condition_val, target_col):
        return self.df.filter(pl.col(condition_col) == condition_val)[target_col].sum()

    def countif(self, condition_col, condition_val):
        return (self.df[condition_col] == condition_val).sum()

    def averageif(self, condition_col, condition_val, target_col):
        return self.df.filter(pl.col(condition_col) == condition_val)[target_col].mean()

    def vlookup(self, lookup_df, key_col, value_col):
        return self.df.join(lookup_df.select([key_col, value_col]), on=key_col, how='left')

    def pivot_table(self, index, values, aggfunc='sum'):
        return self.df.pivot(index=index, values=values, aggregate_fn=aggfunc)

    def unpivot(self, id_vars, value_vars):
        return self.df.melt(id_vars=id_vars, value_vars=value_vars)

    def remove_duplicates(self):
        return self.df.unique()

    def count_unique(self, column):
        return self.df[column].n_unique()

    def mark_duplicates(self):
        return self.df.is_duplicated()

    def fillna(self, column, value):
        return self.df[column].fill_null(value)

    def iferror_divide(self, column):
        return self.df[column].apply(lambda x: 1/x if x != 0 else 'Error')

    def row_sum(self, columns):
        return self.df.select([pl.sum_horizontal([pl.col(c) for c in columns])]).to_series()

    def median(self, column):
        return self.df[column].median()

    def mode(self, column):
        return self.df[column].mode()

    def stddev(self, column):
        return self.df[column].std()

    def variance(self, column):
        return self.df[column].var()

    def rank(self, column):
        return self.df[column].rank()

    def percentile(self, column):
        return self.df[column].rank(method='average', pct=True)

    def transpose(self):
        return self.df.transpose()

    def round_column(self, column, decimals=0):
        return self.df[column].round(decimals)

    def ceil_column(self, column):
        return self.df[column].apply(np.ceil)

    def floor_column(self, column):
        return self.df[column].apply(np.floor)

    def rolling_mean(self, column, window):
        return self.df[column].rolling_mean(window)


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

        # Initialize formula processor
        self.formula_processor = FormulaProcessor()

        # Data structures
        self.loaded_files    = []
        self.loaded_prompts  = []
        self.actions         = []
        self.redo_stack      = []
        self.ref_mode        = "column"
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 1) Toolbar
        self.undo_btn  = QPushButton("Undo")
        self.redo_btn  = QPushButton("Redo")
        self.break_btn = QPushButton("Break")
        self.clear_btn = QPushButton("Clear")
        self.save_and_select_btn = QPushButton("Save & Select")
        self.mode_btn = QPushButton("Mode: Column")

        tb = QHBoxLayout()
        for btn in (self.undo_btn, self.redo_btn,
                    self.break_btn, self.clear_btn, self.save_and_select_btn,
                    self.mode_btn
                    ):
            tb.addWidget(btn)
        main_layout.addLayout(tb)

        # Connect button signals
        self.undo_btn.clicked.connect(self.undo_action)
        self.redo_btn.clicked.connect(self.redo_action)
        self.break_btn.clicked.connect(self.break_action)
        self.clear_btn.clicked.connect(self.clear_prompt) 
        self.save_and_select_btn.clicked.connect(self.save_and_select)
        self.mode_btn.clicked.connect(self.toggle_mode)

        # 2) Relation Builder
        relation_box = QGroupBox("Relation Builder")
        rel_v       = QVBoxLayout(relation_box)

        # Create horizontal layout for prompt builder and formula section
        builder_layout = QHBoxLayout()

        # 2a) Prompt Builder
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

        # hidden custom‐text input & Add button
        self.custom_input   = QLineEdit()
        self.custom_input.setPlaceholderText("Enter custom text…")
        self.custom_input.hide()
        pb_layout.addWidget(self.custom_input)

        self.custom_add_btn = QPushButton("Add")
        self.custom_add_btn.hide()
        pb_layout.addWidget(self.custom_add_btn)

        self.custom_add_btn.clicked.connect(self.add_custom_text)
        self.custom_input.returnPressed.connect(self.add_custom_text)

        # Formula block state
        self.formula_open = False
        self.current_formula = None
        self.formula_buffer = []

        # Bottom row buttons
        bottom_h = QHBoxLayout()
        bottom_h.addWidget(self.new_file_btn)
        bottom_h.addWidget(self.custom_btn)
        bottom_h.addWidget(self.add_col_btn)
        bottom_h.addStretch()
        bottom_h.addWidget(self.save_prompt_btn)
        bottom_h.addWidget(self.start_processing_btn)
        pb_layout.addLayout(bottom_h)

        # connect signals
        self.new_file_btn.clicked.connect(self.create_new_file)
        self.custom_btn.clicked.connect(self.prompt_custom_value)
        self.add_col_btn.clicked.connect(self.prompt_new_column)
        self.save_prompt_btn.clicked.connect(self.save_prompt)
        self.start_processing_btn.clicked.connect(self.start_processing)

        # Add prompt builder to horizontal layout
        builder_layout.addWidget(prompt_box, 3)

        # 2b) Formula Section
        formula_box = QGroupBox("Formulas")
        formula_layout = QVBoxLayout(formula_box)
        
        # Formula list
        self.formula_list = QListWidget()
        self.formula_list.addItems(list(self.formula_processor.available_formulas.keys()))
        self.formula_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.formula_list.itemClicked.connect(self.formula_selected)
        formula_layout.addWidget(self.formula_list)
        
        # Add formula section to horizontal layout
        builder_layout.addWidget(formula_box, 1)
        
        # Add the horizontal layout to relation builder
        rel_v.addLayout(builder_layout)
        
        # Add relation builder to main layout
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
        entry = f"custom <{txt}>"
        if self.formula_open:
            self.formula_buffer.append(entry)
            self._update_prompt_area()
        else:
            self._add_action(("custom", entry))
        self.custom_input.clear()
        self.custom_input.hide()
        self.custom_add_btn.hide()

    def break_action(self):
        # If a formula block is open, close it first
        if self.formula_open:
            self.close_formula_block()
        if not self.actions or self.actions[-1][0] == "break":
            return
        self._add_action(("break", None))

    def clear_prompt(self):
        self.actions.clear()
        self.redo_stack.clear()
        # Also reset formula block state
        self.formula_open = False
        self.current_formula = None
        self.formula_buffer = []
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

            if POLARS_AVAILABLE:
                df_out = pl.DataFrame()
            else:
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
                        if POLARS_AVAILABLE and fpath.lower().endswith(".csv"):
                            df_src = pl.read_csv(fpath)
                            df_out = df_out.with_columns(df_src[col].alias(col))
                        elif POLARS_AVAILABLE and fpath.lower().endswith(('.xls', '.xlsx')):
                            try:
                                df_src = pl.read_excel(fpath, sheet_name=sheet)
                                df_out = df_out.with_columns(df_src[col].alias(col))
                            except Exception:
                                src = lambda p: pd.read_excel(p, sheet_name=sheet)
                                df_src = src(fpath)
                                if isinstance(df_out, pl.DataFrame):
                                    df_out = df_out.with_columns(pl.Series(col, df_src[col].tolist()))
                                else:
                                    df_out[col] = df_src[col]
                        elif fpath.lower().endswith(".csv"):
                            df_src = pd.read_csv(fpath)
                            if isinstance(df_out, pl.DataFrame):
                                df_out = df_out.with_columns(pl.Series(col, df_src[col].tolist()))
                            else:
                                df_out[col] = df_src[col]
                        else:
                            src = lambda p: pd.read_excel(p, sheet_name=sheet)
                            df_src = src(fpath)
                            if isinstance(df_out, pl.DataFrame):
                                df_out = df_out.with_columns(pl.Series(col, df_src[col].tolist()))
                            else:
                                df_out[col] = df_src[col]
                    except Exception as e:
                        if isinstance(df_out, pl.DataFrame):
                            df_out = df_out.with_columns(pl.Series(col, [f"Error: {e}"] * df_out.height))
                        else:
                            df_out[col] = f"Error: {e}"

            if isinstance(df_out, pl.DataFrame):
                df_out.write_csv(out_path)
            else:
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
                    if POLARS_AVAILABLE:
                        df_sheet = pl.DataFrame()
                    else:
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
                            if POLARS_AVAILABLE and fpath.lower().endswith(".csv"):
                                df_src = pl.read_csv(fpath)
                                df_sheet = df_sheet.with_columns(df_src[col].alias(col))
                            elif POLARS_AVAILABLE and fpath.lower().endswith(('.xls', '.xlsx')):
                                try:
                                    df_src = pl.read_excel(fpath, sheet_name=sheet)
                                    df_sheet = df_sheet.with_columns(df_src[col].alias(col))
                                except Exception:
                                    df_src = pd.read_excel(fpath, sheet_name=sheet)
                                    if isinstance(df_sheet, pl.DataFrame):
                                        df_sheet = df_sheet.with_columns(pl.Series(col, df_src[col].tolist()))
                                    else:
                                        df_sheet[col] = df_src[col]
                            elif fpath.lower().endswith(".csv"):
                                df_src = pd.read_csv(fpath)
                                if isinstance(df_sheet, pl.DataFrame):
                                    df_sheet = df_sheet.with_columns(pl.Series(col, df_src[col].tolist()))
                                else:
                                    df_sheet[col] = df_src[col]
                            else:
                                df_src = pd.read_excel(fpath, sheet_name=sheet)
                                if isinstance(df_sheet, pl.DataFrame):
                                    df_sheet = df_sheet.with_columns(pl.Series(col, df_src[col].tolist()))
                                else:
                                    df_sheet[col] = df_src[col]
                        except Exception as e:
                            if isinstance(df_sheet, pl.DataFrame):
                                df_sheet = df_sheet.with_columns(pl.Series(col, [f"Error: {e}"] * df_sheet.height))
                            else:
                                df_sheet[col] = f"Error: {e}"

                    sheet_name = f"Prompt{idx}"
                    if isinstance(df_sheet, pl.DataFrame):
                        pd_df = df_sheet.to_pandas()
                        pd_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

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
        Now handles formulas in addition to column selections.
        """
        # split actions into segments by 'break'
        segments, curr = [], []
        for t, v in self.actions:
            if t == "break":
                segments.append(curr)
                curr = []
            else:
                curr.append((t, v))
        segments.append(curr)

        if self.ref_mode == "column":
            # === CSV mode ===
            out_path, _ = QFileDialog.getSaveFileName(
                self, "Export CSV", "", "CSV Files (*.csv)"
            )
            if not out_path:
                return

            if POLARS_AVAILABLE:
                df_out = pl.DataFrame()
            else:
                df_out = pd.DataFrame()
            for seg in segments:
                for action_type, value in seg:
                    if action_type == "column":
                        parts = value.split(" ▸ ")
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
                            if POLARS_AVAILABLE and fpath.lower().endswith(".csv"):
                                df_src = pl.read_csv(fpath)
                                df_out = df_out.with_columns(df_src[col].alias(col))
                            elif POLARS_AVAILABLE and fpath.lower().endswith(('.xls', '.xlsx')):
                                try:
                                    df_src = pl.read_excel(fpath, sheet_name=sheet)
                                    df_out = df_out.with_columns(df_src[col].alias(col))
                                except Exception:
                                    df_src = pd.read_excel(fpath, sheet_name=sheet)
                                    if isinstance(df_out, pl.DataFrame):
                                        df_out = df_out.with_columns(pl.Series(col, df_src[col].tolist()))
                                    else:
                                        df_out[col] = df_src[col]
                            elif fpath.lower().endswith(".csv"):
                                df_src = pd.read_csv(fpath)
                                if isinstance(df_out, pl.DataFrame):
                                    df_out = df_out.with_columns(pl.Series(col, df_src[col].tolist()))
                                else:
                                    df_out[col] = df_src[col]
                            else:
                                df_src = pd.read_excel(fpath, sheet_name=sheet)
                                if isinstance(df_out, pl.DataFrame):
                                    df_out = df_out.with_columns(pl.Series(col, df_src[col].tolist()))
                                else:
                                    df_out[col] = df_src[col]
                        except Exception as e:
                            if isinstance(df_out, pl.DataFrame):
                                df_out = df_out.with_columns(pl.Series(col, [f"Error: {e}"] * df_out.height))
                            else:
                                df_out[col] = f"Error: {e}"
                    elif action_type == "formula":
                        try:
                            # For now, formulas are processed with pandas fallback
                            if isinstance(df_out, pl.DataFrame):
                                pd_df = df_out.to_pandas()
                                result = self.process_formula(pd_df, value)
                                df_out = df_out.with_columns(pl.Series(f"Formula_{len(df_out.columns)}", result.tolist()))
                            else:
                                result = self.process_formula(df_out, value)
                                df_out[f"Formula_{len(df_out.columns)}"] = result
                        except Exception as e:
                            if isinstance(df_out, pl.DataFrame):
                                df_out = df_out.with_columns(pl.Series(f"Formula_{len(df_out.columns)}", [f"Error: {e}"] * df_out.height))
                            else:
                                df_out[f"Formula_{len(df_out.columns)}"] = f"Error: {e}"

            if isinstance(df_out, pl.DataFrame):
                df_out.write_csv(out_path)
            else:
                df_out.to_csv(out_path, index=False)
            self.add_action_history(f"Processed CSV: {os.path.basename(out_path)}")

        else:
            # === SHEET mode ===
            out_path, _ = QFileDialog.getSaveFileName(
                self, "Export Excel", "", "Excel Files (*.xlsx)"
            )
            if not out_path:
                return

            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                for idx, seg in enumerate(segments, start=1):
                    if POLARS_AVAILABLE:
                        df_sheet = pl.DataFrame()
                    else:
                        df_sheet = pd.DataFrame()
                    for action_type, value in seg:
                        if action_type == "column":
                            parts = value.split(" ▸ ")
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
                                if POLARS_AVAILABLE and fpath.lower().endswith(".csv"):
                                    df_src = pl.read_csv(fpath)
                                    df_sheet = df_sheet.with_columns(df_src[col].alias(col))
                                elif POLARS_AVAILABLE and fpath.lower().endswith(('.xls', '.xlsx')):
                                    try:
                                        df_src = pl.read_excel(fpath, sheet_name=sheet)
                                        df_sheet = df_sheet.with_columns(df_src[col].alias(col))
                                    except Exception:
                                        df_src = pd.read_excel(fpath, sheet_name=sheet)
                                        if isinstance(df_sheet, pl.DataFrame):
                                            df_sheet = df_sheet.with_columns(pl.Series(col, df_src[col].tolist()))
                                        else:
                                            df_sheet[col] = df_src[col]
                                elif fpath.lower().endswith(".csv"):
                                    df_src = pd.read_csv(fpath)
                                    if isinstance(df_sheet, pl.DataFrame):
                                        df_sheet = df_sheet.with_columns(pl.Series(col, df_src[col].tolist()))
                                    else:
                                        df_sheet[col] = df_src[col]
                                else:
                                    df_src = pd.read_excel(fpath, sheet_name=sheet)
                                    if isinstance(df_sheet, pl.DataFrame):
                                        df_sheet = df_sheet.with_columns(pl.Series(col, df_src[col].tolist()))
                                    else:
                                        df_sheet[col] = df_src[col]
                            except Exception as e:
                                if isinstance(df_sheet, pl.DataFrame):
                                    df_sheet = df_sheet.with_columns(pl.Series(col, [f"Error: {e}"] * df_sheet.height))
                                else:
                                    df_sheet[col] = f"Error: {e}"
                        elif action_type == "formula":
                            try:
                                if isinstance(df_sheet, pl.DataFrame):
                                    pd_df = df_sheet.to_pandas()
                                    result = self.process_formula(pd_df, value)
                                    df_sheet = df_sheet.with_columns(pl.Series(f"Formula_{len(df_sheet.columns)}", result.tolist()))
                                else:
                                    result = self.process_formula(df_sheet, value)
                                    df_sheet[f"Formula_{len(df_sheet.columns)}"] = result
                            except Exception as e:
                                if isinstance(df_sheet, pl.DataFrame):
                                    df_sheet = df_sheet.with_columns(pl.Series(f"Formula_{len(df_sheet.columns)}", [f"Error: {e}"] * df_sheet.height))
                                else:
                                    df_sheet[f"Formula_{len(df_sheet.columns)}"] = f"Error: {e}"

                    sheet_name = f"Prompt{idx}"
                    if isinstance(df_sheet, pl.DataFrame):
                        pd_df = df_sheet.to_pandas()
                        pd_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

            self.add_action_history(f"Processed Excel: {os.path.basename(out_path)}")

    def load_prompt(self, path, content):
        """Add a saved-prompt file to history & preview."""
        if any(p == path for p, _ in self.loaded_prompts):
            return
        self.loaded_prompts.append((path, content))
        item = QListWidgetItem(self.file_list_widget)
        w    = QWidget(); hl = QHBoxLayout(w)
        hl.setContentsMargins(4,2,4,2)
        hl.addWidget(QLabel(os.path.basename(path) + " (Prompt)"))
        hl.addStretch()
        btn = QPushButton("✕"); btn.setFixedSize(16,16)
        btn.setStyleSheet("border:none;color:red;")
        hl.addWidget(btn)
        item.setSizeHint(w.sizeHint())
        self.file_list_widget.setItemWidget(item, w)
        btn.clicked.connect(lambda *_,
                            it=item, p=path: self.remove_prompt(it, p))
        self.add_action_history(f"Loaded Prompt: {os.path.basename(path)}")
        self.update_columns()

    def remove_prompt(self, item, path):
        self.loaded_prompts = [(p, c) for p, c in self.loaded_prompts if p != path]
        self.file_list_widget.takeItem(self.file_list_widget.row(item))
        self.update_columns()

    def add_action_history(self, text):
        """Append an entry to Recent Actions."""
        self.actions_list_widget.addItem(text)

    # -- actions stack ---------------------------------------------------------

    def _add_action(self, action):
        self.redo_stack.clear()
        self.actions.append(action)
        self._update_prompt_area()

    def undo_action(self):
        if not self.actions:
            return
        a = self.actions.pop()
        self.redo_stack.append(a)
        self._update_prompt_area()

    def redo_action(self):
        if not self.redo_stack:
            return
        a = self.redo_stack.pop()
        self.actions.append(a)
        self._update_prompt_area()

    def _update_prompt_area(self):
        segments, curr = [], []
        for t, v in self.actions:
            if t == "break":
                segments.append(curr)
                curr = []
            else:
                curr.append(v)
        segments.append(curr)
        if self.formula_open:
            # Show open formula block in prompt
            if self.formula_buffer:
                formula_preview = f"[{self.current_formula} -> {' -> '.join(self.formula_buffer)}"
            else:
                formula_preview = f"[{self.current_formula}"
            if segments:
                segments[-1].append(formula_preview)
            else:
                segments = [[formula_preview]]
        texts = []
        for seg in segments:
            if seg:
                texts.append(" -> ".join(seg))
        self.prompt_area.setPlainText("\n\n".join(texts))

    # -- columns preview -------------------------------------------------------

    def update_columns(self):
        """
        Rebuild the column‐lists for all loaded files/sheets.
        Now each QListWidget supports ExtendedSelection
        so users can ctrl/shift‐click multiple items at once.
        """
        # clear old widgets
        for i in reversed(range(self.columns_layout.count())):
            w = self.columns_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        def make_file_cols(title, cols):
            box = QGroupBox(title)
            v   = QVBoxLayout(box)
            lst = QListWidget()
            # allow multi‐selection in this list
            lst.setSelectionMode(QAbstractItemView.ExtendedSelection)
            # whenever selection changes, add all selected items
            lst.itemSelectionChanged.connect(
                lambda t=title, l=lst: self._add_selected_columns(t, l.selectedItems())
            )
            for c in cols:
                lst.addItem(c)
            v.addWidget(lst)
            return box

        # real files
        for path in self.loaded_files:
            name, ext = os.path.basename(path), os.path.splitext(path)[1].lower()
            try:
                if POLARS_AVAILABLE and ext == ".csv":
                    df = pl.read_csv(path)
                    self.columns_layout.addWidget(
                        make_file_cols(name, df.columns)
                    )
                elif POLARS_AVAILABLE and ext in (".xls", ".xlsx"):
                    # polars supports xlsx via pyxlsb or openpyxl, but not all features
                    try:
                        sheets = pl.read_excel(path, sheet_id=None)
                        for sh, df in sheets.items():
                            title = f"{name} ▸ {sh}"
                            self.columns_layout.addWidget(
                                make_file_cols(title, df.columns)
                            )
                    except Exception:
                        # fallback to pandas
                        sheets = pd.read_excel(path, sheet_name=None)
                        for sh, df in sheets.items():
                            title = f"{name} ▸ {sh}"
                            self.columns_layout.addWidget(
                                make_file_cols(title, df.columns)
                            )
                elif ext == ".csv":
                    df = pd.read_csv(path)
                    self.columns_layout.addWidget(
                        make_file_cols(name, df.columns)
                    )
                else:
                    sheets = pd.read_excel(path, sheet_name=None)
                    for sh, df in sheets.items():
                        title = f"{name} ▸ {sh}"
                        self.columns_layout.addWidget(
                            make_file_cols(title, df.columns)
                        )
            except Exception as e:
                self.columns_layout.addWidget(
                    make_file_cols(f"{name} (error)", [str(e)])
                )

        # saved prompts
        for path, content in self.loaded_prompts:
            segments, cur = [], []
            for line in content.splitlines():
                if not line.strip():
                    if cur:
                        segments.append(" -> ".join(cur))
                        cur = []
                else:
                    cur.append(line)
            if cur:
                segments.append(" -> ".join(cur))
            box = QGroupBox(os.path.basename(path) + " (Prompt)")
            v   = QVBoxLayout(box)
            lst = QListWidget()
            for seg in segments:
                lst.addItem(seg)
            v.addWidget(lst)
            self.columns_layout.addWidget(box)

        self.columns_container.adjustSize()

    def _add_selected_columns(self, source, items):
        for it in items:
            entry = f"{source} ▸ {it.text()}"
            if self.formula_open:
                self.formula_buffer.append(entry)
                self._update_prompt_area()
            else:
                self.add_column_action(source, it.text())

    def add_column_action(self, source, column):
        """
        Record a column-click, respecting ref_mode.
        """
        if self.ref_mode == "sheet":
            val = source
        else:
            val = f"{source} ▸ {column}"
        if self.formula_open:
            self.formula_buffer.append(val)
            self._update_prompt_area()
        else:
            if any(a[0]=="column" and a[1]==val for a in self.actions):
                return
            self._add_action(("column", val))

    def create_new_file(self):
        """
        Prompt for a new CSV/XLSX filename, create an empty file,
        then load it into history & preview.
        """
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Create New File",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        if not path:
            return
        # create an empty DataFrame
        df = pd.DataFrame()
        if path.lower().endswith(".csv"):
            df.to_csv(path, index=False)
        else:
            with pd.ExcelWriter(path, engine="openpyxl") as w:
                df.to_excel(w, index=False)
        self.load_file(path)
        self.add_action_history(f"Created file: {os.path.basename(path)}")

    def prompt_custom_value(self):
        self.custom_input.show()
        self.custom_add_btn.show()
        self.custom_input.setFocus()

    def prompt_new_column(self):
        col, ok = QInputDialog.getText(
            self, "New Column", "Enter new column name:"
        )
        if ok and col:
            entry = f"add column <{col}>"
            if self.formula_open:
                self.formula_buffer.append(entry)
                self._update_prompt_area()
            else:
                self._add_action(("add_column", entry))

    def formula_selected(self, item):
        """Start a formula block in the prompt builder."""
        if self.formula_open:
            return  # Only one formula block at a time
        formula_name = item.text()
        self.formula_open = True
        self.current_formula = formula_name
        self.formula_buffer = []
        self._add_action(("formula_start", f"[{formula_name}"))
        self.formula_list.clearSelection()
        # Optionally, visually indicate formula block is open

    def close_formula_block(self):
        if not self.formula_open:
            return
        # Compose the formula block
        formula_content = " -> ".join(self.formula_buffer)
        formula_str = f"{self.current_formula} [{formula_content}]"
        self._add_action(("formula", formula_str))
        self.formula_open = False
        self.current_formula = None
        self.formula_buffer = []
        self._update_prompt_area()

    def keyPressEvent(self, event):
        # Close formula block on Enter if open
        if self.formula_open and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.close_formula_block()
        else:
            super().keyPressEvent(event)

    def process_formula(self, df, formula_str):
        """Process a formula on the dataframe"""
        try:
            return self.formula_processor.apply_formula(df, formula_str)
        except Exception as e:
            return pd.Series([f"Error: {str(e)}"] * len(df), index=df.index)


# --- FormulaEngine using polars ---
class FormulaEngine:
    def __init__(self, df):
        self.df = df

    # Arithmetic Operations
    def add(self, var1, var2=None):
        return self.df.select([pl.col(var1).sum(axis=1) + (pl.col(var2).sum(axis=1) if var2 else 0)]).to_series()

    def subtract(self, var1, var2):
        return self.df.select([pl.col(var1).sum(axis=1) - pl.col(var2).sum(axis=1)]).to_series()

    def multiply(self, var1, var2=None):
        return self.df.select([pl.col(var1).product(axis=1) * (pl.col(var2).product(axis=1) if var2 else 1)]).to_series()

    def divide(self, var1, var2):
        return self.df.select([pl.col(var1).sum(axis=1) / pl.col(var2).sum(axis=1)]).to_series()

    # Conditional Logic
    def if_condition(self, column, threshold, true_val, false_val):
        return (self.df[column] > float(threshold)).apply(lambda x: true_val if x else false_val)

    # Text Functions
    def concatenate(self, var1, var2=None, custom_text=''):
        base = self.df[var1].cast(pl.Utf8).apply(lambda row: ''.join(row) if isinstance(row, list) else str(row))
        extra = self.df[var2].cast(pl.Utf8).apply(lambda row: ''.join(row) if isinstance(row, list) else str(row)) if var2 else ''
        return base + custom_text + extra

    def upper(self, column):
        return self.df[column].str.to_uppercase()

    def lower(self, column):
        return self.df[column].str.to_lowercase()

    def title_case(self, column):
        return self.df[column].str.to_titlecase()

    def text_length(self, column):
        return self.df[column].str.lengths()

    def find_text(self, column, substring):
        return self.df[column].str.find(substring)

    # Date Functions
    def days_since(self, column):
        return (pl.lit(datetime.now()) - pl.col(column).str.strptime(pl.Datetime)).dt.days()

    def extract_year(self, column):
        return self.df[column].str.strptime(pl.Datetime).dt.year()

    def extract_month(self, column):
        return self.df[column].str.strptime(pl.Datetime).dt.month()

    def extract_day(self, column):
        return self.df[column].str.strptime(pl.Datetime).dt.day()

    # Aggregations
    def sumif(self, condition_col, condition_val, target_col):
        return self.df.filter(pl.col(condition_col) == condition_val)[target_col].sum()

    def countif(self, condition_col, condition_val):
        return (self.df[condition_col] == condition_val).sum()

    def averageif(self, condition_col, condition_val, target_col):
        return self.df.filter(pl.col(condition_col) == condition_val)[target_col].mean()

    # Lookup
    def vlookup(self, lookup_df, key_col, value_col):
        return self.df.join(lookup_df.select([key_col, value_col]), on=key_col, how='left')

    # Pivot and Unpivot
    def pivot_table(self, index, values, aggfunc='sum'):
        return self.df.pivot(index=index, values=values, aggregate_fn=aggfunc)

    def unpivot(self, id_vars, value_vars):
        return self.df.melt(id_vars=id_vars, value_vars=value_vars)

    # Duplicate and Unique
    def remove_duplicates(self):
        return self.df.unique()

    def count_unique(self, column):
        return self.df[column].n_unique()

    def mark_duplicates(self):
        return self.df.is_duplicated()

    # Error Handling
    def fillna(self, column, value):
        return self.df[column].fill_null(value)

    def iferror_divide(self, column):
        return self.df[column].apply(lambda x: 1/x if x != 0 else 'Error')

    # Array/Row-wise Operations
    def row_sum(self, columns):
        return self.df.select([pl.sum_horizontal([pl.col(c) for c in columns])]).to_series()

    # Statistical Functions
    def median(self, column):
        return self.df[column].median()

    def mode(self, column):
        return self.df[column].mode()

    def stddev(self, column):
        return self.df[column].std()

    def variance(self, column):
        return self.df[column].var()

    # Ranking
    def rank(self, column):
        return self.df[column].rank()

    def percentile(self, column):
        return self.df[column].rank(method='average', pct=True)

    # Transpose
    def transpose(self):
        return self.df.transpose()

    # Rounding
    def round_column(self, column, decimals=0):
        return self.df[column].round(decimals)

    def ceil_column(self, column):
        return self.df[column].apply(np.ceil)

    def floor_column(self, column):
        return self.df[column].apply(np.floor)

    # Rolling
    def rolling_mean(self, column, window):
        return self.df[column].rolling_mean(window)

# --- Temp file management ---
TEMP_DIR = os.path.join(os.getcwd(), 'tmp_playground')
os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup_temp_files():
    now = time.time()
    for fname in os.listdir(TEMP_DIR):
        fpath = os.path.join(TEMP_DIR, fname)
        if os.path.isfile(fpath):
            if now - os.path.getmtime(fpath) > 86400:  # 1 day
                try:
                    os.remove(fpath)
                except Exception:
                    pass

def start_periodic_cleanup():
    def loop():
        while True:
            cleanup_temp_files()
            time.sleep(3600)  # every hour
    t = threading.Thread(target=loop, daemon=True)
    t.start()

cleanup_temp_files()
start_periodic_cleanup()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PlaygroundPage()
    w.resize(1000, 700)
    w.show()
    sys.exit(app.exec_())
import pypandoc

# Master plan content for Data Studio in markdown format
data_studio_md = """
# Data Studio – Developer-Ready Master Plan

## 1. Overview
Data Studio is a desktop-based data processing and template execution application, designed to streamline file standardization, cleaning, transformation, and execution workflows with minimal manual intervention. The application is built for **Windows (initial phase)** using **Tkinter + ttkthemes** for UI, with a future plan to migrate to **PyQt/PySide** for cross-platform support.

---

## 2. Core Objectives
- Centralize all data-related tasks (import, cleaning, transformation, execution).
- Provide **template-driven processing** to ensure repeatability.
- Enable **column/file mapping** for renamed or missing files.
- Maintain **detailed logs** of every action and execution.
- Create a **minimal but modern UI** optimized for both normal and low-end devices.

---

## 3. Tech Stack
- **UI Framework (Phase 1):** Tkinter + ttkthemes
- **UI Framework (Phase 2):** PyQt/PySide
- **Data Processing:** Polars (preferred) over Pandas
- **File Handling:** Python built-in modules (`os`, `shutil`, `tempfile`)
- **Parallel Processing:** `concurrent.futures` / multiprocessing
- **File Formats Supported:** CSV, XLSX (via openpyxl), Parquet, JSON
- **OS Target:** Windows (Phase 1), macOS (Phase 2)

---

## 4. Default Project Structure
```
<Project Name>/
│── input_files/       # For uploaded files
│── output_files/      # For processed results
│── mappings/          # For encrypted templates
```

- User can change default storage path from **Settings**.

---

## 5. Core Features (Current Build Reference ✅)

### 5.1 Project Management ✅
- Create new projects with auto-folder structure.
- Recent Projects view with clickable project cards.
- Project status tags: **In Progress**, **Completed**.
- Open project directly from card.

### 5.2 File Handling ✅
- Import multiple files at once.
- Map renamed/missing files to correct ones.
- Search columns in preview panel.
- Confirm before removing a file.

### 5.3 Template Execution ✅
- Map missing columns before execution.
- Auto-update all template references after column/file rename (with confirmation).
- Save a **temporary template** before execution to prevent data loss.
- Allow retry after modifying template.

### 5.4 Playground Integration ✅
- Real-time progress bar with expandable step-by-step log.
- Show error step if execution fails.
- Estimated time remaining (optional).

### 5.5 Cleaning & Transformation ✅
- Remove Duplicates (no toggle).
- Standardize Formats.
- Preview filtered/cleaned data before confirming.
- Join, Split, Aggregate, Format Values (preview before execution).

### 5.6 Logging & Notifications ✅
- Notifications page for:
  - Execution logs
  - Template creation logs
  - Error logs
- Session logs for every action.
- Export logs from **Settings**.

---

## 6. Future Features (Not in Current Build)
- API integrations.
- Multi-step undo.
- Advanced analytics dashboard.
- Drag-and-drop UI for workflow creation.

---

## 7. UI Layout
**Home Page**
- Sidebar with icons + hover labels.
- Summary Cards: Active Projects, Processed Files, Data Volume.
- Recent Projects section.
- Recent Activity log.
- Quick Actions panel.

**Workspace Page**
- Data Sources panel (sortable by last used).
- File preview with column search.
- Templates section (no auto-filter by structure).

**Playground Page**
- Progress bar (expand/collapse).
- Step-by-step execution display.
- Retry after modification.

---

## 8. Developer Guidelines
- Keep processing efficient for low-end devices.
- Use Polars where possible for parallel processing.
- Avoid unnecessary real-time updates if performance cost is high.
- Use encrypted format for templates in `/mappings` folder.

---

## 9. Milestones
1. Core UI with Tkinter + ttkthemes ✅
2. Project structure automation ✅
3. File import & mapping system ✅
4. Template execution with Playground integration ✅
5. Logging & notifications ✅
6. Future migration to PyQt/PySide ⏳

---

## 10. Key References
- **Current Build Reference Items:** Marked with ✅
- **Phase 2 Migration:** Replace Tkinter with PyQt/PySide keeping functionality same.
"""

# Save markdown file
output_path = "/mnt/data/Data_Studio_Master_Plan.md"
pypandoc.convert_text(data_studio_md, 'md', format='md', outputfile=output_path, extra_args=['--standalone'])

output_path
# 📌 Data Studio + Playground - Master Plan

## 1. Overview
This document serves as the **master functional and technical reference** for the **Data Studio** and **Playground** modules.  
It consolidates objectives, finalized features, planned flows, and specific implementation notes for developer reference.

---

## 2. Objectives
1. Provide a **centralized data processing environment** with a user-friendly UI for:
   - Importing, cleaning, transforming, and executing templates (**Data Studio**)
   - Running, testing, and monitoring templates with detailed progress tracking (**Playground**)
2. Ensure **data integrity**, **error handling**, and **minimum data loss** in every workflow.
3. Maintain **cross-platform compatibility** (Windows first, macOS later) using efficient Python libraries.
4. **[CURRENT BUILD]** Provide **session logs**, **execution tracking**, and **error notifications** for transparency.

---

## 3. Key Features

### 3.1 Data Studio (Core Workflow)
#### Home Page
- **[CURRENT BUILD]** Sidebar with icons and hover labels.
- **[CURRENT BUILD]** Summary cards: **Active Projects, Processed Files, Data Volume** (dynamic or refresh option).
- **[CURRENT BUILD]** Recent Projects section with file count, status tags, clickable to open in Projects Page.
- **[CURRENT BUILD]** Recent Activity section (last 5 activities, expandable, timestamps, linked template/output).
- **[CURRENT BUILD]** Quick Actions panel: Import Files, Clean Data, Transform Data, Execute Template.

#### Project & File Management
- **[CURRENT BUILD]** Default project folder structure:  
  - `input_files/`  
  - `output_files/`  
  - `mappings/` (encrypted templates)
- **[CURRENT BUILD]** Allow changing default storage path in Settings.
- Clickable project cards → open in Projects Page.

#### Data Sources & File Preview
- **[CURRENT BUILD]** Sort files by last used (no manual reorder).
- **[CURRENT BUILD]** Confirmation before file removal.
- **[CURRENT BUILD]** Resizable file preview.
- **[CURRENT BUILD]** Search bar for finding columns in large datasets.

#### Cleaning & Transformation
- **[CURRENT BUILD]** No toggle switches for "Remove Duplicates" and "Standardize Format" — keep as selectable actions.
- **[CURRENT BUILD]** Preview filtered data before confirming.
- **[CURRENT BUILD]** Transformation preview for Join, Split, Aggregate, Format Values.

#### Template Management
- **[CURRENT BUILD]** No filtering templates by file structure.
- **[CURRENT BUILD]** Highlight mismatched columns when file doesn't match template.
- **[CURRENT BUILD]** Update all instances where renamed file/column appears in template.

---

### 3.2 Playground (Execution & Monitoring)
#### Execution Flow
- **[CURRENT BUILD]** Auto-save template before execution to prevent data loss.
- **[CURRENT BUILD]** If execution fails, save a temporary version for later retry.
- **[CURRENT BUILD]** Allow reviewing and modifying template before retry when mismatches or errors occur.
- **[CURRENT BUILD]** No retry from last successful step — users must retry from template.

#### Progress Tracking
- **[CURRENT BUILD]** Progress bar:
  - Collapsed: Overall % only.
  - Expanded: Step-by-step execution with overall %.
  - Optional: Estimated time remaining.
- **[CURRENT BUILD]** Log specific step where process fails.

#### Notifications & Logs
- **[CURRENT BUILD]** Execution logs, template creation logs, error logs on Notifications Page.
- **[CURRENT BUILD]** Manual clear option for notifications.
- **[CURRENT BUILD]** Separate detailed log for each Playground session.
- **[CURRENT BUILD]** Export logs from Settings.
- Logs can be auto-deleted after set time.

---

## 4. Technical Guidelines
- **UI Framework:** Tkinter + ttkthemes (**Windows Phase 1**) → PyQt/PySide (**macOS Phase 2**)
- **Data Processing:** Prefer Polars over Pandas for speed; use parallel processing where possible.
- **Storage:** Encrypted templates stored in `/mappings/`.
- **Backup:**  
  - Manual trigger only.  
  - Default: Export templates only (encrypted).  
  - Option to include input/output files.  
  - Notify on successful backup.

---

## 5. User Flow

### 5.1 Data Studio Workflow
1. **Home Page** → Select/Create Project.
2. **Import Files** → Stored in `input_files/`.
3. **Clean Data** (preview before applying).
4. **Transform Data** (preview before applying).
5. **Create/Update Template**.
6. **Execute Template** → Option to send to **Playground**.

### 5.2 Playground Workflow
1. **Select Template** (auto-saved version).
2. **Execution Starts** → Progress tracking visible.
3. If **error occurs**:
   - Save temp version.
   - Show failed step in logs.
   - Allow template review & retry.
4. **Execution Complete** → Output stored in `output_files/`.

---

## 6. Future Enhancements
- Real-time resource-based UI performance adjustment.
- Multi-step undo history.
- Project search & sorting.
- Multi-template batch execution in Playground.
- Cloud backup option.

---

## 7. Reference Notes
- **Consistency rule:** If file or column names change, confirm with user before updating all references.
- **Performance toggle:** Enable/disable real-time updates on low-end devices.
- **No icon overload:** Minimal UI visuals, functional-first approach.

---
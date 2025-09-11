# Playground – Master Plan

## Objective
The Playground is the **execution and testing environment** for templates in Data Studio.  
It provides a real-time, step-by-step view of the process, enabling:
- Execution of templates with live progress monitoring.
- Immediate feedback on errors, mismatches, or missing files/columns.
- Options to fix and retry without losing progress.
- Detailed session logs for review or export.

---

## Core Features (Current Build Reference ✅)
The following are **finalized** for the current build:

### 1. Execution Handling ✅
- Automatically **save the template before execution** to prevent data loss.
- Create a **temporary save** of the template during execution to preserve progress if execution fails.
- Allow retrying execution after **reviewing and modifying** the template if:
  - File names do not match.
  - Column names do not match.
  - Execution fails at any step.

### 2. Progress Display ✅
- **Collapsible progress bar**:
  - **Collapsed view** → Show overall progress percentage only.
  - **Expanded view** → Show:
    - Each step being executed.
    - Overall progress percentage.
    - *(Optional)* Estimated time remaining.
- Steps should display real-time updates (status: pending, in-progress, completed, failed).

### 3. Error Handling & Feedback ✅
- Log and display **specific step** where the process failed.
- Highlight mismatched columns in red for visual clarity.
- Allow user to fix issues and retry execution without restarting from scratch.

### 4. Logging & Session History ✅
- Maintain a **detailed session log** for every Playground run.
- Logs include:
  - Template name and execution time.
  - Files used (with paths).
  - Steps executed (with timestamps).
  - Errors encountered.
  - User actions taken during the run.
- Allow **exporting logs** from the Settings Page.
- Logs can be **auto-deleted after a set period**.

---

## Additional Planned Features (Future Iterations)
The following features are planned but **not in the current build**:

- **Parallel execution optimization** for large datasets.
- **Execution pause & resume** capability.
- Advanced **step-by-step debug mode**.
- Option to compare **expected vs. actual output** side-by-side after execution.
- Integration with **performance metrics** (memory usage, execution time per step).
- Multi-session view to run and monitor multiple executions at once.

---

## Workflow Flowchart (Current Build)
```plaintext
[User Loads Template]
        ↓
[Pre-Execution Checks]
  - Save template (permanent)
  - Save temp backup
  - Verify file mappings
  - Verify column mappings
        ↓
[Execution Starts]
  - Step 1 → Progress update
  - Step 2 → Progress update
  ...
        ↓
[Error?] → Yes → Highlight issue → Allow Fix & Retry
        ↓ No
[Execution Complete]
        ↓
[Log Saved & Session Ended]
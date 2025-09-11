
# Unified vs Legacy Formula Support in Data Studio

## Overview
To make Data Studio both **powerful** and **familiar**, we will allow users to choose between:
1. **Legacy Formulas** – Behaving exactly like Excel, Google Sheets, or SQL formulas they already know.
2. **Unified Formulas** – Smart, simplified versions that combine similar functions into a single, consistent formula.

---

## Why Support Both?
- **User Familiarity:** Users from Excel, Google Sheets, or SQL can use what they already know.
- **Learning Curve Reduction:** Beginners or business users can use simplified, unified formulas without worrying about subtle differences.
- **Flexibility:** Power users can switch modes depending on their workflow or preference.

---

## Example: Text Concatenation
- **Legacy Options:**
  - `CONCAT(A, B)` (Excel)
  - `CONCATENATE(A, B)` (Google Sheets)
  - `TEXTJOIN(" ", TRUE, A, B)` (Google Sheets advanced)
- **Unified Option:**
  - `JOIN(A, B, separator=" ")`

---

## Example: String Length
- **Legacy Options:**
  - `LEN(A)` (Excel & Google Sheets)
  - `LENGTH(A)` (SQL, Python-like syntax)
- **Unified Option:**
  - `STRLEN(A)` (Data Studio standard)

---

## Example: Conditional Logic
- **Legacy Options:**
  - `IF(condition, true_value, false_value)` (Excel/Sheets)
  - `CASE WHEN ... THEN ... ELSE ... END` (SQL)
- **Unified Option:**
  - `IF(condition, true, false)` (kept as universal standard)

---

## Example: Date Extraction
- **Legacy Options:**
  - `DAY(A)`, `MONTH(A)`, `YEAR(A)` (Excel/Sheets)
  - `EXTRACT(DAY FROM A)` (SQL)
- **Unified Option:**
  - `DATEPART(A, "day")`

---

## Example: Lookup Functions
- **Legacy Options:**
  - `VLOOKUP(key, table, index, FALSE)` (Excel)
  - `HLOOKUP(key, table, index, FALSE)` (Excel)
  - `LOOKUP(value, range)` (Google Sheets simplified)
- **Unified Option:**
  - `LOOKUP(key, table, axis="row"/"col")`

---

## Implementation Strategy
1. **Toggle in Settings:**
   - Mode: `Legacy` or `Unified`
   - Default: Unified (for simplicity)
2. **Parser Layer:**
   - Legacy formulas are mapped to Unified equivalents under the hood.
   - Error handling: If a formula fails in Unified mode, Data Studio suggests the Unified equivalent.
3. **Migration Support:**
   - When importing Excel/Sheets formulas, auto-convert to Unified where possible.

---

## Benefits
- Attracts **Excel/Sheets users** who want familiarity.
- Provides **simplicity for new users**.
- Encourages **consistency** across datasets, projects, and teams.
- Makes **Data Studio unique** in offering dual support.

---

## Future Expansion
- AI assistance to suggest Unified formulas when users type Legacy ones.
- One-click formula conversion tool (Legacy → Unified).
- Formula auto-completion to show both options.

---

## Conclusion
Supporting both **Legacy** and **Unified** formulas ensures:
- **Adoption** (no barrier for existing Excel/Sheets/SQL users).
- **Innovation** (clean, simplified functions for the future).
- **Differentiation** (Data Studio stands out among data platforms).

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def merge_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Step 1: Select multiple files (Excel or CSV)
    file_paths = filedialog.askopenfilenames(
        title="Select Excel or CSV files to merge",
        filetypes=[("Excel or CSV Files", "*.xlsx *.xls *.csv")]
    )
    if not file_paths:
        messagebox.showinfo("No files selected", "No files were selected. Exiting.")
        return

    # Step 2: Ask for sheet name (for Excel files)
    sheet_name = simple_input_dialog("Sheet Name", "Enter the Excel sheet name to merge (leave blank for first sheet):")
    if sheet_name is None:
        return

    # Step 3: Read and merge files
    merged_df = None
    for file in file_paths:
        ext = os.path.splitext(file)[1].lower()
        try:
            if ext in [".xlsx", ".xls"]:
                if sheet_name:
                    df = pd.read_excel(file, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(file)
            elif ext == ".csv":
                df = pd.read_csv(file)
            else:
                messagebox.showwarning("Unsupported file", f"Skipping unsupported file: {file}")
                continue
            if merged_df is None:
                merged_df = df
            else:
                merged_df = pd.concat([merged_df, df], ignore_index=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading {os.path.basename(file)}: {e}")
            return

    # Step 4: Save As dialog (Excel or CSV)
    output_path = filedialog.asksaveasfilename(
        title="Save merged file as",
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
    )
    if not output_path:
        messagebox.showinfo("No output file", "No output file selected. Exiting.")
        return

    # Step 5: Write merged data to output file
    try:
        if output_path.lower().endswith('.csv'):
            merged_df.to_csv(output_path, index=False)
        else:
            merged_df.to_excel(output_path, index=False)
        messagebox.showinfo("Success", f"Merged file saved as:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving file: {e}")

def simple_input_dialog(title, prompt):
    def on_ok():
        nonlocal user_input
        user_input = entry.get()
        dialog.destroy()

    user_input = None
    dialog = tk.Tk()
    dialog.title(title)
    tk.Label(dialog, text=prompt).pack(padx=10, pady=10)
    entry = tk.Entry(dialog)
    entry.pack(padx=10, pady=5)
    entry.focus_set()
    tk.Button(dialog, text="OK", command=on_ok).pack(pady=10)
    dialog.mainloop()
    return user_input

if __name__ == "__main__":
    merge_files()
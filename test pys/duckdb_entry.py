import duckdb
import polars as pl
import pandas as pd
import logging
import os
import glob
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def select_files_gui():
    """Open GUI file picker for selecting multiple files"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # Open file dialog for multiple files
        file_paths = filedialog.askopenfilenames(
            title="Select one or more files",
            filetypes=[
                ("All supported files", "*.csv;*.tsv;*.parquet;*.xlsx;*.xls;*.json"),
                ("CSV files", "*.csv"),
                ("TSV files", "*.tsv"),
                ("Parquet files", "*.parquet"),
                ("Excel files", "*.xlsx;*.xls"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            logger.info(f"Selected {len(file_paths)} files via GUI")
            return list(file_paths)
        else:
            logger.info("No files selected via GUI")
            return []
            
    except Exception as e:
        logger.error(f"Error in GUI file picker: {str(e)}")
        return []
    finally:
        root.destroy()

def select_folder_gui():
    """Open GUI folder picker for selecting a directory"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        folder_path = filedialog.askdirectory(
            title="Select folder containing files"
        )
        
        if folder_path:
            # Get all supported files in the folder
            supported_extensions = ['*.csv', '*.tsv', '*.parquet', '*.xlsx', '*.xls', '*.json']
            files = []
            
            for ext in supported_extensions:
                files.extend(glob.glob(os.path.join(folder_path, ext)))
                files.extend(glob.glob(os.path.join(folder_path, ext.upper())))
            
            if files:
                logger.info(f"Found {len(files)} files in selected folder")
                return files
            else:
                logger.warning("No supported files found in selected folder")
                return []
        else:
            logger.info("No folder selected via GUI")
            return []
            
    except Exception as e:
        logger.error(f"Error in GUI folder picker: {str(e)}")
        return []
    finally:
        root.destroy()

def get_file_paths():
    """Get file paths from user input - single file or multiple files"""
    print("\n=== File Import Options ===")
    print("1. Single file")
    print("2. Multiple files (wildcard pattern)")
    print("3. Multiple files (list)")
    print("4. GUI File Picker (select multiple files)")
    print("5. GUI Folder Picker (select folder)")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        file_path = input("Enter the full path to your file: ").strip()
        if os.path.exists(file_path):
            return [file_path]
        else:
            logger.error(f"File not found: {file_path}")
            return []
    
    elif choice == "2":
        pattern = input("Enter wildcard pattern (e.g., /path/to/*.csv): ").strip()
        files = glob.glob(pattern)
        if files:
            logger.info(f"Found {len(files)} files matching pattern")
            return files
        else:
            logger.error(f"No files found matching pattern: {pattern}")
            return []
    
    elif choice == "3":
        print("Enter file paths (one per line, press Enter twice when done):")
        files = []
        while True:
            file_path = input().strip()
            if not file_path:
                break
            if os.path.exists(file_path):
                files.append(file_path)
            else:
                logger.warning(f"File not found: {file_path}")
        
        return files
    
    elif choice == "4":
        print("Opening GUI file picker...")
        return select_files_gui()
    
    elif choice == "5":
        print("Opening GUI folder picker...")
        return select_folder_gui()
    
    else:
        logger.error("Invalid choice")
        return []

def get_column_names(file_path):
    """Get column names from a file using different methods"""
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext in ['.csv', '.tsv']:
            # Try with Polars first (faster)
            try:
                df = pl.read_csv(file_path)
                return df.columns
            except:
                # Fallback to pandas
                df = pd.read_csv(file_path)
                return list(df.columns)
        
        elif file_ext in ['.parquet']:
            try:
                df = pl.read_parquet(file_path)
                return df.columns
            except:
                df = pd.read_parquet(file_path)
                return list(df.columns)
        
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            return list(df.columns)
        
        elif file_ext in ['.json']:
            try:
                df = pl.read_json(file_path)
                return df.columns
            except:
                df = pd.read_json(file_path)
                return list(df.columns)
        
        else:
            # Try DuckDB for other formats
            con = duckdb.connect()
            result = con.execute(f"SELECT * FROM '{file_path}' LIMIT 0").fetchdf()
            con.close()
            return list(result.columns)
    
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return []

def display_column_names(file_paths):
    """Display column names for all files"""
    print("\n=== Column Names by File ===")
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"\n{i}. File: {os.path.basename(file_path)}")
        print(f"   Path: {file_path}")
        
        columns = get_column_names(file_path)
        
        if columns:
            print(f"   Columns ({len(columns)}):")
            for j, col in enumerate(columns, 1):
                print(f"     {j:2d}. {col}")
        else:
            print("   No columns found or error reading file")
        
        print("-" * 50)

def main():
    """Main function to run the file import and column display"""
    print("=== File Column Name Extractor ===")
    
    # Get file paths from user
    file_paths = get_file_paths()
    
    if not file_paths:
        print("No valid files selected. Exiting.")
        return
    
    # Display column names
    display_column_names(file_paths)
    
    # Original functionality (optional)
    if len(file_paths) == 1:
        show_data = input("\nWould you like to see the data from the first file? (y/n): ").strip().lower()
        if show_data == 'y':
            try:
                con = duckdb.connect()
                result = con.execute(f"SELECT * FROM '{file_paths[0]}'").fetchdf()
                print("\n=== Data Preview ===")
                print(result)
                con.close()
            except Exception as e:
                logger.error(f"Error displaying data: {str(e)}")

if __name__ == "__main__":
    main()
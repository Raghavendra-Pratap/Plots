import sys
import subprocess
import importlib.util

def check_and_install_packages():
    required_packages = ['tkinter', 'pyperclip']
    
    def is_package_installed(package_name):
        return importlib.util.find_spec(package_name) is not None
    
    def install_package(package_name):
        try:
            print(f"Installing {package_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"Successfully installed {package_name}")
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to install {package_name}")
            return False

    # Check and install missing packages
    missing_packages = [pkg for pkg in required_packages if not is_package_installed(pkg)]
    
    if missing_packages:
        print("Missing required packages. Installing...")
        for package in missing_packages:
            if not install_package(package):
                print(f"Error: Could not install {package}. Please install it manually using:")
                print(f"pip install {package}")
                sys.exit(1)
        print("All required packages installed successfully!")

# Run package check before importing
check_and_install_packages()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import string
import pyperclip
import csv

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("368x650")
        
        # Store passwords separately for clean copying and saving
        self.generated_passwords = []
        
        # Define special characters
        self.SPECIAL_CHARS = '@#$%&*=?'
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Checkboxes for character types
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)

        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Character Options", padding="10")
        options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)

        ttk.Checkbutton(options_frame, text="Uppercase Letters", variable=self.uppercase_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Lowercase Letters", variable=self.lowercase_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Special Characters (@#$%&*=?)", variable=self.special_var).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Numbers", variable=self.numbers_var).grid(row=3, column=0, sticky=tk.W, pady=5)

        # Length and Count Frame
        settings_frame = ttk.LabelFrame(main_frame, text="Password Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        # Password Length
        ttk.Label(settings_frame, text="Password Length:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.length_var = tk.StringVar(value="12")
        self.length_spinbox = ttk.Spinbox(settings_frame, from_=4, to=50, textvariable=self.length_var, width=10)
        self.length_spinbox.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Password Count
        ttk.Label(settings_frame, text="Number of Passwords:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.count_var = tk.StringVar(value="1")
        self.count_spinbox = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.count_var, width=10)
        self.count_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Generate Button
        ttk.Button(main_frame, text="Generate Passwords", command=self.generate_passwords).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)

        # Result Text Area
        result_frame = ttk.LabelFrame(main_frame, text="Generated Passwords", padding="10")
        result_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)

        self.result_text = tk.Text(result_frame, height=10, width=40, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text['yscrollcommand'] = scrollbar.set

        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)

        # Copy and Save buttons
        ttk.Button(buttons_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Save to CSV", command=self.save_to_csv).grid(row=0, column=1, padx=5)

    def generate_single_password(self, length, chars_dict):
        # Ensure we start with either a letter or number
        start_chars = ''
        if chars_dict['uppercase']: start_chars += chars_dict['uppercase']
        if chars_dict['lowercase']: start_chars += chars_dict['lowercase']
        if chars_dict['numbers']: start_chars += chars_dict['numbers']
        
        if not start_chars:  # If no letters or numbers selected, use whatever is available
            start_chars = ''.join(chars_dict.values())
        
        # Start with a letter or number
        password = [random.choice(start_chars)]
        
        # Initialize password with one character from each selected type
        for char_type, chars in chars_dict.items():
            if chars and not any(c in chars for c in password):  # Add character only if type not already represented
                password.append(random.choice(chars))
        
        # Fill the rest of the password length with random characters from all selected types
        all_chars = ''.join(chars_dict.values())
        while len(password) < length:
            password.append(random.choice(all_chars))
        
        # Shuffle all characters except the first one
        rest = password[1:]
        random.shuffle(rest)
        password = [password[0]] + rest
        
        return ''.join(password)

    def generate_unique_password(self, length, chars_dict, existing_passwords):
        max_attempts = 100  # Prevent infinite loop
        attempts = 0
        
        while attempts < max_attempts:
            # Generate a new password
            password = self.generate_single_password(length, chars_dict)
            
            # Check if this password is unique
            if password not in existing_passwords:
                return password
            
            attempts += 1
        
        # If we couldn't generate a unique password after max attempts
        raise ValueError("Unable to generate unique password after maximum attempts")

    def generate_passwords(self):
        self.result_text.delete(1.0, tk.END)
        self.generated_passwords = []

        try:
            length = int(self.length_var.get())
            count = int(self.count_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for length and count.")
            return

        # Create character sets based on selected options
        chars_dict = {
            'uppercase': ''.join(c for c in string.ascii_uppercase if c not in 'IO'),
            'lowercase': ''.join(c for c in string.ascii_lowercase if c not in 'l'),
            'special': self.SPECIAL_CHARS,
            'numbers': ''.join(c for c in string.digits if c not in '01O')
        }

        # Filter the character sets based on checkbox selection
        chars_dict = {
            'uppercase': chars_dict['uppercase'] if self.uppercase_var.get() else '',
            'lowercase': chars_dict['lowercase'] if self.lowercase_var.get() else '',
            'special': chars_dict['special'] if self.special_var.get() else '',
            'numbers': chars_dict['numbers'] if self.numbers_var.get() else ''
        }

        # Count selected options
        selected_types = sum(1 for chars in chars_dict.values() if chars)

        # Validate selections
        if not selected_types:
            messagebox.showerror("Error", "Please select at least one character type.")
            return

        if length < selected_types:
            messagebox.showerror("Error", f"Password length must be at least {selected_types} to include all selected character types.")
            return

        # Calculate maximum possible unique passwords
        all_chars = ''.join(chars_dict.values())
        max_possible = self.calculate_max_unique_passwords(length, chars_dict)

        if count > max_possible:
            messagebox.showerror(
                "Error",
                f"Cannot generate {count} unique passwords with current settings.\n"
                f"Maximum possible unique passwords: {max_possible}"
            )
            return

        # Generate unique passwords
        try:
            for i in range(count):
                try:
                    password = self.generate_unique_password(length, chars_dict, self.generated_passwords)
                    self.generated_passwords.append(password)
                    self.result_text.insert(tk.END, f"{i+1}. {password}\n")
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return

    def calculate_max_unique_passwords(self, length, chars_dict):
        # Get all available characters
        all_chars = ''.join(chars_dict.values())
        
        # Calculate the theoretical maximum based on character combinations
        # This is a simplified calculation that doesn't account for the requirement
        # of having at least one character from each selected type
        theoretical_max = len(all_chars) ** length
        
        # Return a reasonable maximum (can be adjusted based on needs)
        return min(theoretical_max, 1000000)  # Cap at 1 million to prevent excessive calculations

    def copy_to_clipboard(self):
        if not self.generated_passwords:
            messagebox.showwarning("Warning", "No passwords to copy!")
            return
            
        # Join passwords with newlines, without sequence numbers
        passwords_text = '\n'.join(self.generated_passwords)
        pyperclip.copy(passwords_text)
        messagebox.showinfo("Success", "Passwords copied to clipboard!")

    def save_to_csv(self):
        if not self.generated_passwords:
            messagebox.showwarning("Warning", "No passwords to save!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Passwords as CSV"
        )

        if file_path:
            try:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Password'])  # Header
                    for password in self.generated_passwords:
                        writer.writerow([password])
                messagebox.showinfo("Success", "Passwords saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = PasswordGeneratorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
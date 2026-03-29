import subprocess
import sys
import importlib
import os
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import secrets
import string
import math

# Path to the requirements.txt file
requirements_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../requirements.txt'))


# List of required packages from requirements.txt
def get_required_packages():
    with open(requirements_path, 'r') as file:
        packages = [line.strip() for line in file if line.strip()]
    return packages


def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def check_and_install_packages():
    packages = get_required_packages()
    for package in packages:
        try:
            importlib.import_module(package.split('==')[0])
        except ImportError:
            print(f"Package '{package}' not found. Installing...")
            install_package(package)
        else:
            print(f"Package '{package}' is already installed.")


# Perform package checks and installations
check_and_install_packages()


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("450x550")
        self.root.title("Password Generator")

        # Customization variables
        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar()
        self.exclude_ambiguous_var = tk.BooleanVar()
        self.password_var = tk.StringVar()
        self.password_length_var = tk.IntVar(value=12)

        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Character types frame
        type_frame = ttk.LabelFrame(main_frame, text="Character Types")
        type_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(type_frame, text="Uppercase (A-Z)", variable=self.uppercase_var).pack(anchor=tk.W)
        ttk.Checkbutton(type_frame, text="Lowercase (a-z)", variable=self.lowercase_var).pack(anchor=tk.W)
        ttk.Checkbutton(type_frame, text="Digits (0-9)", variable=self.digits_var).pack(anchor=tk.W)
        ttk.Checkbutton(type_frame, text="Symbols (!@#...)", variable=self.symbols_var).pack(anchor=tk.W)

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(options_frame, text="Exclude ambiguous characters (l,1,O,0)",
                        variable=self.exclude_ambiguous_var).pack(anchor=tk.W)

        # Length selection
        length_frame = ttk.Frame(main_frame)
        length_frame.pack(fill=tk.X, pady=5)

        ttk.Label(length_frame, text="Password Length:").pack(side=tk.LEFT)
        self.length_spin = ttk.Spinbox(length_frame, from_=8, to=32,
                                       textvariable=self.password_length_var, width=5)
        self.length_spin.pack(side=tk.RIGHT)
        self.length_spin.configure(validate="key",
                                   validatecommand=(self.root.register(self.validate_length), '%P'))

        # Generate button
        ttk.Button(main_frame, text="Generate Password", command=self.generate_password).pack(pady=10)

        # Password display
        pass_frame = ttk.Frame(main_frame)
        pass_frame.pack(fill=tk.X, pady=5)

        ttk.Label(pass_frame, textvariable=self.password_var, font=('TkFixedFont 12'),
                  wraplength=400, anchor=tk.CENTER).pack(fill=tk.X)

        # Strength indicator
        self.strength_label = ttk.Label(main_frame, text="Strength: None", font=('Arial', 10))
        self.strength_label.pack(pady=5)

        # Copy button
        self.copy_btn = ttk.Button(main_frame, text="Copy to Clipboard",
                                   command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=5)

    def validate_length(self, value):
        """Ensure password length is valid"""
        if value.isdigit():
            return 8 <= int(value) <= 32
        return False

    def generate_password(self):
        """Generate password based on current settings"""
        # Collect character sets
        chars = []
        if self.uppercase_var.get():
            chars.extend(string.ascii_uppercase)
        if self.lowercase_var.get():
            chars.extend(string.ascii_lowercase)
        if self.digits_var.get():
            chars.extend(string.digits)
        if self.symbols_var.get():
            chars.extend(string.punctuation)

        # Filter ambiguous characters
        if self.exclude_ambiguous_var.get():
            ambiguous = {'l', 'I', '1', 'O', '0'}
            chars = [c for c in chars if c not in ambiguous]

        # Check for valid character set
        if not chars:
            messagebox.showerror("Error", "Please select at least one character type!")
            return

        # Generate password
        try:
            length = self.password_length_var.get()
            password = ''.join(secrets.choice(chars) for _ in range(length))
            self.password_var.set(password)
            self.update_strength_indicator(chars, length)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_strength_indicator(self, chars, length):
        """Update password strength display"""
        char_count = len(chars)
        entropy = length * math.log2(char_count) if char_count else 0

        if entropy < 50:
            strength = "Weak"
            color = "red"
        elif entropy < 80:
            strength = "Moderate"
            color = "orange"
        else:
            strength = "Strong"
            color = "green"

        self.strength_label.config(text=f"Strength: {strength} ({entropy:.1f} bits)", foreground=color)

    def copy_to_clipboard(self):
        """Copy password to clipboard with visual feedback"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.password_var.get())
        self.copy_btn.config(text="Copied!")
        self.root.after(2000, lambda: self.copy_btn.config(text="Copy to Clipboard"))


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = PasswordGeneratorApp(root)
    root.mainloop()
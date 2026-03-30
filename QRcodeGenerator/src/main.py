import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import os
from pathlib import Path


class QRCodeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        self.qr_image = None
        # Use a proper temp directory instead of current directory
        self.qr_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "qrcode.png")
        
        # Title
        title = tk.Label(root, text="QR Code Generator", font=("Arial", 18, "bold"))
        title.pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(input_frame, text="Enter URL:", font=("Arial", 12)).pack(anchor="w")
        self.url_entry = tk.Entry(input_frame, font=("Arial", 11), width=50)
        self.url_entry.pack(pady=5, fill="x")
        self.url_entry.bind("<Return>", lambda e: self.generate_qr())
        
        # Button frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Generate QR Code", command=self.generate_qr, 
                  bg="#4CAF50", fg="white", font=("Arial", 11), padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(button_frame, text="Save As", command=self.save_qr, 
                  bg="#2196F3", fg="white", font=("Arial", 11), padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_all, 
                  bg="#f44336", fg="white", font=("Arial", 11), padx=15, pady=8).pack(side="left", padx=5)
        
        # Image display frame
        self.image_label = tk.Label(root, bg="lightgray", width=300, height=300)
        self.image_label.pack(pady=20, padx=20)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
    
    def generate_qr(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL")
            return
        
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            
            self.qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Ensure directory exists and save with error handling
            os.makedirs(os.path.dirname(self.qr_path), exist_ok=True)
            self.qr_image.save(self.qr_path)
            
            self.display_qr()
            self.status_var.set(f"QR Code generated for: {url}")
            messagebox.showinfo("Success", "QR Code generated successfully!")
        
        except PermissionError:
            messagebox.showerror("Permission Error", "Permission denied. Try running as Administrator or check file permissions.")
            self.status_var.set("Permission error")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
            self.status_var.set("Error generating QR code")
    
    def display_qr(self):
        if self.qr_image:
            photo = ImageTk.PhotoImage(self.qr_image.resize((300, 300)))
            self.image_label.config(image=photo)
            self.image_label.image = photo
    
    def save_qr(self):
        if not self.qr_image:
            messagebox.showwarning("No QR Code", "Generate a QR code first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.qr_image.save(file_path)
                messagebox.showinfo("Success", f"QR Code saved to:\n{file_path}")
                self.status_var.set(f"Saved to: {file_path}")
            except PermissionError:
                messagebox.showerror("Permission Error", "Permission denied. Choose a different location or check file permissions.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def clear_all(self):
        self.url_entry.delete(0, tk.END)
        self.image_label.config(image="")
        self.image_label.image = None
        self.qr_image = None
        self.status_var.set("Cleared")


if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorGUI(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
from PIL import Image
import os
from typing import List, Tuple

class ImageConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        self.root.geometry("800x600")
        
        # Store selected files
        self.files: List[str] = []
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File list
        self.create_file_list()
        
        # Buttons frame
        self.create_buttons()
        
        # Options frame
        self.create_options()
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def create_file_list(self):
        # Create frame for file list and scrollbar
        list_frame = ttk.Frame(self.main_frame)
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create listbox and scrollbar
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def create_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        ttk.Button(button_frame, text="Add Files", command=self.add_files).grid(row=0, column=0, pady=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).grid(row=1, column=0, pady=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).grid(row=2, column=0, pady=5)

    def create_options(self):
        options_frame = ttk.LabelFrame(self.main_frame, text="Conversion Options", padding="5")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Target format
        ttk.Label(options_frame, text="Convert to:").grid(row=0, column=0, padx=5)
        self.target_format = tk.StringVar(value="JPG")
        ttk.Radiobutton(options_frame, text="JPG", variable=self.target_format, value="JPG").grid(row=0, column=1)
        ttk.Radiobutton(options_frame, text="PNG", variable=self.target_format, value="PNG").grid(row=0, column=2)
        
        # Resize options
        ttk.Label(options_frame, text="Max Width:").grid(row=1, column=0, padx=5)
        self.max_width = ttk.Entry(options_frame, width=10)
        self.max_width.grid(row=1, column=1)
        
        ttk.Label(options_frame, text="Max Height:").grid(row=1, column=2, padx=5)
        self.max_height = ttk.Entry(options_frame, width=10)
        self.max_height.grid(row=1, column=3)
        
        # Maintain aspect ratio
        self.maintain_aspect = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Maintain Aspect Ratio", variable=self.maintain_aspect).grid(row=1, column=4, padx=5)
        
        # Add overwrite option before the output folder
        self.overwrite = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame, 
            text="Overwrite in same directory", 
            variable=self.overwrite,
            command=self.toggle_output_controls
        ).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Output folder (now in row 3)
        self.output_folder_btn = ttk.Button(
            options_frame, 
            text="Select Output Folder", 
            command=self.select_output_folder
        )
        self.output_folder_btn.grid(row=3, column=0, columnspan=2, pady=5)
        self.output_folder = tk.StringVar()
        self.output_folder_label = ttk.Label(options_frame, textvariable=self.output_folder)
        self.output_folder_label.grid(row=3, column=2, columnspan=3, sticky=tk.W)
        
        # Convert button (now in row 4)
        ttk.Button(options_frame, text="Convert Selected", command=self.convert_images).grid(row=4, column=0, columnspan=5, pady=10)

    def add_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))

    def remove_selected(self):
        selected = self.file_listbox.curselection()
        for index in reversed(selected):
            self.file_listbox.delete(index)
            self.files.pop(index)

    def clear_all(self):
        self.file_listbox.delete(0, tk.END)
        self.files.clear()

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def calculate_new_dimensions(self, image: Image.Image, max_width: int, max_height: int) -> Tuple[int, int]:
        width, height = image.size
        if not max_width and not max_height:
            return width, height
            
        if self.maintain_aspect.get():
            if max_width and max_height:
                ratio = min(max_width/width, max_height/height)
            elif max_width:
                ratio = max_width/width
            else:
                ratio = max_height/height
            
            return int(width * ratio), int(height * ratio)
        else:
            return (max_width or width), (max_height or height)

    def toggle_output_controls(self):
        """Enable/disable output folder controls based on overwrite option"""
        if self.overwrite.get():
            self.output_folder_btn.state(['disabled'])
            self.output_folder.set("")
        else:
            self.output_folder_btn.state(['!disabled'])

    def convert_images(self):
        if not self.overwrite.get() and not self.output_folder.get():
            messagebox.showerror("Error", "Please select an output folder or enable overwrite option")
            return
            
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select files to convert")
            return
            
        try:
            max_width = int(self.max_width.get()) if self.max_width.get() else 0
            max_height = int(self.max_height.get()) if self.max_height.get() else 0
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dimensions")
            return
            
        target_ext = ".jpg" if self.target_format.get() == "JPG" else ".png"
        
        for index in selected:
            try:
                # Open image
                with Image.open(self.files[index]) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Resize if needed
                    new_width, new_height = self.calculate_new_dimensions(img, max_width, max_height)
                    if (new_width, new_height) != img.size:
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Save with new format
                    base_name = os.path.splitext(os.path.basename(self.files[index]))[0]
                    if self.overwrite.get():
                        output_path = os.path.join(os.path.dirname(self.files[index]), base_name + target_ext)
                    else:
                        output_path = os.path.join(self.output_folder.get(), base_name + target_ext)
                    img.save(output_path)
            
            except Exception as e:
                messagebox.showerror("Error", f"Error converting {os.path.basename(self.files[index])}: {str(e)}")
                continue
        
        messagebox.showinfo("Success", "Conversion completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterGUI(root)
    root.mainloop()

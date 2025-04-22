import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
from pathlib import Path

class ToolTip:
    """Class to create tooltips for widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 10))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def manage_files():
    try:
        with open("path.txt", "r") as f:
            managing_path = Path(f.read().strip())
    except FileNotFoundError:
        messagebox.showerror("Error", "path.txt not found.")
        return

    if not managing_path.is_dir():
        messagebox.showerror("Error", f"The path {managing_path} is not a valid directory.")
        return

    # Define categories with their corresponding file extensions
    categories = {
        "PDF Files": ['.pdf'],
        "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp','.webp','.jpg_large','.ashx','.avif'],
        "Text Files": ['.txt', '.html', '.c', '.py', '.docx', '.md'],
        "Audio Files": ['.mp3', '.wav', '.aac', '.flac', '.ogg'],
        "Video Files": ['.mp4', '.mkv', '.avi', '.mov', '.wmv'],
        "Others": []  # Files that don't fit into any category
    }

    moved_files = []
    total_files = sum(1 for file in managing_path.iterdir() if file.is_file())
    if total_files == 0:
        messagebox.showinfo("No Files", "No files found in the specified directory.")
        return

    progress['maximum'] = total_files
    progress['value'] = 0
    progress.start()

    for file in managing_path.iterdir():
        if file.is_file():
            moved = False
            for category, extensions in categories.items():
                if extensions and file.suffix.lower() in extensions:
                    dest_folder = managing_path / category
                    dest_folder.mkdir(exist_ok=True)
                    shutil.move(str(file), str(dest_folder))
                    moved_files.append(f"MOVED - {file.name} to {category}/\n")
                    moved = True
                    break
            if not moved:
                # If no category matched, move to 'Others'
                dest_folder = managing_path / "Others"
                dest_folder.mkdir(exist_ok=True)
                shutil.move(str(file), str(dest_folder))
                moved_files.append(f"MOVED - {file.name} to Others/\n")
            progress['value'] += 1
            top.update_idletasks()

    moved_files.append("Process Completed\n")

    # Write logs to output.txt
    with open("output.txt", "a") as f:
        f.writelines(moved_files)

    # Update the output Text widget
    output.config(state=tk.NORMAL)
    output.insert(tk.END, ''.join(moved_files))
    output.see(tk.END)  # Scroll to the end
    output.config(state=tk.DISABLED)

    progress.stop()
    progress['value'] = 0  # Reset progress bar

def read_data():
    if not Path("output.txt").exists():
        return ""
    with open("output.txt", "r") as f:
        return f.read()

def save_path():
    inp = path_entry.get()
    if not Path(inp).is_dir():
        messagebox.showerror("Invalid Path", "The provided path does not exist or is not a directory.")
        return
    with open("path.txt", "w") as f:
        f.write(inp)
    messagebox.showinfo("Success", "Path saved successfully.")
    # Clear and update the output log
    output.config(state=tk.NORMAL)
    output.delete(1.0, tk.END)
    output.insert(tk.END, "Path saved successfully.\n")
    output.config(state=tk.DISABLED)

def show_instructions():
    instructions = (
        "1. Enter the directory path where you want to organize your files.\n"
        "2. Click 'Confirm' to save the path.\n"
        "3. Click 'Manage' to organize the files into respective folders.\n"
        "4. The 'OUTPUT' section will display the actions performed."
    )
    messagebox.showinfo("Instructions", instructions)

def create_menu():
    global output, path_entry, progress, top

    # Initialize main window
    top = tk.Tk()
    top.title("Destinii File Manager")
    top.geometry("800x600")
    top.resizable(False, False)  # Prevent resizing for consistent layout

    # Define a style
    style = ttk.Style(top)
    style.theme_use('clam')  # Use 'clam' theme for better aesthetics

    # Customize styles
    style.configure("TFrame", background="#f0f0f0")
    style.configure("Header.TLabel", font=("Arial", 20, "bold"), background="#4a90e2", foreground="white")
    style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
    style.configure("TButton", font=("Arial", 12, "bold"), padding=6)
    style.configure("Output.TLabel", font=("Arial", 14, "bold"), background="#f0f0f0")
    style.configure("TEntry", font=("Arial", 12))

    # Header
    header = ttk.Label(top, text="DESTINII", style="Header.TLabel", anchor="center")
    header.pack(fill=tk.X, pady=10)

    # Main Frame
    main_frame = ttk.Frame(top, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Path Entry Section
    path_label = ttk.Label(main_frame, text="Enter the path where File Management will be Active:")
    path_label.grid(row=0, column=0, sticky=tk.W, pady=5)

    path_entry = ttk.Entry(main_frame, width=60)
    path_entry.grid(row=1, column=0, sticky=tk.W, pady=5)

    # Buttons Frame
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.grid(row=2, column=0, sticky=tk.W, pady=10)

    instructions_btn = ttk.Button(buttons_frame, text="Instructions", command=show_instructions)
    instructions_btn.grid(row=0, column=0, padx=5)
    ToolTip(instructions_btn, "Click to view instructions")

    confirm_btn = ttk.Button(buttons_frame, text="Confirm", command=save_path)
    confirm_btn.grid(row=0, column=1, padx=5)
    ToolTip(confirm_btn, "Click to confirm and save the path")

    # Manage Button
    manage_btn = ttk.Button(main_frame, text="Manage", command=manage_files)
    manage_btn.grid(row=3, column=0, sticky=tk.W, pady=10)
    ToolTip(manage_btn, "Click to organize files into respective folders")

    # Progress Bar
    progress = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate', length=400)
    progress.grid(row=4, column=0, sticky=tk.W, pady=10)

    # Output Section
    output_label = ttk.Label(main_frame, text="OUTPUT")
    output_label.grid(row=5, column=0, sticky=tk.W, pady=(20, 5))

    output = tk.Text(main_frame, height=15, width=80, state=tk.DISABLED, bg="#ffffff", fg="#000000", font=("Arial", 10))
    output.grid(row=6, column=0, pady=5, sticky=tk.W)

    # Scrollbar for Output Text
    scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=output.yview)
    scrollbar.grid(row=6, column=1, sticky='ns', pady=5)
    output['yscrollcommand'] = scrollbar.set

    # Load existing output
    existing_output = read_data()
    output.config(state=tk.NORMAL)
    output.insert(tk.END, existing_output)
    output.config(state=tk.DISABLED)

    # Add padding to all child widgets in main_frame
    for child in main_frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    # Keyboard Shortcuts
    top.bind('<Control-s>', lambda event: save_path())
    top.bind('<Control-m>', lambda event: manage_files())

    top.mainloop()

if __name__ == "__main__":
    create_menu()

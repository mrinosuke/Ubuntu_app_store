import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import json
import os

# JSON থেকে অ্যাপ লোড করা
def load_apps(category):
    file_name = f"{category}.json"
    if not os.path.exists(file_name):
        messagebox.showerror("Error", f"{file_name} file not found!")
        return {}
    
    with open(file_name, "r") as file:
        return json.load(file)

# অ্যাপ ইনস্টল করা
def install_app(app_name, command, progress_bar, status_label):
    def run_install():
        progress_bar["value"] = 0
        progress_bar.start(10)
        status_label.config(text="Installing...")

        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            for line in process.stdout:
                if "Progress" in line or "%" in line:
                    try:
                        percent = int(line.split('%')[0].strip().split()[-1])
                        progress_bar["value"] = percent
                    except ValueError:
                        pass

            process.wait()
            if process.returncode == 0:
                messagebox.showinfo("Success", f"{app_name} installed successfully!")
                status_label.config(text="Installed")
            else:
                messagebox.showerror("Error", f"Failed to install {app_name}")
                status_label.config(text="Failed")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        progress_bar.stop()
    
    threading.Thread(target=run_install, daemon=True).start()

# GUI তৈরি
root = tk.Tk()
root.title("Ubuntu App Store")
root.geometry("600x500")

# সেক্টর এর জন্য বাটন তৈরি
category_buttons_frame = ttk.Frame(root)
category_buttons_frame.pack(fill="x", pady=10)

# ক্যাটেগরির তালিকা
categories = ["hacking", "office", "coding", "etc"]

# সেক্টরের জন্য UI তৈরি
for i, category in enumerate(categories):
    button = ttk.Button(category_buttons_frame, text=category.capitalize(), 
                        command=lambda cat=category: show_category(cat, category_frames))
    button.pack(side="left", padx=10, pady=5)

# একটি ফাংশন যোগ করা হবে যেটি ট্যাব পরিবর্তন করবে
category_frames = {}

def show_category(category, category_frames):
    for frame in category_frames.values():
        frame.pack_forget()  # পুরানো সেক্টর লুকিয়ে ফেলুন
    
    if category not in category_frames:
        frame = ttk.Frame(root, padding=10)
        category_frames[category] = frame
        apps = load_apps(category)

        # স্ক্রলেবল ফ্রেম
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        for app_name, command in apps.items():
            row = ttk.Frame(scrollable_frame)
            row.pack(fill="x", padx=10, pady=2)

            app_label = ttk.Label(row, text=app_name, width=25, anchor="w")
            app_label.pack(side="left")

            progress_bar = ttk.Progressbar(row, orient="horizontal", length=100, mode="determinate")
            progress_bar.pack(side="right", padx=5)

            status_label = ttk.Label(row, text="Pending", width=10)
            status_label.pack(side="right")

            install_button = ttk.Button(row, text="Install", 
                                        command=lambda n=app_name, c=command, p=progress_bar, s=status_label: install_app(n, c, p, s))
            install_button.pack(side="right")

        # ক্যানভাসের স্ক্রল করার জন্য উইন্ডো সাইজ পরিবর্তন করলে ক্যানভাসের সাইজ আপডেট হবে
        def on_canvas_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", on_canvas_configure)

    category_frames[category].pack(fill="both", expand=True)

# প্রথম সেক্টর দেখানোর জন্য
show_category(categories[0], category_frames)

# Tkinter এর মূল লুপ
root.mainloop()

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkthemes import ThemedTk
from tkinter import ttk
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import tweepy
import facebook
import requests

# Directory to store notes
NOTES_DIR = "saved_notes"
os.makedirs(NOTES_DIR, exist_ok=True)

# Global variable to store the current file path
current_file_path = None

# Note saving, opening, and deleting functions
def save_note():
    note_text = text_area.get("1.0", tk.END).strip()
    global current_file_path
    if note_text:
        if current_file_path:
            with open(current_file_path, "w", encoding="utf-8") as file:
                file.write(note_text)
            messagebox.showinfo("Success", "Note saved successfully!")
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(note_text)
                messagebox.showinfo("Success", "Note saved successfully!")
                current_file_path = file_path
    else:
        messagebox.showwarning("Warning", "Cannot save an empty note.")

def open_note():
    global current_file_path
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, file.read())
        current_file_path = file_path

def delete_note():
    if text_area.get("1.0", tk.END).strip():
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this note?"):
            text_area.delete("1.0", tk.END)
            global current_file_path
            current_file_path = None
            messagebox.showinfo("Success", "Note deleted successfully!")
    else:
        messagebox.showwarning("Warning", "No note to delete.")

# Google Drive Authentication and Upload
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def google_drive_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def upload_to_google_drive(file_path):
    try:
        service = google_drive_authenticate()
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype='text/plain')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        messagebox.showinfo("Success", "Note uploaded to Google Drive!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload to Google Drive: {e}")

# Social Media Sharing
def share_on_twitter(note_text):
    try:
        auth = tweepy.OAuth1UserHandler(consumer_key="YOUR_CONSUMER_KEY", consumer_secret="YOUR_CONSUMER_SECRET", access_token="YOUR_ACCESS_TOKEN", access_token_secret="YOUR_ACCESS_TOKEN_SECRET")
        api = tweepy.API(auth)
        api.update_status(note_text)
        messagebox.showinfo("Success", "Note shared on Twitter!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to share on Twitter: {e}")

def share_on_facebook(note_text):
    try:
        graph = facebook.GraphAPI(access_token="YOUR_FACEBOOK_ACCESS_TOKEN")
        graph.put_object(parent_object='me', connection_name='feed', message=note_text)
        messagebox.showinfo("Success", "Note shared on Facebook!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to share on Facebook: {e}")

def share_on_instagram(note_text):
    try:
        response = requests.post("https://graph.instagram.com/me/media",
                                 params={"access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN", "caption": note_text})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Note shared on Instagram!")
        else:
            messagebox.showerror("Error", "Failed to share on Instagram.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to share on Instagram: {e}")

# Toggle Dark Mode
def toggle_dark_mode():
    global dark_mode
    if dark_mode:
        root.style.theme_use("default")
        text_area.config(bg="white", fg="black")
    else:
        root.style.theme_use("equilux")
        text_area.config(bg="#15202B", fg="white")
    dark_mode = not dark_mode

# Main app window
root = ThemedTk(theme="default")
root.title("Notepad")
root.geometry("600x500")
root.style = ttk.Style()

# Sidebar frame
sidebar = tk.Frame(root, bg="#1DA1F2", width=100, height=500)
sidebar.pack(side="left", fill="y")

# Menu Bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# File Menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New Note", command=lambda: text_area.delete("1.0", tk.END))
file_menu.add_command(label="Save Note (Ctrl+S)", command=save_note)
file_menu.add_command(label="Open Note (Ctrl+O)", command=open_note)
file_menu.add_command(label="Delete Note", command=delete_note)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Sidebar Buttons
buttons = [
    ("📝 New", lambda: text_area.delete("1.0", tk.END)),
    ("💾 Save", save_note),
    ("📂 Open", open_note),
    ("🗑 Delete", delete_note),
    ("🌙 Dark Mode", toggle_dark_mode),
    ("🐦 Twitter", lambda: share_on_twitter(text_area.get("1.0", tk.END))),
    ("📘 Facebook", lambda: share_on_facebook(text_area.get("1.0", tk.END))),
    ("📸 Instagram", lambda: share_on_instagram(text_area.get("1.0", tk.END))),
    ("☁️ Google Drive", lambda: upload_to_google_drive("your_note_path_here"))
]

# Add all buttons to the sidebar
for text, cmd in buttons:
    ttk.Button(sidebar, text=text, command=cmd, style="TButton").pack(pady=10, padx=10, fill="x")

# Main text area
text_area = tk.Text(root, wrap="word", font=("Arial", 12), bg="white", fg="black")
text_area.pack(expand=True, fill="both", padx=10, pady=10)

# Floating 'New Note' button
new_note_button = ttk.Button(root, text="➕ New Note", command=lambda: text_area.delete("1.0", tk.END))
new_note_button.place(relx=0.9, rely=0.9, anchor="center")

# Dark mode status
dark_mode = False

# Run the application
root.mainloop()

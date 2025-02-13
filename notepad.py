import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import tweepy
import facebook
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Directory to store notes
NOTES_DIR = "saved_notes"
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

# Function to save note
def save_note():
    note_text = text_area.get("1.0", tk.END)  # Get all text from the text area
    if note_text.strip():  # Check if note is not empty
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(note_text)
            messagebox.showinfo("Success", "Note saved successfully!")
    else:
        messagebox.showwarning("Warning", "Cannot save an empty note.")

# Function to open a note
def open_note():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            note_text = file.read()
            text_area.delete("1.0", tk.END)  # Clear existing content
            text_area.insert(tk.END, note_text)  # Insert opened note content

# Function to delete a note
def delete_note():
    note_text = text_area.get("1.0", tk.END).strip()
    if note_text:
        confirmation = messagebox.askyesno("Confirm", "Are you sure you want to delete this note?")
        if confirmation:
            text_area.delete("1.0", tk.END)
            messagebox.showinfo("Success", "Note deleted successfully!")
    else:
        messagebox.showwarning("Warning", "No note to delete.")

# Google Drive Authentication and Setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def google_drive_authenticate():
    """Authenticate and return the service for Google Drive."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_to_google_drive(file_path):
    """Upload a file to Google Drive."""
    try:
        service = google_drive_authenticate()
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype='text/plain')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        messagebox.showinfo("Success", "Note uploaded to Google Drive!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload to Google Drive: {e}")

# Twitter Sharing using Tweepy
def share_on_twitter(note_text):
    try:
        # Initialize Tweepy API
        auth = tweepy.OAuth1UserHandler(consumer_key="YOUR_CONSUMER_KEY", consumer_secret="YOUR_CONSUMER_SECRET", access_token="YOUR_ACCESS_TOKEN", access_token_secret="YOUR_ACCESS_TOKEN_SECRET")
        api = tweepy.API(auth)
        api.update_status(note_text)
        messagebox.showinfo("Success", "Note shared on Twitter!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to share on Twitter: {e}")

# Facebook Sharing
def share_on_facebook(note_text):
    try:
        # Initialize Facebook SDK
        graph = facebook.GraphAPI(access_token="YOUR_FACEBOOK_ACCESS_TOKEN")
        graph.put_object(parent_object='me', connection_name='feed', message=note_text)
        messagebox.showinfo("Success", "Note shared on Facebook!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to share on Facebook: {e}")

# Instagram Sharing (Use Graph API)
def share_on_instagram(note_text):
    try:
        # Use Instagram Graph API
        response = requests.post("https://graph.instagram.com/me/media",
                                 params={"access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN", "caption": note_text})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Note shared on Instagram!")
        else:
            messagebox.showerror("Error", "Failed to share on Instagram.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to share on Instagram: {e}")

# GUI Setup
root = tk.Tk()
root.title("Persistent Note-Taking App")
root.geometry("600x450")

# Create Menu
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

# Share Menu
share_menu = tk.Menu(menu_bar, tearoff=0)
share_menu.add_command(label="Share on Twitter", command=lambda: share_on_twitter(text_area.get("1.0", tk.END)))
share_menu.add_command(label="Share on Facebook", command=lambda: share_on_facebook(text_area.get("1.0", tk.END)))
share_menu.add_command(label="Share on Instagram", command=lambda: share_on_instagram(text_area.get("1.0", tk.END)))
share_menu.add_command(label="Upload to Google Drive", command=lambda: upload_to_google_drive("your_note_path_here"))
menu_bar.add_cascade(label="Share", menu=share_menu)

# Create text area
text_area = tk.Text(root, wrap="word", font=("Arial", 12))
text_area.pack(expand=True, fill="both", padx=10, pady=10)

# Create Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

save_button = tk.Button(button_frame, text="Save Note", command=save_note)
save_button.pack(side="left", padx=10)

open_button = tk.Button(button_frame, text="Open Note", command=open_note)
open_button.pack(side="left", padx=10)

delete_button = tk.Button(button_frame, text="Delete Note", command=delete_note)
delete_button.pack(side="left")

# Run the app
root.mainloop()

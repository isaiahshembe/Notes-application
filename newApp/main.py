import tkinter as tk
from tkinter import scrolledtext, messagebox

def add_note():
    """Opens a new window to create a note."""
    def save_note():
        title = title_entry.get()
        content = content_text.get("1.0", tk.END)  # Get content from scrolled text

        if not title:
            messagebox.showerror("Error", "Please enter a title.")
            return

        try:
            with open(f"{title}.txt", "w") as file:  # Save as separate text files
                file.write(content)
            messagebox.showinfo("Success", "Note saved successfully!")
            new_window.destroy()  # Close the note window after saving
            load_notes()  # Refresh the listbox to show the new note
        except Exception as e:
            messagebox.showerror("Error", f"Error saving note: {e}")

    new_window = tk.Toplevel(root)  # Create a new top-level window for the note
    new_window.title("Add Note")

    title_label = tk.Label(new_window, text="Title:")
    title_label.pack(pady=(10, 0))  # Add padding to the top

    title_entry = tk.Entry(new_window)
    title_entry.pack()

    content_label = tk.Label(new_window, text="Content:")
    content_label.pack()

    content_text = scrolledtext.ScrolledText(new_window, wrap=tk.WORD, height=10)  # Use scrolledtext
    content_text.pack()

    save_button = tk.Button(new_window, text="Save Note", command=save_note)
    save_button.pack(pady=(10, 10))  # Add padding below the button


def load_notes():
    """Loads and displays the list of notes from saved files."""
    try:
        notes_listbox.delete(0, tk.END)  # Clear current notes in the listbox
        import glob  # Use glob to find all text files easily
        for file_path in glob.glob("*.txt"):  # Assumes notes are saved as .txt
            title = file_path[:-4]  # Extract title by removing '.txt'
            notes_listbox.insert(tk.END, title)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading notes: {e}")


def open_note():
    """Opens the selected note in a new window for viewing/editing."""
    try:
        selected_note = notes_listbox.get(notes_listbox.curselection())
        with open(f"{selected_note}.txt", "r") as file:
            content = file.read()

        view_window = tk.Toplevel(root)
        view_window.title(selected_note)

        content_view = scrolledtext.ScrolledText(view_window, wrap=tk.WORD)  # Use scrolledtext for viewing
        content_view.insert(tk.END, content)
        content_view.config(state=tk.DISABLED)  # Make it read-only
        content_view.pack()

    except Exception as e:
        messagebox.showerror("Error", f"Error opening note: {e}")


root = tk.Tk()
root.title("Notepad")

# Styling similar to the image (you can customize this further)
root.geometry("300x400")  # Adjust size as needed

add_button = tk.Button(root, text="+", command=add_note, font=("Arial", 20))  # Larger "+" button
add_button.pack(pady=(20, 10))  # Add padding

notes_label = tk.Label(root, text="Your Notes:")
notes_label.pack()

notes_listbox = tk.Listbox(root)
notes_listbox.pack()

open_button = tk.Button(root, text="Open", command=open_note)
open_button.pack(pady=(10, 20))  # Padding below the open button

load_notes()  # Load notes when the app starts

root.mainloop()
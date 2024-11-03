import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # For modern widgets
import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import pygame  # For audio playback
import PIL.Image
import PIL.ImageTk


class MP3PlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Modern MP3 Player")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")  # Light, modern background color

        # Initialize audio system
        pygame.mixer.init()

        # Default values
        self.album_directory = ""
        self.albums = []
        self.tracks = []
        self.current_track_index = -1

        # Set up frames
        self.setup_ribbon()
        self.setup_left_pane()
        self.setup_right_pane()
        self.setup_bottom_controls()

    def setup_ribbon(self):
        ribbon = tk.Frame(self, bg="#333", height=30)
        ribbon.pack(side="top", fill="x")

        # Preferences Button
        preferences_btn = tk.Button(ribbon, text="Preferences", command=self.open_preferences, bg="#555", fg="#fff")
        preferences_btn.pack(side="right", padx=10)

    def open_preferences(self):
        self.album_directory = filedialog.askdirectory(title="Select Album Folder")
        if self.album_directory:
            self.load_albums()  # Load albums after selection

    def load_albums(self):
        self.album_listbox.delete(0, tk.END)
        self.albums = [d for d in os.listdir(self.album_directory) if os.path.isdir(os.path.join(self.album_directory, d))]
        for album in self.albums:
            self.album_listbox.insert(tk.END, album)

    def setup_left_pane(self):
        left_frame = tk.Frame(self, width=200, bg="#e6e6e6")
        left_frame.pack(side="left", fill="y")
        album_label = tk.Label(left_frame, text="Albums", font=("Arial", 14))
        album_label.pack(pady=10)

        # Listbox for album list
        self.album_listbox = tk.Listbox(left_frame)
        self.album_listbox.pack(fill="both", expand=True)
        self.album_listbox.bind("<<ListboxSelect>>", self.display_album_details)

    def setup_right_pane(self):
        right_frame = tk.Frame(self, bg="#f0f0f0")
        right_frame.pack(side="right", fill="both", expand=True)

        # Album Artwork
        self.artwork_label = tk.Label(right_frame, text="Artwork", bg="#d9d9d9", width=20, height=10)
        self.artwork_label.grid(row=0, column=0, padx=10, pady=10)

        # Album Information
        info_frame = tk.Frame(right_frame, bg="#f0f0f0")
        info_frame.grid(row=0, column=1, sticky="n")
        self.album_info_label = tk.Label(info_frame, text="Album Info", font=("Arial", 12), bg="#f0f0f0")
        self.album_info_label.pack()

        # Track List
        self.track_listbox = tk.Listbox(right_frame)
        self.track_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    def setup_bottom_controls(self):
        controls_frame = tk.Frame(self, bg="#333")
        controls_frame.pack(side="bottom", fill="x")

        play_btn = tk.Button(controls_frame, text="Play", command=self.play_track, bg="#555", fg="#fff")
        pause_btn = tk.Button(controls_frame, text="Pause", command=self.pause_track, bg="#555", fg="#fff")
        next_btn = tk.Button(controls_frame, text="Next", command=self.next_track, bg="#555", fg="#fff")
        prev_btn = tk.Button(controls_frame, text="Previous", command=self.prev_track, bg="#555", fg="#fff")

        for btn in [prev_btn, play_btn, pause_btn, next_btn]:
            btn.pack(side="left", padx=5, pady=5)

        # Timer
        self.timer_label = tk.Label(controls_frame, text="00:00 / 00:00", bg="#333", fg="#fff")
        self.timer_label.pack(side="right", padx=10)

    def verify_album_files(self, album_path):
        self.tracks = []  # Clear the tracks list for new album
        for root, dirs, files in os.walk(album_path):
            for file in files:
                if file.endswith(".mp3"):
                    audio = MP3(os.path.join(root, file), ID3=EasyID3)
                    # Verify bitrate and metadata
                    if audio.info.bitrate < 320000:
                        messagebox.showwarning("File Error", f"{file} bitrate is below 320kbps")
                        return False
                    if "artist" not in audio or "title" not in audio:
                        messagebox.showwarning("File Error", f"{file} is missing metadata")
                        return False
                    self.tracks.append(os.path.join(root, file))  # Add valid tracks to the list
        return True

    def display_album_details(self, event):
        selected_album = self.album_listbox.get(self.album_listbox.curselection())
        album_path = os.path.join(self.album_directory, selected_album)

        if self.verify_album_files(album_path):
            # Load album artwork, info, and tracks
            self.track_listbox.delete(0, tk.END)
            self.album_info_label.config(text=f"Album: {selected_album}")

            # Display tracks
            for track in self.tracks:
                track_info = MP3(track, ID3=EasyID3)
                self.track_listbox.insert(tk.END, track_info['title'][0])  # Display track title
            
            # Load artwork if available
            self.load_album_artwork(album_path)

    def load_album_artwork(self, album_path):
        # Find the first mp3 file and load its artwork
        for track in self.tracks:
            audio = MP3(track, ID3=EasyID3)
            if 'APIC:' in audio:
                # Load artwork from the first valid track
                img_data = audio['APIC:'][0].data
                image = PIL.Image.open(io.BytesIO(img_data))
                image.thumbnail((200, 200), PIL.Image.ANTIALIAS)  # Resize image
                self.album_artwork = PIL.ImageTk.PhotoImage(image)
                self.artwork_label.config(image=self.album_artwork)
                break

    def get_selected_track_path(self):
        if self.track_listbox.curselection():
            selected_index = self.track_listbox.curselection()[0]
            return self.tracks[selected_index]
        return None

    def play_track(self):
        track_path = self.get_selected_track_path()
        if track_path:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.current_track_index = self.track_listbox.curselection()[0]
            self.update_timer()

    def pause_track(self):
        pygame.mixer.music.pause()

    def next_track(self):
        if self.current_track_index < len(self.tracks) - 1:
            self.current_track_index += 1
            self.track_listbox.selection_clear(0, tk.END)
            self.track_listbox.selection_set(self.current_track_index)
            self.play_track()

    def prev_track(self):
        if self.current_track_index > 0:
            self.current_track_index -= 1
            self.track_listbox.selection_clear(0, tk.END)
            self.track_listbox.selection_set(self.current_track_index)
            self.play_track()

    def update_timer(self):
        if pygame.mixer.music.get_busy():
            current_time = pygame.mixer.music.get_pos() / 1000  # Get current position in seconds
            current_time_str = self.format_time(current_time)
            total_time_str = self.format_time(self.get_selected_track_duration())
            self.timer_label.config(text=f"{current_time_str} / {total_time_str}")
            self.after(1000, self.update_timer)  # Update timer every second

    def format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        return f"{m:02}:{s:02}"

    def get_selected_track_duration(self):
        track_path = self.get_selected_track_path()
        if track_path:
            audio = MP3(track_path)
            return audio.info.length
        return 0


if __name__ == "__main__":
    app = MP3PlayerApp()
    app.mainloop()

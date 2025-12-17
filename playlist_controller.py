# playlist_controller.py
import tkinter as tk
from tkinter import simpledialog, messagebox

class PlaylistController:
    """Controller untuk fitur playlist"""
    def __init__(self, app):
        self.app = app
    
    def create_playlist(self):
        """Buat playlist baru"""
        name = simpledialog.askstring("Buat Playlist", "Masukkan nama playlist:")
        if not name:
            return
        
        if name in self.app.playlists:
            messagebox.showwarning("Gagal", "Nama playlist sudah ada!")
            return
        
        from models import DoublyLinkedList
        self.app.playlists[name] = DoublyLinkedList()
        self.app.save_to_json()
        self.app.refresh_playlist_buttons()
        messagebox.showinfo("Sukses", f"Playlist '{name}' berhasil dibuat!")
    
    def delete_playlist(self, playlist_name):
        """Hapus playlist"""
        if playlist_name == 'My Favorites':
            messagebox.showwarning("Gagal", "Playlist default tidak bisa dihapus!")
            return
        
        if messagebox.askyesno("Konfirmasi", f"Hapus playlist '{playlist_name}'?"):
            del self.app.playlists[playlist_name]
            self.app.save_to_json()
            self.app.refresh_playlist_buttons()
            
            if self.app.selected_playlist == playlist_name:
                self.app.show_library()
            
            messagebox.showinfo("Sukses", "Playlist berhasil dihapus!")
    
    def show_playlist_options(self, playlist_name):
        """Tampilkan opsi untuk playlist (hapus)"""
        options_menu = tk.Menu(self.app.root, tearoff=0, 
                             bg=self.app.colors['entry_bg'], 
                             fg=self.app.colors['text'],
                             activebackground=self.app.colors['accent'], 
                             activeforeground=self.app.colors['white'])
        options_menu.add_command(label="🗑 Hapus Playlist", 
                                command=lambda: self.delete_playlist(playlist_name))
        
        try:
            options_menu.tk_popup(self.app.root.winfo_pointerx(), 
                                self.app.root.winfo_pointery())
        finally:
            options_menu.grab_release()
    
    def refresh_playlist_buttons(self):
        """Perbarui daftar tombol playlist di sidebar"""
        for widget in self.app.playlist_frame.winfo_children():
            widget.destroy()
        
        for playlist_name in self.app.playlists.keys():
            # Frame untuk setiap playlist (button + menu titik 3)
            playlist_container = tk.Frame(self.app.playlist_frame, 
                                        bg=self.app.colors['bg_sec'])
            playlist_container.pack(fill='x', pady=3)
            
            # Tombol playlist
            btn = tk.Button(playlist_container, text="🎶 " + playlist_name, 
                          font=('Arial', 10), bg=self.app.colors['accent_dark'], 
                          fg=self.app.colors['white'], relief='flat', anchor='w', 
                          padx=20, pady=8,
                          command=lambda p=playlist_name: self.show_playlist(p))
            btn.pack(side='left', fill='x', expand=True)
            
            # Tombol titik 3 untuk hapus (hanya untuk playlist selain My Favorites)
            if playlist_name != 'My Favorites':
                menu_btn = tk.Button(playlist_container, text="⋮", font=('Arial', 14),
                                  bg=self.app.colors['bg_sec'], 
                                  fg=self.app.colors['text_sec'], 
                                  relief='flat', width=2, cursor='hand2',
                                  command=lambda p=playlist_name: 
                                  self.show_playlist_options(p))
                menu_btn.pack(side='right', padx=2)
    
    def add_to_playlist(self, playlist_name):
        """Tambah lagu ke playlist"""
        selection = self.app.tree.selection()
        if not selection:
            return
        
        song_id = self.app.tree.item(selection[0])['values'][0]
        song = next((s for s in self.app.library if s['id'] == song_id), None)
        
        if song:
            # Cek jika playlist adalah My Favorites
            if playlist_name == 'My Favorites':
                messagebox.showwarning("Peringatan", 
                    "Playlist 'My Favorites' hanya untuk lagu favorite!\n"
                    "Gunakan menu 'Tambah ke Favorite' untuk menambahkan lagu.")
                return
            
            self.app.playlists[playlist_name].append(song.copy())
            self.app.save_to_json()
            messagebox.showinfo("Sukses", 
                              f"Lagu ditambahkan ke playlist '{playlist_name}'")
    
    def show_playlist(self, playlist_name):
        """Tampilkan playlist"""
        self.app.current_view = 'playlist'
        self.app.selected_playlist = playlist_name
        self.app.title_label.config(text=f"Playlist: {playlist_name}")
        self.app.refresh_song_list()
    
    def remove_from_playlist(self):
        """Hapus lagu dari playlist"""
        if self.app.current_view != 'playlist' or not self.app.selected_playlist:
            return
        
        selection = self.app.tree.selection()
        if not selection:
            return
        
        song_id = self.app.tree.item(selection[0])['values'][0]
        
        removed = self.app.playlists[self.app.selected_playlist].remove(song_id)
        
        if removed:
            self.app.save_to_json()
            self.app.refresh_song_list()
            messagebox.showinfo("Sukses", "Lagu dihapus dari playlist!")
        else:
            messagebox.showwarning("Gagal", "Lagu tidak ditemukan dalam playlist!")
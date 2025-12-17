import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import os

class PlaylistController:
    """Controller untuk fitur playlist"""
    def __init__(self, app):
        self.app = app
    
    def create_playlist(self):
        """Buat playlist baru"""
        from ui_components import PlaylistDialog
        
        dialog = PlaylistDialog(self.app.root, "Buat Playlist", self.app.colors, 
                               existing_names=list(self.app.playlists.keys()))
        result = dialog.show()
        
        if not result:
            return
        
        name = result['name']
        image_path = result['image_path']
        description = result.get('description', "")
        
        from models import DoublyLinkedList
        new_playlist = DoublyLinkedList()
        new_playlist.image_path = image_path
        new_playlist.description = description
        
        self.app.playlists[name] = new_playlist
        self.app.save_to_json()
        self.refresh_playlist_buttons()
        messagebox.showinfo("Sukses", f"Playlist '{name}' berhasil dibuat!")
    
    def delete_playlist(self, playlist_name):
        """Hapus playlist"""
        if playlist_name == 'My Favorites':
            messagebox.showwarning("Gagal", "Playlist default tidak bisa dihapus!")
            return
        
        if messagebox.askyesno("Konfirmasi", f"Hapus playlist '{playlist_name}'?"):
            del self.app.playlists[playlist_name]
            self.app.save_to_json()
            self.refresh_playlist_buttons()
            
            if self.app.selected_playlist == playlist_name:
                self.app.show_library()
            
            messagebox.showinfo("Sukses", "Playlist berhasil dihapus!")
    
    def show_playlist_options(self, playlist_name):
        """Tampilkan opsi untuk playlist (hapus/edit cover)"""
        options_menu = tk.Menu(self.app.root, tearoff=0, 
                             bg=self.app.colors['entry_bg'], 
                             fg=self.app.colors['text'],
                             activebackground=self.app.colors['accent'], 
                             activeforeground=self.app.colors['white'])
        
        # Opsi Edit Playlist (Deskripsi/Nama/Kover)
        if playlist_name != 'My Favorites':
            options_menu.add_command(label="✏ Edit Playlist", 
                                    command=lambda: self.edit_playlist_details(playlist_name))
        else:
            # My Favorites hanya bisa ubah kover (jika admin)
             options_menu.add_command(label="🖼 Ubah Kover", 
                                    command=lambda: self.change_playlist_cover(playlist_name))

        # Opsi Hapus (Jangan tampilkan untuk My Favorites)
        if playlist_name != 'My Favorites':
            options_menu.add_separator()
            options_menu.add_command(label="🗑 Hapus Playlist", 
                                    command=lambda: self.delete_playlist(playlist_name))
        
        try:
            options_menu.tk_popup(self.app.root.winfo_pointerx(), 
                                self.app.root.winfo_pointery())
        finally:
            options_menu.grab_release()
    
    def change_playlist_cover(self, playlist_name):
        """Ubah gambar cover playlist"""
        file_path = filedialog.askopenfilename(
            title="Pilih Gambar Kover",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        
        if file_path:
            self.app.playlists[playlist_name].image_path = file_path
            self.app.save_to_json()
            
            # Refresh UI
            self.refresh_playlist_buttons() 
            if self.app.current_view == 'playlist' and self.app.selected_playlist == playlist_name:
                self.show_playlist(playlist_name)
                
            messagebox.showinfo("Sukses", f"Kover playlist '{playlist_name}' berhasil diubah!")
    
    
    def edit_playlist_details(self, playlist_name):
        """Edit detail playlist (Nama, Deskripsi, Kover)"""
        from ui_components import PlaylistDialog
        
        playlist = self.app.playlists[playlist_name]
        initial_data = {
            'name': playlist_name,
            'description': playlist.description,
            'image_path': playlist.image_path
        }
        
        existing = list(self.app.playlists.keys())
        dialog = PlaylistDialog(self.app.root, "Edit Playlist", 
                              self.app.colors, existing_names=existing,
                              initial_data=initial_data)
        result = dialog.show()
        
        if not result:
            return
        
        new_name = result['name']
        new_desc = result.get('description', "")
        new_image = result['image_path']
        
        # Jika nama berubah, perlu update key di dictionary
        if new_name != playlist_name:
            self.app.playlists[new_name] = self.app.playlists.pop(playlist_name)
            # Dan update selected playlist jika sedang aktif
            if self.app.selected_playlist == playlist_name:
                self.app.selected_playlist = new_name
            playlist = self.app.playlists[new_name]
            
        playlist.description = new_desc
        playlist.image_path = new_image
        
        self.app.save_to_json()
        self.refresh_playlist_buttons()
        
        # Refresh view jika sedang dibuka
        if self.app.current_view == 'playlist' and self.app.selected_playlist == (new_name if new_name else playlist_name):
            self.show_playlist(new_name if new_name else playlist_name)
            
        messagebox.showinfo("Sukses", "Playlist berhasil diperbarui!")

    def refresh_playlist_buttons(self):
        """Perbarui daftar tombol playlist di sidebar"""
        from PIL import Image, ImageTk
        import os
        
        for widget in self.app.playlist_frame.winfo_children():
            widget.destroy()
        
        self.app.playlist_icons = {} # Keep references
        
        for playlist_name in self.app.playlists.keys():
            # Frame untuk setiap playlist (button + menu titik 3)
            playlist_container = tk.Frame(self.app.playlist_frame, 
                                        bg=self.app.colors['bg_sec'])
            playlist_container.pack(fill='x', pady=3)
            
            # Tombol playlist (Tanpa icon di sidebar)
            btn = tk.Button(playlist_container, text="🎶 " + playlist_name, 
                          font=('Arial', 10), bg=self.app.colors['accent_dark'], 
                          fg=self.app.colors['white'], relief='flat', anchor='w', 
                          padx=20, pady=4,
                          command=lambda p=playlist_name: self.show_playlist(p))
            btn.pack(side='left', fill='x', expand=True)
            
            # Tombol titik 3 untuk opsi (hapus/edit)
            # Logika: My Favorites hanya bisa diedit admin. Playlist lain bisa diedit user/admin.
            show_menu = True
            if playlist_name == 'My Favorites' and self.app.role != 'admin':
                show_menu = False
            
            if show_menu:
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
        
        playlist = self.app.playlists[playlist_name]
        song_count = playlist.size
        
        if playlist.description:
            desc_text = playlist.description
        else:
            desc_text = f"Playlist User • {song_count} lagu"
            
        self.app.update_header(
            title=playlist_name,
            type_text="PLAYLIST",
            image_path=playlist.image_path,
            description=desc_text
        )
             
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
# admin_controller.py
import tkinter as tk
from tkinter import messagebox
from ui_components import SongDialog

class AdminController:
    """Controller untuk fitur admin"""
    def _init_(self, app):
        self.app = app
    
    def show_add_song_dialog(self):
        """Dialog untuk menambah lagu baru"""
        existing_ids = [s['id'] for s in self.app.library]
        dialog = SongDialog(self.app.root, "Tambah Lagu Baru", self.app.colors, existing_ids=existing_ids)
        result = dialog.show()
        
        if not result:
            return
        
        title = result['title']
        artist = result['artist']
        
        if not title or not artist:
            messagebox.showwarning("Peringatan", "Judul dan Artis wajib diisi!")
            return
        
        new_song = {
            'id': result['id'],
            'title': title,
            'artist': artist,
            'genre': result['genre'],
            'album': result['album'],
            'year': result['year'],
            'duration': result['duration'],
            'image_path': result.get('image_path'),
            'favorite': False
        }
        
        self.app.library.append(new_song)
        self.app.save_to_json()
        self.app.refresh_song_list()
        messagebox.showinfo("Sukses", "Lagu berhasil ditambahkan!")
    
    def edit_selected_song(self):
        """Edit lagu yang dipilih"""
        selection = self.app.tree.selection()
        if not selection:
            return
        
        values = self.app.tree.item(selection[0])['values']
        song_id = values[0]
        song = next((s for s in self.app.library if s['id'] == song_id), None)
        
        if not song:
            return
        
        dialog = SongDialog(self.app.root, "Edit Lagu", self.app.colors, song)
        result = dialog.show()
        
        if not result:
            return
        
        # Update song data
        song.update(result)
        
        # Update di semua playlist
        for playlist in self.app.playlists.values():
            current = playlist.head
            while current:
                if current.data['id'] == song_id:
                    current.data = song.copy()
                current = current.next
        
        self.app.save_to_json()
        self.app.refresh_song_list()
        messagebox.showinfo("Sukses", "Lagu berhasil diupdate!")
    
    def delete_selected_song(self):
        """Hapus lagu yang dipilih"""
        selection = self.app.tree.selection()
        if not selection:
            return
        
        values = self.app.tree.item(selection[0])['values']
        song_id = values[0]
        song = next((s for s in self.app.library if s['id'] == song_id), None)
        
        if not song:
            return
        
        if messagebox.askyesno("Konfirmasi", 
                              f"Hapus '{song['title']}' dari library?\nLagu juga akan terhapus dari semua playlist."):
            self.app.library = [s for s in self.app.library if s['id'] != song_id]
            self.app.save_to_json()
            
            # Hapus dari semua playlist
            for playlist in self.app.playlists.values():
                playlist.remove(song_id)
            
            # Reset current song jika yang dihapus sedang diputar
            if self.app.current_song and self.app.current_song['id'] == song_id:
                self.app.current_song = None
                self.app.is_playing = False
                self.app.update_player_ui()
            
            self.app.refresh_song_list()
            messagebox.showinfo("Sukses", "Lagu berhasil dihapus!")
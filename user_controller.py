# user_controller.py
import tkinter as tk
from tkinter import messagebox
import random
from ui_components import QueueDialog

class UserController:
    """Controller untuk fitur user"""
    def __init__(self, app):
        self.app = app
    
    def play_selected_song(self):
        """Putar lagu yang dipilih"""
        selection = self.app.tree.selection()
        if not selection:
            return
        
        values = self.app.tree.item(selection[0])['values']
        song_id = values[0]
        
        if self.app.current_view == 'library':
            song = next((s for s in self.app.library if s['id'] == song_id), None)
        else:
            songs = self.app.playlists[self.app.selected_playlist].to_list()
            song = next((s for s in songs if s['id'] == song_id), None)
        
        if song:
            self.app.current_song = song
            self.app.is_playing = True
            if not self.app.played_history or self.app.played_history[-1] != song['id']:
                self.app.played_history.append(song['id'])
            self.app.update_player_ui()
            messagebox.showinfo("Now Playing", f"🎵 Memutar: {song['title']} - {song['artist']}")
    
    def toggle_play(self):
        """Toggle play/pause"""
        if not self.app.current_song:
            messagebox.showwarning("Peringatan", "Pilih lagu terlebih dahulu!")
            return
        
        self.app.is_playing = not self.app.is_playing
        self.app.update_player_ui()
        
        status = "memutar" if self.app.is_playing else "dijeda"
        messagebox.showinfo("Status", f"🎵 Lagu {status}")
    
    def find_similar_song(self, candidates, current_song, priority_types):
        """Cari lagu yang mirip berdasarkan prioritas"""
        for priority in priority_types:
            if priority == 'artist':
                same = [s for s in candidates if s['artist'] == current_song['artist']]
                if same:
                    return same[0]
            elif priority == 'genre':
                same = [s for s in candidates if s['genre'] == current_song['genre']]
                if same:
                    return same[0]
            elif priority == 'decade':
                current_year = current_song['year']
                same = [s for s in candidates if s['year'] // 10 == current_year // 10]
                if same:
                    return same[0]
        return None
    
    def next_song(self):
        """Putar lagu selanjutnya"""
        if not self.app.current_song:
            messagebox.showwarning("Peringatan", "Tidak ada lagu yang sedang diputar!")
            return
        
        # Cek queue dulu
        if self.app.play_queue:
            self.app.current_song = self.app.play_queue.pop(0)
            self.app.is_playing = True
            self.app.update_player_ui()
            messagebox.showinfo("Queue", f"🎵 Dari antrean: {self.app.current_song['title']}")
            return
        
        if self.app.current_view == 'playlist' and self.app.selected_playlist:
            # Next dari playlist
            node = self.app.playlists[self.app.selected_playlist].find_node(self.app.current_song['id'])
            if node and node.next:
                self.app.current_song = node.next.data
                self.app.is_playing = True
                self.app.update_player_ui()
                messagebox.showinfo("Next", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
                return
            else:
                messagebox.showinfo("Info", "Sudah di akhir playlist!")
                return
        
        # Cari lagu mirip dari library
        candidates = [s for s in self.app.library if s['id'] != self.app.current_song['id']]
        
        if not candidates:
            messagebox.showinfo("Info", "Tidak ada lagu lain dalam library!")
            return
        
        # Cari lagu mirip dengan prioritas
        similar = self.find_similar_song(candidates, self.app.current_song, 
                                        ['artist', 'genre', 'decade'])
        
        if similar:
            self.app.current_song = similar
            self.app.is_playing = True
            self.app.update_player_ui()
            messagebox.showinfo("Next (Similar)", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
        elif candidates:
            # Fallback: random
            self.app.current_song = random.choice(candidates)
            self.app.is_playing = True
            self.app.update_player_ui()
            messagebox.showinfo("Next (Random)", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
        else:
            messagebox.showinfo("Info", "Tidak ada lagu mirip yang ditemukan!")
    
    def prev_song(self):
        """Putar lagu sebelumnya"""
        if not self.app.current_song:
            messagebox.showwarning("Peringatan", "Tidak ada lagu yang sedang diputar!")
            return
        
        if self.app.current_view == 'playlist' and self.app.selected_playlist:
            # Prev dari playlist
            node = self.app.playlists[self.app.selected_playlist].find_node(self.app.current_song['id'])
            if node and node.prev:
                self.app.current_song = node.prev.data
                self.app.is_playing = True
                self.app.update_player_ui()
                messagebox.showinfo("Previous", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
                return
            else:
                messagebox.showinfo("Info", "Sudah di awal playlist!")
                return
        
        # Cari lagu mirip dari library
        candidates = [s for s in self.app.library if s['id'] != self.app.current_song['id']]
        
        if not candidates:
            messagebox.showinfo("Info", "Tidak ada lagu lain dalam library!")
            return
        
        # Cari lagu mirip dengan prioritas
        similar = self.find_similar_song(candidates, self.app.current_song, 
                                        ['artist', 'genre', 'decade'])
        
        if similar:
            self.app.current_song = similar
            self.app.is_playing = True
            self.app.update_player_ui()
            messagebox.showinfo("Previous (Similar)", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
        else:
            messagebox.showinfo("Info", "Tidak ada lagu mirip yang ditemukan untuk diputar sebelumnya!")
    
    def add_to_queue(self):
        """Tambah lagu ke queue"""
        selection = self.app.tree.selection()
        if not selection:
            return
        
        song_id = self.app.tree.item(selection[0])['values'][0]
        song = next((s for s in self.app.library if s['id'] == song_id), None)
        
        if song:
            self.app.play_queue.append(song.copy())
            messagebox.showinfo("Queue", f"'{song['title']}' ditambahkan ke antrean!")
    
    def show_queue(self):
        """Tampilkan dialog queue"""
        QueueDialog(self.app.root, "Antrean Lagu", self.app.colors, self.app.play_queue)
    
    def toggle_favorite(self):
        """Toggle status favorite lagu"""
        selection = self.app.tree.selection()
        if not selection:
            return
        
        song_id = self.app.tree.item(selection[0])['values'][0]
        song = next((s for s in self.app.library if s['id'] == song_id), None)
        
        if song:
            song['favorite'] = not song.get('favorite', False)
            
            # Update status favorite di SEMUA playlist
            for playlist in self.app.playlists.values():
                current_node = playlist.head
                while current_node:
                    if current_node.data['id'] == song_id:
                        current_node.data['favorite'] = song['favorite']
                    current_node = current_node.next
            
            # Jika ditambahkan ke favorite, masukkan ke playlist My Favorites
            if song['favorite']:
                # Cek apakah sudah ada di playlist My Favorites
                my_favs = self.app.playlists['My Favorites'].to_list()
                if not any(s['id'] == song_id for s in my_favs):
                    self.app.playlists['My Favorites'].append(song.copy())
                status_msg = "ditambahkan ke favorite dan playlist My Favorites!"
            else:
                # Jika dihapus dari favorite, hapus dari playlist My Favorites
                self.app.playlists['My Favorites'].remove(song_id)
                status_msg = "dihapus dari favorite dan playlist My Favorites!"
            
            self.app.save_to_json()
            self.app.refresh_song_list()
            messagebox.showinfo("Favorite", f"Lagu {status_msg}")
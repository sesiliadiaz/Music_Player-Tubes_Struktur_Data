# user_controller.py
import tkinter as tk
from tkinter import messagebox
import random
from ui_components import QueueDialog

class UserController:
    """Controller untuk fitur user"""
    def __init__(self, app):
        self.app = app
        self.last_context_song = None
    
    def add_to_history(self, song_id):
        """Tambah ke history, jaga max 10 items"""
        # Jangan tambah jika sama dengan yang terakhir (mencegah duplikat berurutan)
        if self.app.played_history and self.app.played_history[-1] == song_id:
            return
        
        self.app.played_history.append(song_id)
        if len(self.app.played_history) > 50:
            self.app.played_history.pop(0)
            
    def show_history(self):
        """Tampilkan riwayat lagu"""
        history_songs = []
        for song_id in reversed(self.app.played_history): # Show newest first
            song = next((s for s in self.app.library if s['id'] == song_id), None)
            if song:
                history_songs.append(song)
        
        QueueDialog(self.app.root, "Riwayat Lagu", 
                   self.app.colors, history_songs)
    
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
            self.last_context_song = song
            self.app.is_playing = True
            self.add_to_history(song['id'])
            self.app.update_player_ui()
            messagebox.showinfo("Now Playing", f"🎵 Memutar: {song['title']} - {song['artist']}")
    
    def toggle_play(self):
        """Toggle play/pause"""
        if not self.app.current_song:
            # Jika belum ada lagu yang diputar, coba putar yang dipilih
            selection = self.app.tree.selection()
            if selection:
                self.play_selected_song()
                return
            
            # Jika tidak ada seleksi, coba putar lagu pertama (auto-start)
            children = self.app.tree.get_children()
            if children:
                first_item = children[0]
                self.app.tree.selection_set(first_item)
                self.play_selected_song()
                return
            else:
                messagebox.showwarning("Peringatan", "Tidak ada lagu untuk diputar!")
                return
        
        self.app.is_playing = not self.app.is_playing
        self.app.update_player_ui()
        
        status = "memutar" if self.app.is_playing else "dijeda"
        messagebox.showinfo("Status", f"🎵 Lagu {status}")
    
    def play_all(self):
        """Putar semua lagu (mulai dari pertama) di view saat ini"""
        children = self.app.tree.get_children()
        if not children:
            messagebox.showwarning("Peringatan", "Tidak ada lagu untuk diputar!")
            return
        
        # Select first item
        first_item = children[0]
        self.app.tree.selection_set(first_item)
        self.app.tree.focus(first_item)
        
        # Play it
        self.play_selected_song()
    
    def get_smart_recommendation(self, current_song, candidates):
        """Cari lagu berdasarkan prioritas: Artist > Album > Genre > Year > Alphabetical"""
        # Prioritas 1: Artist
        same = [s for s in candidates if s['artist'] == current_song['artist']]
        if same: return same[0]
        
        # Prioritas 2: Album
        same = [s for s in candidates if s.get('album') == current_song.get('album')]
        if same: return same[0]
        
        # Prioritas 3: Genre
        same = [s for s in candidates if s['genre'] == current_song['genre']]
        if same: return same[0]
        
        # Prioritas 4: Year (Decade logic removed, strictly year or just close year?)
        # User said "tahun yang sama", so strictly same year.
        same = [s for s in candidates if s['year'] == current_song['year']]
        if same: return same[0]
        
        # Fallback: Urutan abjad judul (candidates sudah disort di caller)
        if candidates:
            return candidates[0]
        
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
            self.add_to_history(self.app.current_song['id'])
            self.app.update_player_ui()
            messagebox.showinfo("Queue", f"🎵 Dari antrean: {self.app.current_song['title']}")
            return
        
        if self.app.current_view == 'playlist' and self.app.selected_playlist:
            # Next dari playlist
            # Coba cari current song di playlist. Jika tidak ada (krn dr queue), gunakan last_context_song
            playlist = self.app.playlists[self.app.selected_playlist]
            node = playlist.find_node(self.app.current_song['id'])
            
            if not node and self.last_context_song:
                node = playlist.find_node(self.last_context_song['id'])
                
            if node and node.next:
                self.app.current_song = node.next.data
                self.last_context_song = self.app.current_song
                self.app.is_playing = True
                self.app.update_player_ui()
                # messagebox.showinfo("Next", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
                # Add to history
                self.add_to_history(self.app.current_song['id'])
                return
            else:
                messagebox.showinfo("Info", "Sudah di akhir playlist!")
                return
        
        # LIBRARY LOGIC (Smart Recommendation)
        
        # Determine anchor song for recommendation
        anchor_song = self.app.current_song
        # If current song was from queue (detached from library flow), use last context if possible
        if self.last_context_song:
             anchor_song = self.last_context_song
             
        # Siapkan candidates dari library (yang belum diputar)
        candidates = [s for s in self.app.library 
                     if s['id'] not in self.app.played_history 
                     and s['id'] != self.app.current_song['id']]
        
        # Jika semua sudah diputar, reset cycle (hapus history, kecuali current)
        if not candidates:
            # self.app.played_history = [self.app.current_song['id']]
            # candidates = [s for s in self.app.library if s['id'] != self.app.current_song['id']]
            messagebox.showinfo("Info", "Semua lagu di library sudah diputar!")
            return
        
        # Sort candidates berdasarkan Judul (Alphabetical) untuk fallback
        candidates.sort(key=lambda x: x['title'].lower())
        
        # Cari rekomendasi smart based on ANCHOR
        next_s = self.get_smart_recommendation(anchor_song, candidates)
        
        if next_s:
            self.app.current_song = next_s
            self.last_context_song = next_s
            self.app.is_playing = True
            
            # Add to history
            self.add_to_history(next_s['id'])
            
            self.app.update_player_ui()
            # messagebox.showinfo("Next", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
        else:
            messagebox.showinfo("Info", "Tidak ada lagu lain yang tersedia!")
    
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
        
        # Gunakan logika yang sama untuk previous jika tidak di playlist
        # Note: Biasanya Prev mengambil dari history, tapi user meminta logika prioritas "pas ditekan next/preview"
        
        # Cek history dulu untuk perilaku natural 'back'
        if len(self.app.played_history) > 1:
             # Pop current song
             self.app.played_history.pop()
             # Get prev song
             prev_id = self.app.played_history[-1]
             prev_song = next((s for s in self.app.library if s['id'] == prev_id), None)
             
             if prev_song:
                 self.app.current_song = prev_song
                 self.app.is_playing = True
                 self.app.update_player_ui()
                 messagebox.showinfo("Previous", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
                 return

        # Jika history kosong (atau cuma 1), gunakan smart logic? 
        # Atau fallback ke random/smart logic tapi tanpa filter history (bisa ulang).
        candidates = [s for s in self.app.library if s['id'] != self.app.current_song['id']]
        candidates.sort(key=lambda x: x['title'].lower())
        
        prev_song = self.get_smart_recommendation(self.app.current_song, candidates)
        
        if prev_song:
            self.app.current_song = prev_song
            self.app.is_playing = True
            # Jangan append history kalau mundur, biarkan flow maju mengurusnya atau biarkan
            # Tapi biar konsisten "semua dapat bagian", kita tidak menambah ke history kalau mundur,
            # atau anggap replay.
            self.app.update_player_ui()
            messagebox.showinfo("Previous", f"🎵 {self.app.current_song['title']} - {self.app.current_song['artist']}")
        else:
            messagebox.showinfo("Info", "Tidak ada lagu lain!")
    
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
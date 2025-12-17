# models.py
from typing import Optional
import json

class SongNode:
    """Node untuk Doubly Linked List"""
    def __init__(self, song_data):
        self.data = song_data
        self.next: Optional[SongNode] = None
        self.prev: Optional[SongNode] = None

class DoublyLinkedList:
    """Doubly Linked List untuk Playlist"""
    def __init__(self):
        self.head: Optional[SongNode] = None
        self.tail: Optional[SongNode] = None
        self.size = 0
        self.image_path = None
        self.description = ""
    
    def append(self, song_data):
        """Menambah lagu di akhir playlist"""
        new_node = SongNode(song_data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.size += 1
    
    def remove(self, song_id):
        """Menghapus lagu berdasarkan ID"""
        current = self.head
        while current:
            if current.data['id'] == song_id:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                
                self.size -= 1
                return True
            current = current.next
        return False
    
    def to_list(self):
        """Konversi linked list ke Python list"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def find_node(self, song_id):
        """Mencari node berdasarkan song_id"""
        current = self.head
        while current:
            if current.data['id'] == song_id:
                return current
            current = current.next
        return None

class DataManager:
    """Manager untuk handle penyimpanan dan pembacaan data"""
    def __init__(self, file_path='music_data.json'):
        self.file_path = file_path
    
    def save_data(self, library, playlists):
        """Simpan data ke JSON"""
        try:
            data = {
                'library': library,
                'playlists': {}
            }
            
            for name, playlist in playlists.items():
                data['playlists'][name] = {
                    'image_path': playlist.image_path,
                    'description': playlist.description,
                    'songs': playlist.to_list()
                }
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            raise Exception(f"Gagal menyimpan data: {e}")
    
    def load_data(self):
        """Load data dari JSON"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            library = data.get('library', [])
            
            playlists = {}
            playlists_data = data.get('playlists', {})
            for name, content in playlists_data.items():
                dll = DoublyLinkedList()
                
                # Check format compatibility (list of songs vs dict with metadata)
                if isinstance(content, list):
                    songs = content
                    image_path = None
                    description = ""
                else:
                    songs = content.get('songs', [])
                    image_path = content.get('image_path')
                    description = content.get('description', "")
                
                dll.image_path = image_path
                dll.description = description
                for song in songs:
                    dll.append(song)
                playlists[name] = dll
                
            return library, playlists
        except FileNotFoundError:
            return [], {'My Favorites': DoublyLinkedList()}
        except Exception as e:
            raise Exception(f"Gagal memuat data: {e}")
# ui_components.py
import tkinter as tk
from tkinter import ttk

class UIStyles:
    """Kelas untuk mengelola style dan warna UI"""
    def __init__(self):
        self.colors = {
            'bg_main': '#0f172a',
            'bg_sec': '#1e293b',
            'accent': '#537FE7',
            'accent_dark': '#3A59A2',
            'text': '#f1f5f9',
            'text_sec': '#94a3b8',
            'success': '#10b981',
            'white': '#ffffff',
            'entry_bg': '#334155',
            'entry_fg': '#ffffff'
        }
    
    def configure_treeview_style(self):
        """Configure style untuk Treeview"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', 
                       background=self.colors['entry_bg'], 
                       foreground=self.colors['text'], 
                       fieldbackground=self.colors['entry_bg'], 
                       borderwidth=0)
        style.configure('Treeview.Heading', 
                       background=self.colors['bg_sec'], 
                       foreground=self.colors['text_sec'],
                       borderwidth=0)
        style.map('Treeview', 
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', self.colors['white'])])

class SongDialog:
    """Dialog untuk menambah/edit lagu"""
    def __init__(self, parent, title, colors, song_data=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.configure(bg=colors['bg_main'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.colors = colors
        self.song_data = song_data
        self.result = None
        
        self.create_widgets()
    
    def create_widgets(self):
        fields = ['Judul', 'Artis', 'Genre', 'Album', 'Tahun', 'Durasi']
        self.entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(self.dialog, text=f"{field}:", font=('Arial', 11), 
                    bg=self.colors['bg_main'], fg=self.colors['text']
                   ).grid(row=i, column=0, padx=20, pady=10, sticky='w')
            
            entry = tk.Entry(self.dialog, font=('Arial', 11), 
                           bg=self.colors['entry_bg'], fg=self.colors['entry_fg'],
                           insertbackground=self.colors['accent'], relief='flat', width=30)
            entry.grid(row=i, column=1, padx=20, pady=10)
            self.entries[field] = entry
        
        if self.song_data:
            self.populate_fields()
        
        btn_frame = tk.Frame(self.dialog, bg=self.colors['bg_main'])
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Simpan", font=('Arial', 11, 'bold'), 
                 bg=self.colors['accent'], fg=self.colors['white'], 
                 command=self.on_save, relief='flat',
                 padx=20, pady=10, cursor='hand2'
                ).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="✖ Batal", font=('Arial', 11), 
                 bg=self.colors['accent_dark'], fg=self.colors['white'], 
                 command=self.dialog.destroy, relief='flat',
                 padx=20, pady=10, cursor='hand2'
                ).pack(side='left', padx=10)
    
    def populate_fields(self):
        """Isi field dengan data lagu yang ada"""
        if self.song_data:
            mapping = {
                'Judul': 'title',
                'Artis': 'artist',
                'Genre': 'genre',
                'Album': 'album',
                'Tahun': 'year',
                'Durasi': 'duration'
            }
            for ui_field, data_field in mapping.items():
                if ui_field in self.entries:
                    self.entries[ui_field].insert(0, str(self.song_data.get(data_field, '')))
    
    def on_save(self):
        """Handler untuk tombol save"""
        self.result = {
            'title': self.entries['Judul'].get(),
            'artist': self.entries['Artis'].get(),
            'genre': self.entries['Genre'].get() or 'Unknown',
            'album': self.entries['Album'].get() or 'Unknown',
            'year': int(self.entries['Tahun'].get()) if self.entries['Tahun'].get().isdigit() else 2024,
            'duration': self.entries['Durasi'].get() or '0:00'
        }
        self.dialog.destroy()
    
    def show(self):
        """Tampilkan dialog dan tunggu hasil"""
        self.dialog.wait_window()
        return self.result

class QueueDialog:
    """Dialog untuk menampilkan antrean lagu"""
    def __init__(self, parent, title, colors, queue):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x400")
        self.dialog.configure(bg=colors['bg_main'])
        
        tk.Label(self.dialog, text="Antrean Lagu", font=('Arial', 14, 'bold'),
                bg=colors['bg_main'], fg=colors['text']).pack(pady=10)
        
        listbox = tk.Listbox(self.dialog, font=('Arial', 11), 
                           bg=colors['entry_bg'], fg=colors['text'])
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        for i, song in enumerate(queue, 1):
            listbox.insert(tk.END, f"{i}. {song['title']} - {song['artist']}")
        
        tk.Button(self.dialog, text="Hapus Antrean", bg=colors['accent_dark'], 
                fg=colors['white'], command=self.dialog.destroy).pack(pady=10)
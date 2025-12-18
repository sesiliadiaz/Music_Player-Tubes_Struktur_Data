import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

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
    def __init__(self, parent, title, colors, song_data=None, existing_ids=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x500")
        self.dialog.configure(bg=colors['bg_main'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.colors = colors
        self.song_data = song_data
        self.existing_ids = existing_ids or []
        self.result = None
        
        self.image_path = None
        
        self.create_widgets()
    
    def create_widgets(self):
        fields = ['ID', 'Judul', 'Artis', 'Genre', 'Album', 'Tahun', 'Durasi']
        self.entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(self.dialog, text=f"{field}:", font=('Arial', 11), 
                    bg=self.colors['bg_main'], fg=self.colors['text']
                   ).grid(row=i, column=0, padx=20, pady=5, sticky='w')
            
            entry = tk.Entry(self.dialog, font=('Arial', 11), 
                           bg=self.colors['entry_bg'], fg=self.colors['entry_fg'],
                           insertbackground=self.colors['accent'], relief='flat', width=30)
            entry.grid(row=i, column=1, padx=20, pady=5)
            self.entries[field] = entry
            
        # Image Upload
        row = len(fields)
        tk.Label(self.dialog, text="Cover:", font=('Arial', 11), 
                bg=self.colors['bg_main'], fg=self.colors['text']
               ).grid(row=row, column=0, padx=20, pady=5, sticky='w')
        
        img_frame = tk.Frame(self.dialog, bg=self.colors['bg_main'])
        img_frame.grid(row=row, column=1, padx=20, pady=5, sticky='w')
        
        self.img_label = tk.Label(img_frame, text="Tidak ada gambar dipilih", 
                                font=('Arial', 9), bg=self.colors['bg_main'], 
                                fg=self.colors['text_sec'], wraplength=200)
        self.img_label.pack(side='left', padx=(0, 10))
        
        tk.Button(img_frame, text="Pilih Gambar", font=('Arial', 9),
                 bg=self.colors['accent'], fg=self.colors['white'],
                 command=self.select_image).pack(side='left')
        
        if self.song_data:
            self.populate_fields()
        
        btn_frame = tk.Frame(self.dialog, bg=self.colors['bg_main'])
        btn_frame.grid(row=row + 1, column=0, columnspan=2, pady=20)
        
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
                'ID': 'id',
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
                if 'ID' in self.entries:
                    self.entries['ID'].config(state='disabled')
            
            if self.song_data.get('image_path'):
                self.image_path = self.song_data['image_path']
                self.img_label.config(text=os.path.basename(self.image_path))
    
    def select_image(self):
        filename = filedialog.askopenfilename(
            title="Pilih Gambar Album",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if filename:
            self.image_path = filename
            self.img_label.config(text=os.path.basename(filename))
    
    def on_save(self):
        """Handler untuk tombol save"""
        # Ambil ID dari entry atau song_data (jika edit mode)
        if self.song_data:
            song_id = self.song_data.get('id', '')
        else:
            raw_id = self.entries['ID'].get() if 'ID' in self.entries else ''
            if not raw_id:
                messagebox.showwarning("Peringatan", "ID wajib diisi!")
                return
            
            try:
                song_id = int(raw_id)
            except ValueError:
                messagebox.showwarning("Peringatan", "ID harus berupa angka!")
                return
            
            if song_id in self.existing_ids:
                messagebox.showerror("Error", f"Lagu dengan ID {song_id} sudah ada!")
                return
        
        self.result = {
            'id': song_id,
            'title': self.entries['Judul'].get(),
            'artist': self.entries['Artis'].get(),
            'genre': self.entries['Genre'].get() or 'Unknown',
            'album': self.entries['Album'].get() or 'Unknown',
            'year': int(self.entries['Tahun'].get()) if self.entries['Tahun'].get().isdigit() else 2024,
            'duration': self.entries['Durasi'].get() or '0:00',
            'image_path': self.image_path
        }
        self.dialog.destroy()
    
    def show(self):
        """Tampilkan dialog dan tunggu hasil"""
        self.dialog.wait_window()
        return self.result


class PlaylistDialog:
    """Dialog untuk menambah playlist"""
    def __init__(self, parent, title, colors, existing_names=None, initial_data=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500") 
        self.dialog.configure(bg=colors['bg_main'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.colors = colors
        self.existing_names = existing_names or []
        self.initial_data = initial_data
        self.result = None
        self.image_path = initial_data.get('image_path') if initial_data else None
        
        self.create_widgets()
        
        if initial_data:
            self.name_entry.insert(0, initial_data.get('name', ''))
            self.desc_entry.insert(0, initial_data.get('description', ''))
            if self.image_path:
                 self.img_label.config(text=os.path.basename(self.image_path))
    
    def create_widgets(self):
        # Name
        tk.Label(self.dialog, text="Nama Playlist:", font=('Arial', 11), 
                bg=self.colors['bg_main'], fg=self.colors['text']
               ).pack(anchor='w', padx=20, pady=(20, 5))
        
        self.name_entry = tk.Entry(self.dialog, font=('Arial', 11), 
                                 bg=self.colors['entry_bg'], fg=self.colors['entry_fg'],
                                 insertbackground=self.colors['accent'], relief='flat', width=30)
        self.name_entry.pack(fill='x', padx=20)
        
        # Cover Image
        tk.Label(self.dialog, text="Kover Playlist:", font=('Arial', 11), 
                bg=self.colors['bg_main'], fg=self.colors['text']
               ).pack(anchor='w', padx=20, pady=(15, 5))
        
        img_frame = tk.Frame(self.dialog, bg=self.colors['bg_main'])
        img_frame.pack(fill='x', padx=20)
        
        self.img_label = tk.Label(img_frame, text="Tidak ada gambar dipilih", 
                                font=('Arial', 9), bg=self.colors['bg_main'], 
                                fg=self.colors['text_sec'], wraplength=200)
        self.img_label.pack(side='left', padx=(0, 10))
        
        tk.Button(img_frame, text="Pilih Gambar", font=('Arial', 9),
                 bg=self.colors['accent'], fg=self.colors['white'],
                 command=self.select_image).pack(side='left')
        
        # Description
        tk.Label(self.dialog, text="Deskripsi (Opsional):", font=('Arial', 11), 
                bg=self.colors['bg_main'], fg=self.colors['text']
               ).pack(anchor='w', padx=20, pady=(15, 5))
        
        self.desc_entry = tk.Entry(self.dialog, font=('Arial', 11), 
                                 bg=self.colors['entry_bg'], fg=self.colors['entry_fg'],
                                 insertbackground=self.colors['accent'], relief='flat', width=30)
        self.desc_entry.pack(fill='x', padx=20)

        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=self.colors['bg_main'])
        btn_frame.pack(pady=30)
        
        action_text = "💾 Simpan" if self.initial_data else "💾 Buat"
        tk.Button(btn_frame, text=action_text, font=('Arial', 11, 'bold'), 
                 bg=self.colors['accent'], fg=self.colors['white'], 
                 command=self.on_save, relief='flat',
                 padx=20, pady=8, cursor='hand2'
                ).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="✖ Batal", font=('Arial', 11), 
                 bg=self.colors['accent_dark'], fg=self.colors['white'], 
                 command=self.dialog.destroy, relief='flat',
                 padx=20, pady=8, cursor='hand2'
                ).pack(side='left', padx=10)
    
    def select_image(self):
        filename = filedialog.askopenfilename(
            title="Pilih Gambar Playlist",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if filename:
            self.image_path = filename
            self.img_label.config(text=os.path.basename(filename))
    
    def on_save(self):
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Peringatan", "Nama playlist wajib diisi!")
            return
        
        # Check duplicate name, but allow same name if editing
        old_name = self.initial_data.get('name') if self.initial_data else None
        if name != old_name and name in self.existing_names:
            messagebox.showwarning("Peringatan", "Nama playlist sudah ada!")
            return
        
        self.result = {
            'name': name,
            'image_path': self.image_path,
            'description': desc
        }
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.result

class QueueDialog:
    """Dialog untuk menampilkan antrean lagu"""
    def __init__(self, parent, title, colors, queue):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x400")
        self.dialog.configure(bg=colors['bg_main'])
        
        tk.Label(self.dialog, text=title, font=('Arial', 14, 'bold'),
                bg=colors['bg_main'], fg=colors['text']).pack(pady=10)
        
        listbox = tk.Listbox(self.dialog, font=('Arial', 11), 
                           bg=colors['entry_bg'], fg=colors['text'])
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        for i, song in enumerate(queue, 1):
            listbox.insert(tk.END, f"{i}. {song['title']} - {song['artist']}")
        
        tk.Button(self.dialog, text="Tutup", bg=colors['accent_dark'], 
                fg=colors['white'], command=self.dialog.destroy).pack(pady=10)
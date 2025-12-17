# main_app.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from models import DataManager
from ui_components import UIStyles
from admin_controller import AdminController
from user_controller import UserController
from playlist_controller import PlaylistController

class MusicPlayerApp:
    def __init__(self, root):
        self.styles = UIStyles()
        self.colors = self.styles.colors
        
        self.root = root
        self.root.title("Music Player - Aplikasi Pemutar Musik")
        self.root.geometry("1200x700")
        self.root.configure(bg=self.colors['bg_main'])
        
        # Initialize controllers
        self.admin_controller = AdminController(self)
        self.user_controller = UserController(self)
        self.playlist_controller = PlaylistController(self)
        self.data_manager = DataManager()
        
        # Load data
        self.library, self.playlists = self.data_manager.load_data()
        
        # State
        self.role = 'user'
        self.current_song = None
        self.played_history = []
        self.play_queue = []
        self.is_playing = False
        self.current_view = 'library'
        self.selected_playlist = None
        self.search_query = ""
        
        # Initialize UI components
        self.title_label = None
        self.tree = None
        self.playlist_frame = None
        self.current_song_label = None
        self.play_btn = None
        self.status_label = None
        self.add_song_btn = None
        self.back_btn = None
        self.add_song_btn = None
        self.back_btn = None
        self.context_menu = None
        self.current_image_label = None
        self.current_image = None # Keep reference
        
        # New Header Elements
        self.header_frame = None
        self.header_img_label = None
        self.header_type = None
        self.header_title = None
        self.header_desc = None
        self.header_play_btn = None 
        self.header_icon = None # Keep ref for header image
        
        self.show_role_selection()
    
    # ==================== DATA MANAGEMENT ====================
    def save_to_json(self):
        try:
            self.data_manager.save_data(self.library, self.playlists)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # ==================== UI SETUP ====================
    def setup_ui(self):
        """Setup UI utama"""
        # Header
        header = tk.Frame(self.root, bg=self.colors['bg_sec'], height=80)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        tk.Label(header, text="🎵 Music Player", font=('Arial', 20, 'bold'), 
                bg=self.colors['bg_sec'], fg=self.colors['text']).pack(side='left', padx=20, pady=20)
        
        tk.Button(header, text="📋 Antrean", font=('Arial', 10, 'bold'),
            bg=self.colors['accent'], fg=self.colors['white'], 
            command=self.user_controller.show_queue,
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side='right', padx=10, pady=20)

        tk.Button(header, text="📜 Riwayat", font=('Arial', 10, 'bold'),
            bg=self.colors['accent'], fg=self.colors['white'], 
            command=self.user_controller.show_history,
            padx=15, pady=8, relief='flat', cursor='hand2'
        ).pack(side='right', padx=10, pady=20)

        self.back_btn = tk.Button(header, text="⬅ Kembali", font=('Arial', 10, 'bold'),
                         bg=self.colors['accent'], fg=self.colors['white'], 
                         command=self.back_to_role_selection,
                         padx=15, pady=8, relief='flat', cursor='hand2')
        self.back_btn.pack(side='right', padx=20, pady=20)
        
        # Player controls (Packed before main container to ensure visibility at bottom)
        self.setup_player_controls()
        
        # Container utama
        main_container = tk.Frame(self.root, bg=self.colors['bg_main'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sidebar
        self.setup_sidebar(main_container)
        
        # Content area
        self.setup_content_area(main_container)
        
    
    def setup_sidebar(self, parent):
        """Setup sidebar dengan menu"""
        sidebar = tk.Frame(parent, bg=self.colors['bg_sec'], width=200)
        sidebar.pack(side='left', fill='y', padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Library button
        library_btn = tk.Button(sidebar, text="🏠 Library", font=('Arial', 11),
                               bg=self.colors['accent_dark'], fg=self.colors['white'], 
                               command=self.show_library,
                               relief='flat', anchor='w', padx=20, pady=12)
        library_btn.pack(fill='x', padx=10, pady=(10, 5))
        
        # Playlists
        tk.Label(sidebar, text="PLAYLISTS", font=('Arial', 9, 'bold'),
                bg=self.colors['bg_sec'], fg=self.colors['text_sec']
               ).pack(fill='x', padx=20, pady=(15, 5))
        
        # Add playlist button (Packed first to ensure visibility at bottom)
        add_pl_btn = tk.Button(sidebar, text="➕ Buat Playlist", font=('Arial', 10),
                              bg=self.colors['accent'], fg=self.colors['white'], 
                              command=self.playlist_controller.create_playlist,
                              relief='flat', padx=20, pady=10)
        add_pl_btn.pack(side='bottom', fill='x', padx=10, pady=10)
        
        self.playlist_frame = tk.Frame(sidebar, bg=self.colors['bg_sec'])
        self.playlist_frame.pack(fill='both', expand=True, padx=10)
        
        self.playlist_controller.refresh_playlist_buttons()
    
    def setup_content_area(self, parent):
        """Setup area konten utama"""
        content = tk.Frame(parent, bg=self.colors['bg_main'])
        content.pack(side='left', fill='both', expand=True)
        
        # Search bar & actions
        search_frame = tk.Frame(content, bg=self.colors['bg_sec'])
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_entry = tk.Entry(search_frame, font=('Arial', 11), 
                               bg=self.colors['entry_bg'], 
                               fg=self.colors['entry_fg'], 
                               insertbackground=self.colors['accent'], 
                               relief='flat')
        search_entry.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        search_entry.insert(0, "🔍 Cari lagu (judul, artis, genre, album, id)...")
        search_entry.bind('<KeyRelease>', lambda e: self.search_songs(search_entry.get()))
        search_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(search_entry))
        search_entry.bind('<FocusOut>', lambda e: self.restore_placeholder(search_entry))
        
        sort_frame = tk.Frame(search_frame, bg=self.colors['bg_sec'])
        sort_frame.pack(side='right', padx=5)

        tk.Label(sort_frame, text="Urutkan:", bg=self.colors['bg_sec'], 
                fg=self.colors['text']).pack(side='left', padx=5)

        sort_by = ttk.Combobox(sort_frame, values=['title', 'artist', 'year', 'id'], 
                            state='readonly', width=10)
        sort_by.set('title')
        sort_by.pack(side='left', padx=5)

        sort_order = ttk.Combobox(sort_frame, values=['asc', 'desc'], 
                                state='readonly', width=8)
        sort_order.set('asc')
        sort_order.pack(side='left', padx=5)

        tk.Button(sort_frame, text="↕ Urutkan", 
                 command=lambda: self.sort_songs(sort_by.get(), sort_order.get()),
                 bg=self.colors['accent'], fg=self.colors['white'], 
                 relief='flat', padx=10, pady=6).pack(side='left', padx=5)

        self.add_song_btn = tk.Button(search_frame, text="➕ Tambah Lagu", 
                                      font=('Arial', 10, 'bold'), 
                                      bg=self.colors['accent'], 
                                      fg=self.colors['white'], 
                                      command=self.admin_controller.show_add_song_dialog,
                                      relief='flat', padx=15, pady=8, cursor='hand2')
        self.add_song_btn.pack(side='right', padx=10, pady=10)
        

        
        if self.role != 'admin':
            self.add_song_btn.pack_forget()
        
        # Song list
        list_frame = tk.Frame(content, bg=self.colors['bg_sec'])
        list_frame.pack(fill='both', expand=True)
        
        # Standard Header (Simple)
        self.title_label = tk.Label(list_frame, text="Library Musik", 
                                    font=('Arial', 16, 'bold'), 
                                    bg=self.colors['bg_sec'], fg=self.colors['text'],
                                    compound='left', padx=10)
        self.title_label.pack(anchor='w', padx=20, pady=15)

        # Header Area - Initially hidden
        self.header_container = tk.Frame(list_frame, bg=self.colors['bg_sec'], height=180)
        # self.header_container.pack(fill='x', padx=20, pady=20) # Don't pack initially
        self.header_container.pack_propagate(False)
        
        # Header Image
        self.header_img_label = tk.Label(self.header_container, bg=self.colors['bg_sec'], 
                                       width=150, height=150) 
        self.header_img_label.pack(side='left', padx=(0, 20))
        
        # Header Info
        header_info = tk.Frame(self.header_container, bg=self.colors['bg_sec'])
        header_info.pack(side='left', fill='both', expand=True, pady=10)
        
        self.header_type = tk.Label(header_info, text="LIBRARY", 
                                   font=('Arial', 10, 'bold'), 
                                   fg=self.colors['text'], bg=self.colors['bg_sec'], anchor='w')
        self.header_type.pack(fill='x')
        
        self.header_title = tk.Label(header_info, text="Library Musik", 
                                    font=('Arial', 32, 'bold'), 
                                    fg=self.colors['white'], bg=self.colors['bg_sec'], anchor='w')
        self.header_title.pack(fill='x')
        
        self.header_desc = tk.Label(header_info, text="Semua lagu anda", 
                                   font=('Arial', 11), 
                                   fg=self.colors['text_sec'], bg=self.colors['bg_sec'], anchor='w')
        self.header_desc.pack(fill='x', pady=(0, 10))
        

        
        # self.title_label removed in favor of this structure
        # But for compatibility if other code references title_label, we alias it or fix them.
        # Fixed: we will use update_header everywhere.
        
        # Treeview untuk daftar lagu
        columns = ('ID', 'Judul', 'Artis', 'Genre', 'Album', 'Tahun', 'Durasi')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', 
                                height=15, selectmode='browse')
        
        # Setup columns
        self.tree.column('#0', width=60, anchor='center')
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Judul', width=200)
        self.tree.column('Artis', width=150)
        self.tree.column('Genre', width=100)
        self.tree.column('Album', width=150)
        self.tree.column('Tahun', width=80, anchor='center')
        self.tree.column('Durasi', width=80, anchor='center')
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side='right', fill='y', padx=(0, 20), pady=(0, 20))
        
        # Bind double click to play
        self.tree.bind('<Double-1>', lambda e: self.user_controller.play_selected_song())
        
        # Context menu
        self.setup_context_menu()
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Apply styles
        self.styles.configure_treeview_style()
        self.refresh_song_list()
    
    def setup_player_controls(self):
        """Setup kontrol player di bagian bawah"""
        player = tk.Frame(self.root, bg=self.colors['bg_sec'], height=100)
        player.pack(fill='x', side='bottom')
        player.pack_propagate(False)
        
        # Current song info container
        info_frame = tk.Frame(player, bg=self.colors['bg_sec'])
        info_frame.pack(side='left', padx=20, pady=10)

        # Image Label
        self.current_image_label = tk.Label(info_frame, bg=self.colors['bg_sec'])
        self.current_image_label.pack(side='left', padx=(0, 15))
        
        # Text Info
        self.current_song_label = tk.Label(info_frame, text="Tidak ada lagu diputar", 
                                          font=('Arial', 12, 'bold'), 
                                          bg=self.colors['bg_sec'], 
                                          fg=self.colors['text'],
                                          anchor='w', justify='left')
        self.current_song_label.pack(side='left')
        
        # Control buttons
        controls = tk.Frame(player, bg=self.colors['bg_sec'])
        controls.pack(side='left', expand=True)
        
        tk.Button(controls, text="⏮", font=('Arial', 20), 
                 bg=self.colors['accent_dark'], fg=self.colors['white'],
                 command=self.user_controller.prev_song, relief='flat', 
                 width=3, cursor='hand2').pack(side='left', padx=5)
        
        self.play_btn = tk.Button(controls, text="▶", font=('Arial', 20), 
                                  bg=self.colors['accent'], fg=self.colors['white'], 
                                  command=self.user_controller.toggle_play, 
                                  relief='flat', width=3, cursor='hand2')
        self.play_btn.pack(side='left', padx=10)
        
        tk.Button(controls, text="⏭", font=('Arial', 20), 
                 bg=self.colors['accent_dark'], fg=self.colors['white'],
                 command=self.user_controller.next_song, relief='flat', 
                 width=3, cursor='hand2').pack(side='left', padx=5)
        
        # Status
        self.status_label = tk.Label(player, text="⏸ Tidak diputar", font=('Arial', 10),
                                    bg=self.colors['bg_sec'], fg=self.colors['text_sec'])
        self.status_label.pack(side='right', padx=30, pady=10)
        self.status_label.pack(side='right', padx=30, pady=10)
    
    def setup_context_menu(self):
        """Setup context menu (klik kanan)"""
        self.context_menu = tk.Menu(self.root, tearoff=0, 
                                   bg=self.colors['entry_bg'], 
                                   fg=self.colors['text'],
                                   activebackground=self.colors['accent'], 
                                   activeforeground=self.colors['white'])
        self.context_menu.add_command(label="▶ Play", 
                                     command=self.user_controller.play_selected_song)
        self.context_menu.add_command(label="➕ Tambah ke Antrean", 
                                     command=self.user_controller.add_to_queue)
        self.context_menu.add_separator()
    
    def show_context_menu(self, event):
        """Tampilkan context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Clear existing menu items after separator
            self.context_menu.delete(2, tk.END)
            
            # Ambil data lagu
            song_id = self.tree.item(item)['values'][0]
            song = next((s for s in self.library if s['id'] == song_id), None)
            
            if self.role == 'admin':
                self.context_menu.add_command(label="✏ Edit", 
                                             command=self.admin_controller.edit_selected_song)
                self.context_menu.add_command(label="🗑 Hapus", 
                                             command=self.admin_controller.delete_selected_song)
            else:
                if self.current_view == 'library':
                    # Add to playlist submenu
                    playlist_menu = tk.Menu(self.context_menu, tearoff=0, 
                                          bg=self.colors['entry_bg'], 
                                          fg=self.colors['text'], 
                                          activebackground=self.colors['accent'])
                    for playlist_name in self.playlists.keys():
                        playlist_menu.add_command(
                            label=playlist_name,
                            command=lambda p=playlist_name: 
                            self.playlist_controller.add_to_playlist(p)
                        )
                    self.context_menu.add_cascade(label="➕ Tambah ke Playlist", 
                                                 menu=playlist_menu)
                elif self.current_view == 'playlist':
                    # Jangan tampilkan opsi hapus jika di playlist My Favorites
                    if self.selected_playlist != 'My Favorites':
                        self.context_menu.add_command(label="🗑 Hapus dari Playlist", 
                                                    command=self.playlist_controller.remove_from_playlist)
            
            # Menu favorite
            if song:
                fav_text = "💔 Hapus dari Favorite" if song.get('favorite', False) else "❤ Tambah ke Favorite"
                self.context_menu.add_separator()
                self.context_menu.add_command(label=fav_text, 
                                             command=self.user_controller.toggle_favorite)
            
            self.context_menu.tk_popup(event.x_root, event.y_root)
    
    # ==================== VIEW CONTROL ====================
    def show_library(self):
        """Menampilkan library"""
        self.current_view = 'library'
        self.selected_playlist = None
        self.show_simple_header("Library Musik")
        self.refresh_song_list()
        
    def show_simple_header(self, title):
        """Tampilkan header sederhana (default)"""
        self.header_container.pack_forget()
        self.title_label.config(text=title)
        self.title_label.pack(anchor='w', padx=20, pady=15, before=self.tree)

    def update_header(self, title, type_text="LIBRARY", image_path=None, description=""):
        """Update tampilan header ala Spotify"""
        self.title_label.pack_forget()
        self.header_container.pack(fill='x', padx=20, pady=20, before=self.tree)
        
        self.header_title.config(text=title)
        self.header_type.config(text=type_text)
        self.header_desc.config(text=description)
        
        # Image Logic
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((150, 150), Image.Resampling.LANCZOS)
                self.header_icon = ImageTk.PhotoImage(img)
                self.header_img_label.config(image=self.header_icon, width=150, height=150)
            except Exception as e:
                print(f"Error header image: {e}")
                self.header_img_label.config(image='', width=20, bg=self.colors['accent'])
        else:
             # Default generic icon or empty
             self.header_img_label.config(image='', width=20, bg=self.colors['accent_dark']) # Simple block color fallback

    
    def refresh_song_list(self):
        """Refresh daftar lagu pada TreeView"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.current_view == 'library':
            songs = self.library
        else:
            playlist = self.playlists[self.selected_playlist]
            songs = playlist.to_list()
        
        # Filter pencarian
        query = self.search_query.lower()
        if query:
            songs = [
                s for s in songs if 
                query in s['title'].lower() or
                query in s['artist'].lower() or
                query in s['genre'].lower() or
                query in s['album'].lower() or
                query in str(s['id']) or
                query in str(s['year'])
            ]
        
        for song in songs:
            icon = '⭐' if song.get('favorite', False) else '🎵'
            self.tree.insert('', 'end', text=icon, values=(
                song['id'], song['title'], song['artist'],
                song['genre'], song['album'], song['year'], song['duration']
            ))
    
    def sort_songs(self, by='title', order='asc'):
        """Mengurutkan lagu berdasarkan kriteria"""
        if self.current_view == 'library':
            songs = self.library
        else:
            songs = self.playlists[self.selected_playlist].to_list()
        
        reverse = (order == 'desc')
        
        if by == 'title':
            songs.sort(key=lambda s: s['title'].lower(), reverse=reverse)
        elif by == 'artist':
            songs.sort(key=lambda s: s['artist'].lower(), reverse=reverse)
        elif by == 'year':
            songs.sort(key=lambda s: s['year'], reverse=reverse)
        elif by == 'id':
            songs.sort(key=lambda s: s['id'], reverse=reverse)
        
        # Update data
        if self.current_view == 'library':
            self.library = songs
        else:
            # Rebuild playlist dengan urutan baru
            from models import DoublyLinkedList
            playlist = DoublyLinkedList()
            playlist.image_path = self.playlists[self.selected_playlist].image_path
            for song in songs:
                playlist.append(song)
            self.playlists[self.selected_playlist] = playlist
        
        self.save_to_json()
        self.refresh_song_list()
    
    # ==================== SEARCH ====================
    def search_songs(self, text):
        self.search_query = text
        self.refresh_song_list()
    
    def clear_placeholder(self, entry):
        if entry.get().startswith("🔍"):
            entry.delete(0, tk.END)
    
    def restore_placeholder(self, entry):
        if not entry.get():
            entry.insert(0, "🔍 Cari lagu (judul, artis, genre, album, id)...")
    
    # ==================== ROLE MODE ====================
    def back_to_role_selection(self):
        """Kembali ke tampilan pemilihan role"""
        if messagebox.askyesno("Konfirmasi", 
                              "Kembali ke pemilihan mode?\nPerubahan yang belum disimpan akan tetap tersimpan."):
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Reset state
            self.current_song = None
            self.is_playing = False
            self.current_view = 'library'
            self.selected_playlist = None
            self.search_query = ""
            
            self.show_role_selection()
    
    def show_admin_login(self):
        """Tampilkan form login di tengah layar utama"""
        login_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        login_frame.pack(fill='both', expand=True)
        
        center_container = tk.Frame(login_frame, bg=self.colors['bg_sec'], 
                                  padx=50, pady=40)
        center_container.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(center_container, text="🔐 Login Admin", font=('Arial', 20, 'bold'),
                bg=self.colors['bg_sec'], fg=self.colors['text']).pack(pady=(0, 30))
        
        # Username
        tk.Label(center_container, text="Username:", font=('Arial', 11),
                bg=self.colors['bg_sec'], fg=self.colors['text']
               ).pack(anchor='w', padx=20, pady=(10, 5))
        username_entry = tk.Entry(center_container, font=('Arial', 12), 
                                bg=self.colors['entry_bg'],
                                fg=self.colors['entry_fg'], width=30, relief='flat')
        username_entry.pack(padx=20, pady=(0, 15))
        
        # Password
        tk.Label(center_container, text="Password:", font=('Arial', 11),
                bg=self.colors['bg_sec'], fg=self.colors['text']
               ).pack(anchor='w', padx=20, pady=(5, 5))
        password_entry = tk.Entry(center_container, font=('Arial', 12), 
                                bg=self.colors['entry_bg'],
                                fg=self.colors['entry_fg'], width=30, show='●', 
                                relief='flat')
        password_entry.pack(padx=20, pady=(0, 20))
        
        def check_login():
            if username_entry.get() == "anakmalem" and password_entry.get() == "tel-u24":
                login_frame.destroy()
                self.role = 'admin'
                self.setup_ui()
            else:
                messagebox.showerror("Login Gagal", "Username atau password salah!")
        
        def go_back():
            login_frame.destroy()
            self.show_role_selection()
        
        # Tombol Login
        tk.Button(center_container, text="Login", font=('Arial', 12, 'bold'),
                bg=self.colors['accent'], fg=self.colors['white'], command=check_login,
                padx=50, pady=12, relief='flat', cursor='hand2').pack(pady=(0, 10))
        
        # Link "kembali"
        back_label = tk.Label(center_container, text="kembali", 
                            font=('Arial', 9, 'underline'),
                            bg=self.colors['bg_sec'], fg=self.colors['text_sec'], 
                            cursor='hand2')
        back_label.pack(pady=(5, 0))
        back_label.bind('<Button-1>', lambda e: go_back())
    
    def show_role_selection(self):
        """Tampilkan pemilihan role"""
        selection_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        selection_frame.pack(fill='both', expand=True)
        
        tk.Label(selection_frame, text="🎵 Music Player", 
                font=('Arial', 28, 'bold'), 
                bg=self.colors['bg_main'], fg=self.colors['text']).pack(pady=80)
        
        tk.Label(selection_frame, text="Pilih mode penggunaan:", 
                font=('Arial', 14), 
                bg=self.colors['bg_main'], fg=self.colors['text_sec']).pack(pady=20)
        
        btn_frame = tk.Frame(selection_frame, bg=self.colors['bg_main'])
        btn_frame.pack(pady=50)
        
        def select_user():
            self.role = 'user'
            selection_frame.destroy()
            self.setup_ui()
        
        def select_admin():
            selection_frame.destroy()
            self.show_admin_login()
        
        tk.Button(btn_frame, text="👤 User Mode", 
                font=('Arial', 14, 'bold'), 
                bg=self.colors['accent_dark'], fg=self.colors['white'],
                command=select_user, relief='flat',
                padx=40, pady=20, cursor='hand2',
                width=15).pack(side='left', padx=20)
        
        tk.Button(btn_frame, text="🛠 Admin Mode", 
                font=('Arial', 14, 'bold'), 
                bg=self.colors['accent'], fg=self.colors['white'],
                command=select_admin, relief='flat',
                padx=40, pady=20, cursor='hand2',
                width=15).pack(side='left', padx=20)
    
    # ==================== PLAYER UI ====================
    def update_player_ui(self):
        """Update tampilan player di bagian bawah"""
        if not self.current_song:
            self.current_song_label.config(text="Tidak ada lagu diputar")
            self.status_label.config(text="⏸ Tidak diputar")
            self.play_btn.config(text="▶", bg=self.colors['accent'], 
                               fg=self.colors['white'])
            
            # Clear image
            self.current_image_label.configure(image='', width=0)
            self.current_image = None
            return
        
        # Update text
        self.current_song_label.config(
            text=f"🎵 {self.current_song['title']}\n👤 {self.current_song['artist']}"
        )
        
        # Update Image
        try:
            image_path = self.current_song.get('image_path')
            if image_path and os.path.exists(image_path):
                # Load and Resize
                img = Image.open(image_path)
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                self.current_image = ImageTk.PhotoImage(img)
                self.current_image_label.config(image=self.current_image, width=60, height=60)
            else:
                # Clear image if no path or file not found
                self.current_image_label.config(image='', width=0)
                self.current_image = None
        except Exception as e:
            print(f"Error updating player image: {e}")
            self.current_image_label.config(image='', width=0)
            self.current_image = None
        
        if self.is_playing:
            self.status_label.config(text="▶ Memutar")
            self.play_btn.config(text="⏸", bg=self.colors['accent_dark'], 
                               fg=self.colors['white'])
        else:
            self.status_label.config(text="⏸ Dijeda")
            self.play_btn.config(text="▶", bg=self.colors['accent'], 
                               fg=self.colors['white'])


# ==================== MAIN PROGRAM ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayerApp(root)
    root.mainloop()
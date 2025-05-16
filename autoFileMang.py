import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import shutil
import time
import threading
from collections import defaultdict
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class SmartFileOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("900x700")  # Slightly larger window for more features
        self.root.resizable(True, True)
        
        # Variables
        self.directory = tk.StringVar()
        self.file_types = {
            '.txt': tk.BooleanVar(value=True),
            '.pdf': tk.BooleanVar(value=False),  # PDF would require PyPDF2 or similar
            '.jpg': tk.BooleanVar(),
            '.png': tk.BooleanVar(),
            '.mp3': tk.BooleanVar(),
            '.mp4': tk.BooleanVar(),
            '.zip': tk.BooleanVar(),
            '.rar': tk.BooleanVar(),
            '.py': tk.BooleanVar(),
            '.doc': tk.BooleanVar(value=False),  # Would require python-docx
            '.docx': tk.BooleanVar(value=False),  # Would require python-docx
            '.xls': tk.BooleanVar(value=False),   # Would require openpyxl
            '.xlsx': tk.BooleanVar(value=False),  # Would require openpyxl
            'other': tk.BooleanVar()
        }
        self.use_tfidf = tk.BooleanVar(value=False)
        self.top_n = tk.IntVar(value=5)
        self.organize_by_type = tk.BooleanVar(value=True)
        self.organize_by_date = tk.BooleanVar(value=False)
        self.organize_by_size = tk.BooleanVar(value=False)
        self.organize_by_keywords = tk.BooleanVar(value=False)
        self.min_keyword_score = tk.DoubleVar(value=0.2)
        self.is_processing = False
        
        # Initialize NLP components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Directory Selection
        dir_frame = ttk.LabelFrame(main_frame, text="Target Directory", padding="10")
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Directory:").pack(anchor=tk.W)
        
        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = ttk.Entry(dir_entry_frame, textvariable=self.directory)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(
            dir_entry_frame, 
            text="Browse", 
            command=self.browse_directory
        ).pack(side=tk.LEFT)
        
        # File Type Selection
        file_type_frame = ttk.LabelFrame(main_frame, text="File Types to Process", padding="10")
        file_type_frame.pack(fill=tk.X, pady=5)
        
        file_type_grid = ttk.Frame(file_type_frame)
        file_type_grid.pack(fill=tk.X)
        
        file_types = [
            ('.txt', 'Text Files'),
            ('.pdf', 'PDF Files (keywords not extracted)'),
            ('.jpg', 'JPG Images'),
            ('.png', 'PNG Images'),
            ('.mp3', 'MP3 Audio'),
            ('.mp4', 'MP4 Video'),
            ('.zip', 'ZIP Archives'),
            ('.rar', 'RAR Archives'),
            ('.py', 'Python Files'),
            ('other', 'Other Files')
        ]
        
        # Organize checkboxes in 3 columns
        cols = 3
        for i, (ext, label) in enumerate(file_types):
            row = i // cols
            col = i % cols
            cb = ttk.Checkbutton(
                file_type_grid, 
                text=label, 
                variable=self.file_types[ext],
                onvalue=True, 
                offvalue=False
            )
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
        
        # Configuration Settings
        config_frame = ttk.LabelFrame(main_frame, text="Organization Settings", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        
        # TF-IDF Options
        tfidf_frame = ttk.Frame(config_frame)
        tfidf_frame.pack(fill=tk.X, pady=2)
        
        ttk.Checkbutton(
            tfidf_frame, 
            text="Extract keywords using TF-IDF", 
            variable=self.use_tfidf,
            onvalue=True, 
            offvalue=False
        ).pack(side=tk.LEFT)
        
        ttk.Label(tfidf_frame, text="Top keywords:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Spinbox(
            tfidf_frame, 
            from_=1, 
            to=10, 
            textvariable=self.top_n, 
            width=5
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            tfidf_frame, 
            text="Organize by keywords", 
            variable=self.organize_by_keywords,
            onvalue=True, 
            offvalue=False
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(tfidf_frame, text="Min score:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Spinbox(
            tfidf_frame, 
            from_=0.1, 
            to=1.0, 
            increment=0.1,
            textvariable=self.min_keyword_score, 
            width=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Organization Options
        org_frame = ttk.Frame(config_frame)
        org_frame.pack(fill=tk.X, pady=2)
        
        ttk.Checkbutton(
            org_frame, 
            text="Organize by file type", 
            variable=self.organize_by_type,
            onvalue=True, 
            offvalue=False
        ).pack(side=tk.LEFT)
        
        ttk.Checkbutton(
            org_frame, 
            text="Organize by date (year-month)", 
            variable=self.organize_by_date,
            onvalue=True, 
            offvalue=False
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Checkbutton(
            org_frame, 
            text="Organize by size", 
            variable=self.organize_by_size,
            onvalue=True, 
            offvalue=False
        ).pack(side=tk.LEFT, padx=10)
        
        # Process Button
        self.process_btn = ttk.Button(
            main_frame, 
            text="Organize Files", 
            command=self.start_processing,
            state=tk.NORMAL
        )
        self.process_btn.pack(fill=tk.X, pady=10)
        
        # Log Display
        log_frame = ttk.LabelFrame(main_frame, text="Process Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            bg='white', 
            fg='black',
            font=('Courier', 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = scrollbar.set
        
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory.set(directory)
            self.add_log(f"Directory selected: {directory}")
        
    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def validate_inputs(self):
        if not self.directory.get():
            messagebox.showerror("Error", "Please select a directory first")
            return False
        
        if not os.path.exists(self.directory.get()):
            messagebox.showerror("Error", "Selected directory does not exist")
            return False
            
        if not any(var.get() for var in self.file_types.values()):
            messagebox.showerror("Error", "Please select at least one file type")
            return False
            
        if self.organize_by_keywords.get() and not self.use_tfidf.get():
            messagebox.showerror("Error", "Keyword organization requires TF-IDF to be enabled")
            return False
            
        return True
        
    def start_processing(self):
        if not self.validate_inputs():
            return
            
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED, text="Processing...")
        
        # Get selected file types
        selected_types = [ext for ext, var in self.file_types.items() if var.get()]
        
        self.add_log("Starting file organization process...")
        self.add_log(f"Directory: {self.directory.get()}")
        self.add_log(f"File types: {', '.join(selected_types)}")
        self.add_log(f"Organize by type: {self.organize_by_type.get()}")
        self.add_log(f"Organize by date: {self.organize_by_date.get()}")
        self.add_log(f"Organize by size: {self.organize_by_size.get()}")
        self.add_log(f"Organize by keywords: {self.organize_by_keywords.get()}")
        
        # Run processing in a separate thread to keep UI responsive
        processing_thread = threading.Thread(
            target=self.process_files,
            args=(self.directory.get(), selected_types),
            daemon=True
        )
        processing_thread.start()
        
        # Check processing status periodically
        self.root.after(100, self.check_processing_status, processing_thread)
        
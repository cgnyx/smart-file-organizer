import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk

# Initialize NLTK components
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

class SmartFileOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("600x700")
        
        # Variables
        self.directory = tk.StringVar()
        self.use_tfidf = tk.BooleanVar(value=True)
        self.top_n = tk.IntVar(value=5)
        self.file_types = {
            '.txt': tk.BooleanVar(value=True),
            '.pdf': tk.BooleanVar(value=True),
            '.jpg': tk.BooleanVar(value=False),
            '.mp3': tk.BooleanVar(value=False),
            '.mp4': tk.BooleanVar(value=False),
            '.zip': tk.BooleanVar(value=False),
            '.py': tk.BooleanVar(value=False)
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # Directory Selection
        tk.Label(self.root, text="Target Directory:").pack(pady=(10, 0))
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(fill=tk.X, padx=10)
        tk.Entry(dir_frame, textvariable=self.directory).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.RIGHT)
        
        # File Type Selection
        tk.Label(self.root, text="File Types to Process:").pack(pady=(10, 0))
        file_type_frame = tk.Frame(self.root)
        file_type_frame.pack(fill=tk.X, padx=10)
        
        for i, (ext, var) in enumerate(self.file_types.items()):
            cb = tk.Checkbutton(file_type_frame, text=ext, variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w")
        
        # Configuration Options
        config_frame = tk.LabelFrame(self.root, text="Organization Settings")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Checkbutton(config_frame, text="Use TF-IDF for keyword extraction", 
                    variable=self.use_tfidf).pack(anchor="w")
        
        tk.Label(config_frame, text="Number of top keywords:").pack(anchor="w")
        tk.Entry(config_frame, textvariable=self.top_n).pack(anchor="w")
        
        # Process Button
        tk.Button(self.root, text="Organize Files", command=self.organize_files, 
                bg="green", fg="white").pack(pady=20)
        
        # Log Display
        self.log_text = tk.Text(self.root, height=15, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory.set(directory)
            self.add_log(f"Selected directory: {directory}")
    
    def organize_files(self):
        if not self.directory.get():
            messagebox.showerror("Error", "Please select a directory first")
            return
        
        selected_types = [ext for ext, var in self.file_types.items() if var.get()]
        if not selected_types:
            messagebox.showerror("Error", "Please select at least one file type")
            return
        
        self.add_log(f"Starting organization in: {self.directory.get()}")
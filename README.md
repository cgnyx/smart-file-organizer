A Python application that automatically organizes files in a directory based on:
- File type (e.g., Images, Documents)
- Creation/modification date
- File size
- **Content keywords** (using TF-IDF analysis)

## Features ✨

- 📂 **Directory Scanning**: Recursively processes all files in a selected directory
- 🏷️ **Smart Categorization**:
  - By file type (e.g., `.pdf`, `.jpg`, `.mp3`)
  - By date (year-month folders)
  - By size (Small, Medium, Large)
  - By **content keywords** (TF-IDF analysis for text files)
- 📊 **TF-IDF Analysis**:
  - Extracts meaningful keywords from text files
  - Scores keywords by importance
  - Organizes files into keyword-based folders
- 📝 **Logging**: Detailed processing logs with timestamps
- 🖥️ **GUI Interface**: Easy-to-use Tkinter interface

# Library Management System (LMS)

A desktop application for managing library operations, including book cataloging, user management, borrowing, returns with overdue handling, and reservation tracking. Built with **Python**, **Tkinter** for the GUI, and **Excel (via pandas + openpyxl)** for data persistence.

---

## Table of Contents

- [Features](#features)  
- [Architecture](#architecture)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Dependencies](#dependencies)  
- [Author](#author)

---

## Features

- Add, modify, delete books and users via an **admin interface**
- Borrow and return books with **due-date calculation** and **overdue fee management**
- **Search books** by ID, title, or author using a **Binary Search Tree**
- Reserve unavailable books with **tentative availability dates**
- **Persist data** to Excel files (`books.xlsx`, `users.xlsx`) on exit and load on startup
- **Activity logging** to `library_management.log`

---

## Architecture

### GUI
- **Tkinter + ttk** for a responsive, multi-frame interface

### Data Structures
- `BookBST`: Binary Search Tree for efficient book lookup by ID, title, author  
- `collections.deque`: Queue-based book reservation system  
- `dict`: In-memory dictionaries for books and users

### Persistence
- **pandas + openpyxl** for Excel read/write operations

### Logging
- Python’s `logging` module logs all admin/user actions to `library_management.log`

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/kavinbalaji2005/LibraryManagementSystem.git
cd LibraryManagementSystem/src
```

### 2. Install dependencies
```bash
pip install pandas openpyxl
```

---

## Usage

Run the application:
```bash
python LMS.py
```

- On launch, select **Admin Mode** (password: `1234`) or **User Mode**
- All changes are automatically saved to Excel files on exit

---

## Dependencies

- **Python 3.7+**
- `tkinter` (preinstalled in most Python distributions)
- `pandas`
- `openpyxl`

## Author

- [Kavin Balaji](https://github.com/kavinbalaji2005)

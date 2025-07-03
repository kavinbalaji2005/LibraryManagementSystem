import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from collections import deque
import pandas as pd
import logging

# Set up logging
logging.basicConfig(filename='library_management.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class TreeNode:
    def __init__(self, book):
        self.book = book
        self.left = None
        self.right = None

class BookBST:
    def __init__(self):
        self.root = None

    def insert(self, book):
        if self.root is None:
            self.root = TreeNode(book)
        else:
            self._insert(self.root, book)

    def _insert(self, node, book):
        if book.book_id < node.book.book_id:
            if node.left is None:
                node.left = TreeNode(book)
            else:
                self._insert(node.left, book)
        elif book.book_id > node.book.book_id:
            if node.right is None:
                node.right = TreeNode(book)
            else:
                self._insert(node.right, book)

    def search_by_id(self, book_id):
        return self._search_by_id(self.root, book_id)

    def _search_by_id(self, node, book_id):
        if node is None:
            return None
        if book_id == node.book.book_id:
            return node.book
        elif book_id < node.book.book_id:
            return self._search_by_id(node.left, book_id)
        else:
            return self._search_by_id(node.right, book_id)

    def search_by_title(self, title):
        return self._search_by_title(self.root, title)

    def _search_by_title(self, node, title):
        if node is None:
            return []
        results = []
        if title.lower() in node.book.title.lower():
            results.append(node.book)
        results += self._search_by_title(node.left, title)
        results += self._search_by_title(node.right, title)
        return results

    def search_by_author(self, author):
        return self._search_by_author(self.root, author)

    def _search_by_author(self, node, author):
        if node is None:
            return []
        results = []
        if author.lower() in node.book.author.lower():
            results.append(node.book)
        results += self._search_by_author(node.left, author)
        results += self._search_by_author(node.right, author)
        return results

class Book:
    def __init__(self, book_id, title, author, copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.copies = copies
        self.reservations = deque()  # Queue for reservations

    def to_dict(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'copies': self.copies
        }
    
    @staticmethod
    def from_dict(data):
        return Book(
            book_id=data['book_id'],
            title=data['title'],
            author=data['author'],
            copies=data['copies']
        )

class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.borrowed_books = []

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'borrowed_books': [(book.to_dict(), date, due_date) for book, date, due_date in self.borrowed_books]
        }

    @staticmethod
    def from_dict(data):
        user = User(
            user_id=data['user_id'],
            name=data['name']
        )
        user.borrowed_books = [(Book.from_dict(book_data), date, due_date) for book_data, date, due_date in data['borrowed_books']]
        return user

class OverdueRequest:
    def __init__(self, user, book, days_overdue):
        self.user = user
        self.book = book
        self.days_overdue = days_overdue
        self.paid = False  # Track if the overdue fee has been paid

    def to_dict(self):
        return {
            'user_id': self.user.user_id,
            'book_id': self.book.book_id,
            'days_overdue': self.days_overdue,
            'paid': self.paid
        }
    
    def calculate_overdue_amount(self, fee_per_day=1):
        return self.days_overdue * fee_per_day
    
class Library:
    def __init__(self):
        self.books_by_id = {}
        self.users = {}
        self.book_bst = BookBST()
        self.overdue_requests = []  
        self.load_data()

    def add_book(self, book):
        self.books_by_id[book.book_id] = book
        self.book_bst.insert(book)  # Insert into the BST
        logging.info(f"Added book: {book.title} (ID: {book.book_id})")

    def add_user(self, user):
        self.users[user.user_id] = user
        logging.info(f"Added user: {user.name} (ID: {user.user_id})")

    def search_by_id(self, book_id):
        return self.books_by_id.get(book_id)

    def borrow_book(self, user_id, book_id):
        user = self.users.get(user_id)
        book = self.books_by_id.get(book_id)
        if user and book:
            if book in [b[0] for b in user.borrowed_books]:  # Check if book is already borrowed
                messagebox.showerror("Error", f"Book '{book.title}' is already borrowed.")
            elif book.copies > 0:
                book.copies -= 1
                borrow_date = datetime.now().strftime("%Y-%m-%d")  # Get current date
                due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")  # Calculate due date
                user.borrowed_books.append((book, borrow_date, due_date))  # Store book, borrow date, and due date
                logging.info(f"Borrowed book: {book.title} (ID: {book.book_id}) by user {user.name} (ID: {user.user_id})")
                messagebox.showinfo("Success", f"You have borrowed '{book.title}' on {borrow_date}. Due date: {due_date}.")
            else:
                messagebox.showerror("Error", "Book not available.")
        else:
            messagebox.showerror("Error", "User or book not found.")

    def return_book(self, user_id, book_id):
        user = self.users.get(user_id)
        book = self.books_by_id.get(book_id)
        if user and book:
            for borrowed_book in user.borrowed_books:
                if borrowed_book[0] == book:
                    book.copies += 1
                    borrow_date = borrowed_book[1]
                    due_date = borrowed_book[2]
                    return_date = datetime.now().strftime("%Y-%m-%d")
                    days_overdue = (datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days

                    if days_overdue > 0:
                        # Create an overdue request instead of returning the book
                        overdue_request = OverdueRequest(user, book, days_overdue)
                        self.overdue_requests.append(overdue_request)
                        overdue_amount = overdue_request.calculate_overdue_amount()
                        messagebox.showinfo("Overdue", f"Book '{book.title}' is overdue by {days_overdue} days. "
                                                        f"The overdue amount is Rs.{overdue_amount}. "
                                                        f"A return request has been submitted to the admin.")
                    else:
                        messagebox.showinfo("Success", f"You have returned '{book.title}'.")

                    user.borrowed_books.remove(borrowed_book)

                    if book.reservations:
                        next_user_id = book.reservations.popleft()  # Get the next user in the queue
                        next_user = self.users[next_user_id]

                    logging.info(f"Requested return of overdue book: {book.title} (ID: {book.book_id}) by user {user.name} (ID: {user.user_id})")
                    return
        messagebox.showerror("Error", "Book not borrowed or user not found.")
    
    def reserve_book(self, user_id, book_id):
        user = self.users.get(user_id)
        book = self.books_by_id.get(book_id)
        if user and book:
            if book.copies == 0:
                # Add user to the reservations queue
                book.reservations.append(user_id)
                logging.info(f"User     {user.name} (ID: {user.user_id}) reserved book: {book.title} (ID: {book.book_id})")

                # Calculate the tentative available date
                if book.reservations:
                    # Find the shortest due date from all borrowed instances of this book
                    tentative_dates = []
                    for u_id in book.reservations:
                        user = self.users.get (u_id)
                        if user:
                            for borrowed_book in user.borrowed_books:
                                if borrowed_book[0] == book:  # Check if this book is borrowed by the user
                                    tentative_dates.append(datetime.strptime(borrowed_book[2], "%Y-%m-%d"))  # due_date

                    if tentative_dates:
                        tentative_date = min(tentative_dates)  # Get the earliest due date
                        tentative_date_str = tentative_date.strftime("%Y-%m-%d")
                    else:
                        tentative_date_str = "Available Now"

                    messagebox.showinfo("Book Reserved", f"Book '{book.title}' is reserved for you. Tentative available date: {tentative_date_str}")
                else:
                    messagebox.showinfo("Book Reserved", f"Book '{book.title}' is reserved for you. Tentative available date: Available Now")
            else:
                messagebox.showerror("Error", "Book is currently available. You can borrow it now.")
        else:
            messagebox.showerror("Error", "User or book not found.")

    def mark_request_as_paid(self, request):
        request.paid = True
        # Return the book back to the library
        request.book.copies += 1
        # Remove the request from the list
        self.overdue_requests.remove(request)
        logging.info(f"Overdue request for book '{request.book.title}' marked as paid by user {request.user.name}.")

    def modify_book(self, book_id, new_title, new_author, new_copies):
        book = self.books_by_id.get(book_id)
        if book:
            book.title = new_title
            book.author = new_author
            book.copies = new_copies
            logging.info(f"Modified book: {book.title} (ID: {book.book_id})")
            messagebox.showinfo("Success", f"Book '{book.title}' modified successfully!")
        else:
            messagebox.showerror("Error", "Book not found.")

    def delete_book(self, book_id):
        if book_id in self.books_by_id:
            del self.books_by_id[book_id]
            logging.info(f"Deleted book: {book_id}")
            messagebox.showinfo("Success", "Book deleted successfully!")
        else:
            messagebox.showerror("Error", "Book not found.")

    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            logging.info(f"Deleted user: {user_id}")
            messagebox.showinfo("Success", "User deleted successfully!")
        else:
            messagebox.showerror("Error", "User not found.")

    def get_all_users(self):
        return self.users.values()

    def save_data(self):
        # Save books to an Excel file
        books_data = {
            'book_id': [],
            'title': [],
            'author': [],
            'copies': []
        }
        for book in self.books_by_id.values():
            books_data['book_id'].append(book.book_id)
            books_data['title'].append(book.title)
            books_data['author'].append(book.author)
            books_data['copies'].append(book.copies)

        books_df = pd.DataFrame(books_data)
        books_df.to_excel('books.xlsx', index=False)

        # Save users to an Excel file
        users_data = {
            'user_id': [],
            'name': [],
            'borrowed_books': []
        }
        for user in self.users.values():
            borrowed_books = ';'.join(f"{book.book_id},{date},{due_date}" for book, date, due_date in user.borrowed_books )
            users_data['user_id'].append(user.user_id)
            users_data['name'].append(user.name)
            users_data['borrowed_books'].append(borrowed_books)

        users_df = pd.DataFrame(users_data)
        users_df.to_excel('users.xlsx', index=False)

    def load_data(self):
        try:
            # Load books from the books.xlsx file
            books_df = pd.read_excel('books.xlsx')
            for index, row in books_df.iterrows():
                # Ensure title and author are treated as strings
                self.add_book(Book(int(row['book_id']), str(row['title']), str(row['author']), int(row['copies'])))

            # Load users from the users.xlsx file
            users_df = pd.read_excel('users.xlsx')
            for index, row in users_df.iterrows():
                user_id = int(row['user_id'])
                name = row['name']
                user = User(user_id, name)

                borrowed_books_data = row['borrowed_books']
                if pd.notna(borrowed_books_data) and borrowed_books_data != "":
                    borrowed_books_info = borrowed_books_data.split(';')
                    for book_info in borrowed_books_info:
                        parts = book_info.split(',')
                        if len(parts) == 3:
                            book_id, borrow_date, due_date = parts
                            book = self.search_by_id(int(book_id))
                            if book:
                                user.borrowed_books.append((book, borrow_date, due_date))

                self.add_user(user)

        except FileNotFoundError:
            print("No saved data found.")

class LibraryApp:
    def __init__(self, master, library):
        self.master = master
        self.library = library
        self.master.title("Library Management System")
        self.master.geometry("800x600") 
        self.master.configure(bg="#f0f0f0")  
        self.style = ttk.Style()
        self.style.theme_use("clam")  
        self.style.configure("TLabel", font=("Arial", 14), background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 12), padding=6)
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TEntry", font=("Arial", 12))

        self.user_id = None
        self.main_menu()

    def main_menu(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Library Management System", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Button(frame, text="Admin Mode", command=self.admin_login, width=20).pack(pady=10)
        ttk.Button(frame, text="User Mode", command=self.enter_user_id, width=20).pack(pady=10)
        ttk.Button(frame, text="Exit", command=self.exit_app, width=20).pack(pady=10)

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def exit_app(self):
        self.library.save_data()  # Save data before exiting
        self.master.destroy()

    def admin_login(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Admin Login", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(frame, text="Enter Admin Password:").pack(pady=5)
        password_entry = ttk.Entry(frame, show="*")
        password_entry.pack(pady=5)

        def check_password():
            if password_entry.get() == '1234':
                self.admin_menu()
            else:
                messagebox.showerror("Error", "Incorrect Password")

        ttk.Button(frame, text="Login", command=check_password, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.main_menu, width=20).pack(pady=10)

    def admin_menu(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Admin Mode", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Button(frame, text="Add Book", command=self.add_book, width=20).pack(pady=10)
        ttk.Button(frame, text="Modify Book", command=self.modify_book, width=20).pack(pady=10)
        ttk.Button(frame, text="Delete Book", command=self.delete_book, width=20).pack(pady=10)
        ttk.Button(frame, text="View Overdue Requests", command=self.view_overdue_requests, width=20).pack(pady=10)
        ttk.Button(frame, text="View Books", command=lambda: self.view_books(self.admin_menu), width=20).pack(pady=10)
        ttk.Button(frame, text="View Users", command=self.view_users, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.main_menu, width=20).pack(pady=10)

    def view_overdue_requests(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Overdue Requests", font=("Arial", 18, "bold")).pack(pady=20)

        columns = ("User  ID", "Book ID", "Days Overdue", "Overdue Amount", "Paid")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("User  ID", text="User      ID")
        tree.heading("Book ID", text="Book ID")
        tree.heading("Days Overdue", text="Days Overdue")
        tree.heading ("Overdue Amount", text="Overdue Amount")
        tree.heading("Paid", text="Paid ")
        tree.pack(expand=True, fill=tk.BOTH, pady= 10)

        for request in self.library.overdue_requests:
            overdue_amount = request.calculate_overdue_amount()  # Calculate the amount
            tree.insert("", "end", values=(request.user.user_id, request.book.book_id, request.days_overdue, overdue_amount, request.paid))

        def mark_request_as_paid():
            selected_item = tree.selection()
            if selected_item:
                request_index = int(selected_item[0].split('I')[-1]) - 1  
                request = self.library.overdue_requests[request_index]
                self.library.mark_request_as_paid(request)
                messagebox.showinfo("Success", f"Overdue request for book '{request.book.title}' marked as paid.")
                self.view_overdue_requests()  # Refresh the list after marking as paid
            else:
                messagebox.showerror("Error", "Please select a request to mark as paid.")

        ttk.Button(frame , text="Mark as Paid", command=mark_request_as_paid, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.admin_menu, width=20).pack(pady=10)
        
    def add_book(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Add Book", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(frame, text="Book ID:").pack()
        book_id_entry = ttk.Entry(frame)
        book_id_entry.pack(pady=5)

        ttk.Label(frame, text="Title:").pack()
        title_entry = ttk.Entry(frame)
        title_entry.pack(pady=5)

        ttk.Label(frame, text="Author:").pack()
        author_entry = ttk.Entry(frame)
        author_entry.pack(pady=5)

        ttk.Label(frame, text="Copies:").pack()
        copies_entry = ttk.Entry(frame)
        copies_entry.pack(pady=5)

        def submit_book():
            try:
                book_id = int(book_id_entry.get())
                title = title_entry.get()
                author = author_entry.get()
                copies = int(copies_entry.get())
                self.library.add_book(Book(book_id, title, author, copies))
                messagebox.showinfo("Success", "Book added successfully!")
                self.admin_menu()
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter valid data.")

        ttk.Button(frame, text="Submit", command=submit_book, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.admin_menu, width=20).pack(pady=10)

    def add_user(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Add User", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(frame, text="User       ID:").pack()
        user_id_entry = ttk.Entry(frame)
        user_id_entry.pack(pady=5)

        ttk.Label(frame, text="Name:").pack()
        name_entry = ttk.Entry(frame)
        name_entry.pack(pady=5)

        def submit_user():
            try:
                user_id = int(user_id_entry.get())
                name = name_entry.get()
                self.library.add_user(User(user_id, name))
                messagebox.showinfo("Success", "User added successfully!")
                self.admin_menu()
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter valid data.")

        ttk.Button(frame, text="Submit", command=submit_user, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.admin_menu, width=20).pack(pady=10)

    def modify_book(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Modify Book", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(frame, text="Enter Book ID:").pack(pady=5)
        book_id_entry = ttk.Entry(frame)
        book_id_entry.pack(pady =5)

        def submit_book_id():
            try:
                book_id = int(book_id_entry.get())
                book = self.library.books_by_id.get(book_id)

                if book:
                    # Show current details of the book
                    ttk.Label(frame, text=f"Current Title: {book.title}").pack(pady=5)
                    ttk.Label(frame, text=f"Current Author: { book.author}").pack(pady=5)
                    ttk.Label(frame, text=f"Current Copies : {book.copies}").pack(pady=5)

                    # Ask which detail to modify
                    ttk.Label(frame, text="What would you like to modify?").pack(pady=10)

                    # Create options to modify
                    modify_option = tk.StringVar()
                    modify_option.set("Title")  # Default option
                    options = ["Title", "Author", "Copies"]
                    modify_menu = ttk.OptionMenu(frame, modify_option, *options)
                    modify_menu.pack(pady=5)

                    new_value_entry = ttk.Entry(frame)
                    new_value_entry.pack(pady=5)

                    def submit_modify():
                        new_value = new_value_entry.get()
                        if modify_option.get() == "Title":
                            book.title = new_value
                        elif modify_option.get() == "Author":
                            book.author = new_value
                        elif modify_option.get() == "Copies":
                            try:
                                book.copies = int(new_value)
                            except ValueError:
                                messagebox.showerror("Error", "Invalid input for copies. Please enter a number.")
                                return

                        messagebox.showinfo("Success", "Book modified successfully!")
                        self.admin_menu()  # Go back to the admin menu after modification

                    ttk.Button(frame, text="Submit Modification", command=submit_modify, width=20).pack(pady=10)

                else:
                    messagebox.showerror("Error", "Book not found.")  # Book does not exist

            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter a valid Book ID.")

        ttk.Button(frame, text="Submit", command=submit_book_id, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.admin_menu, width=20).pack(pady=10)

    def delete_book(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Delete Book", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(frame, text="Enter Book ID to Delete:").pack(pady=5)
        book_id_entry = ttk.Entry(frame)
        book_id_entry.pack(pady=5)

        def submit_delete():
            try:
                book_id = int(book_id_entry.get())
                self.library.delete_book(book_id)
                self.admin_menu()
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter a valid Book ID.")

        ttk.Button(frame, text="Delete", command=submit_delete, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.admin_menu, width=20).pack(pady=10)

    def delete_user(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Delete User", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(frame, text="Enter User ID to Delete:").pack(pady=5)
        user_id_entry = ttk.Entry(frame)
        user_id_entry.pack(pady=5)

        def submit_delete_user():
            try:
                user_id = int(user_id_entry.get())
                self.library.delete_user(user_id)
                self.admin_menu()
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter a valid User ID.")

        ttk.Button(frame, text="Delete", command=submit_delete_user, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.admin_menu, width=20).pack(pady=10)

    def view_books(self, back_callback):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Available Books", font=("Arial", 18, "bold")).pack(pady=20)

        tree = ttk.Treeview(frame, columns=("ID", "Title", "Author", "Copies"), show='headings')
        tree.heading("ID", text="ID")
        tree.heading("Title", text="Title")
        tree.heading("Author", text="Author")
        tree.heading("Copies", text="Copies")
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscroll=scrollbar.set)

        for book in self.library.books_by_id.values():
            tree.insert('', 'end', values=(book.book_id, book.title, book.author, book.copies ))

        ttk.Button(frame, text="Back", command=back_callback, width=20).pack(pady=10)

    def view_users(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Registered Users", font=("Arial", 18, "bold")).pack(pady=20)

        # Create a Treeview to display users
        tree = ttk.Treeview(frame, columns=("ID", "Name"), show='headings')
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar .pack(side='right', fill='y')
        tree.configure(yscroll=scrollbar.set)

        # Populate the Treeview with user data
        for user in self.library.users.values():
            tree.insert('', 'end', values=(user.user_id, user.name))

        # Function to view borrowed books of the selected user
        def view_selected_user_books():
            selected_item = tree.selection()
            if selected_item:
                user_id = tree.item(selected_item)['values'][0]
                self.show_user_borrowed_books(user_id)
            else:
                messagebox.showerror("Error", "Please select a user.")

        # Button to trigger viewing borrowed books
        ttk.Button(frame, text="View Borrowed Books", command=view_selected_user_books, width=20).pack(pady=10)
    
        def add_user():
            self.clear_window()
            add_user_frame = ttk.Frame(self.master)
            add_user_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

            ttk.Label(add_user_frame, text="Add User", font=("Arial", 18, "bold")).pack(pady=20)
            ttk.Label(add_user_frame, text="User  ID:").pack()
            user_id_entry = ttk.Entry(add_user_frame)
            user_id_entry.pack(pady=5)

            ttk.Label(add_user_frame, text="Name:").pack()
            name_entry = ttk.Entry(add_user_frame)
            name_entry.pack(pady=5)

            def submit_user():
                try:
                    user_id = int(user_id_entry.get())
                    name = name_entry.get()
                    self.library.add_user(User(user_id, name))
                    messagebox.showinfo("Success", "User  added successfully!")
                    self.view_users()  # Refresh the user list
                except ValueError:
                    messagebox.showerror("Error", "Invalid input. Please enter valid data.")

            ttk.Button(add_user_frame, text="Submit", command=submit_user, width=20).pack(pady=10)
            ttk.Button(add_user_frame, text="Back", command=self.view_users, width=20).pack(pady=10)

        # Button to add a new user
        ttk.Button (frame, text="Add User", command=add_user, width=20).pack(pady=10)

        # Function to delete a selected user
        def delete_selected_user():
            selected_item = tree.selection()
            if selected_item:
                user_id = tree.item(selected_item)['values'][0]
                self.library.delete_user(user_id)
                messagebox.showinfo("Success", "User deleted successfully!")
                self.view_users()  # Refresh the user list
            else:
                messagebox.showerror("Error", "Please select a user to delete.")

        # Button to delete a selected user
        ttk.Button(frame, text="Delete User", command=delete_selected_user, width=20).pack(pady=10)

        ttk.Button(frame, text="Back", command=self.admin_menu, width=20).pack(pady=10)
        
    def show_user_borrowed_books(self, user_id):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        user = self.library.users.get(user_id)
        if user:
            ttk.Label(frame, text=f"Borrowed Books for {user.name}", font=("Arial", 18, "bold")).pack(pady=20)

            if user.borrowed_books:
                # Create a Treeview to display borrowed book details
                columns = ("ID", "Title", "Author", "Copies", "Borrowed Date", "Due Date")
                tree = ttk.Treeview(frame, columns=columns, show="headings")
                tree.heading("ID", text="Book ID")
                tree.heading("Title", text="Title")
                tree.heading("Author", text="Author")
                tree.heading("Copies", text="Copies")
                tree.heading("Borrowed Date", text="Borrowed Date")
                tree.heading("Due Date", text="Due Date")
                tree.pack(expand=True, fill=tk.BOTH, pady=10)

                # Populate the Treeview with borrowed book data
                for book, borrow_date, due_date in user.borrowed_books:
                    tree.insert("", "end", values=(book.book_id, book.title, book.author, book.copies, borrow_date, due_date))
            else:
                ttk.Label(frame, text="This user has no borrowed books.").pack(pady=20)

        # Button to return to the user list
        ttk.Button(frame, text="Back", command=self.view_users, width=20).pack(pady=10)

    def enter_user_id(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Enter User ID", font=("Arial", 18, "bold")).pack(pady=20)
        user_id_entry = ttk.Entry(frame)
        user_id_entry.pack(pady=5)

        def submit_user_id():
            user_id = user_id_entry.get()
            if user_id.isdigit() and int(user_id) in self.library.users:
                self.user_id = int(user_id)
                self.user_menu()
            else:
                messagebox.showerror("Error", "Invalid User ID.")

        ttk.Button(frame, text="Submit", command=submit_user_id, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.main_menu, width=20).pack(pady=10)

    def user_menu(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="User Mode", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Button(frame, text="Search Book", command=self.search_book, width=20).pack(pady=10)
        ttk.Button(frame, text="View Borrowed Books", command=self.view_borrowed_books, width =20).pack(pady=10)
        ttk.Button(frame, text="View Available Books", command=lambda: self.view_books(self.user_menu), width=20).pack(pady=10)
        ttk.Button(frame, text="Reserve Status", command=self.view_reserve_status, width=20).pack(pady =10)  # New button
        ttk.Button(frame, text="Back", command=self.main_menu, width=20).pack(pady=10)

    def search_book(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Search Book", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(frame, text="Search by:").pack(pady=5)
    
        search_by = tk.StringVar()
        search_by.set("Book ID")  # Default search option
        options = ["Book ID", "Title", "Author"]
        search_by_menu = ttk.OptionMenu(frame , search_by, *options)
        search_by_menu.pack(pady=5)

        search_entry = ttk.Entry(frame)
        search_entry.pack(pady=5)

        def submit_search():
            search_term = search_entry.get()
            results = []
            try:
                if search_by.get() == "Book ID":
                    book = self.library.book_bst.search_by_id(int(search_term))
                    if book:
                        results.append(book)
                elif search_by.get() == "Title":
                    results = self.library.book_bst.search_by_title(search_term)
                elif search_by.get() == "Author":
                    results = self.library.book_bst.search_by_author(search_term)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid Book ID.")
            self.display_search_results(results)

        ttk.Button(frame, text="Search", command=submit_search, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.user_menu, width=20).pack(pady=10)

    def view_reserve_status(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Reserve Status", font=("Arial", 18, "bold")).pack(pady=20)

        # Create a Treeview to display reserve status
        columns = ("Book ID", "Title", "Author", "Reserve Status", "Tentative Available Date")
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        tree.heading("Book ID", text="Book ID")
        tree.heading("Title", text="Title")
        tree.heading("Author", text="Author")
        tree.heading("Reserve Status", text="Reserve Status")
        tree.heading("Tentative Available Date", text="Tentative Available Date")
        tree.pack(expand=True, fill=tk.BOTH, pady=10)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscroll=scrollbar.set)

        # Get user's reserved books and display their status
        user = self.library.users.get(self.user_id)
        if user:
            for book in self.library.books_by_id.values():  # Iterate through all books
                reserve_status = "Available"
                tentative_date_str = ""  # Default value

                if book.copies == 0:  # If no copies are available
                    if book.reservations and user.user_id in book.reservations:
                        reserve_status = "Reserved"
                        # Calculate the tentative available date
                        tentative_dates = []
                        for u_id in book.reservations:
                            if u_id in self.library.users:
                                for borrowed_book in self.library.users[u_id].borrowed_books:
                                    if borrowed_book[0] == book:  # Check if this book is borrowed by the user
                                        tentative_dates.append(datetime.strptime(borrowed_book[2], "%Y-%m-%d"))  # due_date

                        if tentative_dates:
                            tentative_date = min(tentative_dates)  # Get the earliest due date
                            tentative_date_str = tentative_date.strftime("%Y-%m-%d")
                    else:
                        reserve_status = "Not Available"  # If no copies and not reserved, mark as not available
                else:
                    reserve_status = "Available"  # If copies are available, mark as available

                tree.insert("", "end", values=(book.book_id, book.title, book.author, reserve_status, tentative_date_str if tentative_date_str else "N/A"))

        else:
            ttk.Label(frame, text="You have no reserved books.").pack(pady=20)

        ttk.Button(frame, text="Back", command=self.user_menu, width=20).pack(pady=10)

    def display_search_results(self, books):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame , text="Search Results", font=("Arial", 18, "bold")).pack(pady=20)

        # Define the columns correctly
        columns = ("ID", "Title", "Author", "Copies")  # Make sure this matches
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("ID", text="Book ID")
        tree.heading("Title", text="Title")
        tree.heading("Author", text="Author")
        tree.heading("Copies", text="Copies")  # Ensure this matches the column definition
        tree.pack(expand=True, fill=tk.BOTH, pady=10)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscroll=scrollbar.set)

        for book in books:
            tree.insert("", "end", values=(book.book_id, book.title, book.author, book.copies))

        def borrow_selected_book():
            selected_item = tree.selection()
            if selected_item:
                book_id = tree.item(selected_item)['values'][0]
                book = self.library.books_by_id[book_id]
                if book.copies > 0:
                    self.library.borrow_book(self.user_id, book_id)
                    self.display_search_results(books)  # Refresh the search results after borrowing
                else:
                    self.library.reserve_book(self.user_id, book_id)
                    self.display_search_results(books)  # Refresh the search results after reserving
            else:
                messagebox.showerror("Error", "Please select a book to borrow or reserve.")

        ttk.Button(frame, text="Borrow/Reserve Book", command=borrow_selected_book, width=20).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.user_menu, width=20).pack(pady=10)

    def view_borrowed_books(self):
        self.clear_window()
        frame = ttk.Frame(self.master)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        ttk.Label(frame, text="Your Borrowed Books", font=("Arial", 18, "bold")).pack(pady=20)

        if self.user_id in self.library.users:
            user = self.library.users[self.user_id]
            borrowed_books = user.borrowed_books

            if borrowed_books:
                columns = ("ID", "Title", "Author", "Borrowed Date", "Due Date")
                tree = ttk.Treeview(frame, columns=columns, show="headings")
                tree.heading("ID", text="Book ID")
                tree.heading("Title", text="Title")
                tree.heading("Author", text="Author")
                tree.heading("Borrowed Date", text="Borrowed Date")
                tree.heading("Due Date", text="Due Date")
                tree.pack(expand=True, fill=tk.BOTH, pady=10)

                for book, borrow_date, due_date in borrowed_books:
                    tree.insert("", "end", values=(book.book_id, book.title, book.author, borrow_date, due_date))
                
                # Function to return a selected book
                def return_selected_book():
                    selected_item = tree.selection()
                    if selected_item:
                        book_id = tree.item(selected_item)['values'][0]
                        self.library.return_book(self.user_id, book_id)
                        self.view_borrowed_books()  # Refresh the list after returning
                    else:
                        messagebox.showerror("Error", "Please select a book to return.")

                ttk.Button(frame, text="Return Book", command=return_selected_book, width=20).pack(pady=10)        
            else:
                ttk.Label(frame, text="You have no borrowed books.").pack(pady=20)

        ttk.Button(frame, text="Back", command=self.user_menu, width=20).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    library = Library ()
    app = LibraryApp(root, library)
    root.mainloop()
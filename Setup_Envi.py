from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime

root = Tk()
root.title('Data app')
root.state('zoomed')

# -------------------- Database Setup --------------------
dataConnect = sqlite3.connect('myData.db')
cursor = dataConnect.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    first_name text,
                    last_name  text,
                    username text UNIQUE,
                    email  text,
                    password text)""")

# title and body now for posts
cursor.execute("""CREATE TABLE IF NOT EXISTS posts(
                    username text,
                    title text,
                    body text,
                    timestamp text)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS comments(
                    post_id INTEGER,
                    username text,
                    comment text,
                    timestamp text)""")

dataConnect.commit()
dataConnect.close()

# -------------------- Registration --------------------
def submit():
    dataConnect = sqlite3.connect('myData.db')
    cursor = dataConnect.cursor()
    try:
        cursor.execute("INSERT INTO users VALUES(:first_name, :last_name, :username, :email, :password)",
                       {'first_name': reg_first_name.get(),
                        'last_name': reg_last_name.get(),
                        'username': reg_username.get(),
                        'email': reg_email.get(),
                        'password': reg_password.get()
                        })
        dataConnect.commit()
        messagebox.showinfo("Registration", "Registration successful!")
        reg_first_name.delete(0, END)
        reg_last_name.delete(0, END)
        reg_username.delete(0, END)
        reg_email.delete(0, END)
        reg_password.delete(0, END)
    finally:
        dataConnect.close()

# -------------------- Login --------------------
def login():
    dataConnect = sqlite3.connect('myData.db')
    cursor = dataConnect.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username=? AND password=?",
                   (username.get(), password.get()))
    row = cursor.fetchone()
    dataConnect.close()
    if row:
        homePage(username.get())
    else:
        messagebox.showerror("Login", "Invalid username or password")

# -------------------- Scrollable Feed Helper --------------------
def create_scrollable_feed(parent_frame):
    canvas = Canvas(parent_frame)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar = Scrollbar(parent_frame, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    inner_frame = Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor='nw')
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    inner_frame.bind("<Configure>", on_frame_configure)
    return inner_frame

# -------------------- Home Page --------------------
def homePage(current_user):
    home = Toplevel(root)
    home.title("Dashboard")
    home.state('zoomed')

    notebook = ttk.Notebook(home)
    notebook.pack(expand=1, fill='both')

    selected_post_id = {'id': None, 'frame': None}
    show_timestamps = BooleanVar(value=True)

    # -------------------- Home Tab --------------------
    home_tab = Frame(notebook)
    notebook.add(home_tab, text='Home')

    header = Label(home_tab, text=f"Hi {current_user}, welcome to Hi Space", font=("Arial", 18, "bold"))
    header.pack(pady=10)

    timestamp_chk = Checkbutton(home_tab, text="Show timestamps", variable=show_timestamps,
                                command=lambda: refresh_feed(home_feed_frame))
    timestamp_chk.pack()

    home_feed_container = Frame(home_tab, bd=2, relief=SOLID, padx=5, pady=5)
    home_feed_container.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
    home_feed_frame = create_scrollable_feed(home_feed_container)

    home_left_frame = Frame(home_tab)
    home_left_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    # Title
    Label(home_left_frame, text="Title").grid(row=0, column=0, sticky="w")
    home_title_entry = Entry(home_left_frame, width=40)
    home_title_entry.grid(row=1, column=0, columnspan=2, pady=(0,5))

    # Body
    Label(home_left_frame, text="Body").grid(row=2, column=0, sticky="w")
    home_body_entry = Text(home_left_frame, width=40, height=5)
    home_body_entry.grid(row=3, column=0, columnspan=2, pady=(0,5))

    Button(home_left_frame, text="Post",
           command=lambda: create_post(home_title_entry, home_body_entry)).grid(row=4, column=1, sticky="e", pady=(0,10))

    # Comment entry + button
    home_comment_entry = Entry(home_left_frame, width=40)
    home_comment_entry.grid(row=5, column=0)
    Button(home_left_frame, text="Comment", command=lambda: add_comment(home_comment_entry)).grid(row=5, column=1, padx=(5,0))

    # -------------------- Posts Tab --------------------
    posts_tab = Frame(notebook)
    notebook.add(posts_tab, text='Posts')

    posts_feed_container = Frame(posts_tab, bd=2, relief=SOLID, padx=5, pady=5)
    posts_feed_container.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
    posts_feed_frame = create_scrollable_feed(posts_feed_container)

    posts_left_frame = Frame(posts_tab)
    posts_left_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    # Title
    Label(posts_left_frame, text="Title").grid(row=0, column=0, sticky="w")
    posts_title_entry = Entry(posts_left_frame, width=40)
    posts_title_entry.grid(row=1, column=0, columnspan=2, pady=(0,5))

    # Body
    Label(posts_left_frame, text="Body").grid(row=2, column=0, sticky="w")
    posts_body_entry = Text(posts_left_frame, width=40, height=5)
    posts_body_entry.grid(row=3, column=0, columnspan=2, pady=(0,5))

    Button(posts_left_frame, text="Post",
           command=lambda: create_post(posts_title_entry, posts_body_entry)).grid(row=4, column=1, sticky="e", pady=(0,10))

    posts_comment_entry = Entry(posts_left_frame, width=40)
    posts_comment_entry.grid(row=5, column=0)
    Button(posts_left_frame, text="Comment", command=lambda: add_comment(posts_comment_entry)).grid(row=5, column=1, padx=(5,0))

    # -------------------- Users Tab --------------------
    users_tab = Frame(notebook)
    notebook.add(users_tab, text='Users')
    users_listbox = Listbox(users_tab, width=50)
    users_listbox.pack(padx=10, pady=10, fill='both', expand=True)

    # -------------------- Functions --------------------
    def select_post(post_id, frame_widget):
        old_frame = selected_post_id.get('frame')
        if old_frame and old_frame.winfo_exists():
            old_frame.config(bg=home_tab["bg"])
        selected_post_id['id'] = post_id
        selected_post_id['frame'] = frame_widget
        frame_widget.config(bg="lightblue")

    def refresh_feed(frame):
        for widget in frame.winfo_children():
            widget.destroy()
        con = sqlite3.connect('myData.db')
        cur = con.cursor()
        cur.execute("SELECT rowid, username, title, body, timestamp FROM posts")
        for post_id, u, post_title, post_body, ts in cur.fetchall():
            post_frame = Frame(frame, bd=1, relief=SOLID, padx=5, pady=5)
            post_frame.pack(fill=X, pady=5)

            title_label = Label(post_frame, text=f"{post_title}", font=("Arial",14,"bold"))
            title_label.pack(anchor="w")

            body_label = Label(post_frame, text=post_body, wraplength=600, justify=LEFT)
            body_label.pack(anchor="w")

            if show_timestamps.get():
                ts_label = Label(post_frame, text=f"[{ts}]", font=("Arial",9))
                ts_label.pack(anchor="w")

            post_frame.bind( "<Button-1>", lambda e, pid=post_id, f=post_frame: select_post(pid, f))
            title_label.bind("<Button-1>", lambda e, pid=post_id, f=post_frame: select_post(pid, f))
            body_label.bind("<Button-1>",  lambda e, pid=post_id, f=post_frame: select_post(pid, f))

            cur.execute("SELECT username, comment, timestamp FROM comments WHERE post_id=?", (post_id,))
            for cu, ct, cts in cur.fetchall():
                comment_frame = Frame(post_frame, bd=0, padx=10, pady=2)
                comment_frame.pack(fill=X)
                comment_label = Label(comment_frame, text=f"→ {cu}: {ct}", font=("Arial",10,"bold"))
                comment_label.pack(anchor="w")
                if show_timestamps.get():
                    cts_label = Label(comment_frame, text=f"[{cts}]", font=("Arial",8))
                    cts_label.pack(anchor="w")
        con.close()

    def create_post(title_entry, body_widget):
        title = title_entry.get().strip()
        body  = body_widget.get("1.0", END).strip()
        if title and body:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            con = sqlite3.connect('myData.db')
            cur = con.cursor()
            cur.execute("INSERT INTO posts(username,title,body,timestamp) VALUES(?,?,?,?)",
                        (current_user, title, body, timestamp))
            con.commit()
            con.close()
            title_entry.delete(0, END)
            body_widget.delete("1.0", END)
            refresh_feed(home_feed_frame)
            refresh_feed(posts_feed_frame)

    def add_comment(entry_widget):
        if selected_post_id['id'] is None:
            messagebox.showerror("Error", "Please click a post first.")
            return
        text = entry_widget.get().strip()
        if text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            con = sqlite3.connect('myData.db')
            cur = con.cursor()
            cur.execute("INSERT INTO comments(post_id, username, comment, timestamp) VALUES(?,?,?,?)",
                        (selected_post_id['id'], current_user, text, timestamp))
            con.commit()
            con.close()
            entry_widget.delete(0, END)
            refresh_feed(home_feed_frame)
            refresh_feed(posts_feed_frame)

    def load_users():
        users_listbox.delete(0, END)
        con = sqlite3.connect('myData.db')
        cur = con.cursor()
        cur.execute("SELECT username FROM users")
        for u in cur.fetchall():
            users_listbox.insert(END, u[0])
        con.close()

    # -------------------- Initial Load --------------------
    refresh_feed(home_feed_frame)
    refresh_feed(posts_feed_frame)
    load_users()

# -------------------- Registration Window --------------------
def openRegistrationWindow():
    global reg_first_name, reg_last_name, reg_username, reg_email, reg_password
    reg = Toplevel(root)
    reg.title("Register")
    Label(reg, text="First Name").grid(row=1, column=0)
    reg_first_name = Entry(reg, width=30); reg_first_name.grid(row=1, column=1)
    Label(reg, text="Last Name").grid(row=2, column=0)
    reg_last_name = Entry(reg, width=30); reg_last_name.grid(row=2, column=1)
    Label(reg, text="Email").grid(row=3, column=0)
    reg_email = Entry(reg, width=30); reg_email.grid(row=3, column=1)
    Label(reg, text="Username").grid(row=4, column=0)
    reg_username = Entry(reg, width=30); reg_username.grid(row=4, column=1)
    Label(reg, text="Password").grid(row=5, column=0)
    reg_password = Entry(reg, width=30, show="*"); reg_password.grid(row=5, column=1)
    Button(reg, text="Create Account", command=submit).grid(row=6, column=0, columnspan=2, pady=5)

# -------------------- Login Form --------------------
username = Entry(root, width=30); username.grid(row=3, column=1)
password = Entry(root, width=30, show="*"); password.grid(row=4, column=1)
Label(root, text="Username").grid(row=3, column=0)
Label(root, text="Password").grid(row=4, column=0)

Button(root, text="Register", command=openRegistrationWindow).grid(row=5, column=0, pady=5)
Button(root, text="Login", command=login).grid(row=5, column=1, pady=5)

root.mainloop()

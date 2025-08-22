from tkinter import *
from tkinter import messagebox, filedialog, ttk
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk   # for image handling

root = Tk()
root.title('Data app')
root.state('zoomed')

APP_BG = "#f3f4f6"     # light gray app background
CARD_BG = "#ffffff"    # white cards
CARD_BORDER = "#e5e7eb"
TEXT = "#0f172a"       # dark slate
MUTED = "#475569"      # slate-600
PRIMARY = "#2563eb"    # blue-600
PRIMARY_HOVER = "#1d4ed8"

root.configure(bg=APP_BG)

style = ttk.Style()
try:
    style.theme_use("clam")
except:
    pass

root.option_add("*Font", "{Segoe UI} 10")
style.configure("TLabel", background=APP_BG, foreground=TEXT)
style.configure("Muted.TLabel", background=APP_BG, foreground=MUTED)
style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT)
style.configure("CardMuted.TLabel", background=CARD_BG, foreground=MUTED)
style.configure("Primary.TButton", background=PRIMARY, foreground="#ffffff", padding=(14,8))
style.map("Primary.TButton", background=[("active", PRIMARY_HOVER), ("pressed", PRIMARY_HOVER)])


# -------------------- Database Setup --------------------
dataConnect = sqlite3.connect('myData.db')
cursor = dataConnect.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                    first_name text,
                    last_name  text,
                    username text UNIQUE,
                    email  text,
                    password text)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS posts(
                    username text,
                    title text,
                    body text,
                    timestamp text,
                    image_path text)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS comments(
                    post_id INTEGER,
                    username text,
                    comment text,
                    timestamp text,
                    image_path text)""")

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
    canvas = Canvas(parent_frame, bg=APP_BG, highlightthickness=0)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar = Scrollbar(parent_frame, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = Frame(canvas, bg=APP_BG)
    canvas.create_window((0, 0), window=inner_frame, anchor='nw')

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    inner_frame.bind("<Configure>", on_frame_configure)

    # smooth mouse wheel
    def _on_mousewheel(e):
        canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return inner_frame


# -------------------- Image Picker --------------------
def choose_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
    )
    return file_path if file_path else None


# === Card helper ===
def make_card(parent):
    card = Frame(parent, bg=CARD_BG, bd=1, relief="solid",
                 highlightthickness=1, highlightbackground=CARD_BORDER)
    return card



# -------------------- Home Page --------------------
def homePage(current_user):
    home = Toplevel(root)
    # --- Top bar (ADD) ---
    home.configure(bg=APP_BG)
    topbar = Frame(home, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
    topbar.pack(fill="x")
    Label(topbar, text="Hi Space", bg=CARD_BG, fg=TEXT, font=("Segoe UI Semibold", 16)).pack(side=LEFT, padx=16, pady=10)
    search = ttk.Entry(topbar, width=40)
    search.insert(0, "Search…")
    search.pack(side=LEFT, padx=12, pady=10)
    ttk.Button(topbar, text="New Post", style="Primary.TButton").pack(side=RIGHT, padx=16, pady=8)
    home.title("Dashboard")
    home.state('zoomed')

    notebook = ttk.Notebook(home)
    notebook.pack(expand=1, fill='both')

    selected_post_id = {'id': None, 'frame': None}
    show_timestamps = BooleanVar(value=True)

    post_image_path = {'path': None}
    comment_image_path = {'path': None}

    # -------------------- Home Tab --------------------
    home_tab = Frame(notebook, bg=APP_BG)
    notebook.add(home_tab, text='Home')

    header = Label(home_tab, text=f"Hi {current_user}, Welcome to Hi-Space", font=("Arial", 18, "bold"))
    header.pack(pady=10)

    timestamp_chk = Checkbutton(home_tab, text="Show timestamps", variable=show_timestamps,
                                command=lambda: refresh_feed(home_feed_frame))
    timestamp_chk.pack()

    # Home feed container
    home_feed_container = Frame(home_tab, bg=APP_BG)
    home_feed_container.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
    home_feed_frame = create_scrollable_feed(home_feed_container)

    # Left composer column 
    home_left_frame = Frame(home_tab, bg=APP_BG)
    home_left_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    # --- Composer card  ---
    composer_card = make_card(home_left_frame)
    composer_card.pack(fill="x", padx=2, pady=2)

    Label(composer_card, text=f"What's on your mind, {current_user}?",
        font=("Segoe UI Semibold", 11), bg=CARD_BG, fg=TEXT).pack(anchor="w", padx=12, pady=(10,6))

    inner = Frame(composer_card, bg=CARD_BG)
    inner.pack(fill="x", padx=12, pady=(0,10))

    Label(inner, text="Title", bg=CARD_BG, fg=TEXT).grid(row=0, column=0, sticky="w")
    home_title_entry = Entry(inner, width=40)
    home_title_entry.grid(row=1, column=0, columnspan=2, pady=(0,5), sticky="we")

    Label(inner, text="Body", bg=CARD_BG, fg=TEXT).grid(row=2, column=0, sticky="w")
    home_body_entry = Text(inner, width=40, height=5, wrap="word",
                        bd=1, relief="solid", highlightthickness=1, highlightbackground=CARD_BORDER)
    home_body_entry.grid(row=3, column=0, columnspan=2, pady=(0,6), sticky="we")

    ttk.Button(inner, text="Attach Image",
            command=lambda: post_image_path.update({'path': choose_image()})).grid(row=4, column=0, sticky="w", pady=(2,8))
    ttk.Button(inner, text="Post", style="Primary.TButton",
            command=lambda: create_post(home_title_entry, home_body_entry, post_image_path)).grid(row=4, column=1, sticky="e", pady=(2,8))

    home_comment_entry = Entry(inner, width=40)
    home_comment_entry.grid(row=5, column=0, sticky="we")

    ttk.Button(inner, text="Attach Img",
            command=lambda: comment_image_path.update({'path': choose_image()})).grid(row=6, column=0, sticky="w", pady=(2,8))
    ttk.Button(inner, text="Comment",
            command=lambda: add_comment(home_comment_entry, comment_image_path)).grid(row=5, column=1, padx=(5,0), sticky="e")


    # -------------------- Posts Tab --------------------
    posts_tab = Frame(notebook, bg=APP_BG)
    notebook.add(posts_tab, text='Posts')

    posts_feed_container = Frame(posts_tab, bd=2, relief=SOLID, padx=5, pady=5)
    posts_feed_container.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
    posts_feed_frame = create_scrollable_feed(posts_feed_container)

    posts_left_frame = Frame(posts_tab)
    posts_left_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    Label(posts_left_frame, text="Title").grid(row=0, column=0, sticky="w")
    posts_title_entry = Entry(posts_left_frame, width=40)
    posts_title_entry.grid(row=1, column=0, columnspan=2, pady=(0,5))

    Label(posts_left_frame, text="Body").grid(row=2, column=0, sticky="w")
    posts_body_entry = Text(posts_left_frame, width=40, height=5)
    posts_body_entry.grid(row=3, column=0, columnspan=2, pady=(0,5))

    Button(posts_left_frame, text="Attach Image",
           command=lambda: post_image_path.update({'path': choose_image()})).grid(row=4, column=0, sticky="w")

    Button(posts_left_frame, text="Post",
           command=lambda: create_post(posts_title_entry, posts_body_entry, post_image_path)).grid(row=4, column=1, sticky="e", pady=(0,10))

    posts_comment_entry = Entry(posts_left_frame, width=40)
    posts_comment_entry.grid(row=5, column=0)

    Button(posts_left_frame, text="Attach Img",
           command=lambda: comment_image_path.update({'path': choose_image()})).grid(row=6, column=0, sticky="w")

    Button(posts_left_frame, text="Comment",
           command=lambda: add_comment(posts_comment_entry, comment_image_path)).grid(row=5, column=1, padx=(5,0))

    # -------------------- Users Tab --------------------
    users_tab = Frame(notebook, bg=APP_BG)
    notebook.add(users_tab, text='Users')
    users_listbox = Listbox(users_tab, width=50, bg="#ffffff",
                        highlightthickness=1, highlightcolor=CARD_BORDER)
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
        cur.execute("SELECT rowid, username, title, body, timestamp, image_path FROM posts")
        for post_id, u, post_title, post_body, ts, img_path in cur.fetchall():
            post_frame = make_card(frame)
            post_frame.pack(fill="x", padx=8, pady=8)
            inner_post = Frame(post_frame, bg=CARD_BG)
            inner_post.pack(fill="x", padx=10, pady=10)

            title_label = Label(inner_post, text=f"{post_title}", font=("Arial",14,"bold"))
            title_label.pack(anchor="w")

            body_label = Label(inner_post, text=post_body, wraplength=600, justify=LEFT)
            body_label.pack(anchor="w")

            # Show image if available
            if img_path:
                try:
                    img = Image.open(img_path)
                    img.thumbnail((200,200))
                    tk_img = ImageTk.PhotoImage(img)
                    img_label = Label(inner_post, image=tk_img)
                    img_label.image = tk_img
                    img_label.pack(anchor="w", pady=5)
                except:
                    Label(inner_post, text="[Image not found]").pack(anchor="w")

            if show_timestamps.get():
                ts_label = Label(inner_post, text=f"[{ts}]", font=("Arial",9))
                ts_label.pack(anchor="w")

            post_frame.bind("<Button-1>", lambda e, pid=post_id, f=post_frame: select_post(pid, f))
            title_label.bind("<Button-1>", lambda e, pid=post_id, f=post_frame: select_post(pid, f))
            body_label.bind("<Button-1>",  lambda e, pid=post_id, f=post_frame: select_post(pid, f))

            cur.execute("SELECT username, comment, timestamp, image_path FROM comments WHERE post_id=?", (post_id,))
            for cu, ct, cts, cimg in cur.fetchall():
                comment_frame = Frame(inner_post, bd=0, padx=10, pady=2)
                comment_frame.pack(fill=X)
                comment_label = Label(comment_frame, text=f"→ {cu}: {ct}", font=("Arial",10,"bold"))
                comment_label.pack(anchor="w")
                if cimg:
                    try:
                        cimage = Image.open(cimg)
                        cimage.thumbnail((150,150))
                        tk_cimg = ImageTk.PhotoImage(cimage)
                        cimg_label = Label(comment_frame, image=tk_cimg)
                        cimg_label.image = tk_cimg
                        cimg_label.pack(anchor="w", pady=3)
                    except:
                        Label(comment_frame, text="[Image not found]").pack(anchor="w")
                if show_timestamps.get():
                    cts_label = Label(comment_frame, text=f"[{cts}]", font=("Arial",8))
                    cts_label.pack(anchor="w")
        con.close()

    def create_post(title_entry, body_widget, img_holder):
        title = title_entry.get().strip()
        body  = body_widget.get("1.0", END).strip()
        img_path = img_holder['path']
        if title and body:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            con = sqlite3.connect('myData.db')
            cur = con.cursor()
            cur.execute("INSERT INTO posts(username,title,body,timestamp,image_path) VALUES(?,?,?,?,?)",
                        (current_user, title, body, timestamp, img_path))
            con.commit()
            con.close()
            title_entry.delete(0, END)
            body_widget.delete("1.0", END)
            img_holder['path'] = None
            refresh_feed(home_feed_frame)
            refresh_feed(posts_feed_frame)

    def add_comment(entry_widget, img_holder):
        if selected_post_id['id'] is None:
            messagebox.showerror("Error", "Please click a post first.")
            return
        text = entry_widget.get().strip()
        img_path = img_holder['path']
        if text or img_path:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            con = sqlite3.connect('myData.db')
            cur = con.cursor()
            cur.execute("INSERT INTO comments(post_id, username, comment, timestamp, image_path) VALUES(?,?,?,?,?)",
                        (selected_post_id['id'], current_user, text, timestamp, img_path))
            con.commit()
            con.close()
            entry_widget.delete(0, END)
            img_holder['path'] = None
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
    reg_first_name = ttk.Entry(reg, width=30); reg_first_name.grid(row=1, column=1)
    Label(reg, text="Last Name").grid(row=2, column=0)
    reg_last_name = ttk.Entry(reg, width=30); reg_last_name.grid(row=2, column=1)
    Label(reg, text="Email").grid(row=3, column=0)
    reg_email = ttk.Entry(reg, width=30); reg_email.grid(row=3, column=1)
    Label(reg, text="Username").grid(row=4, column=0)
    reg_username = ttk.Entry(reg, width=30); reg_username.grid(row=4, column=1)
    Label(reg, text="Password").grid(row=5, column=0)
    reg_password = ttk.Entry(reg, width=30, show="*"); reg_password.grid(row=5, column=1)
    Button(reg, text="Create Account", command=submit).grid(row=6, column=0, columnspan=2, pady=5)

# -------------------- Login Form --------------------
username = ttk.Entry(root, width=30); username.grid(row=3, column=1)
password = ttk.Entry(root, width=30, show="*"); password.grid(row=4, column=1)

Label(root, text="Username").grid(row=3, column=0)
Label(root, text="Password").grid(row=4, column=0)

Button(root, text="Register", command=openRegistrationWindow).grid(row=5, column=0, pady=5)
Button(root, text="Login", command=login).grid(row=5, column=1, pady=5)

root.mainloop()

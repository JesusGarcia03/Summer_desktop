from tkinter import *
from tkinter import messagebox
import sqlite3

# Root Widget for running the app
root = Tk()
root.title('Data app')

###########################
# Create the data base

# Step 1: data connect & the cursor
dataConnect = sqlite3.connect('myData.db')
cursor = dataConnect.cursor()

#### Create the database table (executed just one time)

cursor.execute(""" CREATE TABLE IF NOT EXISTS users(
					first_name text,
					last_name  text,
					username text UNIQUE,
					email  text,
					password text
				)
				""")

dataConnect.commit()
dataConnect.close()

# Method for submitting data from a data form (Registering Account)
def submit():
	# Pointing to myData.db database
	dataConnect = sqlite3.connect('myData.db')
	cursor = dataConnect.cursor()
	try:
		cursor.execute("""INSERT INTO users VALUES(:first_name, :last_name, :username, :email, :password)""",
			{
				'first_name': reg_first_name.get().strip(),
				'last_name': reg_last_name.get().strip(),
				'username': reg_username.get().strip(),
				'email': reg_email.get().strip(),
				'password': reg_password.get().strip()
			})

		dataConnect.commit()
		messagebox.showinfo("Registration", "Registration successful!")
		

		#Delete the entry form, after pushing data
		reg_first_name.delete(0,END)
		reg_last_name.delete(0,END)
		reg_username.delete(0,END)
		reg_email.delete(0,END)
		reg_password.delete(0,END)
	except sqlite3.IntegrityError:
		messagebox.showerror("Error", "Username already exists.")
	finally:
		dataConnect.close()
		

#method for search data from database (Login)
def login():
	dataConnect = sqlite3.connect('myData.db')
	cursor = dataConnect.cursor()
	cursor.execute(
		"SELECT 1 FROM users WHERE username=? AND  password=?", 
		(username.get().strip(), password.get().strip())
	)
	row = cursor.fetchone()
	dataConnect.close()
	if row:
		messagebox.showinfo("Login", "Login successful!")
	else:
		messagebox.showerror("Login", "Invalid username or password.")

def openRegistrationWindow():
	global reg_first_name, reg_last_name, reg_username, reg_email, reg_password
	reg = Toplevel(root)
	reg.title("Register")

	Label(reg, text="Please fill in the details below to register:").pack(pady=10)
	
	Label(reg, text="First Name").grid(row=0, column=0, sticky="e", padx=5, pady=2)
	reg_first_name = Entry(reg, width=30)
	reg_first_name.grid(row=0, column=1, padx=5, pady=2)

	Label(reg, text="Last Name").grid(row=1, column=0, sticky="e", padx=5, pady=2)
	reg_last_name = Entry(reg, width=30)
	reg_last_name.grid(row=1, column=1, padx=5, pady=2)

	Label(reg, text="Email").grid(row=2, column=0, sticky="e", padx=5, pady=2)
	reg_email = Entry(reg, width=30)
	reg_email.grid(row=2, column=1, padx=5, pady=2)

	Label(reg, text="Username").grid(row=3, column=0, sticky="e", padx=5, pady=2)
	reg_username = Entry(reg, width=30)
	reg_username.grid(row=3, column=1, padx=5, pady=2)

	Label(reg, text="Password").grid(row=4, column=0, sticky="e", padx=5, pady=2)
	reg_password = Entry(reg, width=30, show="*")
	reg_password.grid(row=4, column=1, padx=5, pady=2)

	Button(reg, text="Create Account", command=submit).grid(row=5, column=0, columnspan=2, pady=8)


#####################################################
# Labels
'''firstN_label = Label(root, text="First Name").grid(row=0, column=0, sticky="e", padx = 5, pady = 2)
lastN_label = Label(root, text="Last Name").grid(row=1, column=0, sticky="e", padx = 5, pady = 2)
email_label = Label(root, text="Email").grid(row=2, column=0, sticky="e", padx = 5, pady = 2)
'''
username_label = Label(root, text="Username").grid(row=3, column=0, sticky="e", padx = 5, pady = 2)
password_label = Label(root, text="Password").grid(row=4, column=0, sticky="e", padx = 5, pady = 2)

# Entry fields
'''first_name = Entry(root, width=30)
last_name = Entry(root, width=30)
email = Entry(root, width=30)
'''

username = Entry(root, width=30)
password = Entry(root, width=30, show="*")

# Positioning Entry fields
'''first_name.grid(row=0, column=1, padx = 5, pady = 2)
last_name.grid(row=1, column=1, padx = 5, pady = 2)
email.grid(row=2, column=1, padx = 5, pady = 2)'''
username.grid(row=3, column=1, padx = 5, pady = 2)
password.grid(row=4, column=1, padx = 5, pady = 2)

#Buttons
register_b = Button(root, text="Register", command = openRegistrationWindow)
register_b.grid(row=5, column=0, pady = 6)
login_b = Button(root, text="Login", command=login)
login_b.grid(row=5, column=1, pady = 6)

root.mainloop()

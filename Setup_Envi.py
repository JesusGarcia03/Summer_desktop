from tkinter import *
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
'''
cursor.execute(""" CREATE TABLE addresses(
					first_name text,
					last_name  text,
					address    text,
					student_id text,
					age        integer
					)
				""")
'''

# Method for submitting data from a data form
def submit():
	# Pointing to myData.db database
	dataConnect = sqlite3.connect('myData.db')
	cursor = dataConnect.cursor()

	cursor.execute("""INSERT INTO addresses VALUES(:first_name, :last_name, :address, :student_id, :age)""",
		{
			'first_name': first_name.get(),
			'last_name': last_name.get(),
			'address': address.get(),
			'student_id': student_id.get(),
			'age': age.get()
		})
	dataConnect.commit()
	dataConnect.close()
	#Delete the entry form, after pushing data
	first_name.delete(0,END)
	last_name.delete(0,END)
	address.delete(0,END)
	student_id.delete(0,END)
	age.delete(0,END)

#method for search data from database
def query_contacts():
	dataConnect = sqlite3.connect('myData.db')
	cursor = dataConnect.cursor()

	cursor.execute("SELECT *, oid FROM addresses")
	contacts = cursor.fetchall()

	show_contacts = ""
	for contact in contacts:
		show_contacts += str(contact) + "\n"
		query_label = Label(root, text = show_contacts).grid(row=7, column=1)
		dataConnect.close()

	#print query in terminal for debugging process
	print(contacts)



#####################################################

submit_b = Button(root, text="Add to contacts", command=submit)

# Labels
firstN_label = Label(root, text="First Name").grid(row=0, column=0)
lastN_label = Label(root, text="Last Name").grid(row=1, column=0)
address_label = Label(root, text="Address").grid(row=2, column=0)
SID_label = Label(root, text="Student ID").grid(row=3, column=0)
age_label = Label(root, text="Age").grid(row=4, column=0)

# Entry fields
first_name = Entry(root, width=30)
last_name = Entry(root, width=30)
address = Entry(root, width=30)
student_id = Entry(root, width=8)
age = Entry(root, width=2)

# Positioning Entry fields
first_name.grid(row=0, column=1)
last_name.grid(row=1, column=1)
address.grid(row=2, column=1)
student_id.grid(row=3, column=1)
age.grid(row=4, column=1)

submit_b.grid(row=5, column=1)
query_db = Button(root, text= "Show contacts", command=query_contacts)
query_db.grid(row=6, column=1)

dataConnect.commit()
dataConnect.close()

root.mainloop()

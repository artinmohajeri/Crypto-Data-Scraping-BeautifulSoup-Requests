from bs4 import BeautifulSoup
import requests
import certifi
import sqlite3

url = "https://coinmarketcap.com/"
response = requests.get(url, verify=certifi.where())

# connect to the database (or create if not exist) ↓
connect = sqlite3.connect("crypto_data.db")
# create a cursor object to interact with the database ↓
cursor = connect.cursor()
# create a table to store the info ↓
cursor.execute('''
    CREATE TABLE IF NOT EXISTS crypto_data(
                name TEXT,
                price TEXT,
                volume TEXT
    )''')

doc = BeautifulSoup(response.text, "html.parser")
name_tags = doc.find_all(class_="sc-4984dd93-0 kKpPOn", limit=100)
price_tags = doc.find_all(class_ = "sc-a0353bbc-0 gDrtaY", limit=100)
volume_tags = doc.find_all(class_ = "sc-4984dd93-0 jZrMxO font_weight_500", limit=100)

for name_tag, price_tag, volume_tag in zip(name_tags, price_tags, volume_tags):
    name = name_tag.string
    price = price_tag.a.span.string
    volume = volume_tag.string
    cursor.execute('INSERT INTO crypto_data (name, price, volume) VALUES (?,?,?)', (name,price,volume))

with open("display.py","w") as f:
    f.write('''
from tkinter import *
from tkinter import ttk
import sqlite3

# window configurations
win = Tk()
# win.minsize(400,300)
win.title("Crypto Data")

# connecting to the database
connect = sqlite3.connect("crypto_data.db")
cursor = connect.cursor()
cursor.execute("SELECT * FROM crypto_data")
rows = cursor.fetchall()

# style of the table
style = ttk.Style()
style.configure("Treeview", font=("Arial", 14), rowheight=40, foreground="black", background="white",)


tree = ttk.Treeview(win, columns=("name", "price", "volume"), show="headings")
tree.heading("name", text="Name")
tree.heading("price", text="Price")
tree.heading("volume", text="Volume")
tree.tag_configure("evenrow", background="#d1d1d1")
tree.tag_configure("oddrow", background="white")

for i, row in enumerate(rows):
    if i % 2 == 0:
        tree.insert("", "end", values=row, tags=("evenrow",))
    else:
        tree.insert("", "end", values=row, tags=("oddrow",))
tree.pack()

win.mainloop()

''')


# commit the changes and close the connection
connect.commit()
connect.close()


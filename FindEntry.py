from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3

from Vault import run_vault

sq_con = sqlite3.connect("CvaultDB.sqlite")
sq_cur = sq_con.cursor()


class FindEntry(Toplevel):
    def __init__(self, skeleton_key, entries):
        Toplevel.__init__(self)
        self.skeleton_key = skeleton_key
        self.entries = entries

        self.title("Find Entry")
        self.resizable(False, False)
        self.geometry("+560+320")
        self.iconbitmap("Icons\\V2.ico")

        # ttk style config
        self.ttk_style = ttk.Style()
        self.ttk_style.configure("TButton", font="Courier 8", justify="c")

        # top canvas
        self.top_canvas = Canvas(self, width=160, height=80, bg="lightgrey")
        self.lock_icon = PhotoImage(file="Icons\\lock.png")
        self.top_canvas.create_image(84, 42, image=self.lock_icon)
        self.top_canvas.grid(row=0, column=0, sticky="ew")

        # bottom frame
        self.bottom_frame = Frame(self)
        self.bottom_frame.grid(row=1, column=0, sticky="news")

        def list_box_open(_event=None):
            # extract _id, needed due to alignment padding in a listbox
            try:
                cur_entry = self.list_box.get(self.list_box.curselection())
                cur_entry_split = cur_entry.split(" ")
                cur_entry_id = int()
                for split in cur_entry_split:
                    if split:
                        cur_entry_id = split
                        break
            except TclError:
                pass
            else:
                _top_level_entry = run_vault(self.skeleton_key, "open", cur_entry_id)
                self.destroy()

        self.list_box = Listbox(
            self.bottom_frame,
            width=24,
            height=12,
            borderwidth=2,
            relief="groove",
            bg="#f0eb4b",
            selectbackground="#f0eb4b",
            selectforeground="darkred",
        )
        self.list_box.bind("<Double-Button>", list_box_open)
        self.list_box.grid(row=0, column=0, padx=3, sticky="ns")
        self.sb = Scrollbar(self.bottom_frame, orient=VERTICAL)
        self.sb.config(command=self.list_box.yview)
        self.list_box.config(font=("Consolas Bold", 10), yscrollcommand=self.sb.set)
        # self.sb.grid(row=0, column=1, sticky='news')  # no visible scrollbar

        # close button
        self.close_button = ttk.Button(
            self.bottom_frame, text="Close", style="TButton", command=self.destroy
        )
        self.close_button.grid(column=0, row=1, pady=(3, 6), sticky="s")

        # show results
        for entry in self.entries:
            list_string = f"{entry[0]:>4}  {entry[1]:<20}"
            self.list_box.insert(END, list_string)


def find(skeleton_key, enquiry):
    query = 'SELECT * FROM "entries" WHERE master LIKE ?'
    query_data = [f"%{enquiry}%"]
    entries = sq_cur.execute(query, query_data).fetchall()
    if not entries:
        messagebox.showinfo("Find", "No Matches found!", icon="info")
    else:
        FindEntry(skeleton_key, entries)

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from pathlib import Path

from VaultZero import run_zero
from VaultInit import vault_init
from Vault import run_vault
from FindEntry import find

sq_con = sqlite3.connect('CvaultDB.sqlite')
sq_cur = sq_con.cursor()


class MainApp:
    def __init__(self, master):
        self.master = master
        self.skeleton_key = tuple()

        # ttk style config
        self.ttk_style = ttk.Style()
        self.ttk_style.configure('TButton', font='Courier 8', justify='c')

        # top canvas
        self.top_canvas = Canvas(master, width=420, height=80, bg='lightgrey')
        self.lock_icon = PhotoImage(file='Icons\\lock.png')
        self.top_canvas.create_image(54, 42, image=self.lock_icon)
        self.text_icon = PhotoImage(file='Icons\\CryptoVault.png')
        self.top_canvas.create_image(204, 30, image=self.text_icon)
        self.top_canvas.grid(row=0, column=0, sticky='ew')

        # search box
        def find_button():
            enquiry = self.search_box.get()
            find(self.skeleton_key, enquiry)

        self.search_box = Entry(master, font='Courier 12')
        self.search_box.grid(row=0, column=0, sticky='es', padx=(0, 96), pady=(0, 13))

        self.find_button = ttk.Button(master, text='Find\nEntry', width=8,
                                      style='TButton', command=find_button)
        self.find_button.grid(row=0, column=0, sticky='es', padx=(3, 24), pady=(0, 12))

        # bottom frame
        self.bottom_frame = Frame(master, bg='#f0eb4b')
        self.bottom_frame.grid(row=1, column=0, sticky='news')

        # listbox

        # function for edit button and double-click action
        def list_box_open(_event=None):
            try:
                cur_entry = self.list_box.get(self.list_box.curselection())
                cur_entry_split = cur_entry.split(' ')
                cur_entry_id = int()
                for split in cur_entry_split:
                    if split:
                        cur_entry_id = split
                        break
            except TclError:
                pass
            else:
                _top_level_entry = run_vault(self.skeleton_key, 'open', cur_entry_id)
                self.list_box.delete(0, END)
                listbox_data()

        self.list_box = Listbox(self.bottom_frame, width=42, height=24,
                                borderwidth=2, relief='groove', bg='#f0f0f0',
                                selectbackground='#f0f0f0', selectforeground='darkred')
        self.list_box.bind('<Double-Button>', list_box_open)
        self.list_box.grid(row=0, column=0, sticky='ns')
        self.sb = Scrollbar(self.bottom_frame, orient=VERTICAL)
        self.sb.config(command=self.list_box.yview)
        self.list_box.config(font='Consolas 10', yscrollcommand=self.sb.set)
        self.sb.grid(row=0, column=1, sticky='news')

        # populate listbox
        def listbox_data():
            entries = sq_cur.execute('SELECT * FROM entries').fetchall()
            if entries:
                self.list_box.configure(state='normal')
                for entry in entries:
                    list_string = f'{entry[0]:>4}  {entry[1]:<20}'
                    self.list_box.insert(END, list_string)
            else:
                self.list_box.insert(END, '  No Entries...')
                self.list_box.configure(state='disabled')

        # bottom_logo
        self.bottom_logo = PhotoImage(file='Icons\\CryptoVault_V2.png')
        self.bottom_logo_canvas = Canvas(master, width=94, height=380, bg='#f0f0f0')
        self.bottom_logo_canvas.create_image(0, 0, anchor='nw', image=self.bottom_logo)
        self.bottom_logo_canvas.grid(row=1, column=0, padx=(0, 186), pady=(3, 3), sticky='e')

        # functions buttons
        # new entry func and button
        def new_entry():
            _top_level_entry = run_vault(self.skeleton_key, 'new')
            self.list_box.configure(state='normal')
            self.list_box.delete(0, END)
            listbox_data()

        self.new_button = ttk.Button(self.bottom_frame, text='New', width=8,
                                     style='TButton',  command=new_entry)
        self.new_button.grid(row=0, column=2, padx=(48, 0), pady=(30, 0), sticky='nw')

        # edit entry button
        self.new_button = ttk.Button(self.bottom_frame, text='Open', width=8,
                                     style='TButton', command=list_box_open)
        self.new_button.grid(row=0, column=2, padx=(48, 0), pady=(90, 0), sticky='nw')

        # delete entry func and button
        def del_entry():
            try:
                # extract _id, needed due to alignment padding in a listbox
                cur_entry = self.list_box.get(self.list_box.curselection())
                cur_entry_split = cur_entry.split(' ')
                cur_entry_id = int()
                for split in cur_entry_split:
                    if split:
                        cur_entry_id = split
                        break
            except TclError:
                pass
            else:
                query = f'DELETE FROM "entries" WHERE _id={cur_entry_id}'
                sq_cur.execute(query)
                if messagebox.askokcancel('Delete',
                                          'Warning!\nEntry will be permanently deleted\n\nProceed?',
                                          icon='warning'):
                    sq_con.commit()
                    self.list_box.delete(0, END)
                    listbox_data()

        self.new_button = ttk.Button(self.bottom_frame, text='Delete', width=8,
                                     style='TButton', command=del_entry)
        self.new_button.grid(row=0, column=2, padx=(48, 0), pady=(150, 0), sticky='nw')

        # About info button
        def _about():
            with open('about.txt') as about_file:
                about_text = about_file.read()
                messagebox.showinfo('About', about_text, icon='info')
        self.new_button = ttk.Button(self.bottom_frame, text='About', width=8,
                                     style='TButton', command=_about)  # TODO add 'about'
        self.new_button.grid(row=0, column=2, padx=48, pady=(0, 60), sticky='s')

        # quit button
        self.quit_button = ttk.Button(self.bottom_frame, text='Quit', width=8,
                                      style='TButton', command=sys.exit)
        self.quit_button.grid(row=0, column=2, padx=48, pady=(0, 30), sticky='s')

        # load user master key and pin, initiate and create 'new' if not any
        if not Path('CryptoKey.dat').is_file():
            if not messagebox.askokcancel('First Run', 'User Master Key not Found\nCreate new?'):
                sys.exit()
            else:
                sq_cur.execute('CREATE TABLE IF NOT EXISTS "entries"'
                               ' ("_id" INTEGER PRIMARY KEY,'
                               ' "master" TEXT,'
                               ' "login" BLOB,'
                               ' "password" BLOB,'
                               ' "notes" BLOB)')
                self.skeleton_key = run_zero()  # Create Password and Pin, VaultZero.py

        else:
            self.skeleton_key = vault_init()  # Check Password, VaultInit.py

        if not self.skeleton_key:
            sys.exit()
        else:
            listbox_data()


def main():
    root = Tk()
    root.title('CryptoVault v2')
    root.geometry('+480+200')
    root.resizable(False, False)
    root.iconbitmap('Icons\\V2.ico')
    root.lift()
    _main_app = MainApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

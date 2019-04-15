from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from Crypto.Cipher import AES
import hashlib

import pickle


class VaultInit(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title('Log In')
        self.resizable(False, False)
        self.geometry('+540+360')
        self.attributes('-topmost', True)

        self.skeleton_key = tuple()

        # ttk style config
        self.ttk_style = ttk.Style()
        self.ttk_style.configure('TButton', font='Courier 8', justify='c', takefocus=False)

        # top canvas
        self.top_canvas = Canvas(self, width=300, height=80, bg='lightgrey')
        self.text_icon = PhotoImage(file='Icons\\CryptoVault.png')
        self.top_canvas.create_image(156, 42, image=self.text_icon)
        self.top_canvas.grid(row=0, column=0, sticky='ew')

        # bottom frame
        self.bottom_frame = Frame(self, bg='#f0eb4b')
        self.bottom_frame.grid(row=1, column=0, sticky='news')

        self.lock_icon = PhotoImage(file='Icons\\lock.png')
        self.bottom_logo = Label(self, image=self.lock_icon, bg='#f0eb4b')
        self.bottom_logo.grid(column=0, row=1, padx=(0, 12), pady=(36, 0), sticky='en')

        # entry boxes
        Label(self.bottom_frame, text='*Master Password:', font='Courier 8', bg='#f0eb4b')\
            .grid(column=0, row=0, padx=12, pady=(6, 0), sticky='w')
        self.master_key = Entry(self.bottom_frame, font='Courier 10', width=24, show='✱')
        self.master_key.grid(column=0, row=0, padx=12, pady=(36, 0), sticky='w')

        Label(self.bottom_frame, text='*Master PIN:', font='Courier 8', bg='#f0eb4b')\
            .grid(column=0, row=2, padx=12, pady=(6, 0), sticky='w')
        self.master_pin = Entry(self.bottom_frame, font='Courier 10', width=24, show='✱')
        self.master_pin.grid(column=0, row=2, padx=12, pady=(36, 0), sticky='w')

        # buttons and store key and pin function
        self.cancel_button = ttk.Button(self.bottom_frame, text='Quit', width=8, command=self.destroy)
        self.cancel_button.grid(column=0, row=3, columnspan=2, pady=(30, 12), sticky='e')

        def _decrypt(cypher_text, key):
            iv = cypher_text[:AES.block_size]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(cypher_text[AES.block_size:])
            plaintext = plaintext.rstrip(b"\0").decode('utf-8')
            return plaintext

        def _login():
            master_key = self.master_key.get()
            master_pin = self.master_pin.get()

            with open('CryptoKey.dat', 'rb') as key_file:
                master_data = pickle.load(key_file)

            master_key_hash = hashlib.sha256(str(master_key).encode('utf-8')).digest()

            try:
                true_key = _decrypt(master_data[0], master_key_hash)
                true_pin = _decrypt(master_data[1], master_key_hash)
            except UnicodeError:
                messagebox.showwarning('Error', 'Wrong Key or PIN!', icon='warning')
            else:
                if true_key == master_key and true_pin == master_pin:
                    self.skeleton_key = (master_key, master_pin)
                    self.destroy()
                else:
                    messagebox.showwarning('Error', 'Wrong Key or PIN!', icon='warning')

        self.confirm_button = ttk.Button(self.bottom_frame, text='Confirm', width=8, command=_login)
        self.confirm_button.grid(column=0, row=3, columnspan=2, pady=(30, 12), padx=(0, 72), sticky='e')

        self.wait_window()


def vault_init():
    _v_init = VaultInit()
    if _v_init.skeleton_key:
        _v_init.destroy()
        return _v_init.skeleton_key  # if encrypted data matches user entry, return correct "skeleton_key" tuple,
    else:                            # (str(master_key), str(master_pin)
        return False

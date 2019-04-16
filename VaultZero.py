from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from Crypto.Cipher import AES
from Crypto import Random
import hashlib

import pickle


class KeyInit:
    def __init__(self, user_key: str, user_pin: str):
        self.user_key = user_key
        self.user_pin = user_pin
        key_hash = hashlib.sha256(user_key.encode('utf-8')).digest()

        def encrypt(crypto_string, key):
            crypto_string = crypto_string.encode('utf-8')
            crypto_string = crypto_string + b"\0" * (AES.block_size - len(crypto_string) % AES.block_size)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return iv + cipher.encrypt(crypto_string)

        self.master_key = encrypt(user_key, key_hash)
        self.master_pin = encrypt(user_pin, key_hash)


class VaultInit(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title('Zero Run')
        self.resizable(False, False)
        self.geometry('+720+360')
        self.iconbitmap('Icons\\V2.ico')

        self.skeleton_key = tuple()

        # ttk style config
        self.ttk_style = ttk.Style()
        self.ttk_style.configure('TButton', font='Courier 8', justify='c', takefocus=False)

        # top canvas
        self.top_canvas = Canvas(self, width=320, height=80, bg='lightgrey')
        self.lock_icon = PhotoImage(file='Icons\\lock.png')
        self.top_canvas.create_image(48, 42, image=self.lock_icon)
        self.text_icon = PhotoImage(file='Icons\\CryptoVault.png')
        self.top_canvas.create_image(204, 42, image=self.text_icon)
        self.top_canvas.grid(row=0, column=0, sticky='ew')

        # bottom frame
        self.bottom_frame = Frame(self, bg='#d7d240')
        self.bottom_frame.grid(row=1, column=0, sticky='news')

        # warning logo
        self.warning_canvas = Canvas(self, width=90, height=224, bg='#d7d240', highlightbackground='darkred')
        self.warning_image = PhotoImage(file='Icons\\init_warning.png')
        self.warning_canvas.create_image(0, 0, anchor='nw', image=self.warning_image)
        self.warning_canvas.grid(row=1, column=0, padx=(0, 30), pady=(12, 12), sticky='e')

        # entry boxes
        Label(self.bottom_frame, text='*Master Password:', font='Courier 8', bg='#d7d240')\
            .grid(column=0, row=0, padx=12, pady=(6, 0), sticky='w')
        self.master_entry = Entry(self.bottom_frame, font='Courier 8')
        self.master_entry.grid(column=0, row=0, padx=12, pady=(36, 0), sticky='w')

        Label(self.bottom_frame, text='*Confirm Password:', font='Courier 8', bg='#d7d240')\
            .grid(column=0, row=1, padx=12, pady=(6, 0), sticky='w')
        self.second_entry = Entry(self.bottom_frame, font='Courier 8')
        self.second_entry.grid(column=0, row=1, padx=12, pady=(36, 0), sticky='w')

        Label(self.bottom_frame, text='*Master PIN:', font='Courier 8', bg='#d7d240')\
            .grid(column=0, row=2, padx=12, pady=(6, 0), sticky='w')
        self.master_pin = Entry(self.bottom_frame, font='Courier 8')
        self.master_pin.grid(column=0, row=2, padx=12, pady=(36, 0), sticky='w')

        # buttons and store key and pin function
        self.cancel_button = ttk.Button(self.bottom_frame, text='Quit', width=8, command=sys.exit)
        self.cancel_button.grid(column=0, row=3, pady=(54, 12), padx=(90, 0), sticky='w')

        def _create_key():
            pass_1 = self.master_entry.get()
            pass_2 = self.second_entry.get()
            pin = self.master_pin.get()
            try:
                _ = int(pin)  # TODO fix ugly check int, try:/Raise method for all
            except ValueError:
                messagebox.showwarning('PIN Error', 'PIN must be number values only!', icon='warning')
                self.lift()
            else:
                if pass_1 != pass_2:
                    messagebox.showwarning('Key Mismatch', 'Passwords do not Match!', icon='warning')
                    self.lift()
                elif len(pin) < 4:
                    messagebox.showwarning('PIN Error', 'PIN must be at least 4 numbers long!', icon='warning')
                    self.lift()
                elif len(pass_1) < 8:
                    messagebox.showwarning('Key Length', 'Password must be at least 8 characters long!', icon='warning')
                    self.lift()
                else:
                    skeleton_key = KeyInit(pass_1, str(pin))
                    self.skeleton_key = (skeleton_key.user_key, skeleton_key.user_pin)
                    key_dump = (skeleton_key.master_key, skeleton_key.master_pin)
                    try:
                        with open('CryptoKey.dat', 'wb') as key_file:
                            pickle.dump(key_dump, key_file)
                    except OSError:
                        messagebox.showwarning('Error', 'Cannot write to file!\nCheck Permissions', icon='warning')
                    else:
                        messagebox.showinfo('Crypto Vault V2', 'Successfully Created and Encrypted!')
                        self.destroy()

        self.create_button = ttk.Button(self.bottom_frame, text='Create', width=8, command=_create_key)
        self.create_button.grid(column=0, row=3, pady=(54, 12), padx=(12, 0), sticky='w')

        self.wait_window()


# First run, if CryptoKey.dat wasn't found
# Store user-created tuple(master_key, master_PIN) encrypted with itself
def run_zero():
    _v_one = VaultInit()
    if _v_one.skeleton_key:
        return _v_one.skeleton_key

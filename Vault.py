from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pyperclip
import sqlite3

from Crypto.Cipher import AES
from Crypto import Random
import hashlib

from PIN import pin_check
from KeyGenerator import key_gen


sq_con = sqlite3.connect("CvaultDB.sqlite")
sq_cur = sq_con.cursor()


class Vault:
    def __init__(self, key_hash, master: str, login: str, password: str, notes=""):
        self.key_hash = key_hash
        self.master = master

        def encrypt(crypto_string, key):
            crypto_string = crypto_string.encode("utf-8")
            crypto_string = crypto_string + b"\0" * (
                AES.block_size - len(crypto_string) % AES.block_size
            )
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return iv + cipher.encrypt(crypto_string)

        self.login = encrypt(login, key_hash)
        self.password = encrypt(password, key_hash)
        self.notes = encrypt(notes, key_hash)


class VaultEntry(Toplevel):
    def __init__(self, skeleton_key, action, _id=0):
        Toplevel.__init__(self)
        self.title("Vault Entry")
        self.resizable(False, False)
        self.geometry("+720+360")
        self.iconbitmap("Icons\\V2.ico")

        self.skeleton_key = skeleton_key
        self.action = action
        self._id = _id
        self.key_hash = hashlib.sha256(str(skeleton_key[0]).encode("utf-8")).digest()

        # ttk style config
        self.ttk_style = ttk.Style()
        self.ttk_style.configure("TButton", font="Courier 8", justify="c")

        # top canvas
        self.top_canvas = Canvas(self, width=320, height=80, bg="lightgrey")
        self.lock_icon = PhotoImage(file="Icons\\lock.png")
        self.top_canvas.create_image(48, 42, image=self.lock_icon)
        self.text_icon = PhotoImage(file="Icons\\CryptoVault.png")
        self.top_canvas.create_image(204, 42, image=self.text_icon)
        self.top_canvas.grid(row=0, column=0, sticky="ew")

        # bottom frame
        self.bottom_frame = Frame(self, bg="#f0eb4b")
        self.bottom_frame.grid(row=1, column=0, sticky="news")

        # entry boxes
        Label(
            self.bottom_frame, text="*Master Account:", font="Courier 8", bg="#f0eb4b"
        ).grid(column=0, row=0, padx=12, pady=(6, 0), sticky="w")
        self.master_entry = Entry(self.bottom_frame, font="Courier 8")
        self.master_entry.grid(column=0, row=0, padx=12, pady=(36, 0), sticky="w")

        Label(
            self.bottom_frame, text="*Login Name:", font="Courier 8", bg="#f0eb4b"
        ).grid(column=0, row=1, padx=12, sticky="w")
        self.login_entry = Entry(self.bottom_frame, font="Courier 8")
        self.login_entry.grid(column=0, row=1, padx=12, pady=(30, 0), sticky="w")

        Label(
            self.bottom_frame, text="*Password:", font="Courier 8", bg="#f0eb4b"
        ).grid(column=0, row=2, padx=12, sticky="w")
        self.password_entry = Entry(self.bottom_frame, font="Courier 8")
        self.password_entry.grid(column=0, row=2, padx=12, pady=(30, 0), sticky="w")

        # notes text box
        Label(self.bottom_frame, text="Notes:", font="Courier 8", bg="#f0eb4b").grid(
            column=0, row=3, padx=12, pady=(12, 0), sticky="ws"
        )
        self.notes_entry = Text(
            self.bottom_frame, width=20, height=8, wrap=WORD, font="Courier 8"
        )
        self.notes_entry.grid(column=0, row=4, padx=12, pady=(0, 0), sticky="wn")

        # if an existing entry, decrypt and populate
        def decrypt(cypher_text, key_hash):
            iv = cypher_text[: AES.block_size]
            cipher = AES.new(key_hash, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(cypher_text[AES.block_size :])
            plaintext = plaintext.rstrip(b"\0").decode("utf-8")
            return plaintext

        if self.action == "open":
            entry_data = sq_cur.execute(
                f'SELECT * FROM "entries" WHERE _id={self._id}'
            ).fetchone()
            self.master_entry.insert(0, entry_data[1])
            self.master_entry.configure(state="disabled")
            self.login_entry.insert(0, decrypt(entry_data[2], self.key_hash))
            self.login_entry.configure(state="disabled")
            self.password_entry.insert(0, decrypt(entry_data[3], self.key_hash))
            self.password_entry.configure(state="disabled")
            self.notes_entry.insert(END, decrypt(entry_data[4], self.key_hash))
            self.notes_entry.configure(state="disabled")

        # strong random password generator func and button
        def _generator():
            key_string = key_gen()
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, key_string)

        self.generate_pass = ttk.Button(
            self.bottom_frame,
            text="Generate\nSecure",
            width=9,
            style="TButton",
            command=_generator,
        )
        self.generate_pass.grid(column=0, row=2, padx=(12, 0), pady=(96, 0), sticky="w")

        # copy to clipboard func and button
        def _clip_copy():
            clip = self.password_entry.get()
            pyperclip.copy(clip)

        self.clip_copy = ttk.Button(
            self.bottom_frame,
            text="Copy to\nClipboard",
            width=9,
            style="TButton",
            command=_clip_copy,
        )
        self.clip_copy.grid(column=0, row=2, padx=(84, 0), pady=(96, 0), sticky="w")

        # logo
        self.bottom_logo = PhotoImage(file="Icons\\CryptoVault_V2.png")
        self.bottom_logo_canvas = Canvas(
            self.bottom_frame,
            width=90,
            height=380,
            bg="#f0eb4b",
            highlightbackground="#f0eb4b",
        )
        self.bottom_logo_canvas.create_image(0, 0, ancho="nw", image=self.bottom_logo)
        self.bottom_logo_canvas.grid(
            row=0, column=1, rowspan=5, padx=(64, 0), pady=(3, 3), sticky="e"
        )

        # cancel/close button
        close_button_text = "Cancel"
        if self.action == "open":
            close_button_text = "Close"

        self.cancel_button = ttk.Button(
            self.bottom_frame, text=close_button_text, width=10, command=self.destroy
        )
        self.cancel_button.grid(
            column=0, row=5, columnspan=2, pady=(24, 12), padx=(0, 12), sticky="e"
        )

        # save entry function and button, replaced with unlock button for existing entries
        def _vault_it():
            master = self.master_entry.get()
            login = self.login_entry.get()
            password = self.password_entry.get()
            notes = self.notes_entry.get(1.0, "end-1c")

            write_confirm = False

            if not all([master, login, password]):
                messagebox.showwarning(
                    "Missing Entries",
                    "please ensure all * fields are filled!",
                    icon="warning",
                )
                self.lift()
            else:
                vault_entry = Vault(self.key_hash, master, login, password, notes)
                query_data = [
                    vault_entry.master,
                    vault_entry.login,
                    vault_entry.password,
                    vault_entry.notes,
                ]
                query = ""

                if self.action == "new":
                    query = 'INSERT INTO "entries" (master, login, password, notes) VALUES(?,?,?,?)'
                    write_confirm = True

                elif self.action == "open":
                    query = f'UPDATE "entries" SET master=?, login=?, password=?, notes=? WHERE _id={self._id}'
                    write_confirm = messagebox.askokcancel(
                        "Overwrite",
                        "Warning!\n" "Entry will be overwritten,\n" "\nProceed?",
                        icon="warning",
                    )
                else:
                    pass

                if write_confirm:
                    try:
                        sq_cur.execute(query, query_data)
                    except OSError:
                        messagebox.showwarning(
                            "Error", "Cannot Write to File!", icon="warning"
                        )
                    else:
                        sq_con.commit()
                        messagebox.showinfo(
                            "Success", "Vault Entry Successfully Encrypted!"
                        )
                        self.destroy()

        def _unlock_it():
            self.master_entry.configure(state="normal")
            self.login_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self.notes_entry.configure(state="normal")
            self.unlock_button.grid_forget()
            self.save_button = ttk.Button(
                self.bottom_frame, text="reVault it", width=12, command=_vault_it
            )
            self.save_button.grid(
                column=0, row=5, columnspan=2, pady=(24, 12), padx=(0, 99), sticky="e"
            )

        # save button
        if self.action == "new":
            self.save_button = ttk.Button(
                self.bottom_frame, text="Vault it", width=10, command=_vault_it
            )
            self.save_button.grid(
                column=0, row=5, columnspan=2, pady=(24, 12), padx=(0, 96), sticky="e"
            )
        elif self.action == "open":
            self.unlock_button = ttk.Button(
                self.bottom_frame, text="Unlock", width=10, command=_unlock_it
            )
            self.unlock_button.grid(
                column=0, row=5, columnspan=2, pady=(24, 12), padx=(12, 0), sticky="w"
            )

        # self close
        if self.action == "open":
            Label(
                self.bottom_frame,
                text="*Warning! this window will close itself in 3 minutes!",
                font=("Verdana", 7, "italic"),
                bg="#f0eb4b",
                fg="darkred",
            ).grid(
                column=0, row=5, columnspan=2, pady=(0, 33), padx=(0, 12), sticky="e"
            )
            self.after(180000, self.destroy)

        self.wait_window(self)


def run_vault(skeleton_key, action, cur_entry_id=None):
    if action == "open":
        pin = pin_check(skeleton_key)
        if not pin:
            pass
        else:
            _v = VaultEntry(skeleton_key, action, cur_entry_id)

    elif action == "new":
        _v = VaultEntry(skeleton_key, action)

from tkinter import *
from tkinter import ttk
from tkinter import messagebox


class PIN(Toplevel):
    def __init__(self, skeleton_key):
        Toplevel.__init__(self)

        self.skeleton_key = skeleton_key
        self.auth = False

        self.title('Confirm PIN')
        self.resizable(False, False)
        self.geometry('+540+360')
        self.iconbitmap('Icons\\V2.ico')

        # ttk style config
        self.ttk_style = ttk.Style()
        self.ttk_style.configure('TButton', font='Courier 8', justify='c')

        # top canvas
        self.top_canvas = Canvas(self, width=160, height=80, bg='lightgrey')
        self.lock_icon = PhotoImage(file='Icons\\lock.png')
        self.top_canvas.create_image(84, 42, image=self.lock_icon)
        self.top_canvas.grid(row=0, column=0, sticky='ew')

        # bottom frame
        self.bottom_frame = Frame(self, bg='#f0eb4b')
        self.bottom_frame.grid(row=1, column=0, sticky='news')

        # entry box
        Label(self.bottom_frame, text='*Confirm PIN  ', font='Courier 8', bg='#f0eb4b')\
            .grid(column=0, row=0, pady=(6, 0), sticky='ns')
        self.user_pin = Entry(self.bottom_frame, font='Courier 8', justify='c', show='✱')
        self.user_pin.focus_force()
        self.user_pin.grid(column=0, row=0, padx=(10, 12), pady=(36, 0), sticky='n')

        self.cancel_button = ttk.Button(self.bottom_frame, text='Cancel', width=8, command=self.destroy)
        self.cancel_button.grid(column=0, row=3, pady=(54, 12), padx=(88, 0), sticky='w')

        def _login(_event=None):
            master_pin = self.user_pin.get()
            if master_pin == skeleton_key[1]:
                self.auth = True
                self.destroy()
            else:
                messagebox.showwarning('Error', 'Wrong PIN!', icon='warning')

        self.confirm_button = ttk.Button(self.bottom_frame, text='Confirm', width=8, command=_login)
        self.confirm_button.grid(column=0, row=3, pady=(54, 12), padx=(14, 0), sticky='w')

        self.lift()
        self.bind('<Return>', _login)
        self.wait_window()


# simple secondary check after user been logged in, un-encrypted compare PIN input vs skeleton_key in memory
def pin_check(skeleton_key):
    pin = PIN(skeleton_key)
    if pin.auth:
        return True
    else:
        return False

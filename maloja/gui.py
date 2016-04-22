import tkinter as tk
from tkinter import messagebox

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.QUIT = tk.Button(self, text="QUIT", fg="red",
                                            command=root.destroy)
        self.QUIT.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")

#root = tk.Tk()
#app = Application(master=root)
#app.mainloop()

def is_valid_salutation(salutation):
    """
    Salutations to be valid must start with one of:
         ['hello', 'hi', 'howdy'] + ',' [COMMA]
    and must end with '!' [EXCLAMATION MARK]

    >>> is_valid_salutation('howdy, moon!')
    True
    >>> is_valid_salutation('random phrase')
    False
    """
    return any(salutation.startswith(i+',') for i in ['hello', 'hi', 'howdy']) \
           and salutation.endswith('!')

class ValidEntry(tk.Entry):

    def __init__(self, *args, validator=lambda text: True, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = validator

    def get(self):
        text = super().get()
        if not self.validator(text):
            raise ValueError('Invalid input')
        return text

class ValidatorFrame(tk.Frame):

    INSTRUCTION_FONT = '20px'

    def __init__(self, root, *args, button_text='Validate', instructions=None,
                 validator=lambda text: True, **kwargs):
        super().__init__(root, *args, **kwargs)
        if instructions is None:
            instructions = validator.__doc__
        self.instructions = tk.Label(
            root,
            font=ValidatorFrame.INSTRUCTION_FONT,
            justify=tk.LEFT,
            text=instructions
        )
        self.instructions.pack(expand=1, fill=tk.X)
        self.user_input = ValidEntry(root, validator=validator)
        self.user_input.pack(expand=1, fill=tk.X)
        self.validate = tk.Button(root, command=self.validate, text=button_text)
        self.validate.pack()

    def validate(self):
        try:
            text = self.user_input.get()
        except ValueError:
            messagebox.showerror(
                "Input NOT valid.",
                "Please try again and enter a valid input."
            )
        else:
            messagebox.showinfo(
                "Input valid.",
                "Congratulations, you entered valid input."
            )

class TestGui(tk.Tk):

    TITLE_FONT = '25px'

    def __init__(self, *args, title=None, validator=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.title_label = tk.Label(self, font=self.TITLE_FONT, text=title)
        self.title_label.pack(expand=1, fill=tk.X)
        self.frame = ValidatorFrame(self, validator=validator)
        self.frame.pack(expand=1, fill=tk.X)
        if title is None:
            title = validator.__name__.replace('_', ' ').capitalize()
        self.wm_title(title)

if __name__ == '__main__':
    app = TestGui(validator=is_valid_salutation)
    app.mainloop()

import tkinter as tk
from tkinter import messagebox

def user_valid(text):
    return text

def url_valid(text):
    return text

class ValidEntry(tk.Entry):

    def __init__(self, *args, validator=lambda text: text, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = validator

    def get(self):
        text = self.validator(super().get())
        if not text:
            raise ValueError('Invalid input')
        return text

class DialogFrame(tk.Frame):

    INSTRUCTION_FONT = '20px'

    def __init__(self, root, *args, intro=None, **kwargs):
        super().__init__(root, *args, **kwargs)
        if intro is None:
            intro = self.__doc__
        self.intro = tk.Label(
            root,
            font=DialogFrame.INSTRUCTION_FONT,
            justify=tk.LEFT,
            text=intro
        )
        self.intro.grid(row=0, sticky=tk.N)

        tk.Label(root, text="URL:").grid(row=1, column=0, sticky=tk.W)
        self.url = ValidEntry(root, validator=url_valid)
        self.url.grid(row=1, column=1, columnspan=4, sticky=tk.E)

        tk.Label(root, text="User:").grid(row=2, column=0, sticky=tk.W)
        self.user = ValidEntry(root, validator=user_valid)
        self.user.grid(row=2, column=1, columnspan=4, sticky=tk.E)

        self.survey = tk.Button(root, command=self.survey, text="Survey")
        self.survey.grid(row=3, column=1)
        self.quit = tk.Button(root, text="Quit", command=root.destroy)
        self.quit.grid(row=3, column=3)

    def survey(self):
        try:
            text = self.user.get()
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

class MalojaGui(tk.Tk):

    TITLE_FONT = '25px'

    def __init__(self, *args, title="GUI", **kwargs):
        super().__init__(*args, **kwargs)
        self.grid(300, 120, 5, 5)
        self.resizable(False, False)
        self.title_label = tk.Label(self, font=self.TITLE_FONT, text=title)
        # self.title_label.grid()
        self.frame = DialogFrame(self)
        self.frame.grid(row=0, column=0)
        self.wm_title(title)
        self.update()
        self.geometry(self.geometry())

if __name__ == '__main__':
    app = MalojaGui(title="Maloja quick ops")
    app.mainloop()

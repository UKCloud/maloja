#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

# Copyright Skyscape Cloud Services
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font
import webbrowser

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

    """
    Not for advanced use.
    Please consult the documentation on how to operate
    the Maloja command line interface (CLI).

    """

    def __init__(self, root, *args, intro=None, **kwargs):
        super().__init__(root, *args, **kwargs)

        h1 = Font(family="Verdana", size=10, weight="normal")
        h2 = Font(family="Courier", size=12, weight="normal")
        h3 = Font(family="Helvetica", size=10, weight="bold")

        if intro is None:
            intro = self.__doc__
        self.intro = tk.Label(
            root,
            font=h1,
            justify=tk.LEFT,
            text=intro
        )
        self.intro.grid(row=0, column=0, columnspan=6)

        tk.Label(root, text="URL:", font=h2).grid(row=1, column=0, sticky=tk.E)
        self.url = ValidEntry(root, width=80, validator=url_valid)
        self.url.grid(row=1, column=1, columnspan=5)

        tk.Label(root, text="User:", font=h2).grid(row=2, column=0, sticky=tk.E)
        self.user = ValidEntry(root, width=80, validator=user_valid)
        self.user.grid(row=2, column=1, columnspan=5)

        self.survey = tk.Button(root, command=self.survey, text="Survey", font=h3)
        self.survey.grid(row=3, column=1)
        self.quit = tk.Button(root, text="Quit", command=root.destroy, font=h3)
        self.quit.grid(row=3, column=3)
        self.help = tk.Button(root, text="Help...", command=self.help, font=h3)
        self.help.grid(row=3, column=5)

    def help(self):
        webbrowser.open_new_tab("http://pythonhosted.org/maloja")

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
        self.resizable(False, False)
        self.title_label = tk.Label(self, font=self.TITLE_FONT, text=title)
        self.frame = DialogFrame(self, width=120, height=60)
        self.frame.grid()
        self.wm_title(title)
        self.update()
        self.geometry(self.geometry())

if __name__ == '__main__':
    app = MalojaGui(title="Maloja command panel")
    app.mainloop()

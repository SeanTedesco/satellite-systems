import tkinter as tk
from typing import Callable

class GUI:
    '''Provide basic wrappers for tkinter GUIs
    
    To use the class, first creat an instance of the GUI
    class, include widgets to your liking with the add-
    methods, then use the .run() method at the end.
    '''

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.widget_height = 5
        self.widget_width = 20


    def run(self):
        self.root.mainloop()

    def make_fullscreen(self):
        window_width = self.root.winfo_screenwidth()
        window_height = self.root.winfo_screenheight()
        self.root.geometry(f"{window_width}x{window_height}")

    def add_title(self, title_text:str):
        self.root.title(title_text)
    
    def add_label(self, label_text:str, row_col:tuple):
        label = tk.Label(self.root, 
                         text=label_text,
                         width=self.widget_width,
                         height=self.widget_height
                        )
        label.grid(row=row_col[0], column=row_col[1], sticky='W', pady=2)
        return label
    
    def add_button(self, button_text:str, row_col:tuple, button_function:Callable, **kwargs):
        button = tk.Button(self.root, 
                           text=button_text, 
                           command=lambda: button_function(**kwargs),
                         width=self.widget_width,
                         height=self.widget_height
                        )
        button.grid(row=row_col[0], column=row_col[1], sticky='W', pady=2)
        return button

    def add_entry(self, default_text:str, row_col:tuple):
        entry = tk.Entry(self.root, width=20)
        entry.insert(0, default_text)
        entry.grid(row=row_col[0], column=row_col[1], sticky='W', pady=2)
        return entry
    
    def add_text_box(self, row_col:tuple):
        text = tk.Text(self.root,
                        width=self.widget_width,
                        height=self.widget_height)
        text.grid(row=row_col[0], column=row_col[1], sticky='W', pady=2)
        return text
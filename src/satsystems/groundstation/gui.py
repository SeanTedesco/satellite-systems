import tkinter as tk
import yaml
from typing import Callable
from ..common.logger import SatelliteLogger

class GUI:
    '''Provide basic wrappers for tkinter GUIs
    
    To use the class, first creat an instance of the GUI
    class, set the config, include widgets to your liking
    with the add- methods, then use the .run() method at the end.
    '''

    def __init__(self) -> None:
        self.logger = SatelliteLogger.get_logger('ground_station')
        self.root = tk.Tk()
        self.widget_height = 0
        self.widget_width = 0
        self.paddingx = 0
        self.paddingy = 0
        self.font_style = 'Courier'
        self.large_font_size = 0
        self.medium_font_size = 0
        self.small_font_size = 0

    def set_config(self, config_file_path:str='./config/groundstation_config.yaml'):
        with open(config_file_path, "r") as stream:
            try:
                configs = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                raise exc
        gui_styles = configs.get("gui").items()
        for style, value in gui_styles:
            setattr(self, style, value)

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
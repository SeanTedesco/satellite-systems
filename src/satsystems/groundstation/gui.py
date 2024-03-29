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

    def add_frame(self, frame_title:str, row_col:tuple, frame=None):
        if frame is None:
            frame = self.root
        frame = tk.LabelFrame(frame,
                                text=frame_title
                            )
        frame.config(font=(self.font_style, self.large_font_size))
        frame.grid(row=row_col[0], column=row_col[1], columnspan=1, rowspan=1, sticky='NW', padx=self.paddingx, pady=self.paddingy)
        return frame
    
    def add_label(self, label_text:str, row_col:tuple, frame=None):
        if frame is None:
            frame = self.root
        label = tk.Label(frame,
                            text=label_text,
                            width=self.widget_width,
                            height=self.widget_height
                        )
        label.config(font=(self.font_style, self.large_font_size))
        label.grid(row=row_col[0], column=row_col[1], sticky='W', padx=self.paddingx, pady=self.paddingy)
        return label
    
    def add_button(self, button_text:str, row_col:tuple, button_function:Callable, function_kwargs={}, frame=None):
        if frame is None:
            frame = self.root
        button = tk.Button(frame,
                            text=button_text, 
                            command=lambda: button_function(**function_kwargs),
                            width=self.widget_width,
                            height=self.widget_height
                        )
        button.config(font=(self.font_style, self.medium_font_size))
        button.grid(row=row_col[0], column=row_col[1], sticky='W', padx=self.paddingx, pady=self.paddingy)
        return button

    def add_entry(self, default_text:str, row_col:tuple, frame=None):
        if frame is None:
            frame = self.root
        entry = tk.Entry(frame, 
                            width=20
                        )
        entry.insert(0, default_text)
        entry.config(font=(self.font_style, self.medium_font_size))
        entry.grid(row=row_col[0], column=row_col[1], sticky='W', padx=self.paddingx, pady=self.paddingy)
        return entry
    
    def add_text_box(self, row_col:tuple, frame=None):
        if frame is None:
            frame = self.root
        text = tk.Text(frame,
                        width=self.widget_width,
                        height=self.widget_height
                    )
        text.config(font=(self.font_style, self.medium_font_size))
        text.grid(row=row_col[0], column=row_col[1], rowspan=2, sticky='W', padx=self.paddingx, pady=self.paddingy)
        return text
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import customtkinter as ctk

from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog

font_default = ("Arial",16)
COLORS = ['blue','purple','brown']
COLOR_DICT = {'blue': 'tab:blue',
              'brown': 'tab:brown',
              'purple': 'tab:purple'}

def generate_timeline_plot(df, figsize=(10,5)):
    df = df[::-1].reset_index(drop=True)
    xmax = np.max(df['End'])
    ymax = len(df)
    
    fig, ax = plt.subplots(layout='constrained',figsize=figsize)
    
    for i,row in df.iterrows():
        if row['End'] != 0:
            ax.add_patch(Rectangle(
                (row['Start'], i),
                row['End'] - row['Start'] + 1,
                1,
                color=row['Color']
            ))

    [ax.axvline(i,c='gray',linestyle='-',linewidth=1) for i in range(2,xmax+1)]
    [ax.axhline(i,c='gray',linestyle='-',linewidth=1) for i in range(1,ymax)]
    
    ax.set_xlim([1,xmax+1])
    ax.set_ylim([0,ymax])
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xticks(range(1,xmax+2))
    ax.set_yticks(np.array(range(0,ymax))+0.5)
    ax.set_yticklabels(df.loc[:,'Name'])
    ax.set_xlabel('Month')
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax.xaxis.set_label_position('top')

    for tick, (_, row) in zip(ax.get_yticklabels(), df.iterrows()):
        if row.get('Highlight', False):
           tick.set_bbox(dict(
                facecolor='yellow',
                edgecolor='none',
                boxstyle='round,pad=0.3'
            ))
        else:
            tick.set_bbox(dict(
                facecolor='none',
                edgecolor='none'
            ))

    return fig

class TimelineChart:
    def __init__(self, frame):
        self.frame = frame
        self.canvas = None 
        self.fig = None
        
    def plot(self, df, figsize=(10,5)):
        self.fig = generate_timeline_plot(df, figsize)
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew")
    
    def save(self):
        if self.fig is None:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")]
        )
        if filepath:
            self.fig.savefig(filepath, bbox_inches="tight")
            
class MyTabView(ctk.CTkTabview):
    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app=app
        self.df = None
        self.color_vars = []  # holds the color selection per row
        self.color_widgets_frame = None
        
        # create tabs
        self.add("Instructions").grid_columnconfigure(0, weight=1)
        self.add("Make Timeline Chart").grid_columnconfigure(0, weight=1)

        # add widgets on tabs
        self.label1 = ctk.CTkLabel(
            master=self.tab("Instructions"),
            text='Hello! This tool is made to create a Gantt chart from an Excel sheet template (.xlsx). The template needs to have 3 columns titled "Name", "Start", and "End" and be on sheet 1 of the Excel file. Values are inclusive. For entries without a bar, place a 0 in the "End" column.',
            wraplength=600,
            justify='left',
            anchor='w', 
            font=font_default
        )
        self.label1.grid(row=0, column=0, padx=20, pady=10)

        test_df = pd.DataFrame(
            {
                "Name": ['Task 1', 'Task 2', 'Task 3'],
                "Start": [1, 0, 3],
                "End": [4, 0, 3],
                "Color":['tab:blue']*3,
                "Highlight": [False]*3
            }
        )
        
        self.textbox1 = ctk.CTkTextbox(
            master=self.tab('Instructions'), 
            font=font_default,
            width=170,
            height=110
        )
        self.textbox1.insert("0.0",test_df.iloc[:,:3].to_string(index=False))
        self.textbox1.configure(state='disabled')
        self.textbox1.grid(row=1, column=0, padx=20, pady=10)

        chart_frame = ctk.CTkFrame(self.tab('Instructions'))
        chart_frame.grid(row=2, column=0, sticky="nsew")
        canvas1 = TimelineChart(chart_frame)
        canvas1.plot(test_df,(5,3))
        
        upload_button = ctk.CTkButton(self.tab("Make Timeline Chart"), text="Upload File", command=self.upload_file, font=font_default)
        upload_button.grid(row=0, column=0, padx=20, pady=10)

        timelinechart_frame = ctk.CTkFrame(self.tab("Make Timeline Chart"))
        timelinechart_frame.grid(row=1, column=0, sticky="nsew")
        self.timeline_chart = TimelineChart(timelinechart_frame)

        save_button = ctk.CTkButton(self.tab("Make Timeline Chart"), text="Save Chart", command=self.timeline_chart.save, font=font_default)
        save_button.grid(row=2, column=0, padx=20, pady=10)
    
    def upload_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")]
        )
        
        if filepath:
            self.df = pd.read_excel(filepath, engine='openpyxl')
            self.df['Color'] = 'tab:blue'
            self.df['Highlight'] = False
            self.build_color_pickers()
            new_fig = self.timeline_chart.plot(self.df)

            if self.app:
                self.app.update_idletasks()
                new_height = self.app.winfo_reqheight()
                new_width = self.app.winfo_reqwidth()
                self.app.geometry(f"{new_width}x{new_height}")

    def build_color_pickers(self):
        # clear old color pickers if they exist
        if self.color_widgets_frame:
            self.color_widgets_frame.destroy()

        self.color_widgets_frame = ctk.CTkScrollableFrame(
            self.tab("Make Timeline Chart"), 
            height=150
        )
        self.color_widgets_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        self.color_vars = []
        self.highlight_vars = []

         # column headers
        ctk.CTkLabel(self.color_widgets_frame, text="Name", font=font_default).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(self.color_widgets_frame, text="Color", font=font_default).grid(row=0, column=1, padx=10)
        ctk.CTkLabel(self.color_widgets_frame, text="Highlight", font=font_default).grid(row=0, column=2, padx=10)

        
        for i, row in self.df.iterrows():
            if row['End'] != 0:        
                label = ctk.CTkLabel(
                    self.color_widgets_frame, 
                    text=row['Name'], 
                    font=font_default,
                    width=150,
                    anchor="w"
                )
                label.grid(row=i+1, column=0, padx=10, pady=2, sticky="w")
    
                var = ctk.StringVar(value='blue')
                self.color_vars.append((i, var))
    
                dropdown = ctk.CTkComboBox(
                    self.color_widgets_frame,
                    values=COLORS,
                    variable=var,
                    font=font_default,
                    command=lambda val, idx=i: self.update_color(idx, COLOR_DICT[val])
                )
                dropdown.grid(row=i+1, column=1, padx=10, pady=2)

                highlight_var = ctk.BooleanVar(value=False)
                self.highlight_vars.append((i, highlight_var))
                ctk.CTkCheckBox(
                    self.color_widgets_frame,
                    text="",
                    variable=highlight_var,
                    command=lambda idx=i: self.update_highlight(idx)
                ).grid(row=i+1, column=2, padx=10, pady=2)

    def update_color(self, row_idx, color):
        self.df.at[row_idx, 'Color'] = color
        self.timeline_chart.plot(self.df)

    def update_highlight(self, row_idx):
        for idx, var in self.highlight_vars:
            self.df.at[idx, 'Highlight'] = var.get()
        self.timeline_chart.plot(self.df)
    
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.tab_view = MyTabView(master=self, app=self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20)
        self.title("Your App")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    def on_close(self):
        plt.close('all')  # close all matplotlib figures
        self.quit()
        self.destroy()

if __name__ == "__main__":
        
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
    
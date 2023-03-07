import os
import threading
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import PhotoImage
from tkinter import filedialog
from tkinter import messagebox

from miner import PDFMiner

import pyttsx3

cwd = os.getcwd()
engine = pyttsx3.init()
volume = engine.getProperty('volume')
engine.setProperty('volume', volume-0.12)
voices = engine.getProperty('voices')
engine.setProperty('voices', voices[0].id)
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-30)

class Application(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master=master)
        self.master = master
        self.grid()

        self.fileisopen = False
        self.path = None
        self.speaker_on = False
        self.author = None
        self.name = None
        self.current_page = 0
        self.numPages = None

        self.draw_frames()
        self.draw_display_frame()
        self.draw_control_frame()

        self.master.bind('<Enter>', self.search_page)
        self.master.bind('<Up>', self.prev_page)
        self.master.bind('<Down>', self.next_page)

    def draw_frames(self):
        self.display_frame = tk.Frame(self, width=400, height=400, bg='gray18' )
        self.display_frame.grid(row=0, column=0)
        self.display_frame.grid_propagate(False)

        self.controls_frame = tk.Frame(self, width=400, height=50, bg='#252525' )
        self.controls_frame.grid(row=1, column=0)
        self.controls_frame.grid_propagate(False)

    def draw_display_frame(self):
        self.scrolly = tk.Scrollbar(self.display_frame, orient=tk.VERTICAL)
        self.scrolly.grid(row=0, column=1, sticky='ns')

        self.scrollx = tk.Scrollbar(self.display_frame, orient=tk.HORIZONTAL)
        self.scrollx.grid(row=1, column=0, sticky='we')

        self.output = tk.Canvas (self.display_frame, bg='gray18')
        self.output.configure( width=380, height=380, yscrollcommand=self.scrolly.set,
                                    xscrollcommand=self.scrollx.set )
        self.output.grid(row=0 , column=0)

        self.scrolly.configure(command=self.output.yview)
        self.scrollx.configure(command=self.output.xview)

    def draw_control_frame(self):
        self.open_file_btn = ttk.Button(self.controls_frame, text='Open File', width=10, command=self.open_file)
        self.open_file_btn.grid(row=0, column=0, padx=5, pady=10)

        self.up_btn = tk.Button(self.controls_frame, image=up_icon, bg='#252525', relief=tk.FLAT, command=self.prev_page)
        self.up_btn.grid(row=0, column=1, padx=(70,5), pady=8)

        self.pagevar = tk.StringVar()
        self.entry = ttk.Entry(self.controls_frame, textvariable=self.pagevar, width=4)
        self.entry.grid(row=0, column=2, pady=5)

        self.down_btn = tk.Button(self.controls_frame, image=down_icon, bg='#252525', relief=tk.FLAT, command=self.next_page)
        self.down_btn.grid(row=0, column=3, pady=8)

        self.speak_btn = tk.Button(self.controls_frame, image=speakoff_icon, bg='#252525', relief=tk.FLAT, command=self.speak_toggle)
        self.speak_btn.grid(row=0, column=4, padx=(55,5), pady=8)

        self.page_label = tk.Label(self.controls_frame, text='', bg='#252525', fg='white', font=('Papyrus', 12, 'bold'))
        self.page_label.grid(row=0, column=5)

    def open_file(self):
        temppath = filedialog.askopenfilename(initialdir=cwd, filetypes=(("PDF","*.pdf"),))
        if temppath:
            #print(temppath)
            self.path = temppath
            filename = os.path.basename(self.path)
            self.miner = PDFMiner(filename)    
            data, numPages = self.miner.get_metadata()
            self.current_page = 0
            if numPages:
                self.name = data.get('title', filename[:-4])
                self.author = data.get('author', None)
                self.numPages = numPages

                self.fileisopen = True
                self.display_page()
                self.update_idletasks()
                print(self.name, self.author)
            else:
                self.fileisopen = False
                messagebox.showerror('PDF AudioBook', 'Cannot read file')

    def display_page(self):
        if 0 <= self.current_page < self.numPages: 
            self.img_file = self.miner.get_page(self.current_page)
            self.output.create_image(0, 0, anchor='nw', image=self.img_file)
            self.page_label['text'] = self.current_page + 1

            region = self.output.bbox(tk.ALL)
            self.output.configure(scrollregion=region)

            if self.speaker_on:
                self.speak()

    def prev_page(self, event=None):
        if self.fileisopen:
            if self.speaker_on:
                engine.endLoop()
            if self.current_page > 0:
                self.current_page -= 1
                self.display_page()

    def next_page(self, event=None):
        if self.fileisopen:
            if self.speaker_on:
                engine.endLoop()
            if self.current_page <= self.numPages - 1:
                self.current_page += 1
                self.display_page()

    def search_page(self, event=None):
        if self.fileisopen:
            page = self.pagevar.get()
            if page and page != ' ':
                page = int(self.pagevar.get())
                if 0 < page < self.numPages + 1:
                    if page == 0:
                        page = 1
                    else:
                        page -= 1
                    
                    self.current_page = page
                    if self.speaker_on:
                        engine.endLoop()
                    self.display_page()
                    self.pagevar.set('')

    def speak_toggle(self, event=None):
        if not self.speaker_on:
            self.speaker_on = True
            self.speak_btn['image'] = speakon_icon

            self.speak()
        else:
            self.speaker_on = False
            self.speak_btn['image'] = speakoff_icon
            engine.endLoop()

    def speak(self):
        if self.fileisopen:
            if self.speaker_on:
                text = self.miner.getText(self.current_page)
                thread = threading.Thread(target=self.read, args=(text,), daemon=True)
                thread.start()
                self.poll_thread(thread)

    def poll_thread(self, thread):
        if thread.is_alive():
            self.after(100, lambda : self.poll_thread(thread))
        else:
            pass


    def read(self, text):
        engine.say(text)
        engine.startLoop()




if __name__ == '__main__':
    root=tk.Tk()
    root.geometry('400x450+400+170')
    root.title('My AudioBook')
    root.resizable(0,0)

    up_icon = PhotoImage(file = 'icons/up.png')
    down_icon = PhotoImage(file = 'icons/down.png')
    speakon_icon = PhotoImage(file = 'icons/speaker.png')
    speakoff_icon = PhotoImage(file = 'icons/mute.png')

    app=Application(master=root)
    app.mainloop()
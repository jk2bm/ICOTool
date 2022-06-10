from asyncio.tasks import ALL_COMPLETED
import pathlib
from PIL import Image,ImageTk
import tkinter as tk
from tkinter import ttk,Radiobutton,StringVar,OptionMenu,Button,Label,LabelFrame,Menu,messagebox
from tkinter import filedialog
from pathlib import Path
from configparser import ConfigParser
import os
import subprocess
import time
import asyncio
from asyncio import FIRST_COMPLETED

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    pass

config=ConfigParser()

def load_config(data_loc):
    config_loc=data_loc+"config.ini"
    win_size="358x335"
    icon_size="64x64"
    output_path="Output/"
    if os.path.isfile(config_loc):
        try:
            config.read(config_loc)
            win_size=config.get("DEFAULT","win_size")
            icon_size=config.get("DEFAULT","icon_size")
            output_path=config.get("DEFAULT","output_path")
        except:
            pass
    else:
        config["DEFAULT"]={"win_size":win_size,
                           "icon_size":icon_size,
                           "output_path":output_path}
        config.write(open(config_loc,"w+"))
    return win_size,icon_size,output_path

class ico_converter(object):
    def __init__(self,**kwargs):
        self.win=tk.Tk()
        self.win.title("ICOTool [build "+kwargs.get("version")+"]")
        self.version=kwargs.get("version")
        self.win.option_add("*Font","20")
        self.data_loc=kwargs.get("data_loc")
        self.win_size=kwargs.get("win_size")
        self.icon_size=kwargs.get("icon_size")
        self.output_path=kwargs.get("output_path")
        self.win.geometry(self.win_size)
        self.win.minsize(self.win_size.split("x")[0],self.win_size.split("x")[1])
        self.win.maxsize(self.win_size.split("x")[0],self.win_size.split("x")[1])
        self.options_image_size=["16x16","24x24","32x32","48x48","64x64","128x128","256x256"]

    def dummy():
        pass

    def missing_data(self):
        messagebox.showwarning(title="Error",message="Data folder is missing or corrupt!")
        self.win.quit()
        exit()

    def load_data(self):
        try:
            self.win.iconbitmap(default=self.data_loc+"app.ico")
            self.image_check=ImageTk.PhotoImage(Image.open(self.data_loc+"Check.png"))
            self.image_cancel=ImageTk.PhotoImage(Image.open(self.data_loc+"Cancel.png"))
        except:
            self.missing_data()

    async def save_ico(self,image,image_info,sizes,filename):
        await(self.progress_step())
        try:
            if os.path.isdir(self.output_path)==False:
                os.mkdir(self.output_path)
        except:
            pass
        width=image.width
        height=image.height
        if width/height!=1:
            long_side=width if width>height else height
            background=Image.new("RGBA",(long_side,long_side),(0,0,0,0))
            offset=(int(round((long_side-width)/2,0)),int(round((long_side-height)/2,0)))
            background.paste(image,offset)
            image=background
        image=image.resize(sizes)
        image.save(self.output_path+filename+".ico",format="ICO",bitmap_format="bmp",**image_info)
        self.file.close()

    async def progress_step(self):
        self.status["text"]="Working..."
        """
        self.progress["value"]+=10
        time.sleep(0.00001)
        """
        self.win.update_idletasks()

    def convert(self):
        if self.file:
            filename=Path(self.file.name).stem
            data = self.file.read()
            image=Image.open(self.file)
            image_info=image.info
            image_size=image.size
            print(image_size)

            sizes=tuple([int(size) for size in self.selection.get().split("x")])
            i=self.options_image_size.index(self.selection.get())
            while any(x<y for x,y in zip(image_size,sizes)):
                if i>=1:
                    i-=1
                    sizes=tuple([int(size) for size in self.options_image_size[i].split("x")])
                else:
                    messagebox.showwarning(title="Error",message="This Image is too small!")
                    self.win.quit()
                    exit()

            config["DEFAULT"]={"win_size":self.win_size,
                               "icon_size":self.selection.get(),
                               "output_path":self.output_path}
            config.write(open(self.data_loc+"config.ini","w+"))

            print(sizes)

            self.loop=asyncio.get_event_loop()
            task=[asyncio.ensure_future(self.progress_step()),
                  asyncio.ensure_future(self.save_ico(image,image_info,sizes,filename))]
            self.loop.run_until_complete(asyncio.wait(task,return_when=ALL_COMPLETED))
            self.clear_image()
            if len(filename)>30:
                filename=filename[:30]+"(...)"
            self.status["text"]="Saved to "+filename+".ico"
        else:
            pass

    def exit(self):
        self.win.quit()
        exit()

    def open_folder(self):
        print(os.path)
        subprocess.Popen('explorer /select,""')

    def about(self):
        messagebox.showwarning(title="About",message="ICOTool [build "+self.version+"]")

    def create_menu(self):
        menubar=Menu(self.win)
        filemenu=Menu(menubar,tearoff=0)
        filemenu.add_command(label="Open New...",command=self.on_load)
        filemenu.add_command(label="Open Folder",command=self.open_folder)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=self.exit)
        #filemenu.add_command(label="Open",command=open_file)
        menubar.add_cascade(label="File",menu=filemenu)
        helpmenu=Menu(menubar,tearoff=0)
        helpmenu.add_command(label="About",command=self.about)
        menubar.add_cascade(label="Help",menu=helpmenu)
        self.win.config(menu=menubar)

    def create_grid(self):
        self.selection=StringVar()
        self.selection.set(self.icon_size)
        self.preview=LabelFrame(self.win,text="Preview")
        self.preview.grid(row=0,column=0,sticky="wens")
        try:
            self.label=Label(self.preview,image=ImageTk.PhotoImage(Image.open("ICOTool_Data/blank.png")))
            self.label.pack(anchor="center",expand=1)
        except:
            self.missing_data()
        self.sizeGroup=LabelFrame(self.win,text="Size")
        self.sizeGroup.grid(row=0,column=1,sticky="wens")
        for option in self.options_image_size:
            Radiobutton(self.sizeGroup,text=option,variable=self.selection,value=option).pack(anchor="w")
        self.sep=ttk.Separator(self.win,orient="horizontal").grid(row=1,columnspan=2,sticky="ew")
        self.button_check=Button(self.win,text="Create ICO!",command=self.convert,image=self.image_check,compound="left").grid(row=2,column=0,columnspan=1,sticky="wens")
        self.button_cancel=Button(self.win,text="Cancel",command=self.clear_image,image=self.image_cancel,compound="left").grid(row=2,column=1,columnspan=1,sticky="wens")
        #self.progress=ttk.Progressbar(self.win,orient="horizontal",length=100,mode="determinate")
        #self.progress.grid(row=3,columnspan=2,sticky="wens")
        self.status=Label(self.win,text="Ready",bd=1,relief="sunken",anchor="w")
        self.status.grid(row=3,columnspan=2,stick="wens")

    def on_load(self):
        self.file=filedialog.askopenfile(parent=self.win,mode='rb',title='Choose an image file')
        self.status["text"]="Ready"
        self.refresh_preview()

    def clear_image(self):
        self.file=None
        self.label.destroy()
        self.win.update_idletasks()

    def refresh_preview(self):
        if self.file:
            self.label.destroy()
            try:
                image=Image.open(self.file)
            except:
                tk.messagebox.showwarning(title="Error",message="Invalid image file!")
                return
            width=image.width
            height=image.height
            if width/height!=1:
                long_side=width if width>height else height
                background=Image.new("RGBA",(long_side,long_side),(0,0,0,0))
                offset=(int(round((long_side-width)/2,0)),int(round((long_side-height)/2,0)))
                background.paste(image,offset)
                image=background
            self.image=ImageTk.PhotoImage(image.resize(size=(256,256)))
            self.label=Label(self.preview,image=self.image)
            self.label.pack(anchor="w")
        self.win.mainloop()

    def collectAndRun(self,**kwargs):
        self.load_data()
        self.create_menu()
        self.create_grid()
        self.on_load()
        self.win.mainloop()

data_loc="ICOTool_Data/"
win_size,icon_size,output_path=load_config(data_loc)
hello=ico_converter(version="0.5.2.1",win_size=win_size,icon_size=icon_size,data_loc=data_loc,output_path=output_path)
hello.collectAndRun()
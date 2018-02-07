#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  
from __future__ import print_function

import os
import sys
import argparse
import dataparse
import tempfile
import shutil
import json

from PIL import Image

usage = """
%(prog)s ../btn.plist
%(prog)s ../btn.plist -i ../btn.png
%(prog)s ../data
%(prog)s ../data -r
"""

pvr_file_ext = (".pvr", ".pvr.gz", ".pvr.ccz")
support_file_ext = (".png", ".jpg", ) + pvr_file_ext

logger = None


def log(text):
    if logger:
        logger(text)
    else:
        print(text)    

def get_image_ext(image_file):
    for ext in pvr_file_ext:
        if image_file.endswith(ext):
            return ext
    return os.path.splitext(image_file)[1]

def convert_pvr_to_png(image_file):
    temp_dir = tempfile.mkdtemp()

    shutil.copyfile(image_file, os.path.join(temp_dir, os.path.basename(image_file)))
    image_path = os.path.join(temp_dir, "temp.png")
    plist_path = os.path.join(temp_dir, "temp.plist")

    if os.system("TexturePacker {temp_dir} --sheet {image_path} --texture-format png --border-padding 0 --shape-padding 0 --disable-rotation --allow-free-size --no-trim --data {plist_path}".format(temp_dir = temp_dir, image_path = image_path, plist_path = plist_path)) == 0:
        return image_path

    return None

def unpacker(data_file, image_file=None, output_dir=None, config=None, extra_data_receiver=None):
    # parse file
    data = dataparse.parse_file(data_file, config, extra_data_receiver)
    frame_data_list = data.get("frames") if data else None
    if not data or not frame_data_list:
        log("fail: unknown file type:" + data_file)
        return -1

    # check imagefile
    if not image_file:
        file_path,_ = os.path.split(data_file)
        image_file = os.path.join(file_path , data["texture"])

    # check image format
    image_ext = get_image_ext(image_file)
    if image_ext in pvr_file_ext:
        new_image_file = convert_pvr_to_png(image_file)
        if new_image_file:
            image_file = new_image_file
        else:
            log("fail: can't convert pvr to png, are you sure installed TexturePacker command line tools ? More infomation:\nhttps://www.codeandweb.com/texturepacker/documentation#install-command-line")
            return -1

    # create output dir
    if not output_dir:
        output_dir,_ = os.path.splitext(data_file)
    if not os.path.isdir(output_dir):
        if os.path.exists(os.path.dirname(output_dir)):
            os.mkdir(output_dir)
        else:
            os.makedirs(output_dir)

    try:
        src_image = Image.open(image_file)
    except Exception:
        log("fail: can't open image %s " %image_file)
        return -1

    for frame_data in frame_data_list:
        temp_image = src_image.crop(frame_data["src_rect"])
        if frame_data["rotated"]:
            temp_image = temp_image.rotate(90, expand=1)

        # create dst image
        mode = "RGBA" if (src_image.mode in ('RGBA', 'LA') or (src_image.mode == 'P' and 'transparency' in src_image.info)) else "RGB"
        dst_image = Image.new(mode, frame_data["source_size"], (0,0,0,0))
        dst_image.paste(temp_image, frame_data["offset"], mask=0)

        output_path = os.path.join(output_dir, frame_data["name"])
        pre,ext = os.path.splitext(output_path)
        if not ext:
            output_path = output_path + "." + image_ext
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        dst_image.save(output_path)

    log("success:" + data_file)
    return 0

# Get the all files & directories in the specified directory (path).
def unpacker_dir(path, recursive, output_dir=None, output=None):
    if output == None:
        output = list()

    for name in os.listdir(path):
        full_name = os.path.join(path, name)
        pre,ext = os.path.splitext(name)
        if ext in ('.plist', ".fnt"):
            output.append(full_name)
            unpacker(full_name, output_dir=os.path.join(output_dir, pre) if output_dir else None)
        elif recursive and os.path.isdir(full_name):
            unpacker_dir(full_name, recursive, os.path.join(output_dir, name) if output_dir else None, output)

    return output
    
def gui():
    try:
        import Tkinter as tk
        import ttk
        import tkFileDialog
    except Exception:
        import tkinter as tk
        import tkinter.ttk as ttk
        import tkinter.filedialog as tkFileDialog
        

    class Application(tk.Frame):
        def __init__(self, root=None):
            tk.Frame.__init__(self, root)
            self.root = root
            self.last_path = None
            root.title("untp")
            self.pack(fill="both", expand=True)
            self.createWidgets()
            self.center()

        def createWidgets(self):

            frame = tk.Frame(self)
            for row in range(0, 2):
                tk.Grid.rowconfigure(frame, row, weight=1)
            for col in range(0, 2):
                tk.Grid.columnconfigure(frame, col, weight=1)
            tk.Button(frame, width=20, text="Unpack Files", command=self.select_file).grid(row=0, column=0, sticky=("N", "S", "E", "W"))
            tk.Button(frame, width=20, text="Unpack Directory", command=self.select_directory).grid(row=0, column=1, sticky=("N", "S", "E", "W"))
            self.recursive_var = tk.IntVar(0)
            self.recursive_var.set(1)
            tk.Checkbutton(frame, text="Recursive", variable=self.recursive_var).grid(row=1, column=1, sticky=tk.W)
            frame.pack(fill="x")

            ttk.Separator(self).pack(fill="x")

            frame = tk.Frame(self)
            scrollbar = tk.Scrollbar(frame) 
            self.logger = tk.Text(frame, width=0, height=5, wrap="word", yscrollcommand=scrollbar.set, borderwidth=0, highlightthickness=0)
            self.logger.bind("<1>", lambda event: self.logger.focus_set())
            scrollbar.config(command=self.logger.yview)
            self.logger.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            frame.pack(fill="both", expand=True)

        def log(self, text):
            self.logger.config(state='normal')
            self.logger.insert(tk.END, text + '\n')
            self.logger.see(tk.END)  # Scroll to the bottom
            self.logger.config(state='disabled')

        def center(self):
            self.root.update_idletasks()
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight()
            size = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
            x = w/2 - size[0]/2
            y = h/2 - size[1]/2
            self.root.geometry("%dx%d+%d+%d" % (size + (x, y)))            

        def select_directory(self):
            path =tkFileDialog.askdirectory()
            if not path:
                return
            self.last_path = path
            unpacker_dir(path, self.recursive_var.get() == 1)

        def select_file(self):
            path = tkFileDialog.askopenfilenames(initialdir=self.last_path)
            file_list = self.root.tk.splitlist(path)
            if not file_list:
                return
            
            self.last_path = os.path.dirname(file_list[0])

            for v in file_list:
                if v.endswith(".plist"):
                    pre,_ = os.path.splitext(v)
                    image_file = None
                    for ext in support_file_ext:
                        if (pre + ext) in file_list:
                            image_file = pre + ext

                    unpacker(v, image_file = image_file)

    root = tk.Tk()
    app = Application(root)

    global logger
    logger = app.log    

    from os import system
    from platform import system as platform
    if platform() == 'Darwin':  # How Mac OS X is identified by Python
        system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

    app.mainloop()
    try:
        root.destroy()
    except Exception:
        pass

def main():

    parser = argparse.ArgumentParser(prog="untp", usage=usage)
    parser.add_argument("path", type=str, help="plist/fnt file name or directory")
    parser.add_argument("-o", "--output", type=str, metavar="output", help="specified output directory")

    group_file = parser.add_argument_group('For file')
    group_file.add_argument("-i", "--image_file", type=str, metavar="image_file", help="specified image file for plist")

    group_dir = parser.add_argument_group('For directory')
    group_dir.add_argument("-r", "--recursive", action="store_true", default=False)

    if len(sys.argv) > 1:
        argument = parser.parse_args()

        if os.path.isdir(argument.path):
            return unpacker_dir(argument.path, argument.recursive, output_dir = argument.output)
        elif os.path.isfile(argument.path):
            return unpacker(argument.path, image_file = argument.image_file, output_dir = argument.output)
    else:
        gui()

if __name__ == '__main__':
    main()
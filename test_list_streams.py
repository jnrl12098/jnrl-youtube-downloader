# test displaying list of available streams of the YouTube object
# stream: a video or audio track of the YouTube object
from tkinter import *
from pytube import YouTube
from time import *

yt: YouTube
tag_list: list[int] = []

def display_streams(video_url):
    global yt, tag_list
    item: StringVar
    yt = YouTube(url = video_url)

    for i in yt.streams.filter():
        print(i)
    
    tag_list.clear()
    options_listbox.delete(0, END)
    for stream in yt.streams.filter():
        if stream.type == "video":
            item = stream.type + " - " + stream.resolution + str(stream.fps) + " - " + stream.subtype + " (" + convertBytes(stream.filesize) + ")"
            if stream.is_adaptive:
                item += " (no audio)"
        elif stream.type == "audio":
            item = stream.type + " - " + stream.abr + " - " + stream.subtype + " (" + convertBytes(stream.filesize) + ")"
        options_listbox.insert(END, item)
        tag_list.append(stream.itag)

    options_frame.pack()

def choose_stream():
    global yt
    print(tag_list[options_listbox.curselection()[0]])
    # stream = yt.streams.get_by_itag(tag_list[options_listbox.curselection()[0]])
    # stream.download()

def convertBytes(bytes: int) -> str:
    if bytes < 1024:
        return "{i} B".format(bytes)
    elif bytes < (1024*1024):
        return "{:.2f} KB".format(bytes/1024)
    elif bytes < (1024*1024*1024):
        return "{:.2f} MB".format(bytes/1024/1024)
    else:
        return "{:.2f} GB".format(bytes/1024/1024/1024) # assuming video sizes don't get into terabyte territory
    
mainWindow = Tk()

url_entrybox = Entry(mainWindow)
display_button = Button(mainWindow, text = "Display Options", command = lambda: display_streams(url_entrybox.get()))

options_frame = Frame(mainWindow)
options_label = Label(options_frame, text = "Options:")
filter_button = Button(options_frame, text = "Choose Stream", command = choose_stream)
options_listbox = Listbox(options_frame, width = 50)

options_label.grid(row = 0, column = 0)
filter_button.grid(row = 0, column = 1)
options_listbox.grid(row = 1, column = 0, columnspan = 2)

url_entrybox.pack()
display_button.pack()

mainWindow.mainloop()

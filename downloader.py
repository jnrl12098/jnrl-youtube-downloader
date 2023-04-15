from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from pytube import YouTube
from time import *
import threading
import urllib.request
import io
from PIL import Image, ImageTk

yt: YouTube = None
max_file_size: int = None
photoimage_holder: PhotoImage = None
tag_list: list[int] = []

def on_progress(stream, chunk, bytes_remaining):
    global max_file_size
    bytes_downloaded: int = max_file_size - bytes_remaining
    percent_downloaded: float = bytes_downloaded / max_file_size
    downloadProgressBar["value"] = percent_downloaded * 100
    mainWindow.update_idletasks()
    print(convertBytes(bytes_downloaded) + " downloaded") # for debugging

def on_complete(stream, path):
    messagebox.showinfo("Information", "Download complete.")
    downloadButton['state'] = NORMAL

def searchVideo(videoURL):
    global yt
    yt = YouTube(videoURL, on_progress_callback = on_progress, on_complete_callback = on_complete)
    video_length: StringVar
    video_views: StringVar

    if downloadProgressBar["value"] != 0:
        downloadProgressBar["value"] = 0
    searchButton["state"] = DISABLED  
        
    display_streams_thread = threading.Thread(target = display_streams, args = (yt,))
    display_streams_thread.start()          
    
    display_image_thread = threading.Thread(target = display_image, args = (yt.thumbnail_url,)) # (x, ) to emphasize that x is one argument and not a list of individual characters
    display_image_thread.start()
    if yt.length < 3600:   
        video_length = "Length: " + strftime("%M:%S", gmtime(yt.length)) # gmtime converts the int yt.length into a tuple to be used for strftime
    else:        
        video_length = "Length: " + strftime("%H:%M:%S", gmtime(yt.length))    
    if yt.views < 1000:
        video_views = f"{yt.views} views"
    elif yt.views < 1000*10:
        video_views = f"{yt.views/1000: .1f}K views"
    elif yt.views < 1000*1000:
        video_views = f"{int(yt.views/1000)}K views"
    elif yt.views < 1000*1000*10:
        video_views = f"{yt.views/1000/1000: .1f}M views"
    else:
        video_views = f"{int(yt.views/1000/1000)} M views"
    title_label.configure(text = yt.title)
    time_label.configure(text = video_length)
    channel_label.configure(text = yt.author)
    views_label.configure(text = video_views)
    date_label.configure(text = "Published on: " + yt.publish_date.strftime("%b %m, %Y"))
    details_frame.grid()

def display_image(thumbnail_url):
    global photoimage_holder
    with urllib.request.urlopen(thumbnail_url) as image_url:
        thumbnail_data = image_url.read()
        thumbnail_bytes = io.BytesIO(thumbnail_data)
        with Image.open(thumbnail_bytes) as thumbnail_image:
            effective_image = thumbnail_image.resize((240, 180))
            thumbnail_photoimage = ImageTk.PhotoImage(effective_image)
            thumbnail_box.configure(image = thumbnail_photoimage)
    # keep a reference to PhotoImage object so that it appears properly
    photoimage_holder = thumbnail_photoimage
    searchButton["state"] = NORMAL

def display_streams(yt_object):
    global tag_list
    item: StringVar
    tag_list.clear()
    options_listbox.delete(0, END)
    for stream in yt_object.streams.filter():
        print(stream) # for debugging; to check if tag_list and listbox match
        if stream.type == "video":
            item = stream.type + " - " + stream.resolution + str(stream.fps) + " - " + stream.subtype + " (" + convertBytes(stream.filesize) + ")"
            if stream.is_adaptive:
                item += " (no audio)"
        elif stream.type == "audio":
            item = stream.type + " - " + stream.abr + " - " + stream.subtype + " (" + convertBytes(stream.filesize) + ")"
        options_listbox.insert(END, item)
        tag_list.append(stream.itag)
    options_frame.grid()
    searchButton["state"] = NORMAL

def advanced_options():
    print("You pressed the advanced options button.")

def downloadVideo():
    global yt, max_file_size    
    downloadButton['state'] = DISABLED
    print(tag_list[options_listbox.curselection()[0]]) # for debugging; to check if tag_list and listbox match
    stream = yt.streams.get_by_itag(tag_list[options_listbox.curselection()[0]])
    max_file_size = stream.filesize
    x = threading.Thread(target = stream.download, daemon = True)
    x.start()

# UTILITY FUNCTIONS
# convert bytes to KB/MB/GB for better readability
def convertBytes(bytes: int) -> str:
    if bytes < 1024:
        return "{i} B".format(bytes)
    elif bytes < (1024*1024):
        return "{:.2f} KB".format(bytes/1024)
    elif bytes < (1024*1024*1024):
        return "{:.2f} MB".format(bytes/1024/1024)
    else:
        return "{:.2f} GB".format(bytes/1024/1024/1024)
# show threads for debugging 
def showThreads():
    print(threading.active_count())
    print(threading.enumerate())

mainWindow = Tk()

urlLabel = Label(mainWindow, text = "Enter URL of YouTube Video:", width = 50, justify = "left")
urlEntrybox = Entry(mainWindow, width = 50)
searchButton = Button(mainWindow, text = "Search", command = lambda: searchVideo(urlEntrybox.get()))
downloadButton = Button(mainWindow, text = "Download", command = downloadVideo)
downloadProgressBar = Progressbar(mainWindow, orient = HORIZONTAL, length = 200)
details_frame = Frame(mainWindow)
options_frame = Frame(mainWindow)

urlLabel.grid(row = 0, column = 0)
urlEntrybox.grid(row = 1, column = 0)
searchButton.grid(row = 1, column = 1)
details_frame.grid(row = 2, column = 0, columnspan = 2)
details_frame.grid_remove()
downloadProgressBar.grid(row = 3, column = 0)
downloadButton.grid(row = 3, column = 1)
options_frame.grid(row = 4, column = 0, columnspan = 2)
options_frame.grid_remove()

threadsButton = Button(mainWindow, text = "Threads", command = showThreads)
threadsButton.grid(row = 0, column = 1)

# SEARCH VIDEO DETAILS WIDGETS
thumbnail_box = Label(details_frame)
title_label = Label(details_frame)
time_label = Label(details_frame)
channel_label = Label(details_frame)
views_label = Label(details_frame)
date_label = Label(details_frame)
thumbnail_box.grid(row = 0, column = 0, rowspan = 5)
title_label.grid(row = 0, column = 1)
time_label.grid(row = 1, column = 1)
channel_label.grid(row = 2, column = 1)
views_label.grid(row = 3, column = 1)
date_label.grid(row = 4, column = 1)

# DOWNLOAD OPTIONS WIDGETS
options_label = Label(options_frame, text = "Options:")
advanced_options_button = Button(options_frame, text = "Advanced Options", command = advanced_options)
options_listbox = Listbox(options_frame, width = 50)
options_label.grid(row = 0, column = 0)
advanced_options_button.grid(row = 0, column = 1)
options_listbox.grid(row = 1, column = 0, columnspan = 2)

mainWindow.mainloop()
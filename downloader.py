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

def searchVideo(videoURL, videoResolution):
    global yt
    yt = YouTube(videoURL, on_progress_callback = on_progress, on_complete_callback = on_complete)
    video_length: StringVar
    video_views: StringVar

    if downloadProgressBar["value"] != 0:
        downloadProgressBar["value"] = 0
    searchButton["state"] = DISABLED        
    
    display_image_thread = threading.Thread(target = display_image, args = (yt.thumbnail_url,)) # (x, ) to emphasize that x is one argument and not a list of individual characters
    display_image_thread.start()
    
    filter_streams_thread = threading.Thread(target = filter_streams, args = (videoResolution,))
    filter_streams_thread.start()
    # print(yt.check_availability()) # if available, returns None
    # print(yt.description)
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

def filter_streams(video_resolution):
    for stream in yt.streams.filter(res = video_resolution):
        print(stream)

def downloadVideo(videoTagNumber):
    global yt, max_file_size
    stream = yt.streams.get_by_itag(videoTagNumber)
    max_file_size = stream.filesize
    print(stream.filesize)
    print(convertBytes(stream.filesize))
    x = threading.Thread(target = stream.download, daemon = True)
    x.start()
    downloadButton['state'] = DISABLED

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
# show threads for debugging purposes
def showThreads():
    print(threading.active_count())
    print(threading.enumerate())

mainWindow = Tk()

urlEntrybox = Entry(mainWindow)
searchButton = Button(mainWindow, text = "Search", command = lambda: searchVideo(urlEntrybox.get(), resolutionEntrybox.get()))
resolutionEntrybox = Entry(mainWindow)
resolutionLabel = Label(mainWindow, text = "resolution")
idEntrybox = Entry(mainWindow)
downloadButton = Button(mainWindow, text = "Download", command = lambda: downloadVideo(idEntrybox.get()))
downloadProgressBar = Progressbar(mainWindow, orient = HORIZONTAL)
details_frame = Label(mainWindow)
threadsButton = Button(mainWindow, text = "Threads", command = showThreads)

details_frame = Frame(mainWindow)
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

urlEntrybox.grid(row = 1, column = 0)
searchButton.grid(row = 1, column = 1)
resolutionEntrybox.grid(row = 2, column = 0)
resolutionLabel.grid(row = 2, column = 1)
idEntrybox.grid(row = 3, column = 0)
downloadButton.grid(row = 3, column = 1)
downloadProgressBar.grid(row = 4, column = 0)
threadsButton.grid(row = 4, column = 1)
details_frame.grid(row = 5, column = 0, columnspan = 2)

mainWindow.mainloop()
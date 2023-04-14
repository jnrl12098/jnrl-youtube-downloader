from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from pytube import YouTube
from time import *
import threading
import urllib.request
import io
from PIL import Image, ImageTk

yt = None
max_file_size: int = None
photoimage_holder: PhotoImage = None

def on_progress(stream, chunk, bytes_remaining):
    global max_file_size
    bytes_downloaded = max_file_size - bytes_remaining
    percent_downloaded = (bytes_downloaded / max_file_size)
    downloadProgressBar['value'] = percent_downloaded * 100
    mainWindow.update_idletasks()
    print(convertBytes(bytes_downloaded) + " downloaded")

def on_complete(stream, path):
    messagebox.showinfo("Information", "Download complete.")
    downloadButton['state'] = NORMAL

def searchVideo(videoURL, videoResolution):
    global yt
    searchButton["state"] = DISABLED    
    yt = YouTube(videoURL, on_progress_callback = on_progress, on_complete_callback = on_complete)
    
    display_image_thread = threading.Thread(target = display_image, args = (yt.thumbnail_url,)) # (x, ) to emphasize that x is one argument and not a list of individual characters
    display_image_thread.start()
    
    print(yt.streams.filter(res = videoResolution))
    print(yt.author)
    # print(yt.check_availability()) # if available, returns None
    # print(yt.description)
    if yt.length < 3600:   
        timeString = strftime("%M:%S", gmtime(yt.length)) # gmtime converts the int yt.length into a tuple to be used for strftime
    else:        
        timeString = strftime("%H:%M:%S", gmtime(yt.length))
    print(timeString)
    print(yt.title)
    print(yt.thumbnail_url)

def display_image(thumbnail_url):
    global photoimage_holder
    with urllib.request.urlopen(thumbnail_url) as image_url:
        thumbnail_data = image_url.read()
        thumbnail_bytes = io.BytesIO(thumbnail_data)
        with Image.open(thumbnail_bytes) as thumbnail_image:
            effective_image = thumbnail_image.resize((240, 180))
            thumbnail_photoimage = ImageTk.PhotoImage(effective_image)
            thumbnail_frame.configure(image = thumbnail_photoimage)
    # keep a reference to PhotoImage object so that it appears properly
    photoimage_holder = thumbnail_photoimage

    searchButton["state"] = NORMAL

def downloadVideo(videoTagNumber):
    global yt, max_file_size
    stream = yt.streams.get_by_itag(videoTagNumber)
    max_file_size = stream.filesize
    print(stream.filesize)
    print(convertBytes(stream.filesize))
    x = threading.Thread(target = stream.download, daemon = True)
    x.start()
    downloadButton['state'] = DISABLED

def convertBytes(bytes: int) -> str:
    if bytes < 1024:
        return "{i} B".format(bytes)
    elif bytes < (1024*1024):
        return "{:.2f} KB".format(bytes/1024)
    elif bytes < (1024*1024*1024):
        return "{:.2f} MB".format(bytes/1024/1024)
    else:
        return "{:.2f} GB".format(bytes/1024/1024/1024)

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
thumbnail_frame = Label(mainWindow, image = None)
threadsButton = Button(mainWindow, text = "Threads", command = showThreads)

urlEntrybox.grid(row = 1, column = 0)
searchButton.grid(row = 1, column = 1)
resolutionEntrybox.grid(row = 2, column = 0)
resolutionLabel.grid(row = 2, column = 1)
idEntrybox.grid(row = 3, column = 0)
downloadButton.grid(row = 3, column = 1)
downloadProgressBar.grid(row = 4, column = 0)
thumbnail_frame.grid(row = 5, column = 0)
threadsButton.grid(row = 4, column = 1)

mainWindow.mainloop()
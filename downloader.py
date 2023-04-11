from tkinter import *
from tkinter.ttk import *
from pytube import YouTube
from time import *

yt = None

def searchVideo(videoURL, videoResolution):
    global yt
    yt = YouTube(videoURL)
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
    # yt.register_on_progress_callback()

def downloadVideo(videoTagNumber):
    global yt
    stream = yt.streams.get_by_itag(videoTagNumber)
    # stream.download()
    print(stream.filesize)
    print(convertBytes(stream.filesize))

def convertBytes(bytes: int) -> str:
    if bytes < 1024:
        return "{i} B".format(bytes)
    elif bytes < (1024*1024):
        return "{:.2f} KB".format(bytes/1024)
    elif bytes < (1024*1024*1024):
        return "{:.2f} MB".format(bytes/1024/1024)
    else:
        return "{:.2f} GB".format(bytes/1024/1024/1024)

mainWindow = Tk()

urlEntrybox = Entry(mainWindow)
searchButton = Button(mainWindow, text = "Search", command = lambda: searchVideo(urlEntrybox.get(), resolutionEntrybox.get()))
resolutionEntrybox = Entry(mainWindow)
resolutionLabel = Label(mainWindow, text = "resolution")
idEntrybox = Entry(mainWindow)
downloadButton = Button(mainWindow, text = "Download", command = lambda: downloadVideo(idEntrybox.get()))

urlEntrybox.grid(row = 1, column = 0)
searchButton.grid(row = 1, column = 1)
resolutionEntrybox.grid(row = 2, column = 0)
resolutionLabel.grid(row = 2, column = 1)
idEntrybox.grid(row = 3, column = 0)
downloadButton.grid(row = 3, column = 1)

mainWindow.mainloop()
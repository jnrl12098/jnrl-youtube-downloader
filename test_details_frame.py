# test displaying basic details about YouTube video
from tkinter import *
from pytube import YouTube
import urllib.request
import io
from PIL import Image, ImageTk
import threading
from time import *

photoimage_holder: PhotoImage

def display_result(video_url):
    yt = YouTube(url = video_url)

    display_image_thread = threading.Thread(target = display_image, args = (yt.thumbnail_url, ))
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
    details_frame.pack()

def display_image(thumbnail_url):
    global image_holder
    # print(thumbnail_url)
    with urllib.request.urlopen(thumbnail_url) as image_url:
        thumbnail_data = image_url.read()
        thumbnail_bytes = io.BytesIO(thumbnail_data)
        with Image.open(thumbnail_bytes) as thumbnail_image:
            resize_image = thumbnail_image.resize((240, 180))
            thumbnail_photoimage = ImageTk.PhotoImage(resize_image)
            thumbnail_box.configure(image = thumbnail_photoimage)
    # keep a reference to PhotoImage object so that it appears properly
    image_holder = thumbnail_photoimage 

mainWindow = Tk()

url_entrybox = Entry(mainWindow)
display_button = Button(mainWindow, text = "Display Thumbnail", command = lambda: display_result(url_entrybox.get()))

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

url_entrybox.pack()
display_button.pack()

mainWindow.mainloop()

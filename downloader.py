from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from pytube import YouTube, request
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
    download_progress_bar["value"] = percent_downloaded * 100
    main_window.update_idletasks()
    print(convert_bytes(bytes_downloaded) + " downloaded") # for debugging

def on_complete(stream, path):
    messagebox.showinfo("Information", "Download complete.")
    download_button['state'] = NORMAL

def search_video(videoURL):
    global yt
    yt = YouTube(videoURL, on_progress_callback = on_progress, on_complete_callback = on_complete)
    video_length: StringVar
    video_views: StringVar

    if download_progress_bar["value"] != 0:
        download_progress_bar["value"] = 0
    search_button["state"] = DISABLED  
        
    threading.Thread(target = display_streams, args = (yt,)).start() # (x, ) to emphasize that string x is one argument and not just a list of individual characters
    threading.Thread(target = display_image, args = (yt.thumbnail_url,)).start() 
    
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
    title_label["text"] = yt.title
    time_label["text"] = video_length
    channel_label["text"] = yt.author
    views_label["text"] = video_views
    date_label["text"] = "Published on: " + yt.publish_date.strftime("%b %m, %Y")
    details_frame.grid()

def display_image(thumbnail_url):
    global photoimage_holder
    with urllib.request.urlopen(thumbnail_url) as image_url:
        thumbnail_data = image_url.read()
        thumbnail_bytes = io.BytesIO(thumbnail_data)
        with Image.open(thumbnail_bytes) as thumbnail_image:
            effective_image = thumbnail_image.resize((240, 180))
            thumbnail_photoimage = ImageTk.PhotoImage(effective_image)
            thumbnail_box["image"] = thumbnail_photoimage
    # keep a reference to PhotoImage object so that it appears properly
    photoimage_holder = thumbnail_photoimage
    search_button["state"] = NORMAL

def display_streams(yt_object):
    global tag_list
    item: StringVar
    filename_entrybox.delete(0, END)
    filename_entrybox.insert(0, yt_object.title)
    tag_list.clear()
    options_listbox.delete(0, END)
    for stream in yt_object.streams.filter():
        print(stream) # for debugging; to check if tag_list and listbox match
        if stream.type == "video":
            item = stream.type + " - " + stream.resolution + str(stream.fps) + " - " + stream.subtype + " (" + convert_bytes(stream.filesize) + ")"
            if stream.is_adaptive:
                item += " (no audio)"
        elif stream.type == "audio":
            item = stream.type + " - " + stream.abr + " - " + stream.subtype + " (" + convert_bytes(stream.filesize) + ")"
        options_listbox.insert(END, item)
        tag_list.append(stream.itag)
    options_frame.grid()
    search_button["state"] = NORMAL

def advanced_options():
    print("You pressed the advanced options button.")

def download_video():
    global yt, max_file_size    
    download_button['state'] = DISABLED
    print(tag_list[options_listbox.curselection()[0]]) # for debugging; to check if tag_list and listbox match
    stream = yt.streams.get_by_itag(tag_list[options_listbox.curselection()[0]])
    max_file_size = stream.filesize
    # threading.Thread(target = stream.download, daemon = True).start()
    filename = filename_entrybox.get() + "." + stream.subtype
    with open(filename, "wb") as download_file:
        stream = request.stream(stream.url) # turn the stream into an iterable where pytube's default chunk size is 9MB
        bytes_downloaded: int = 0
        while True:
            chunk = next(stream, None)  
            if chunk is not None:
                download_file.write(chunk)
                bytes_downloaded += len(chunk)
                percent_downloaded: float = bytes_downloaded / max_file_size
                download_progress_bar["value"] = percent_downloaded * 100
                main_window.update_idletasks()
            else:
                messagebox.showinfo("Information", "Download complete.")
                download_button['state'] = NORMAL
                break
    

# UTILITY FUNCTIONS
# convert bytes to KB/MB/GB for better readability
def convert_bytes(bytes: int) -> str:
    if bytes < 1024:
        return "{i} B".format(bytes)
    elif bytes < (1024*1024):
        return "{:.2f} KB".format(bytes/1024)
    elif bytes < (1024*1024*1024):
        return "{:.2f} MB".format(bytes/1024/1024)
    else:
        return "{:.2f} GB".format(bytes/1024/1024/1024)
# show threads for debugging 
def show_threads():
    print(threading.active_count())
    print(threading.enumerate())

main_window = Tk()

url_label = Label(main_window, text = "Enter URL of YouTube Video:", width = 50, justify = "left")
url_entrybox = Entry(main_window, width = 50)
search_button = Button(main_window, text = "Search", command = lambda: search_video(url_entrybox.get()))
download_button = Button(main_window, text = "Download", command = download_video)
download_progress_bar = Progressbar(main_window, orient = HORIZONTAL, length = 200)
details_frame = Frame(main_window)
options_frame = Frame(main_window)

url_label.grid(row = 0, column = 0)
url_entrybox.grid(row = 1, column = 0)
search_button.grid(row = 1, column = 1)
details_frame.grid(row = 2, column = 0, columnspan = 2)
details_frame.grid_remove()
download_progress_bar.grid(row = 3, column = 0)
download_button.grid(row = 3, column = 1)
options_frame.grid(row = 4, column = 0, columnspan = 2)
options_frame.grid_remove()

threads_button = Button(main_window, text = "Threads", command = show_threads)
threads_button.grid(row = 0, column = 1)

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
filename_label = Label(options_frame, text = "Enter preferred file name:", width = 50, justify = "left")
filename_entrybox = Entry(options_frame, width = 50)
options_label = Label(options_frame, text = "Options:")
advanced_options_button = Button(options_frame, text = "Advanced Options", command = advanced_options)
options_listbox = Listbox(options_frame, width = 50)
filename_label.grid(row = 0, column = 0)
filename_entrybox.grid(row = 1, column = 0)
options_label.grid(row = 2, column = 0)
advanced_options_button.grid(row = 2, column = 1)
options_listbox.grid(row = 3, column = 0, columnspan = 2)

main_window.mainloop()
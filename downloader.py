from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from pytube import YouTube, request, exceptions
from time import *
import threading
import urllib.request
import urllib.error
import io
import os
from PIL import Image, ImageTk

yt: YouTube = None
photoimage_holder: PhotoImage = None
tag_list: list[int] = []
is_paused: bool = False
is_cancelled: bool = False
search_is_loading: bool = False

def search_stream(video_url):
    global yt 
    global photoimage_holder
    global tag_list
    global search_is_loading
    search_button["state"] = DISABLED 
    
    try:
        yt = YouTube(video_url) 
    except exceptions.RegexMatchError:
        messagebox.showerror(title = "ERROR", message = "Invalid URL")
        search_button["state"] = NORMAL
        return
    
    if download_progress_bar["value"] != 0:
        download_progress_bar["value"] = 0
            
    search_is_loading = True
    loading_label.grid()
    threading.Thread(target = loading_search, args = (), daemon = True).start()

    try:
        with urllib.request.urlopen(yt.thumbnail_url) as image_url:
            thumbnail_data = image_url.read()
            thumbnail_bytes = io.BytesIO(thumbnail_data)
            with Image.open(thumbnail_bytes) as thumbnail_image:
                effective_image = thumbnail_image.resize((240, 180))
                thumbnail_photoimage = ImageTk.PhotoImage(effective_image)
                thumbnail_box["image"] = thumbnail_photoimage
        # keep a reference to PhotoImage object so that it appears properly
        photoimage_holder = thumbnail_photoimage
    except urllib.error.HTTPError:
        messagebox.showerror(title = "ERROR", message = "Invalid URL (HTTP Error 404: Not Found)")
        search_button["state"] = NORMAL
        search_is_loading = False
        loading_label.grid_forget()
        return

    video_title: str
    retry_count = 0
    while True:
        try:
            video_title = yt.title
            print("Successfully retrieved title of video")
            break
        except Exception as e:
            yt = YouTube(video_url)
            retry_count += 1
            print(e)
            print(f"Retrying... ({retry_count} time/s)")
            continue
    char_per_line: int = 40
    if len(video_title) > char_per_line:
        reversed_first_line = video_title[0:char_per_line][::-1] # for some reason, slicing via indexing [0:char_per_line:-1] doesn't work
        whitespace_index = char_per_line - reversed_first_line.find(" ")
        character_limit = whitespace_index + char_per_line - 3 # display 2 lines maximum + "..." at the end
        if len(video_title) > character_limit:
            title_label["text"] = video_title[0:whitespace_index] + "\n" + video_title[whitespace_index:character_limit] + "..."
        else:
            title_label["text"] = video_title[0:whitespace_index] + "\n" + video_title[whitespace_index:]
    else:
        title_label["text"] = video_title
    
    try:
        if yt.length < 3600:   
            time_label["text"] = "Length: " + strftime("%M:%S", gmtime(float(yt.length))) # gmtime converts the int yt.length into a tuple to be used for strftime
        else:        
            time_label["text"] = "Length: " + strftime("%H:%M:%S", gmtime(float(yt.length)))
    except TypeError:
        time_label["text"] = "Length: Unavailable"

    try:
        if yt.views < 1000:
            views_label["text"] = f"{yt.views} views"
        elif yt.views < 1000*10:
            views_label["text"] = f"{yt.views/1000: .1f}K views"
        elif yt.views < 1000*1000:
            views_label["text"] = f"{int(yt.views/1000)}K views"
        elif yt.views < 1000*1000*10:
            views_label["text"] = f"{yt.views/1000/1000: .1f}M views"
        else:
            views_label["text"] = f"{int(yt.views/1000/1000)} M views"
    except TypeError:
        views_label["text"] = "Views: Unavailable"

    channel_label["text"] = yt.author
    date_label["text"] = "Published on: " + yt.publish_date.strftime("%b %m, %Y")
    # DISPLAY STREAM OPTIONS
    item: str
    filename_entrybox.delete(0, END)
    filename_entrybox.insert(0, yt.title)
    tag_list.clear()
    options_listbox.delete(0, END)
    for stream in yt.streams.filter():
        # print(stream) # for debugging; to check if tag_list and listbox match
        if stream.type == "video":
            item = stream.type + " - " + stream.resolution + str(stream.fps) + " - " + stream.subtype + " (" + convert_bytes(stream.filesize) + ")"
            if stream.is_adaptive:
                item += " (no audio)"
        elif stream.type == "audio":
            item = stream.type + " - " + stream.abr + " - " + stream.subtype + " (" + convert_bytes(stream.filesize) + ")"
        options_listbox.insert(END, item) # sometimes results in error: "RuntimeError: main thread is not in main loop"
        tag_list.append(stream.itag)

    search_is_loading = False
    loading_label.grid_forget()
    details_frame.pack()
    download_frame.pack()
    options_frame.pack()
    search_button["state"] = NORMAL

def loading_search():
    global search_is_loading
    while search_is_loading:
        loading_label["text"] = "Loading"
        sleep(1)
        loading_label["text"] = "Loading."
        sleep(1)
        loading_label["text"] = "Loading.."
        sleep(1)
        loading_label["text"] = "Loading..."
        sleep(1)
    return

def start_search():
    threading.Thread(target = search_stream, args = (url_entrybox.get(),)).start()

def advanced_options():
    print("You pressed the advanced options button.")
    # TODO post-processing options with FFMPEG in mind

def download_stream():
    global yt, is_paused, is_cancelled  
    stream = yt.streams.get_by_itag(tag_list[options_listbox.curselection()[0]])
    filename: str = filename_entrybox.get() + "." + stream.subtype
    if os.path.exists(filename): # TODO when implementing download queue, must also check if filename has already been taken
        messagebox.showerror(title = "ERROR", message = "File name is already taken.")
        return
    download_button["state"] = DISABLED
    pause_button["state"] = NORMAL
    cancel_button["state"] = NORMAL
    filesize: int = stream.filesize
    stream_url: str = stream.url
    converted_filesize: str = convert_bytes(filesize)
    try:
        with open(filename, "wb") as download_file:
            is_paused = False
            is_cancelled = False
            stream = request.stream(stream_url) # turn the stream into an iterable; pytube's default chunk size is 9MB
            bytes_downloaded: int = 0
            while True:
                if is_cancelled:
                    break
                if is_paused:
                    continue
                chunk = next(stream, None)  
                if chunk is not None:
                    download_file.write(chunk)
                    bytes_downloaded += len(chunk)
                    download_progress_bar["value"] = (bytes_downloaded / filesize) * 100
                    progress_label["text"] = convert_bytes(bytes_downloaded) + " / " + converted_filesize
                    main_window.update_idletasks()
                else:
                    messagebox.showinfo(title = "Information", message = "Download complete.")
                    break
        if is_cancelled:
            os.remove(filename)
    except OSError:
        messagebox.showerror(title = "ERROR", message = "File name can't contain any of the following characters:\n\ / : * ? \" < > |")
    download_button["state"] = NORMAL
    pause_button["state"] = DISABLED
    pause_button["text"] = "Pause"
    cancel_button["state"] = DISABLED
    download_progress_bar["value"] = 0
    progress_label["text"] = ""

def start_download():
    if len(options_listbox.curselection()) == 1:
        threading.Thread(target = download_stream, daemon = True).start()
    else:
        messagebox.showinfo(title = "Information", message = "Choose a stream to download.")
    
def toggle_download():
    global is_paused
    is_paused = not is_paused
    if is_paused:
        pause_button["text"] = "Resume"
    else:
        pause_button["text"] = "Pause"

def cancel_download():
    global is_cancelled
    is_cancelled = True
    download_progress_bar["value"] = 0
    messagebox.showinfo(title = "Information", message = "Download was cancelled.")

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

search_frame = Frame(main_window)
download_frame = Frame(main_window)
details_frame = Frame(main_window)
options_frame = Frame(main_window)

search_frame.pack()

# SEARCH WIDGETS
url_label = Label(search_frame, text = "Enter URL of YouTube Video:", width = 50, justify = "left")
url_entrybox = Entry(search_frame, width = 50)
search_button = Button(search_frame, text = "Search", command = start_search)
loading_label = Label(search_frame)
url_label.grid(row = 0, column = 0)
url_entrybox.grid(row = 1, column = 0)
search_button.grid(row = 1, column = 1)
loading_label.grid(row = 2, columnspan = 2)
loading_label.grid_forget()
# show threads for debugging
threads_button = Button(search_frame, text = "Threads", command = show_threads)
threads_button.grid(row = 0, column = 1)

# DOWNLOAD STREAM WIDGETS
download_progress_bar = Progressbar(download_frame, orient = HORIZONTAL, length = 200)
progress_label = Label(download_frame)
download_button = Button(download_frame, text = "Download", command = start_download)
pause_button = Button(download_frame, text = "Pause", state = DISABLED, command = toggle_download)
cancel_button = Button(download_frame, text = "Cancel", state = DISABLED, command = cancel_download)
download_progress_bar.grid(row = 0, column = 0, columnspan = 3)
progress_label.grid(row =1, column = 0, columnspan = 3)
download_button.grid(row = 2, column = 0)
pause_button.grid(row = 2, column = 1)
cancel_button.grid(row = 2, column = 2)

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

# STREAM OPTIONS WIDGETS
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
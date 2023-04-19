# test adding streams to the download queue + automatically downloading streams as long as the queue is not empty
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar
from pytube import YouTube, Stream, request
from time import *
import threading
import os
import urllib.request
import urllib.error
import io
from PIL import Image, ImageTk


yt: YouTube
tag_list: list[int] = []
download_queue: list = []
is_paused: bool = False
is_cancelled: bool = False
video_title: str = ""

def display_streams(video_url):
    global yt, tag_list, video_title
    item: StringVar
    yt = YouTube(url = video_url)

    # for some reason, pytube sometimes cannot properly load the details of the video, requiring us to reload the YouTube object yt until the details are retrieved properly
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
    
    tag_list.clear()
    options_listbox.delete(0, END)
    for stream in yt.streams.filter():
        if stream.type == "video":
            item = stream.type + " - " + stream.resolution + str(stream.fps) + " - " + stream.subtype + " (" + convert_bytes(stream.filesize) + ")"
            if stream.is_adaptive:
                item += " (no audio)"
        elif stream.type == "audio":
            item = stream.type + " - " + stream.abr + " - " + stream.subtype + " (" + convert_bytes(stream.filesize) + ")"
        options_listbox.insert(END, item)
        tag_list.append(stream.itag)

    options_frame.pack()

def add_stream_to_queue():

    if len(options_listbox.curselection()) == 0:
        messagebox.showerror(title = "ERROR", message = "Choose an option to download.")
        return

    global yt
    # print(tag_list[options_listbox.curselection()[0]])

    stream = yt.streams.get_by_itag(tag_list[options_listbox.curselection()[0]])
    filename: str = filename_entrybox.get()
    filename_is_invalid: bool = False
    for char in filename:
        if char in "\/:*?\"<>|":
            filename_is_invalid = True
            break
    if filename_is_invalid:
        messagebox.showerror(title = "ERROR", message = "File name can't contain any of the following characters:\n\ / : * ? \" < > |")
        return
    filename = filename + "." + stream.subtype
    if os.path.exists(filename): # TODO when implementing download queue, must also check if filename has already been taken
        messagebox.showerror(title = "ERROR", message = "File name is already taken.")
        return
    
    thumbnail_photoimage: PhotoImage = None
    try:
        # load the thumbnail into the thumbnail_box
        with urllib.request.urlopen(yt.thumbnail_url) as image_url:
            thumbnail_data = image_url.read()
            thumbnail_bytes = io.BytesIO(thumbnail_data)
            with Image.open(thumbnail_bytes) as thumbnail_image:
                effective_image = thumbnail_image.resize((240, 180))
                thumbnail_photoimage = ImageTk.PhotoImage(effective_image)
                # thumbnail_box["image"] = thumbnail_photoimage
        # keep a reference to PhotoImage object so that it appears properly
        # photoimage_holder = thumbnail_photoimage
    except urllib.error.HTTPError:
        messagebox.showerror(title = "ERROR", message = "Invalid URL (HTTP Error 404: Not Found)")
        search_button["state"] = NORMAL
        search_is_loading = False
        # loading_label.grid_forget()
        return   
    
    details: str = options_listbox.get(options_listbox.curselection()[0])
    stream_url: str = stream.url
    filesize: int = stream.filesize

    download_queue.append([thumbnail_photoimage, filename, details, stream_url, filesize])
    queue_listbox.insert(END, filename + "(" + convert_bytes(filesize) + ")")
    # print("Streams:")
    # for stream in download_queue:
    #     print(stream.itag)
    if len(download_queue) == 1:
        threading.Thread(target = download_stream, daemon = True).start()

def download_stream():
    global is_paused, is_cancelled, download_queue  
    queue_frame.pack()
    while len(download_queue) > 0:
        queue_listbox.delete(0)
        pause_button["state"] = NORMAL
        cancel_button["state"] = NORMAL
        thumbnail: PhotoImage = download_queue[0][0]
        filename: str = download_queue[0][1]
        details: str = download_queue[0][2]
        stream_url: str = download_queue[0][3]
        filesize: int = download_queue[0][4]

        current_thumbnail["image"] = thumbnail
        current_details["text"] = filename + "\n" + details

        converted_filesize: str = convert_bytes(filesize)
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
                    break
        if is_cancelled:
            messagebox.showinfo(title = "Information", message = "Download was cancelled.")
            os.remove(filename)
        else:
            messagebox.showinfo(title = "Information", message = "Download complete.")
        download_progress_bar["value"] = 0
        download_queue.pop(0)
        pause_button["state"] = DISABLED
        pause_button["text"] = "Pause"
        cancel_button["state"] = DISABLED
        progress_label["text"] = ""
    queue_frame.pack_forget()

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

def convert_bytes(bytes: int) -> str:
    if bytes < 1024:
        return "{i} B".format(bytes)
    elif bytes < (1024*1024):
        return "{:.2f} KB".format(bytes/1024)
    elif bytes < (1024*1024*1024):
        return "{:.2f} MB".format(bytes/1024/1024)
    else:
        return "{:.2f} GB".format(bytes/1024/1024/1024) # assuming video sizes don't get into terabyte territory
    
main_window = Tk()

search_frame = Frame(main_window)
search_actions = Frame(search_frame)
url_label = Label(search_actions, text = "Enter YouTube URL:", width = 50, justify = "left")
url_entrybox = Entry(search_actions, width = 50)
search_button = Button(search_actions, text = "Search", command = lambda: display_streams(url_entrybox.get()))
url_label.grid(row = 0, column = 0)
url_entrybox.grid(row = 1, column = 0)
search_button.grid(row = 1, column = 1)

options_frame = Frame(search_frame)
url_label = Label(search_actions, text = "Enter YouTube URL:", width = 50, justify = "left")
filename_label = Label(options_frame, text = "Save as:", width = 50, justify = "left")
filename_entrybox = Entry(options_frame, width = 50)
url_label.grid(row = 0, column = 0)
download_button = Button(options_frame, text = "Download", command = add_stream_to_queue)
options_label = Label(options_frame, text = "Options:")
options_listbox = Listbox(options_frame, width = 50)

filename_label.grid(row = 0, column = 0)
filename_entrybox.grid(row = 1, column = 0)
download_button.grid(row = 1, column = 1)
options_label.grid(row = 2, column = 0)
options_listbox.grid(row = 3, column = 0, columnspan = 2)

search_actions.pack()
options_frame.pack()
options_frame.pack_forget()

queue_frame = Frame(main_window)
now_downloading = Label(queue_frame, text = "Now downloading:")
current_thumbnail = Label(queue_frame)
current_details = Label(queue_frame)
download_progress_bar = Progressbar(queue_frame, orient = "horizontal", length = 300)
progress_label = Label(queue_frame)
pause_button = Button(queue_frame, text = "Pause", command = toggle_download, state = DISABLED)
cancel_button = Button(queue_frame, text = "Cancel", command = cancel_download, state = DISABLED)
queue_label = Label(queue_frame, text = "Up next:", width = 100, justify = "left")
queue_listbox = Listbox(queue_frame, width = 100)

now_downloading.grid(row = 0, column = 0, columnspan = 2)
current_thumbnail.grid(row = 1, column = 0, columnspan = 2)
current_details.grid(row = 2, column = 0, columnspan = 2)
download_progress_bar.grid(row = 3, column = 0, columnspan = 2)
progress_label.grid(row = 4, column = 0, columnspan = 2)
pause_button.grid(row = 5, column = 0)
cancel_button.grid(row = 5, column = 1)
queue_label.grid(row = 6, column = 0, columnspan = 2)
queue_listbox.grid(row = 7, column = 0, columnspan = 2)

search_frame.pack(anchor = W)
queue_frame.pack(anchor = E)
queue_frame.pack_forget()

main_window.mainloop()
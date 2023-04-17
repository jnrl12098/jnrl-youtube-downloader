# helping hand
# from https://stackoverflow.com/questions/63533960/how-to-cancel-and-pause-a-download-using-pytube#:~:text=You%20can%20try%20pytube.,the%20download%20as%20you%20wish.
import tkinter as tk
import threading
from pytube import YouTube, request

is_paused = False
is_cancelled = False

def download_video(url):
    global is_paused, is_cancelled
    download_button['state'] ='disabled'
    pause_button['state'] ='normal'
    cancel_button['state'] ='normal'
    try: 
        progress['text'] = 'Connecting ...'
        yt = YouTube(url)
        stream = yt.streams.first() # specify the desired stream from the YouTube object
        filesize = stream.filesize  # get the video size
        print(filesize)
        with open('sample.mp4', 'wb') as f: # since 'wb' then if a download was cancelled and the same stream was downloaded again then it will overwrite the old file, not append to it
            is_paused = is_cancelled = False
            print(stream.url)
            stream = request.stream(stream.url) # get an iterable stream which is read in chunks
                # stream.url is the url specific to the stream specified in line 18; streams of diff resolutions don't share the same url
            downloaded = 0
            while True:
                if is_cancelled:
                    progress['text'] = 'Download cancelled'
                    break
                if is_paused:
                    continue
                chunk = next(stream, None) # get next chunk of video
                if chunk: # if chunk exists; is not None
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress['text'] = f'Downloaded {downloaded} / {filesize}'
                else:
                    # no more data
                    progress['text'] = 'Download completed'
                    break
        print('done')
    except Exception as e:
        print(e)
    download_button['state'] ='normal'
    pause_button['state'] ='disabled'
    cancel_button['state'] ='disabled'

def start_download():
    threading.Thread(target=download_video, args=(url_entry.get(),), daemon=True).start()

def toggle_download():
    global is_paused
    is_paused = not is_paused
    pause_button['text'] = 'Resume' if is_paused else 'Pause'

def cancel_download():
    global is_cancelled
    is_cancelled = True

root = tk.Tk()
root.title("YouTube Downloader")

tk.Label(root, text='URL:').grid(row=0, column=0, sticky='e')
url_entry = tk.Entry(root, width=60)
url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10)

download_button = tk.Button(root, text='Download', width=20, command=start_download)
download_button.grid(row=1, column=2, sticky='e', padx=10, pady=(0,10))

pause_button = tk.Button(root, text='Pause', width=10, command=toggle_download, state='disabled')
pause_button.grid(row=2, column=0)

progress = tk.Label(root)
progress.grid(row=2, column=1, sticky='w')

cancel_button = tk.Button(root, text='Cancel', width=10, command=cancel_download, state='disabled')
cancel_button.grid(row=2, column=2, sticky='e')

root.mainloop()
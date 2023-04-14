YouTube Downloader with GUI
* goal is to replicate the user experience of downloading youtube videos with clipconverter.cc,
  but allow user to queue downloads like with the Steam downloads page

[MODULES]
io
 * used to convert raw image data into bytes for the thumbnail
PIL (Image, ImageTk)
 * used to open bytes into an image, to resize the image, to turn the image into a PhotoImage object
pytube (YouTube)
 * used for all functions related to YouTube videos
threading
 * used to perform multi-threading (e.g. to allow downloads to be performed in the background)
time (*)
 * used to turn YouTube video length (seconds: int) into a string (H:M:S format)
tkinter (*, messagebox)
 * used for the GUI
tkinter.ttk (*)
 * used for the progress bar
urllib.request
 * used to access pages behind URLs
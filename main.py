import json
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import *
from tkinter.messagebox import *
from PIL import Image, ImageTk
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
from datetime import datetime, date
from threading import Thread
from pydub import AudioSegment
from eyed3.id3.frames import ImageFrame
# from bs4 import BeautifulSoup
import traceback, sys, os, validators, time, sv_ttk, math, requests, random, importlib.util, re, types, pydub, eyed3, \
    subprocess

try:
    for moduleName in "pydub.utils", "pydub.audio_segment":
        spec = importlib.util.find_spec(moduleName, None)
        source = spec.loader.get_source(moduleName)
        snippet = "__import__('subprocess').STARTUPINFO(dwFlags=__import__('subprocess').STARTF_USESHOWWINDOW)"
        source, n = re.subn(r"(Popen)\((.+?)\)", rf"\1(\2, startupinfo=print('worked') or {snippet})", source,
                            flags=re.DOTALL)
        module = importlib.util.module_from_spec(spec)
        exec(compile(source, module.__spec__.origin, "exec"), module.__dict__)
        sys.modules[moduleName] = module
    module = importlib.reload(sys.modules["pydub"])
    for k, v in module.__dict__.items():
        if isinstance(v, types.ModuleType):
            setattr(module, k, importlib.import_module(v.__name__))
except Exception as e:
    print(traceback.format_exc())


# def ScrapeYTData(url: str) -> dict:
#     # send a GET request to the URL
#     response = requests.get(url)
#
#     # parse the HTML content using BeautifulSoup
#     soup = BeautifulSoup(response.content, 'html.parser')
#
#     # find the structured description content
#     description = soup.find('div', {'class': 'style-scope ytd-watch-metadata'})
#
#     # find the info row for the song name and extract its text
#     song_info = description.find('div',
#                                  {'id': 'title', 'class': 'style-scope ytd-info-row-renderer'}).find_next_sibling()
#     song_name = song_info.find('yt-formatted-string', {'id': 'default-metadata'}).text
#
#     # find the info row for the artist and extract its text
#     artist_info = song_info.find_next_sibling()
#     artist_name = artist_info.find('yt-formatted-string', {'id': 'default-metadata'}).find('a').text
#     return {"Artist": artist_name}


class GUI():
    def __init__(self, master):
        self.testG = 1
        self.WIN = master
        self.WIN.resizable(0, 0)
        self.WIN.protocol("WM_DELETE_WINDOW", False)
        self.windowHeight = int(self.WIN.winfo_reqheight())
        self.windowWidth = int(self.WIN.winfo_reqwidth())
        self.positionRight = int(self.WIN.winfo_screenwidth() / 2 - (self.windowWidth / 2))
        self.positionDown = int(self.WIN.winfo_screenheight() / 2 - (self.windowHeight / 2))
        self.WIN.iconphoto(False, PhotoImage(file='images/youtube.png'))
        self.W = 1000
        self.H = 750
        self.WIN.geometry(f"{self.W}x{self.H}+{self.positionRight - 400}+{self.positionDown - 300}")
        self.WIN.title("Youtube Downloader")
        style = Style()
        style.configure('W.TButton', font=('Comic sans ms', 10, 'normal', 'italic'), foreground='black')
        self.style1 = 'W.TButton'
        sv_ttk.set_theme("dark")  # Set dark theme

        # etc VAR/ FUNC
        self.MANY = self.ONE = False
        self.DATA = {}
        self.URL = ''
        self.DOWNLOAD_DIR = 'download'
        self.PLAYLIST_TITLE = ''
        self.PLAYLIST = []
        if not os.path.exists(os.path.abspath(self.DOWNLOAD_DIR)):
            os.makedirs(self.DOWNLOAD_DIR)
            if not os.path.exists(os.path.abspath('logs')):
                os.makedirs('logs')
        # create temp.json if not exist
        # if not os.path.exists(os.path.abspath("temp/temp.json")):
        #     c = open("temp/temp.json", "w")
        #     c.write("{}")
        #     c.close()

        # main frame
        self.f_up = Frame(self.WIN, relief=RAISED, width=100, height=100)
        self.f_up.pack(fill=BOTH)
        self.f_mid = Frame(self.WIN, width=100, height=100, relief=RAISED)
        self.f_mid.pack(fill=BOTH, expand=True)
        self.f_end = Frame(self.WIN, relief=RAISED)
        self.f_end.pack(fill=BOTH)

        # f_up
        Label(self.f_up, text='Search URL: ', font=('Comic sans ms', 10, 'normal', 'italic')).grid(row=0, column=1,
                                                                                                   sticky=W + E)
        self.e_search = Entry(self.f_up)
        self.e_search.grid(row=0, column=2, sticky=W + E, ipadx=self.W / 3 + 14, ipady=4)
        self.b_clear = Button(self.f_up, text="Clear", style=self.style1)
        self.b_clear.grid(row=0, column=3, sticky=W + E)

        # f_mid
        self.bar_main = Progressbar(self.f_mid, orient='horizontal', mode='indeterminate', maximum=100,
                                    length=self.W / 4)
        self.bar_main.start()
        self.bar_main.grid(row=0, column=0, ipadx=self.W / 3, ipady=4, sticky=W + E)
        self.lbl_barMain = Label(self.f_mid, text='0/0', font=('Comic sans ms', 13, 'bold', 'italic'),
                                 background='cyan', foreground='grey')
        self.lbl_barMain.grid(row=0, column=1, sticky=W + E, ipadx=25)
        self.txt_main = ScrolledText(self.f_mid, undo=True)
        self.txt_main.grid(row=1, column=0, sticky='nsew', columnspan=2)
        self.txt_main.config(state=DISABLED)
        self.lbl_totalMB = Label(self.f_mid, text='TOTAL DOWNLOAD: 0.0 MB',
                                 font=('Comic sans ms', 13, 'normal', 'italic'), background='grey')
        self.lbl_totalMB.grid(row=2, column=0, sticky=W + E)
        self.lbl_remainTime = Label(self.f_mid, text='REMAIN TIMES: 0.0 Minute(s)',
                                    font=('Comic sans ms', 13, 'normal', 'italic'), background='dark blue')
        self.lbl_remainTime.grid(row=3, column=0, sticky=W + E, pady=2)
        f_mid2 = Canvas(self.f_mid, relief=RAISED)
        f_mid2.grid(row=4, column=0, sticky=W + E, pady=1)
        self.b_mp3 = Button(f_mid2, text="MP3", style=self.style1, state='disabled')
        self.b_mp3.grid(row=0, column=0, sticky=W + E)
        self.b_mp4 = Button(f_mid2, text="MP4", style=self.style1, state='disabled')
        self.b_mp4.grid(row=0, column=1, sticky=W + E)
        self.b_openFolder = Button(f_mid2, text="Open Download Folder", style=self.style1)
        self.b_openFolder.grid(row=0, column=2, sticky=W + E)
        self.b_logFile = Button(f_mid2, text="Log File", style=self.style1)
        self.b_logFile.grid(row=0, column=3, sticky=W + E)

        self.txt_main.tag_config('success', background="grey", foreground="green")
        self.txt_main.tag_config('warning', background="yellow", foreground="red")
        self.txt_main.tag_config('error', background="grey", foreground="red")

        # f_end
        self.b_exit = Button(self.f_end, text="Exit", style=self.style1, command=lambda: sys.exit())
        self.b_exit.pack(side=RIGHT, padx=5, pady=5)

        # function end
        def youtube(url):
            try:
                try:
                    check = YouTube(url)
                    check = check.vid_info
                    self.ONE = True
                    self.MANY = False
                except:
                    check = Playlist(url)
                    check = check.title
                    self.MANY = True
                    self.ONE = False
                return True
            except:
                self.MANY = self.ONE = False
                return False

        def checkSTR(*args):
            def youtube_tag(url):
                # Regex pattern to match YouTube URLs
                youtube_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)'
                return bool(re.search(youtube_pattern, url, re.IGNORECASE))
            
            if len(self.e_search.get()) == 0:
                # print('zero')
                self.e_search.after(1000, checkSTR)
            elif not youtube_tag(self.e_search.get()):
                self.txt_main.config(state=NORMAL)
                self.txt_main.delete("1.0", "end")
                self.txt_main.insert(INSERT, "NOT YOUTUBE, PLS COPY AND PASTE A REAL YOUTUBE URL")
                self.txt_main.config(state=DISABLED)
                self.e_search.delete(0, 'end')
                self.e_search.after(1000, checkSTR)
            else:
                self.e_search.config(state='disabled')
                check_url = validators.url(str(self.e_search.get()))
                if check_url:
                    URL = str(self.e_search.get())
                    print(URL)
                    if youtube(URL):
                        Thread(target=self.youtubeData, args=(URL,)).start()
                        self.txt_main.config(state=NORMAL)
                        self.txt_main.delete("1.0", "end")
                        self.txt_main.insert(INSERT, f"URL FOUND, {URL}")
                        self.txt_main.config(state=DISABLED)
                    else:
                        self.e_search.config(state='normal')
                        self.e_search.delete(0, 'end')
                        self.txt_main.config(state=NORMAL)
                        self.txt_main.delete("1.0", "end")
                        self.txt_main.insert(INSERT, f"URL NOT FOUND, {URL}")
                        self.txt_main.config(state=DISABLED)
                        self.e_search.after(1000, checkSTR)

                else:
                    self.txt_main.config(state=NORMAL)
                    self.txt_main.delete("1.0", "end")
                    self.txt_main.insert(END, "URL NOT FOUND, PLS COPY AND PASTE A REAL URL")
                    self.txt_main.config(state=DISABLED)
                    self.e_search.config(state='normal')
                    self.e_search.delete(0, 'end')
                    self.e_search.after(2000, checkSTR)

        self.e_search.after(2000, checkSTR)

        def clear(*args):
            self.txt_main.config(state=NORMAL)
            self.txt_main.delete("1.0", "end")
            self.txt_main.config(state=DISABLED)
            self.e_search.config(state='normal')
            self.e_search.delete(0, 'end')
            self.e_search.after(2000, checkSTR)
            self.MANY = self.ONE = False
            self.DATA = {}
            self.URL = ''
            self.b_mp3.config(state=DISABLED)
            self.b_mp4.config(state=DISABLED)

        self.b_clear.config(command=clear)

        self.WIN.mainloop()

        # main function

    def youtubeData(self, url):
        if self.ONE:
            try:
                print('one ' + str(self.ONE))
                engine = YouTube(url)
                self.txt_main.config(state=NORMAL)
                self.txt_main.insert(END, f"\nVIDEO FOUND, {engine.title} @{engine.author}_{engine.publish_date}@")
                self.txt_main.insert(END, f"\nVIDEO LENGTH, {round(float(engine.length) / 60, 2)} minute")
                self.URL = [url]
                self.txt_main.config(state=DISABLED)
                self.b_mp3.config(state=NORMAL,
                                  command=lambda: Thread(target=self.mp3Download, args=(self.URL,)).start(), )
            except Exception as e:
                print(traceback.format_exc())
                self.logSave(e, traceback.format_exc(), "findFile Exception")
                self.txt_main.config(state=NORMAL)
                self.txt_main.delete("1.0", "end")
                self.txt_main.insert(INSERT, f"\nEXCEPTION HAPPEN: {e} \n {traceback.format_exc()}")
                self.txt_main.insert(INSERT, f"\nSAVE IN LOG FILE: {e}")
                self.txt_main.config(state=DISABLED)

        elif self.MANY:
            try:
                print('many ' + str(self.MANY))
                engine = Playlist(url)
                self.txt_main.config(state=NORMAL)
                self.PLAYLIST_TITLE = engine.title
                self.txt_main.insert(INSERT,
                                     f"\nPLAYLIST FOUND, {self.PLAYLIST_TITLE} @{engine.owner} #{engine.playlist_id}@")
                urls = engine.video_urls
                self.URL = urls

                def totalVideo():
                    temp_object = []
                    try:
                        with open("temp/temp.json", 'r') as r:
                            temp_object = json.load(r)
                            r.close()
                        if self.PLAYLIST_TITLE in temp_object:
                            temp_object = temp_object[self.PLAYLIST_TITLE]
                            print(f"TEMP_OBJ = {temp_object}")
                    except Exception as e:
                        print(f"{e}-{traceback.format_exc()}")

                    self.txt_main.insert(INSERT, f"\nCALCULATE TOTAL VIDEO... PLEASE WAIT..")
                    self.bar_main.config(mode='determinate')
                    self.b_clear.config(state=DISABLED)
                    self.bar_main['value'] = 0
                    self.bar_main.start(1000)
                    self.check_downloaded = []
                    for u in list(urls):
                        filter = ''
                        try:
                            engine = YouTube(u)
                            char_list = [str(engine.title)[j] for j in range(len(str(engine.title))) if
                                        ord(str(engine.title)[j]) in range(65536)]
                            for j in char_list:
                                filter = filter + j
                            self.DATA[filter] = u
                            print(filter)
                            if u not in temp_object:
                                self.check_downloaded.append(filter)
                            self.bar_main['value'] = float(len(self.DATA) / len(urls)) * 100
                            self.lbl_barMain.config(text=f'0/{len(self.DATA)}')
                        except Exception as e:
                            print(f"{e} in parsing {u}: \n {traceback.format_exc()}")
                            self.txt_main.insert(INSERT, f"\nEXCEPTION HAPPEN: {e} in parsing {u} [{filter}]")

                    self.bar_main['value'] = self.bar_main['maximum']
                    time.sleep(6)
                    self.bar_main.config(mode='indeterminate')
                    self.bar_main.start()
                    self.txt_main.insert(INSERT, f"\nTOTAL VIDEO FOUND, {len(urls)}")
                    self.txt_main.insert(INSERT, f"\nFOR NOW PLAYLIST, CAN ONLY DOWNLOAD MP3 FORMAT\n")
                    if len(self.check_downloaded) != len(list(urls)):
                        self.txt_main.insert(INSERT, f"\n{len(self.check_downloaded)} not download yet", 'warning')
                        self.txt_main.insert(INSERT, f"\n")
                        for d in self.check_downloaded:
                            self.txt_main.insert(INSERT, f"{d}", 'warning')
                            self.txt_main.insert(INSERT, f"\n")
                        print(f"NOT DOWNLOAD SONG = {self.check_downloaded}")
                    self.txt_main.config(state=DISABLED)
                    self.b_mp3.config(state=NORMAL, command=lambda: Thread(target=self.mp3Download,
                                                                           args=(self.URL, self.DATA)).start(), )
                    self.b_clear.config(state=NORMAL)

                Thread(target=totalVideo).start()
            except Exception as e:
                print(traceback.format_exc())
                self.txt_main.config(state=NORMAL)
                self.txt_main.delete("1.0", "end")
                self.txt_main.insert(INSERT, f"\nEXCEPTION HAPPEN: {e} \n {traceback.format_exc()}")
                self.txt_main.insert(INSERT, f"\nSAVE IN LOG FILE: {e}")
                self.txt_main.config(state=DISABLED)

    def mp3Download(self, url=[], data={}):

        def thumbPhoto(image_url):
            try:
                response = requests.get(image_url, timeout=10)
                return response.content
            except Exception as e:
                print(f"Thumbnail download failed: {e}")
                return None

        def startDownload(url):
            try:
                self.txt_main.config(state=NORMAL)
                self.txt_main.delete("1.0", "end")
                self.txt_main.insert(INSERT, f"Starting Downloading {len(url)} file(s)\n")
                self.txt_main.config(state=DISABLED)
                c = k = 0
                total_mb = 0
                start_time = time.time()
                self.lbl_remainTime.config(text=f'REMAIN TIMES: Calculating...')
                
                for u in url:
                    START = time.time()
                    try:
                        global MaxFileSize

                        def show_progress_bar_pytubefix(chunk=None, file_handle=None, bytes_remaining=None):
                            try:
                                loading = int(100 - (100 * (bytes_remaining / MaxFileSize)))
                                if loading < 0:
                                    loading = 0
                                self.bar_main.config(mode='determinate')
                                self.bar_main['value'] = loading
                            except:
                                pass

                        def show_progress_bar_ytdlp(d):
                            try:
                                if d['status'] == 'downloading':
                                    percent = 0
                                    
                                    # Method 1: Use bytes if available (most accurate)
                                    if 'total_bytes' in d and d['total_bytes'] and 'downloaded_bytes' in d:
                                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                                    
                                    # Method 2: Parse percentage string (fallback)
                                    elif '_percent_str' in d:
                                        try:
                                            # Clean the percentage string of ANSI codes and extract number
                                            import re
                                            clean_percent = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str'])
                                            clean_percent = re.sub(r'[^\d.]', '', clean_percent)
                                            if clean_percent:
                                                percent = float(clean_percent)
                                        except:
                                            return
                                    
                                    # Method 3: Use _percent if available
                                    elif '_percent' in d:
                                        percent = d['_percent']
                                    
                                    else:
                                        return  # No usable progress data
                                    
                                    # Update the progress bar safely
                                    self.bar_main.config(mode='determinate')
                                    self.bar_main['value'] = min(max(percent, 0), 100)
                                    
                                elif d['status'] == 'finished':
                                    self.bar_main['value'] = 100
                                    
                            except Exception:
                                # Silently ignore progress bar errors to prevent console spam
                                pass


                        # Initialize variables
                        artist = album = "UNKNOWN"
                        song = title = "UNKNOWN"
                        thumbnail = None
                        upload_date = None
                        uploader = "UNKNOWN"
                        duration = 0
                        file_size_mb = 0.0
                        use_pytubefix = True
                        video_stream = None
                        
                        self.txt_main.config(state=NORMAL)
                        self.txt_main.insert(INSERT, f"\n{k + 1}. Processing: {u}\n")
                        self.txt_main.config(state=DISABLED)

                        # STEP 1: Extract metadata using pytubefix first
                        pytubefix_success = False
                        try:
                            self.txt_main.config(state=NORMAL)
                            self.txt_main.insert(INSERT, f"Extracting info with pytubefix...\n")
                            self.txt_main.config(state=DISABLED)
                            
                            yt = YouTube(u, client="WEB", on_progress_callback=show_progress_bar_pytubefix)
                            title = yt.title
                            uploader = yt.author
                            upload_date = str(yt.publish_date) if yt.publish_date else 'Unknown'
                            duration = yt.length
                            thumbnail = yt.thumbnail_url
                            
                            # Try to get music metadata from pytubefix
                            try:
                                if yt.metadata and len(yt.metadata) > 0:
                                    artist = yt.metadata[0].get('Artist', uploader) or uploader
                                    album = yt.metadata[0].get('Album', 'Unknown') or 'Unknown'
                                else:
                                    artist = uploader
                                    album = 'Unknown'
                            except:
                                artist = uploader
                                album = 'Unknown'
                            
                            song = title
                            video_stream = yt.streams.filter(only_audio=True).first()
                            
                            if video_stream and video_stream.filesize:
                                MaxFileSize = video_stream.filesize
                                file_size_mb = float(video_stream.filesize / 1000000).__round__(2)
                            elif duration:
                                MaxFileSize = duration * 32000  # Rough estimate
                                file_size_mb = float((duration * 128 * 1000) / 8000000).__round__(2)
                            
                            pytubefix_success = True
                            use_pytubefix = True
                            
                            self.txt_main.config(state=NORMAL)
                            self.txt_main.insert(INSERT, f"✓ Pytubefix info extraction successful\n")
                            self.txt_main.config(state=DISABLED)
                            
                        except Exception as e:
                            pytubefix_success = False
                            use_pytubefix = False
                            print(f"Pytubefix info extraction failed: {e}")
                            self.txt_main.config(state=NORMAL)
                            self.txt_main.insert(INSERT, f"✗ Pytubefix failed: {str(e)[:100]}...\n")
                            self.txt_main.insert(INSERT, f"Trying yt_dlp for info extraction...\n")
                            self.txt_main.config(state=DISABLED)

                        # FALLBACK: Extract metadata using yt_dlp (only if pytubefix failed)
                        if not pytubefix_success:
                            try:
                                import yt_dlp
                                
                                ydl_opts_info = {
                                    'quiet': True,
                                    'no_warnings': True,
                                    'extract_flat': False,
                                }
                                
                                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                                    info = ydl.extract_info(u, download=False)
                                    
                                    title = info.get('title', 'Unknown')
                                    uploader = info.get('uploader', info.get('channel', 'Unknown'))
                                    upload_date = info.get('upload_date', 'Unknown')
                                    duration = info.get('duration', 0)
                                    thumbnail = info.get('thumbnail', None)
                                    
                                    # Extract music metadata
                                    artist = info.get('artist', info.get('creator', uploader))
                                    album = info.get('album', info.get('playlist_title', 'Unknown'))
                                    song = info.get('track', title)
                                    
                                    # Estimate file size
                                    if 'filesize' in info and info['filesize']:
                                        MaxFileSize = info['filesize']
                                        file_size_mb = float(info['filesize'] / 1000000).__round__(2)
                                    elif duration:
                                        MaxFileSize = duration * 32000
                                        file_size_mb = float((duration * 128 * 1000) / 8000000).__round__(2)
                                    
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"✓ yt_dlp info extraction successful\n")
                                self.txt_main.config(state=DISABLED)
                                
                            except Exception as e2:
                                print(f"Both pytubefix and yt_dlp info extraction failed: {e2}")
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"✗ Both info extraction methods failed: {str(e2)[:100]}...\n", 'error')
                                self.txt_main.config(state=DISABLED)
                                self.logSave(f"Info extraction failed for {u}: {e} | {e2}", traceback.format_exc(), "info_extraction_error")
                                k += 1
                                continue

                        # Display extracted info
                        self.txt_main.config(state=NORMAL)
                        self.txt_main.insert(INSERT, f"Title: {title}\n")
                        self.txt_main.insert(INSERT, f"Artist: {artist}\n")
                        self.txt_main.insert(INSERT, f"Album: {album}\n")
                        self.txt_main.insert(INSERT, f"Uploader: {uploader}\n")
                        self.txt_main.insert(INSERT, f"Upload Date: {upload_date}\n")
                        if duration:
                            self.txt_main.insert(INSERT, f"Duration: {duration//60}:{duration%60:02d}\n")
                        self.txt_main.insert(INSERT, f"Size: ~{file_size_mb}MB\n")
                        self.txt_main.config(state=DISABLED)
                        
                        # Clean filename for saving
                        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        if not clean_title:
                            clean_title = f"youtube_audio_{k}"
                        check_path = f'{self.DOWNLOAD_DIR}/{clean_title}.mp3'
                        
                        # Check if file already exists
                        if os.path.exists(os.path.abspath(check_path)):
                            self.txt_main.config(state=NORMAL)
                            self.txt_main.insert(INSERT, f"WARNING: FILE ALREADY EXISTS", 'warning')
                            self.txt_main.insert(INSERT, f"\n{os.path.abspath(check_path)}\n")
                            self.logSave(e=f"@{u}@", log_name="video-url-check")
                            self.txt_main.insert(INSERT, f"Saved in logs\n")
                            self.txt_main.config(state=DISABLED)
                            k += 1
                            continue

                        # STEP 2: Download the file
                        download_success = False
                        new_file = None
                        
                        # Try pytubefix download first
                        if use_pytubefix and video_stream:
                            try:
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"Downloading with pytubefix...\n")
                                self.txt_main.config(state=DISABLED)
                                
                                out_file = video_stream.download(output_path=os.path.abspath(self.DOWNLOAD_DIR))
                                base, ext = os.path.splitext(out_file)
                                new_file = base + '.mp3'
                                
                                # Convert to MP3 using pydub
                                AudioSegment.from_file(out_file).export(new_file, format="mp3")
                                os.remove(out_file)
                                download_success = True
                                
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"✓ Pytubefix download successful!\n")
                                self.txt_main.config(state=DISABLED)
                                
                            except Exception as e:
                                print(f"Pytubefix download failed: {e}")
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"✗ Pytubefix download failed: {str(e)[:100]}...\n")
                                self.txt_main.insert(INSERT, f"Trying yt_dlp download...\n")
                                self.txt_main.config(state=DISABLED)
                        
                        
                        # FALLBACK: yt_dlp download
                        if not download_success:
                            try:
                                import yt_dlp
                                
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"Downloading with yt_dlp...\n")
                                self.txt_main.config(state=DISABLED)
                                
                                # Different approach - download audio directly without postprocessing
                                ydl_opts = {
                                    'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
                                    'outtmpl': f'{os.path.abspath(self.DOWNLOAD_DIR)}/{clean_title}_temp.%(ext)s',
                                    'progress_hooks': [show_progress_bar_ytdlp],
                                    'quiet': True,
                                    'no_color': True,
                                    'no_warnings': True,
                                    'extractaudio': True,
                                    'audioformat': 'mp3',
                                    'embed_subs': False,
                                    'writesubtitles': False,
                                }
                                
                                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                    info = ydl.extract_info(u, download=True)
                                    downloaded_file = ydl.prepare_filename(info)
                                
                                # Convert to MP3 using pydub (more reliable than ffmpeg)
                                try:
                                    from pydub import AudioSegment
                                    
                                    # Find all temporary files (various extensions)
                                    temp_files = []
                                    for file in os.listdir(self.DOWNLOAD_DIR):
                                        if file.startswith(f'{clean_title}_temp'):
                                            temp_files.append(file)
                                    
                                    if temp_files:
                                        # Use the first found temp file
                                        temp_file = os.path.join(self.DOWNLOAD_DIR, temp_files[0])
                                        new_file = f'{os.path.abspath(self.DOWNLOAD_DIR)}/{clean_title}.mp3'
                                        
                                        # Convert to MP3
                                        audio = AudioSegment.from_file(temp_file)
                                        audio.export(new_file, format="mp3", bitrate="192k")
                                        
                                        # Clean up ALL temporary files
                                        for temp_file_name in temp_files:
                                            temp_file_path = os.path.join(self.DOWNLOAD_DIR, temp_file_name)
                                            try:
                                                os.remove(temp_file_path)
                                                m4a_file = os.path.join(self.DOWNLOAD_DIR, clean_title + ".m4a")
                                                if os.path.exists(m4a_file):
                                                    os.remove(m4a_file)
                                                print(f"Cleaned up: {temp_file_name}")
                                            except Exception as cleanup_error:
                                                print(f"Could not remove {temp_file_name}: {cleanup_error}")

                                        
                                        download_success = True
                                        
                                        self.txt_main.config(state=NORMAL)
                                        self.txt_main.insert(INSERT, f"✓ yt_dlp download successful!\n")
                                        self.txt_main.config(state=DISABLED)
                                    else:
                                        raise Exception("Downloaded file not found")
                                        
                                except Exception as conv_error:
                                    print(f"Audio conversion failed: {conv_error}")
                                    
                                    # Clean up any leftover temp files from failed conversion
                                    try:
                                        temp_files = [f for f in os.listdir(self.DOWNLOAD_DIR) if f.startswith(f'{clean_title}_temp')]
                                        for temp_file_name in temp_files:
                                            temp_file_path = os.path.join(self.DOWNLOAD_DIR, temp_file_name)
                                            try:
                                                os.remove(temp_file_path)
                                                print(f"Cleaned up failed conversion file: {temp_file_name}")
                                            except:
                                                pass
                                    except:
                                        pass
                                    
                                    # Fallback: try direct download as MP3
                                    try:
                                        ydl_opts_direct = {
                                            'format': 'bestaudio',
                                            'outtmpl': f'{os.path.abspath(self.DOWNLOAD_DIR)}/{clean_title}.%(ext)s',
                                            'progress_hooks': [show_progress_bar_ytdlp],
                                            'quiet': True,
                                            'no_warnings': True,
                                        }
                                        
                                        with yt_dlp.YoutubeDL(ydl_opts_direct) as ydl:
                                            ydl.download([u])
                                        
                                        # Find downloaded file and convert/rename to .mp3 if needed
                                        downloaded_files = [f for f in os.listdir(self.DOWNLOAD_DIR) if f.startswith(clean_title) and not f.endswith('.mp3')]
                                        if downloaded_files:
                                            downloaded_file = os.path.join(self.DOWNLOAD_DIR, downloaded_files[0])
                                            new_file = f'{os.path.abspath(self.DOWNLOAD_DIR)}/{clean_title}.mp3'
                                            
                                            # Check if it's an audio file that needs conversion
                                            file_ext = os.path.splitext(downloaded_file)[1].lower()
                                            if file_ext in ['.m4a', '.webm', '.ogg', '.wav', '.aac']:
                                                try:
                                                    # Convert to MP3 using pydub
                                                    audio = AudioSegment.from_file(downloaded_file)
                                                    audio.export(new_file, format="mp3", bitrate="192k")
                                                    os.remove(downloaded_file)  # Remove original file
                                                    print(f"Converted {file_ext} to MP3 and cleaned up original")
                                                except Exception as conv_error2:
                                                    # If conversion fails, just rename
                                                    os.rename(downloaded_file, new_file)
                                                    print(f"Conversion failed, renamed {file_ext} to .mp3")
                                            else:
                                                # Just rename to .mp3
                                                os.rename(downloaded_file, new_file)
                                            
                                            download_success = True
                                            
                                            self.txt_main.config(state=NORMAL)
                                            self.txt_main.insert(INSERT, f"✓ yt_dlp direct download successful!\n")
                                            self.txt_main.config(state=DISABLED)
                                        else:
                                            raise Exception("No file downloaded")
                                            
                                    except Exception as direct_error:
                                        # Final cleanup attempt - remove any leftover files
                                        try:
                                            leftover_files = [f for f in os.listdir(self.DOWNLOAD_DIR) 
                                                            if clean_title in f and not f.endswith('.mp3')]
                                            for leftover_file in leftover_files:
                                                leftover_path = os.path.join(self.DOWNLOAD_DIR, leftover_file)
                                                try:
                                                    os.remove(leftover_path)
                                                    print(f"Final cleanup: removed {leftover_file}")
                                                except:
                                                    pass
                                        except:
                                            pass
                                            
                                        raise Exception(f"Both conversion methods failed: {conv_error} | {direct_error}")
                                        
                            except Exception as e:
                                print(f"yt_dlp download also failed: {e}")
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"✗ ALL DOWNLOAD METHODS FAILED: {str(e)[:100]}...\n", 'error')
                                self.txt_main.config(state=DISABLED)
                                self.logSave(f"All download methods failed for {u}: {e}", traceback.format_exc(), "download_error")
                                
                                # Final cleanup attempt for any leftover files
                                try:
                                    cleanup_files = [f for f in os.listdir(self.DOWNLOAD_DIR) 
                                                   if clean_title in f and not f.endswith('.mp3')]
                                    for cleanup_file in cleanup_files:
                                        cleanup_path = os.path.join(self.DOWNLOAD_DIR, cleanup_file)
                                        try:
                                            os.remove(cleanup_path)
                                            print(f"Emergency cleanup: removed {cleanup_file}")
                                        except:
                                            pass
                                except:
                                    pass
                                    
                                k += 1
                                continue
                        
                        # STEP 3: Add MP3 metadata and cover art
                        if download_success and new_file and os.path.exists(new_file):
                            try:
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"Adding metadata and cover art...\n")
                                self.txt_main.config(state=DISABLED)
                                
                                audiofile = eyed3.load(new_file)
                                if audiofile.tag is None:
                                    audiofile.initTag()

                                # Set basic metadata
                                audiofile.tag.artist = artist
                                audiofile.tag.album = album
                                audiofile.tag.album_artist = artist
                                audiofile.tag.title = song
                                
                                # Add upload date as recording date
                                try:
                                    if upload_date and upload_date != 'Unknown':
                                        if len(upload_date) >= 4:
                                            audiofile.tag.recording_date = upload_date[:4]
                                except:
                                    pass

                                # Download and set thumbnail
                                if thumbnail:
                                    try:
                                        thumb_path = os.path.join(self.DOWNLOAD_DIR, 'temp_thumb.jpg')
                                        thumb_data = thumbPhoto(thumbnail)
                                        if thumb_data:
                                            with open(thumb_path, 'wb') as f:
                                                f.write(thumb_data)
                                            
                                            with open(thumb_path, 'rb') as f:
                                                audiofile.tag.images.set(ImageFrame.FRONT_COVER, f.read(), 'image/jpeg')
                                            
                                            os.remove(thumb_path)
                                            
                                            self.txt_main.config(state=NORMAL)
                                            self.txt_main.insert(INSERT, f"✓ Thumbnail added\n")
                                            self.txt_main.config(state=DISABLED)
                                    except Exception as e:
                                        print(f"Thumbnail error: {e}")
                                        self.txt_main.config(state=NORMAL)
                                        self.txt_main.insert(INSERT, f"⚠ Thumbnail failed: {str(e)[:50]}...\n", 'warning')
                                        self.txt_main.config(state=DISABLED)

                                audiofile.tag.save()
                                
                            except Exception as e:
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"⚠ Metadata error: {str(e)[:100]}...\n", 'warning')
                                self.txt_main.config(state=DISABLED)
                                print(f"Metadata error: {traceback.format_exc()}")

                            # Success message
                            self.txt_main.config(state=NORMAL)
                            self.txt_main.insert(INSERT, f"✅ SUCCESSFUL", 'success')
                            self.txt_main.insert(INSERT, f" >> {new_file}\n")
                            self.txt_main.config(state=DISABLED)
                            
                            c += 1
                            total_mb += file_size_mb
                            self.lbl_totalMB.config(text=f"TOTAL DOWNLOAD: {total_mb.__round__(2)} MB")

                        k += 1
                        self.lbl_barMain.config(text=f'{c}/{len(url)}')
                        self.PLAYLIST.append(u)
                        
                    except Exception as e:
                        print(f"Unexpected error: {traceback.format_exc()}")
                        self.txt_main.config(state=NORMAL)
                        self.txt_main.insert(INSERT, f"❌ UNSUCCESSFUL", 'error')
                        self.txt_main.insert(INSERT, f"\n{str(e)[:200]}...\n")
                        self.logSave(f"@{u}@ \n{e}", traceback.format_exc(), "url Exception", "url-e")
                        self.txt_main.insert(INSERT, f"Saved in logs\n")
                        self.txt_main.config(state=DISABLED)
                        k += 1

                    # Update time estimation
                    self.txt_main.see(INSERT)
                    END = time.time()
                    if c > 0:
                        avg_time = (time.time() - start_time) / c / 60
                        remaining_files = len(url) - k
                        estimated_time = round(avg_time * remaining_files, 2)
                        self.lbl_remainTime.config(text=f'REMAIN TIME: {estimated_time} Minute(s)')
                    
                # Final completion message
                self.txt_main.config(state=NORMAL)
                self.txt_main.insert(INSERT, f"\n\n🎉 DOWNLOAD COMPLETED 🎉\n")
                self.txt_main.insert(INSERT, f"Successfully downloaded: {c}/{len(url)} files\n")
                self.txt_main.insert(INSERT, f"Total size: {total_mb.__round__(2)} MB\n")
                total_time = (time.time() - start_time) / 60
                self.txt_main.insert(INSERT, f"Total time: {total_time.__round__(2)} minutes\n")
                self.txt_main.config(state=DISABLED)
                
                self.lbl_remainTime.config(text='COMPLETED!')
                self.bar_main.config(mode='indeterminate')
                self.bar_main.start()

            except Exception as e:
                self.logSave(e, traceback.format_exc(), "startDownload Exception")
                self.txt_main.config(state=NORMAL)
                self.txt_main.insert(INSERT, f"\n\n💥 FATAL ERROR OCCURRED", 'error')
                self.txt_main.insert(INSERT, f"\nPLEASE CHECK LOG FOLDER WITH DATE-TODAY")
                self.txt_main.config(state=DISABLED)

        
        if self.ONE:
            Thread(target=startDownload, args=(url,)).start()
        elif self.MANY:
            win = Toplevel(self.WIN)
            win.geometry('400x400')
            win.title("MP3 DOWNLOAD")
            win.iconphoto(False, PhotoImage(file='images/youtube.png'))

            canvas = Canvas(win)
            frameA = Frame(canvas)
            canvas.create_window((0, 0), window=frameA, anchor="nw")

            scroll_y = Scrollbar(canvas, orient='vertical', command=canvas.yview)
            scroll_x = Scrollbar(win, orient='horizontal', command=canvas.xview)
            canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

            data_len = len(data)
            c = r = int(math.sqrt(data_len + 1))
            while True:
                if c * r < data_len + 1:
                    r += 1
                else:
                    break

            var_all = StringVar()
            Checkbutton(frameA, text="SELECT ALL", variable=var_all, onvalue='ALL', offvalue='0').grid(column=0, row=0)
            checkbox_data = {0: var_all}

            a = 0
            b = k = 1
            for s in data:
                var = StringVar()
                Checkbutton(frameA, text=s, variable=var, onvalue=data[s], offvalue='0').grid(column=a, row=b)
                checkbox_data[k] = var
                if b == c - 2:
                    a += 1
                    b = 0
                b += 1
                k += 1

            frameA.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            canvas.pack(side="top", fill="both", expand=True)
            scroll_x.pack(side='bottom', fill="x", expand=True)
            scroll_y.pack(side="right", fill="y")

            def checkDownload():
                URL_FILTER = []
                for j in checkbox_data:
                    chk = str(checkbox_data[j].get())
                    if chk == 'ALL':
                        for d in data:
                            URL_FILTER.append(data[d])
                        break
                    elif chk != '0' and chk != '':
                        URL_FILTER.append(chk)
                if len(URL_FILTER) == 0:
                    showwarning('PLEASE TICK', 'YOU NEED TO TICK THE BOX')
                else:
                    win.destroy()
                    Thread(target=startDownload, args=(URL_FILTER,)).start()

                print(URL_FILTER)

            Button(win, text="OK", style=self.style1, command=checkDownload).pack(side='bottom', expand=True)



    def logSave(self, e='', trace='', title='', log_name=''):
        catch_date = datetime.now().strftime('%d-%m-%Y')
        if log_name != '':
            log_path = f"logs/log_{log_name}"
        else:
            log_path = f"logs/log_{catch_date}"

        if os.path.exists(os.path.abspath(log_path)):
            with open(log_path, 'a') as log:
                if title != '':
                    log.write("---------------------------" * 5 + "\n")
                log.write(f"{e}\n")
                log.write(f"{trace}\n")
                log.close()
        else:
            with open(log_path, 'w') as log:
                log.write(f"{catch_date}\n")
                if title != '':
                    log.write("---------------------------" * 5 + "\n")
                    log.write(f"{title}\n")
                    log.write("---------------------------" * 5 + "\n")
                log.write(f"{e}\n")
                log.write(f"{trace}\n")
                log.close()


if __name__ == '__main__':
    engine = Tk()
    GUI(engine)


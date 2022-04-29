from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import *
from tkinter.messagebox import *
from PIL import Image, ImageTk
from pytube import YouTube, Playlist
from datetime import datetime, date
from threading import Thread
from pydub import AudioSegment
import eyed3
from eyed3.id3.frames import ImageFrame
import traceback, sys, os, validators, time, sv_ttk ,math, requests


class GUI():
    def __init__(self, master):
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
        if not os.path.exists(os.path.abspath(self.DOWNLOAD_DIR)):
            os.makedirs(self.DOWNLOAD_DIR)
            if not os.path.exists(os.path.abspath('logs')):
                os.makedirs('logs')

        # main frame
        self.f_up = Frame(self.WIN, relief=RAISED, width=100, height=100)
        self.f_up.pack(fill=BOTH)
        self.f_mid = Frame(self.WIN, width=100, height=100, relief=RAISED)
        self.f_mid.pack(fill=BOTH, expand=True)
        self.f_end = Frame(self.WIN, relief=RAISED)
        self.f_end.pack(fill=BOTH)

        # f_up
        Label(self.f_up, text='Search URL: ',font=('Comic sans ms', 10, 'normal', 'italic')).grid(row=0, column=1,sticky=W+E)
        self.e_search = Entry(self.f_up)
        self.e_search.grid(row=0, column=2, sticky=W+E, ipadx=self.W/3 + 14, ipady=4)
        self.b_clear = Button(self.f_up, text="Clear", style=self.style1)
        self.b_clear.grid(row=0, column=3, sticky=W + E)

        # f_mid
        self.bar_main = Progressbar(self.f_mid,orient='horizontal',mode='indeterminate', maximum=100,  length=self.W/4)
        self.bar_main.start()
        self.bar_main.grid(row=0, column=0,  ipadx=self.W/3, ipady=4, sticky=W+E)
        self.lbl_barMain = Label(self.f_mid, text='0/0',font=('Comic sans ms', 13, 'bold', 'italic'), background='cyan', foreground='grey')
        self.lbl_barMain.grid(row=0, column=1,sticky=W+E,ipadx=25)
        self.txt_main = ScrolledText(self.f_mid, undo=True)
        self.txt_main.grid(row=1, column=0,  sticky='nsew', columnspan= 2)
        self.txt_main.config(state=DISABLED)
        self.lbl_totalMB = Label(self.f_mid, text='TOTAL DOWNLOAD: 0.0 MB',font=('Comic sans ms', 13, 'normal', 'italic'), background='grey')
        self.lbl_totalMB.grid(row=2, column=0,sticky=W+E)
        f_mid2 = Canvas(self.f_mid, relief=RAISED)
        f_mid2.grid(row=3, column=0,sticky=W+E)
        self.b_mp3 = Button(f_mid2, text="MP3", style=self.style1, state='disabled')
        self.b_mp3.grid(row=0, column=0,sticky=W+E)
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
        self.b_exit = Button(self.f_end, text="Exit",style=self.style1, command=lambda: sys.exit())
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
            if len(self.e_search.get()) == 0:
                # print('zero')
                self.e_search.after(1000, checkSTR)
            elif 'youtube.com' not in self.e_search.get():
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
                        Thread(target=self.youtubeData, args=(URL, )).start()
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
                    self.txt_main.delete("1.0","end")
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
                self.txt_main.insert(END, f"\nVIDEO LENGTH, {round(float(engine.length)/60, 2)} minute")
                self.URL = [url]
                self.txt_main.config(state=DISABLED)
                self.b_mp3.config(state=NORMAL,command=lambda: Thread(target=self.mp3Download, args=(self.URL, )).start(), )
            except Exception as e:
                print(traceback.format_exc())
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
                self.txt_main.insert(INSERT, f"\nPLAYLIST FOUND, {engine.title} @{engine.owner} #{engine.playlist_id}@")
                urls = engine.video_urls
                self.URL = urls
                def totalVideo():
                    self.txt_main.insert(INSERT, f"\nCALCULATE TOTAL VIDEO... PLEASE WAIT..")
                    self.bar_main.config(mode='determinate')
                    self.b_clear.config(state=DISABLED)
                    self.bar_main['value'] = 0
                    self.bar_main.start(1000)
                    for u in list(urls):
                        engine = YouTube(u)
                        char_list = [str(engine.title)[j] for j in range(len(str(engine.title))) if ord(str(engine.title)[j]) in range(65536)]
                        filter = ''
                        for j in char_list:
                            filter = filter + j
                        self.DATA[filter] = u
                        print(filter)
                        self.bar_main['value'] = float(len(self.DATA)/len(urls)) * 100
                        self.lbl_barMain.config(text=f'0/{len(self.DATA)}')

                    self.bar_main['value'] = self.bar_main['maximum']
                    time.sleep(6)
                    self.bar_main.config(mode='indeterminate')
                    self.bar_main.start()
                    self.txt_main.insert(INSERT, f"\nTOTAL VIDEO FOUND, {len(urls)}")
                    self.txt_main.insert(INSERT, f"\nFOR NOW PLAYLIST, CAN ONLY DOWNLOAD MP3 FORMAT")
                    self.txt_main.config(state=DISABLED)
                    self.b_mp3.config(state=NORMAL,command=lambda: Thread(target=self.mp3Download, args=(self.URL, self.DATA)).start(), )
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
            response = requests.get(image_url)
            img_data = response.content
            return img_data

        def startDownload(url):
            try:
                self.txt_main.config(state=NORMAL)
                self.txt_main.delete("1.0", "end")
                self.txt_main.insert(INSERT, f"Starting Downloading {len(url)} file(s)\n")
                self.txt_main.config(state=DISABLED)
                c = k = 0
                total_mb = 0
                start_time = time.time()
                for u in url:
                    try:
                        global MaxFileSize

                        def show_progress_bar(chunk=None, file_handle=None, bytes_remaining=None):
                            # loadingPercent label configure value %
                            loading = int(100 - (100 * (bytes_remaining / MaxFileSize)))
                            if loading < 0:
                                loading = 0
                            self.bar_main.config(mode='determinate')
                            self.bar_main['value'] = loading

                        yt = YouTube(u, on_progress_callback=show_progress_bar)
                        thumbnail = yt.thumbnail_url
                        # print(yt.metadata)
                        try:
                            artist = yt.metadata[0]['Artist']
                            album = yt.metadata[0]['Album']
                            song = yt.title
                        except:
                            artist = album = "UNKNOWN"
                            song = yt.title
                        print(artist, album, song)
                        video = yt.streams.filter(only_audio=True).first()
                        MaxFileSize = video.filesize
                        FILESIZEMB = float(MaxFileSize / 1000000).__round__(2)

                        self.txt_main.config(state=NORMAL)
                        self.txt_main.insert(INSERT, f"\n{k + 1}. Now Downloading {yt.title} >> {FILESIZEMB}MB")
                        self.txt_main.insert(INSERT, f"\nartist: {artist}\nalbum: {album}\nsong: {song} \n>>>>>")
                        self.txt_main.config(state=DISABLED)
                        check_path = f'{self.DOWNLOAD_DIR}/{yt.title}.mp3'
                        if os.path.exists(os.path.abspath(check_path)):
                            self.txt_main.config(state=NORMAL)
                            self.txt_main.insert(INSERT, f"WARNING FILE EXIST", 'warning')
                            self.txt_main.insert(INSERT, f" >>\n{os.path.abspath(check_path)}\n")
                            self.logSave(e=f"@{u}@", log_name="video-url-check")
                            self.txt_main.insert(INSERT, f"\n saved in logs\n")
                            self.txt_main.config(state=DISABLED)
                            k += 1
                        else:
                            out_file = video.download(output_path=os.path.abspath("download"))
                            base, ext = os.path.splitext(out_file)
                            new_file = base + '.mp3'

                            # os.rename(out_file, new_file)
                            AudioSegment.from_file(out_file).export(new_file, format="mp3")
                            os.remove(out_file)

                            # mp3 cover
                            try:
                                thumb_path = self.DOWNLOAD_DIR + '/temp.jpg'
                                audiofile = eyed3.load(new_file)
                                if (audiofile.tag == None):
                                    audiofile.initTag()


                                try:
                                    with open(thumb_path, 'wb') as file:
                                        thumb_data = thumbPhoto(thumbnail)
                                        file.write(thumb_data)

                                except error:
                                    pass

                                audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(thumb_path, 'rb').read(),
                                                         'image/jpeg')
                                audiofile.tag.artist = artist
                                audiofile.tag.album = album
                                audiofile.tag.album_artist = artist
                                audiofile.tag.title = song

                                audiofile.tag.save()
                                os.remove(thumb_path)
                            except Exception as e:
                                self.txt_main.config(state=NORMAL)
                                self.txt_main.insert(INSERT, f"CANT CREATE MP3 COVER PHOTO", 'warning')
                                self.txt_main.insert(INSERT, f" >>\n{e}\n")
                                self.txt_main.config(state=DISABLED)
                                print(traceback.format_exc())

                            self.txt_main.config(state=NORMAL)
                            self.txt_main.insert(INSERT, f"SUCCESSFUL", 'success')
                            self.txt_main.insert(INSERT, f" >>\n{new_file}\n")
                            self.txt_main.config(state=DISABLED)
                            c += 1
                            k += 1
                            self.lbl_barMain.config(text=f'{c}/{len(url)}')
                            total_mb += FILESIZEMB
                            self.lbl_totalMB.config(text=f"TOTAL DOWNLOAD: {total_mb.__round__(2)} MB (estimated)")

                    except Exception as e:
                        print(traceback.format_exc())
                        self.txt_main.config(state=NORMAL)
                        self.txt_main.insert(INSERT, f"UNSUCCESSFUL", 'error')
                        self.txt_main.insert(INSERT, f"\n{e}")
                        self.logSave(f"@{u}@ \n{e}", traceback.format_exc(), "url Exception", "url-e")
                        self.logSave(e=f"@{u}@", log_name="video-url-check")
                        self.txt_main.insert(INSERT, f"\n saved in logs\n")
                        self.txt_main.config(state=DISABLED)
                        self.lbl_barMain.config(text=f'{c}/{len(url)}')
                        k += 1
                    self.txt_main.see(INSERT)

                self.txt_main.config(state=NORMAL)
                end_time = time.time()
                time_taken = float((end_time - start_time) / 60).__round__(2)
                self.txt_main.insert(INSERT, f"\n\n{c} file(s) SUCCESS", 'success')
                self.txt_main.insert(INSERT, f"\n{len(url) - c} files FAIL", 'error')
                self.txt_main.insert(INSERT, f"\n{time_taken} minute(s) to download {c} file(s)", 'success')

                self.txt_main.config(state=DISABLED)
                self.e_search.config(state='normal')
                self.e_search.delete(0, 'end')
                self.bar_main.config(mode='indeterminate')
                self.b_mp3.config(state=DISABLED)

            except Exception as e:
                self.logSave(e, traceback.format_exc(), "startDownload Exception")
                self.txt_main.config(state=NORMAL)
                self.txt_main.insert(INSERT, f"\n\nUPPER EXCEPTION HAPPEN", 'error')
                self.txt_main.insert(INSERT, f"\n PLEASE CHECK LOG FOLDER WITH DATE-TODAY")
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
            c = r = int(math.sqrt(data_len+ 1))
            while True:
                if c*r < data_len+1:
                    r += 1
                else:
                    break

            var_all = StringVar()
            Checkbutton(frameA, text="SELECT ALL", variable=var_all, onvalue='ALL', offvalue='0').grid(column=0, row=0)
            checkbox_data = {0:var_all}

            b = 0
            a = k = 1
            for s in data:
                var = StringVar()
                Checkbutton(frameA, text=s, variable=var, onvalue=data[s], offvalue='0').grid(column=a, row=b)
                checkbox_data[k] = var
                if a == c-2:
                    b+=1
                    a = 0
                a += 1
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
                    Thread(target=startDownload, args=(URL_FILTER, )).start()

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


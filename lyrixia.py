# Size per char = 8*5
from blessed import Terminal
from pathlib import Path
from math import floor
import threading
import pygame
import pygame.mixer
import copy
import time
import json
import os

# ASCII DICTIONARY 
from Dictionary.basic_ascii import alphabet

term = Terminal()
stop_event = threading.Event()
terminal_lock = threading.Lock()
stopwatch = ''
def progress_watcher():
    global stopwatch
    while not stop_event.is_set():
        elapsed = time.monotonic() - stopwatch

        with terminal_lock:
            song_progress(
                elapsed,
                song_duration,
                term.width,
                term.height
            )
            
            if elapsed >= song_duration or not pygame.mixer.music.get_busy():
                stop_event.set()
                break

        stop_event.wait(0.1)
   
# DEBUG TERMINAL SIZE 
# print(f"{term.width} x {term.height}")
# print(f"Center = {term.width//2} x {term.height//2}")

font_height = 5
limiter = 8
INITIALtext = "dikala hujan turun deras pekatnya"
INITIALtext = INITIALtext.upper()

buffers = []
longBuffers = []

def clear_terminal():
    # 'nt' indicates Windows; otherwise, use 'clear' for macOS/Linux
    os.system('cls' if os.name == 'nt' else 'clear')

clear_terminal()

def refresh_line(initx,inity,width,height):
     for i in range(height):
          with term.location(initx, inity+i):
               print(" "*width, sep='', end="", flush=True)
               
def reset_menu():
    initY = 0
    for i in range(term.height):
            with term.location(0,initY):
                    print(" " * term.width)
                    initY+=1
    for i in range(menu_margin):
        print(
            " " * term.width, flush=True
        )

    print(" " * int((term.width-len(title))/2) + title, flush=True)
    print(" " * int((term.width-len(version))/2) + version, flush=True)
    print(" ")
    print(" " * int(((term.width)-menu_width)/2) + prompt, flush=True)
    print(" ")
    for i in range(len(songs)):
        print(" " * int(((term.width)-menu_width)/2) + f'[{i+1}] '+ songs[i])

    for i in range(menu_margin-4):
        print(
            " " * term.width, flush=True
        )
    total_margin = menu_margin+menu_height+(menu_margin-4)
    with term.location(0, total_margin):
                    print("-" * (int(term.width)-1), flush=True)
    print(" ")
    print(" ")

def song_progress(elapsed, duration, term_width, term_height):
     margin_side = 40
     margin_bottom = 5
     
     width = term_width - margin_side*2
     width -= 2
     
     progress = min(elapsed/duration, 1)
     bar = int(progress*width)
     
     start_minute = floor(int(elapsed))//60
     start_seconds = round(floor(int(elapsed))%60)
    
     remain_minute = floor(int(duration-elapsed))//60
     remain_seconds = round(floor(int(duration-elapsed))%60)
     
     time_marker = [start_minute,start_seconds,remain_minute,remain_seconds]
     
     for i in range(4):
         if len(str(time_marker[i])) == 1:
             time_marker[i] = f"0{str(time_marker[i])}"

     start = f"{time_marker[0]}.{time_marker[1]}"
     remain = f"{time_marker[2]}.{time_marker[3]}"
     
     if elapsed == duration:
        print(term.home + term.clear, end="")
     else:
        with term.location(margin_side, (term_height-margin_bottom-1)):
            print(" " + start  + " " * (width-(len(start)+len(remain)+1)) + "-" + remain,
                  end="",
                  flush=True
                  )     
        with term.location(margin_side, (term_height-margin_bottom)):
            print(
                 "[" + "O" *(bar) + '-' * int((width-bar)) + ']',
                 end="",
            )
        

               
def render_ui(term_width, term_height):
     margin = 3
     controls = "🞀-  (||)  -🞂"
     
     with term.location(int(term_width/2)-int(len(controls)/2), term_height-margin):
          print("🞀-  ||  -🞂",
                end="",
                flush=True
                )

def renderTiktok(inputText, delay=1):
    global buffer, longBuffers
    text = copy.deepcopy(inputText)
    text = text.split()
    buffers = [[]]
    selector = 0
    counter = 0
    
    for i in range(len(text)):
        buffers[selector] += text[i]
        if i != len(text)-1:
            buffers[selector] += ' '
        counter += len(text[i])
        if counter >= limiter:
            buffers += [[]]
            counter = 0
            selector += 1

    # print(*buffers, sep='')

    longBuffers = []
    for buffer in range(len(buffers)):
        longBuffers += [[]]
        for fh in range(font_height):
            longBuffers[buffer] += [[]]
            for i in range(len(buffers[buffer])):
               try:
                    longBuffers[buffer][fh] += alphabet[buffers[buffer][i]][fh]
               except:
                    longBuffers[buffer][fh] += alphabet['EMPTY']
            # print(*longBuffers[buffer][fh], sep='')

    with terminal_lock:
     
         render_ui(term.width, term.height)
         box_width = max((len(row[0]) for row in longBuffers), default=0)
         box_height = font_height*len(longBuffers)+1*len(longBuffers)

         initX = (term.width - box_width) // 2
         initY = (term.height - box_height) // 2
         pointerY = copy.deepcopy(initY)
         # x = (term.width - term.length(pesan)) // 2
         # y = term.height // 2

         for i in range(len(longBuffers)):
             for j in range(len(longBuffers[i])):
                 with term.location(initX, pointerY):
                     print(*longBuffers[i][j], sep='', end="", flush=True)
                     pointerY+=1
             with term.location(initX, pointerY):
                 print(" ", sep='', end='', flush=True)
                 pointerY+=1
                 
    time.sleep(delay)
    with terminal_lock:
          refresh_line(initX,initY,box_width,box_height)

# 1 -> Line, 2 -> Lines
songs = []
songs_path = Path("Songs")

# PLACE FILES HERE
def get_songs():
    for item in songs_path.iterdir():
        if item.is_dir():
            songs.append(item.name)
            
get_songs()
clear_terminal()

pygame.mixer.init()
title = "LYRIXIA"
version = "Ver. 0.9 beta"
prompt = "Founds Songs:"
menu_width = 45
menu_height = 5+len(songs)
menu_margin = (term.height-menu_height)//2
while True:
    
    reset_menu()
    selected = input(" Select>  ")

    valid_select = [str(i+1) for i in range(len(songs))]
    if selected not in valid_select:
        clear_terminal()
        pass
    else:
        try:
            jsonPATH = f"./Songs/{songs[int(selected)-1]}/{songs[int(selected)-1]}.json"
            mp3PATH = f"./Songs/{songs[int(selected)-1]}/{songs[int(selected)-1]}.mp3"

            with open(jsonPATH, encoding="utf-8") as f:
                data = json.load(f)

            pygame.mixer.music.load(mp3PATH)

            currentLine = ""
            lines = []
            delays = []
            for line in data:
                for w in line["words"]:
                    currentLine += w["text"]
                    currentLine += " "
                    delays.append(w["delay"])
                lines += [currentLine]
                currentLine = ""

            currentWord = 0
            print(term.home + term.clear, end="")
            song_duration = pygame.mixer.Sound(mp3PATH).get_length()

            with term.fullscreen(), term.hidden_cursor():
                 pygame.mixer.music.play()
                 stopwatch = time.monotonic()
                 
                 stop_event.clear()

                 progress_thread = threading.Thread(target=progress_watcher, daemon=True)
                 progress_thread.start()  

                 try:
                      for line in range(len(lines)):
                          splitted = lines[line].split()
                          for word in range(len(splitted)):
                              joined = " ".join(splitted[0:word+1])
                              renderTiktok(joined, delays[currentWord])

                              currentWord +=1 
                          if stop_event.is_set():
                              break
                 finally:
                      pygame.mixer.music.stop()
                      stop_event.set()
                      progress_thread.join()
                      print(term.home + term.clear, end="")
                      reset_menu()
        except:
            pygame.mixer.music.stop()
            stop_event.set()
            progress_thread.join()
            print(term.home + term.clear, end="")
            reset_menu()
# progressiveText = ""
# initsplit = INITIALtext.split(' ')
# for i in range(len(initsplit)-1):
#     joined = " ".join(initsplit[0:i+1])
#     renderTiktok(joined,1.4)
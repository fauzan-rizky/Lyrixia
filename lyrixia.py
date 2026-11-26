# Size per char = 8*5
from blessed import Terminal
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

def progress_watcher():
    while not stop_event.is_set():
        elapsed = time.monotonic() - stopwatch

        with terminal_lock:
            song_progress(
                elapsed,
                song_duration,
                term.width,
                term.height
            )

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

def song_progress(elapsed, duration, term_width, term_height):
     margin_side = 5
     margin_bottom = 5
     
     width = term_width - margin_side*2
     
     progress = min(elapsed/duration, 1)
     bar = int(progress*width)
     
     with term.location(margin_side, term_height-margin_bottom):
          print(
               "█" * bar + '-' * int((width-bar)),
               end="",
               flush=True
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

# PLACE FILES HERE
jsonPATH = "./HighForever/HighForever.json"
mp3PATH = "./HighForever/HighForever.mp3"

with open(jsonPATH, encoding="utf-8") as f:
    data = json.load(f)
    
pygame.mixer.init()
pygame.mixer.music.load(mp3PATH)

clear_terminal()

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
     
     progress_thread = threading.Thread(target=progress_watcher)
     progress_thread.start()  
     
     try:
          for line in range(len(lines)):
              splitted = lines[line].split()
              for word in range(len(splitted)):
                  joined = " ".join(splitted[0:word+1])
                  renderTiktok(joined, delays[currentWord])
                  
                  currentWord +=1 
     except:
          stop_event.set()
          progress_thread.join()
# progressiveText = ""
# initsplit = INITIALtext.split(' ')
# for i in range(len(initsplit)-1):
#     joined = " ".join(initsplit[0:i+1])
#     renderTiktok(joined,1.4)
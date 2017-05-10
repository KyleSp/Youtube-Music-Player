#run in IDLE: exec(open("YoutubeMusicPlayer2.py").read())

import time
from random import randint
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from tkinter import *

#constants
PYTHON_DIR = "C:\\Users\\Kyle\\AppData\\Local\\Programs\\Python\\Python36\\"
PLAYLISTS_DIR = PYTHON_DIR + "Python Programs\\Playlists\\"
CHROME_DRIVER_DIR = PYTHON_DIR + "selenium\\webdriver\\chrome\\chromedriver"
AD_BLOCK_DIR = PYTHON_DIR + "Python Programs\\AdBlock_v2.59.crx"

def secToMinSec(sec):
	newMin = 0
	while sec >= 60:
		newMin += 1
		sec -= 60
	newSec = sec
	newMin2 = str(newMin)
	newSec2 = str(newSec)
	if newSec < 10:
		newSec2 = "0" + str(newSec)
	return newMin2, newSec2

class Playlist:
	def __init__(self, playlistName, playlistIndex):
		#name and index
		self.playlistName = playlistName
		self.cleanPlaylistName = ""
		self.playlistIndex = playlistIndex
		
		#read from file
		self.songWebsite = ""
		self.songNames = []
		self.songURLs = []
		self.songStarts = []
		self.songStops = []
	
	def getCleanPlaylistName(self):
		cleanPlaylistName = self.playlistName.replace("_", " ")
		cleanPlaylistName = cleanPlaylistName.replace(".txt", "")
		self.cleanPlaylistName = cleanPlaylistName
	
	def readInPlaylistFile(self):
		inFile = open(PLAYLISTS_DIR + self.playlistName)
		lines = inFile.readlines()
		self.songWebsite = lines[0]
		for i in range(1, len(lines)):
			words = lines[i].split()
			self.songNames.append(words[0])
			self.songURLs.append(words[1])
			self.songStarts.append(int(words[2]))
			self.songStops.append(int(words[3]))
		for i in range(0, len(self.songNames)):
			self.songNames[i] = self.songNames[i].replace("_", " ")

class Window:
	def __init__(self, driver, playlist):
		self.driver = driver
		
		self.playlist = playlist
		
		self.playOrder = list(range(0, len(self.playlist.songNames)))
		
		self.running = True
		self.skip = False
		self.back = False
		self.shuffle = False
		self.replay = False
		
		self.songStrs = []
		self.songLabels = []
	
	def play(self):
		time.sleep(2)
		print("START")
		i = 0
		while i < len(self.playOrder):
			songLength = self.playlist.songStops[self.playOrder[i]] - self.playlist.songStarts[self.playOrder[i]]
			url = self.playlist.songWebsite + self.playlist.songURLs[self.playOrder[i]] + str(self.playlist.songStarts[self.playOrder[i]])
			
			mins, secs = secToMinSec(songLength)
			self.songStrs[0].set(self.playlist.cleanPlaylistName)
			self.songStrs[1].set(self.playlist.songNames[self.playOrder[i]])
			self.songStrs[2].set("(" + mins + ":" + secs + ")")
			songName = self.playlist.cleanPlaylistName + " - " + self.playlist.songNames[self.playOrder[i]] + " (" + mins + ":" + secs + ")"
			print(songName)
			
			self.driver.get(url)
			
			#wait for song to finish or be skipped or shuffled
			t = 0
			while t < songLength and not self.skip and not self.shuffle and not self.replay and not (self.back and i > 0):
				while not self.running:
					self.app.update()
					if self.skip or self.shuffle or self.replay or (self.back and i > 0):
						break
					time.sleep(0.1)
				t += 0.1
				self.app.update()
				time.sleep(0.1)
				
			if self.shuffle:
				i = -1
			elif self.replay:
				i -= 1
			elif self.back and i > 0:
				i -= 2
			self.skip = False
			self.shuffle = False
			self.replay = False
			self.back = False
			self.running = True
			self.pauseVar.set("Pause")
			
			i += 1
			
		print("END")
	
	def windowInit(self):
		#make window
		self.root = Tk()
		self.root.title("Youtube Music Player")
		
		SCREEN_WIDTH = self.root.winfo_screenwidth()
		SCREEN_HEIGHT = self.root.winfo_screenheight()
		
		#set window to constant size
		self.root.resizable(width = False, height = False)
		
		#move window to specific location and set size
		WINDOW_WIDTH = 400
		WINDOW_HEIGHT = 400
		#x = (SCREEN_WIDTH / 2) - (WINDOW_WIDTH / 2)
		#y = (SCREEN_HEIGHT / 2) - (WINDOW_HEIGHT / 2)
		x = 0
		y = 0
		self.root.geometry("%dx%d+%d+%d" % (WINDOW_WIDTH, WINDOW_HEIGHT, x, y))
		
		#bring window to the top
		self.root.lift()
		
		#make frame
		self.app = Frame(self.root)
		self.app.grid()
		self.app.configure(background = "gray")
		
		#title label
		self.title = Label(self.app, text = "Kyle's Youtube Music Player", width = 30, font = "-weight bold")
		self.title.grid(row = 0, column = 0, columnspan = 4)
		
		#pause button
		self.pauseVar = StringVar()
		self.pauseVar.set("Pause")
		self.pauseButton = Button(self.app, font = "-weight bold", textvariable = self.pauseVar, command = self.pauseButtonPressed)
		self.pauseButton.grid(row = 1, column = 3, sticky = E)
		
		#back button
		self.backButton = Button(self.app, font = "-weight bold", text = "Back", command = self.backButtonPressed)
		self.backButton.grid(row = 2, column = 3, sticky = E)
		
		#next button
		self.skipButton = Button(self.app, font = "-weight bold", text = "Skip", command = self.skipButtonPressed)
		self.skipButton.grid(row = 3, column = 3, sticky = E)
		
		#replay button
		self.replayButton = Button(self.app, font = "-weight bold", text = "Replay", command = self.replayButtonPressed)
		self.replayButton.grid(row = 4, column = 3, sticky = E)
		
		#shuffle button
		self.shuffleButton = Button(self.app, font = "-weight bold", text = "Shuffle", command = self.shuffleButtonPressed)
		self.shuffleButton.grid(row = 5, column = 3, sticky = E)
		
		#change playlist dropdown menu
		self.playlistMenuChoice = StringVar()
		self.playlistMenuChoice.set(self.playlist.playlistName)
		
		cleanPlaylistNames = []
		for playlist in playlists:
			cleanPlaylistNames.append(playlist.cleanPlaylistname)
		
		self.playlistMenu = OptionMenu(self.app, playlistMenuChoice, *cleanPlaylistNames, command = self.playlistMenuChanged)
		self.playlistMenu.grid(row = 6, column = 0, sticky = W)
		
		#song playing
		for i in range(0, 3):
			self.songStrs.append(StringVar())
			self.songLabels.append(Label(self.app, font = "-weight bold", textvariable = self.songStrs[i]))
			self.songLabels[i].grid(row = 1 + i, column = 0, columnspan = 2, sticky = W)
	
	def pauseButtonPressed(self):
		self.driver.find_element_by_tag_name("body").send_keys("k")
		self.running = not self.running
		if not self.running:
			self.pauseVar.set("Play")
			print("pause")
		else:
			self.pauseVar.set("Pause")
			print("play")
	
	def backButtonPressed(self):
		print("back")
		self.back = True
	
	def skipButtonPressed(self):
		print("skip")
		self.skip = True
	
	def replayButtonPressed(self):
		print("replay")
		self.replay = True
	
	def shuffleButtonPressed(self):
		print("shuffle")
		self.shuffle = True
		numSongs = len(self.playlist.songNames)
		songsUsed = []
		songListIndices = []
		for i in range(0, numSongs):
			songsUsed.append(False)
		i = 0
		while i < numSongs:
			r = randint(0, numSongs - 1)
			if not songsUsed[r]:
				songListIndices.append(r)
				songsUsed[r] = True
				i += 1
		self.playOrder = songListIndices[:]
	
	def playlistMenuChanged(self):
		print("playlist menu changed")


#read file playlists
playlistNames = os.listdir(PLAYLISTS_DIR)

#prompt user choice of playlist
playlists = []
prompt = "Enter Playlist Number:\n("
for i in range(0, len(playlistNames)):
	#initialize playlists
	playlist = Playlist(playlistNames[i], i)
	playlist.getCleanPlaylistName()
	playlist.readInPlaylistFile()
	playlists.append(playlist)
	
	prompt += str(i) + " = " + playlist.cleanPlaylistName
	if (i != len(playlistNames) - 1):
		prompt += ", "

prompt += "): "

chosenPlaylistIndex = int(input(prompt))

#webdriver initialization
chromedriver = CHROME_DRIVER_DIR
os.environ["webdriver.chrome.driver"] = chromedriver
adblock = webdriver.ChromeOptions()
adblock.add_extension(AD_BLOCK_DIR)
driver = webdriver.Chrome(chromedriver, chrome_options = adblock)

#make new tab
driver.find_element_by_tag_name("body").send_keys(Keys.COMMAND + "t")

#tkinter window initialization
window = Window(driver, playlists[chosenPlaylistIndex])
window.windowInit()

#play songs
window.play()

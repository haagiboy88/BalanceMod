#---------------
# BalanceMod.py
# by Zamiel
#---------------

# Configuration
version = 1.0

# Imports
import _winreg
import shutil, os, ConfigParser
from string import ascii_uppercase, digits
from Tkinter import *
from tkFileDialog import askopenfilename
from random import seed, randint, choice, shuffle
from PIL import Image, ImageFont, ImageDraw, ImageTk
from binascii import crc32
from subprocess import call

# Subroutines
def regkey_value(path, name="", start_key = None): # Used to find the path to Steam
	if isinstance(path, str):
		path = path.split("\\")
	if start_key is None:
		start_key = getattr(_winreg, path[0])
		return regkey_value(path[1:], name, start_key)
	else:
		subkey = path.pop(0)
	with _winreg.OpenKey(start_key, subkey) as handle:
		assert handle
		if path:
			return regkey_value(path, name, handle)
		else:
			desc, i = None, 0
			while not desc or desc[0] != name:
				desc = _winreg.EnumValue(handle, i)
				i += 1
			return desc[1]

def newRandomSeed():
	global seedIsRNG
	seed()
	seedIsRNG = ''.join(choice(ascii_uppercase + digits) for _ in range(6))
	entryseed.set(seedIsRNG)

def installMod():
	# trim the whitespace on the string if there is any
	s = entryseed.get()
	entryseed.set(s.strip().encode('ascii','replace'))

	# if no seed entered, generate one
	if entryseed.get() == '':
		newRandomSeed()

	# set the RNG seed
	global dmseed
	dmseed = entryseed.get()
	seed(crc32(dmseed))

	# write the seed to a text file
	with open("seed.txt", "w") as f:
		f.write(dmseed)

	# Remove all the files and folders EXCEPT packed and dmtmpfolder
	for resourcefile in os.listdir(resourcepath):
		if resourcefile != 'packed' and resourcefile != dmtmpfolder :
			if os.path.isfile(os.path.join(resourcepath, resourcefile)):
				os.unlink(os.path.join(resourcepath, resourcefile))
			elif os.path.isdir(os.path.join(resourcepath, resourcefile)):
				shutil.rmtree(os.path.join(resourcepath, resourcefile))

	# Copy game files
	for resourcefile in os.listdir('gameFiles'):
		if os.path.isfile(os.path.join('gameFiles', resourcefile)):
			shutil.copyfile(os.path.join('gameFiles', resourcefile), os.path.join(resourcepath, resourcefile))
		elif os.path.isdir(os.path.join('gameFiles', resourcefile)):
			shutil.copytree(os.path.join('gameFiles', resourcefile), os.path.join(resourcepath, resourcefile))

	if practiceStart == '':
		itemBuildNum = str(1)
		# TODO - random generation here
	else:
		if not os.path.isdir('startFiles/' + practiceStart):
			print "Error: You specified an incorrect practiceStart value in the options.ini file. Exiting..."
			sys.exit()
		else:
			itemBuildNum = practiceStart

	# Copy room specific files
	for resourcefile in os.listdir('startFiles/' + itemBuildNum):
		if os.path.isfile(os.path.join('startFiles/' + itemBuildNum, resourcefile)):
			shutil.copyfile(os.path.join('startFiles/' + itemBuildNum, resourcefile), os.path.join(resourcepath, resourcefile))
		elif os.path.isdir(os.path.join('startFiles/' + itemBuildNum, resourcefile)):
			shutil.copytree(os.path.join('startFiles/' + itemBuildNum, resourcefile), os.path.join(resourcepath, resourcefile))

	# If Rebirth is running, kill it
	FNULL = open(os.devnull, 'w')
	call(['taskkill', '/im', 'isaac-ng.exe', '/f'], stderr=FNULL)

	# re/start Rebirth
	if os.path.exists(resourcepath + "/../../../../steam.exe"):
		call([resourcepath + '/../../../../steam.exe', '-applaunch', '250900'])
	elif os.path.exists(resourcepath + "/../isaac-ng.exe"):
		call(resourcepath + '/../isaac-ng.exe')

def uninstallMod():
	# remove all the files and folders EXCEPT packed and dmtmpfolder
	for resourcefile in os.listdir(resourcepath):
		if resourcefile != 'packed' and resourcefile != dmtmpfolder :
			if os.path.isfile(os.path.join(resourcepath, resourcefile)):
				os.unlink(os.path.join(resourcepath, resourcefile))
			elif os.path.isdir(os.path.join(resourcepath, resourcefile)):
				shutil.rmtree(os.path.join(resourcepath, resourcefile))

	# copy all the files and folders EXCEPT the 'packed' folder to dmtmpfolder
	for dmtmpfile in os.listdir(os.path.join(resourcepath, dmtmpfolder)):
		if os.path.isfile(os.path.join(resourcepath, dmtmpfolder, dmtmpfile)):
			shutil.copyfile(os.path.join(resourcepath, dmtmpfolder, dmtmpfile), os.path.join(resourcepath, dmtmpfile))
		elif os.path.isdir(os.path.join(resourcepath, dmtmpfolder, dmtmpfile)):
			shutil.copytree(os.path.join(resourcepath, dmtmpfolder, dmtmpfile), os.path.join(resourcepath, dmtmpfile))

	# remove the temporary directory we created
	shutil.rmtree(os.path.join(resourcepath, dmtmpfolder))
	sys.exit()

def setcustompath():
	# open file dialog
	isaacpath = askopenfilename()
	# check that the file is isaac-ng.exe and the path is good
	if isaacpath [-12:] == "isaac-ng.exe" and os.path.exists(isaacpath[0:-12] + 'resources'):
		customs.set('options', 'custompath', isaacpath [0:-12] + 'resources')
		with open('options.ini', 'wb') as configfile:
			customs.write(configfile)
		feedback.set("Your Balance Mod path has been correctly set.\nClose this window and restart Balance Mod.")
	else:
		feedback.set("That file appears to be incorrect. Please try again to find isaac-ng.exe")
	root.update_idletasks()





# root is the GUI, entryseed is the rng seed, feedback is the message for user
root = Tk()
entryseed = StringVar()
feedback = StringVar()
d6start = BooleanVar()
# just the gui icon and title
root.iconbitmap("otherFiles/libra.ico")
root.title("Balance Mod v" + str(version))

# Import options.ini
customs = ConfigParser.RawConfigParser()
customs.read('options.ini')
if not customs.has_section('options'):
	customs.add_section('options')

# Check for a practice start
practiceStart = ''

if customs.has_option('options', 'practiceStart'):
	practiceStart = customs.get('options', 'practiceStart')

# check and set the paths for file creation, exit if not found
currentpath = os.getcwd()
SteamPath = regkey_value(r"HKEY_CURRENT_USER\Software\Valve\Steam", "SteamPath")
# first check custom path
if customs.has_option('options', 'custompath') and os.path.exists(customs.get('options', 'custompath')):
	resourcepath = customs.get('options', 'custompath')
# then check steam path
elif os.path.isdir(SteamPath + "/steamapps/common/The Binding of Isaac Rebirth/resources"):
	resourcepath = SteamPath + "/steamapps/common/The Binding of Isaac Rebirth/resources"
else: # if neither, then go through the motions of writing and saving a new path to options
	feedback.set("")
	Message(root, justify = CENTER, font = "font 10", text = "Balance Mod was unable to find your resources directory.\nNavigate to the program isaac-ng.exe in your Steam directories.", width = 600).grid(row = 0, pady = 10)
	Message(root, justify = CENTER, font = "font 12", textvariable = feedback, width = 600).grid(row = 1)
	Button(root, font = "font 12", text = "Navigate to isaac-ng.exe", command = setcustompath).grid(row = 2, pady = 10)
	Message(root, justify = LEFT, font = "font 10", text = "Example:\nC:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth\isaac-ng.exe", width = 800).grid(row = 3, padx = 15, pady = 10)
	mainloop()
	sys.exit()

# Check if you're inside the resources path. give warning and close if necessary.
if os.path.normpath(resourcepath).lower() in os.path.normpath(currentpath).lower():
	Message(root, justify = CENTER, font = "font 12", text = "Balance Mod is in your resources directory.\nMove it elsewhere before running.", width = 600).grid(row = 0, pady = 10)
	mainloop()
	sys.exit()

# Create a folder to temporarily hold files until Balance Mod is done
seed()
dmtmpfolder = '../resources_tmp' + str(randint(1000000000,9999999999))
if not os.path.exists(os.path.join(resourcepath, dmtmpfolder)):
	os.mkdir(os.path.join(resourcepath, dmtmpfolder))

# Copy all the files and folders EXCEPT the 'packed' folder to dmtmpfolder
for resourcefile in os.listdir(resourcepath):
	if resourcefile != 'packed' and resourcefile != dmtmpfolder:
		try:
			if os.path.isfile(os.path.join(resourcepath, resourcefile)):
				shutil.copyfile(os.path.join(resourcepath, resourcefile), os.path.join(resourcepath, dmtmpfolder, resourcefile))
			elif os.path.isdir(os.path.join(resourcepath, resourcefile)):
				shutil.copytree(os.path.join(resourcepath, resourcefile), os.path.join(resourcepath, dmtmpfolder, resourcefile))
		except Exception, e:
			print e

# Button to install mod and restart Rebirth
dmiconimage = Image.open("otherFiles/libra.png")
dmicon = ImageTk.PhotoImage(dmiconimage)
Button(root, image = dmicon, text = '   Start Balance Mod   ', compound = "left", command = installMod, font = "font 16").grid(row = 1, pady = 30, columnspan = 2)

# Instructions
Message(root, justify = CENTER, text = "Rebirth will open when you start the mod.", font = "font 13", width = 475).grid(row = 2, column = 0, columnspan = 2, padx = 20)
Message(root, justify = CENTER, text = "Keep this program open while playing.", font = "font 13", width = 475).grid(row = 3, column = 0, columnspan = 2, padx = 20)
Message(root, justify = CENTER, text = "Rebirth will returns to normal when this program is closed.\n\n", font = "font 13", width = 500).grid(row = 4, column = 0, columnspan = 2, padx = 20)

# Uninstall mod files when the window is closed
root.protocol("WM_DELETE_WINDOW", uninstallMod)

# Infinite loop
mainloop()

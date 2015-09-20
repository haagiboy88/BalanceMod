#---------------
# BalanceMod.py
# by Zamiel
#---------------

# Configuration
version = 1.0

# Imports
import _winreg
import shutil, os, ConfigParser
import xml.etree.ElementTree as ET
from string import ascii_uppercase, digits
from Tkinter import *
from tkFileDialog import askopenfilename
from random import seed, randint, choice, shuffle
from PIL import Image, ImageFont, ImageDraw, ImageTk
from binascii import crc32
from subprocess import call

# Constants
items_icons_path = "otherFiles/collectibles/"
trinket_icons_path = "otherFiles/trinkets/"
builds = ET.parse('otherFiles/builds.xml').getroot()

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

# **** Practice Window Stuff ****

# Load the image from the provided path in a format suitable for Tk
def get_image(path):
	from os import sep
	image = _image_library.get(path)
	if image is None:
		canonicalized_path = path.replace('/', sep).replace('\\', sep)
		image = ImageTk.PhotoImage(Image.open(canonicalized_path))
		_image_library[path] = image
	return image

# Return an item dictionary based on the provided item id or name
def get_item_dict(id):
	id = str(id)
	if id.isdigit():
		for child in items_info:
			if child.attrib['id'] == id and child.tag != 'trinket':
				return child.attrib
	else:
		for child in items_info:
			if child.attrib['name'] == id and child.tag != 'trinket':
				return child.attrib

# Given an item name or id, return its id
def get_item_id(id):
	id = str(id)
	if id.isdigit():
		for child in items_info:
			if child.attrib['id'] == id and child.tag != 'trinket':
				return child.attrib['id']
	else:
		for child in items_info:
			if child.attrib['name'] == id and child.tag != 'trinket':
				return child.attrib['id']

# Given an item name or id, return its id
def get_trinket_id(id):
	id = str(id)
	if id.isdigit():
		for child in items_info:
			if child.attrib['id'] == id and child.tag == 'trinket':
				return child.attrib['id']
	else:
		for child in items_info:
			if child.attrib['name'] == id and child.tag == 'trinket':
				return child.attrib['id']

# Given the name or id of an item, return its icon image
def get_item_icon(id):
	dict = get_item_dict(id)
	if dict:
		icon_file = dict['gfx'][:16].lower() + '.png'
		return get_image(items_icons_path + icon_file)
	else:
		return get_image(items_icons_path + "questionmark.png")

# Given the name or id of a trinket, return its icon image
def get_trinket_icon(id):
	id = str(id)
	if id.isdigit():
		for child in items_info:
			if child.attrib['id'] == id and child.tag == 'trinket':
				return get_image(trinket_icons_path + child.attrib['gfx'])
	else:
		for child in items_info:
			if child.attrib['name'] == id and child.tag == 'trinket':
				return get_image(trinket_icons_path + child.attrib['gfx'])
	return get_image(trinket_icons_path + "questionmark.png")

# Process the hearts image into the individual heart icons and return them
def get_heart_icons():
	hearts_list = [None]*10
	hearts = Image.open('otherFiles/ui_hearts.png')
	# 16x16 left upper right lower
	hearts_list[0] = ImageTk.PhotoImage(hearts.crop((0,0,16,16)))  # Full red
	hearts_list[1] = ImageTk.PhotoImage(hearts.crop((16,0,32,16))) # Half red
	hearts_list[2] = ImageTk.PhotoImage(hearts.crop((32,0,48,16))) # Empty heart
	hearts_list[3] = ImageTk.PhotoImage(hearts.crop((48,0,64,16))) # left half eternal
	hearts_list[4] = ImageTk.PhotoImage(hearts.crop((64,0,80,16))) # right half eternal overlap
	hearts_list[5] = ImageTk.PhotoImage(hearts.crop((0,16,16,32))) # full soul
	hearts_list[6] = ImageTk.PhotoImage(hearts.crop((16,16,32,32)))# half soul
	hearts_list[7] = ImageTk.PhotoImage(hearts.crop((32,16,48,32)))# full black
	hearts_list[8] = ImageTk.PhotoImage(hearts.crop((48,16,64,32)))# half black
	return hearts_list

# Display the practice mode window
def practiceWindow(root=None):
	def close_window():
		global pWin
		pWin.destroy()
		pWin = None

	def select_build(event):
		global practiceStart
		widget = event.widget
		while not hasattr(widget, 'build'):
			widget = widget._nametowidget(widget.winfo_parent())
		build = widget.build
		practiceStart = build.attrib['id']
		close_window()
		installMod()

	def make_hearts_frame(parent, redhearts, soulhearts, blackhearts, heartcontainers):
		hearts_frame = Canvas(parent)
		current = 0

		if redhearts:
			fullreds = int(int(redhearts)/2)
			for i in range(0, fullreds):
				widget = Label(hearts_frame)
				widget.image = hearts_list[0]
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(column=current, row=0)
				current+=1
			if int(redhearts)%2 == 1:
				widget = Label(hearts_frame)
				widget.image = hearts_list[1]
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(column=current, row=0)
				current+=1
		if heartcontainers:
			for i in range(0, int(heartcontainers)/2):
				widget = Label(hearts_frame)
				widget.image = hearts_list[2]
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(column=current, row=0)
				current+=1
		if soulhearts:
			fullsouls = int(int(soulhearts)/2)
			for i in range(0, fullsouls):
				widget = Label(hearts_frame)
				widget.image = hearts_list[5]
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(column=current, row=0)
				current+=1
			if int(soulhearts)%2 == 1:
				widget = Label(hearts_frame)
				widget.image = hearts_list[6]
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(column=current, row=0)
				current+=1
		if blackhearts:
			fullblacks = int(int(blackhearts)/2)
			for i in range(0, fullblacks):
				widget = Label(hearts_frame)
				widget.image = hearts_list[7]
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(column=current, row=0)
				current+=1
			if int(blackhearts)%2 == 1:
				widget = Label(hearts_frame)
				widget.image = hearts_list[8]
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(column=current, row=0)
				current+=1
		return hearts_frame

	global pWin
	if not pWin:
		pWin = Toplevel(root) if root else Tk()
		pWin.title("Practice Selector")
		pWin.resizable(False,True)
		pWin.protocol("WM_DELETE_WINDOW", close_window)

		# Initialize the scrolling canvas
		canvas = Canvas(pWin, borderwidth=0)
		scrollbar = Scrollbar(canvas, orient="vertical", command=canvas.yview)
		scrollbar.pack(side="right", fill="y")
		canvas.configure(yscrollcommand=scrollbar.set)
		canvas.configure(scrollregion=canvas.bbox("all"), width=200, height=200)
		canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)

		# Scrolling code taken from:
		# http://stackoverflow.com/questions/16188420/python-tkinter-scrollbar-for-frame
		imageBox = LabelFrame(canvas, borderwidth=0)
		interior_id = canvas.create_window(0, 0, window=imageBox, anchor=NW)

		# track changes to the canvas and frame width and sync them, also updating the scrollbar
		def _configure_interior(event):
			# update the scrollbars to match the size of the inner frame
			size = (imageBox.winfo_reqwidth(), imageBox.winfo_reqheight())
			canvas.config(scrollregion="0 0 %s %s" % size)
			if imageBox.winfo_reqwidth() != canvas.winfo_width():
				# update the canvas's width to fit the inner frame
				canvas.config(width=imageBox.winfo_reqwidth())
		imageBox.bind('<Configure>', _configure_interior)
		def _configure_canvas(event):
			if imageBox.winfo_reqwidth() != imageBox.winfo_width():
				# update the inner frame's width to fill the canvas
				canvas.itemconfigure(interior_id, width=canvas.winfo_width())
		canvas.bind('<Configure>', _configure_canvas)

		hearts_list = get_heart_icons()
		Label(imageBox, text="Click a build to play it", font="font 32 bold").pack(pady=5)
		for child in builds:
			redhearts = child.attrib.get('redhearts')
			soulhearts = child.attrib.get('soulhearts')
			blackhearts = child.attrib.get('blackhearts')
			heartcontainers = child.attrib.get('heartcontainers')
			items = child.attrib.get('items')
			if items:
				items = items.split(' + ')
			trinket = child.attrib.get('trinket')
			removed_items = child.attrib.get('removed')
			if removed_items:
				removed_items = removed_items.split(' + ')
			# Draw the build frame here
			build_frame = LabelFrame(imageBox)
			build_frame.build = child
			build_frame.bind("<Button-1>", select_build)
			# ID
			widget = Label(build_frame, text=child.attrib['id'], font="font 32 bold" )
			widget.bind("<Button-1>", select_build)
			widget.grid(row=0, rowspan=3)
			# Items
			widget = Label(build_frame, text="Items: ")
			widget.bind("<Button-1>", select_build)
			widget.grid(row=0, column=1, sticky=E)
			items_frame = Canvas(build_frame)
			for i, item in enumerate(items):
				widget = Label(items_frame)
				widget.image = get_item_icon(item)
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(row=0, column=i)
			if trinket:
				widget = Label(items_frame)
				widget.image = get_trinket_icon(trinket)
				widget.configure(image=widget.image)
				widget.bind("<Button-1>", select_build)
				widget.grid(row=0, column=len(items)+1)
			items_frame.grid(row=0, column=2, sticky=W)
			# Health
			widget = Label(build_frame, text="Health: ")
			widget.bind("<Button-1>", select_build)
			widget.grid(row=1, column=1, sticky=E)
			hearts_frame = make_hearts_frame(build_frame, redhearts, soulhearts, blackhearts, heartcontainers)
			hearts_frame.bind("<Button-1>", select_build)
			hearts_frame.grid(row=1, column=2, sticky=W)
			# Removed Items
			widget = Label(build_frame, text="Removed Items: ")
			widget.bind("<Button-1>", select_build)
			widget.grid(row=2, column=1, sticky=E)
			if removed_items:
				removed_items_frame = Canvas(build_frame)
				for i, item in enumerate(removed_items):
					widget = Label(removed_items_frame)
					widget.image = get_item_icon(item)
					widget.configure(image=widget.image)
					widget.bind("<Button-1>", select_build)
					widget.grid(row=2, column=i)
				removed_items_frame.grid(row=2, column=2, sticky=W)
			build_frame.pack(pady=5, fill=X)

		pWin.update() # Update the window so the widgets give their actual dimensions
		height = max(min(int(pWin.winfo_vrootheight() * 2 / 3), imageBox.winfo_height() + 4),
				pWin.winfo_height())
		width = imageBox.winfo_width() + scrollbar.winfo_width() + 2
		pWin.geometry('%dx%d' % (width, height))
		pWin.update() # Then update with the newly calculated height
		pWin.mainloop()


# **** Main window and installation functions ****

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
		current_file = os.path.join('gameFiles', resourcefile)
		if os.path.isfile(current_file) and current_file not in ['players.xml', 'items.xml', 'itempools.xml']:
			shutil.copyfile(current_file, os.path.join(resourcepath, resourcefile))
		elif os.path.isdir(current_file):
			shutil.copytree(current_file, os.path.join(resourcepath, resourcefile))

	if practiceStart == '':
		itemBuildNum = str(1)
		# TODO - random generation here
	else:
		itemBuildNum = practiceStart

	current_build = None
	for build in builds:
		if build.attrib['id'] == itemBuildNum:
			current_build = build
			break

	players_xml = ET.parse('gameFiles/players.xml')
	players_info = players_xml.getroot()
	itempools_xml = ET.parse('gameFiles/itempools.xml')
	itempools_info = itempools_xml.getroot()

	# Parse the build info
	items = current_build.get('items')
	trinket = current_build.get('trinket')
	removed_items = current_build.get('removed')
	redhearts = current_build.get('redhearts')
	soulhearts = current_build.get('soulhearts')
	blackhearts = current_build.get('blackhearts')
	heartcontainers = current_build.get('heartcontainers')

	if items or trinket:
		for child in players_info:
			if child.attrib['name']=='Isaac':
				if items:
					for item in items.split(' + '):
						id = get_item_id(item)
						child.attrib['items'] += ("," + id)
				if trinket:
						child.set('trinket', get_trinket_id(trinket))
				break

	if removed_items:
		removed_items = removed_items.split(' + ')
		for i in range(0, len(removed_items)):
			removed_items[i] = get_item_id(removed_items[i])
		for pool in itempools_info:
			for item in pool.findall('Item'):
				if item.attrib['Id'] in removed_items:
					pool.remove(item)

	# We use the Black Candle to set the player's health
	for child in items_info:
		if child.attrib['name']=='Black Candle':
			child.set('hearts', redhearts)
			child.set('maxhearts', str(int(redhearts) + int(redhearts)%2 + (int(heartcontainers) if heartcontainers else 0)))
			if soulhearts:
				child.set('soulhearts', soulhearts)
			if blackhearts:
				child.set('blackhearts', blackhearts)

	players_xml.write(os.path.join(resourcepath, 'players.xml'))
	itempools_xml.write(os.path.join(resourcepath, 'itempools.xml'))
	items_xml.write(os.path.join(resourcepath, 'items.xml'))

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

# Item images for the practice selection window
_image_library = {}
pWin = None # Keep track of whether the practice window is open
# Item info for the practice selection window
items_xml = ET.parse('gameFiles/items.xml')
items_info = items_xml.getroot()

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
Button(root, image = dmicon, text = '   Start Balance Mod   ', compound = "left", command = installMod, font = "font 16").grid(row = 1, pady = 30, columnspan = 1)
Button(root, image = get_item_icon('Undefined'), text = '   Practice Mode   ', compound = "left", command = lambda:practiceWindow(root), font = "font 16").grid(row=1, column=1, pady=30)

# Instructions
Message(root, justify = CENTER, text = "Rebirth will open when you start the mod.", font = "font 13", width = 475).grid(row = 2, column = 0, columnspan = 2, padx = 20)
Message(root, justify = CENTER, text = "Keep this program open while playing.", font = "font 13", width = 475).grid(row = 3, column = 0, columnspan = 2, padx = 20)
Message(root, justify = CENTER, text = "Rebirth will returns to normal when this program is closed.\n\n", font = "font 13", width = 500).grid(row = 4, column = 0, columnspan = 2, padx = 20)

# Uninstall mod files when the window is closed
root.protocol("WM_DELETE_WINDOW", uninstallMod)

# Infinite loop
mainloop()

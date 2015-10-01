#---------------
# DrawBuilds.py
# by Inschato
# Generates an image describing the builds in builds.xml.
#---------------

__author__ = 'Inschato'
target_file = "builds.png"

from BalanceMod import *

def get_heart_icons():
	icon_zoom = 1
	icon_filter = Image.NEAREST
	'''
	hearts_list[0] = # Full red
	hearts_list[1] = # Half red
	hearts_list[2] = # Empty heart
	hearts_list[3] = # Left half eternal
	hearts_list[4] = # Right half eternal overlap
	hearts_list[5] = # Full soul
	hearts_list[6] = # Half soul
	hearts_list[7] = # Full black
	hearts_list[8] = # Half black
	'''
	hearts_list = [None] * 9
	hearts = Image.open('otherFiles/ui_hearts.png')

	# 16x16 left upper right lower
	for index in range(0, 9):
		left = (16 * index) % 80
		top = 0 if index < 5 else 16
		bottom = top + 16
		right = left + 16
		hearts_list[index] = hearts.crop((left, top, right, bottom))
		hearts_list[index] = hearts_list[index].resize((int(hearts_list[index].width * icon_zoom), int(hearts_list[index].height * icon_zoom)), icon_filter)
	return hearts_list

# Draw and return the background image listing starting and removed items for the
# starting room and attach it to the controls image.
def draw_builds(items, health=None, removed_items=None, trinket=None, id="Undefined", width=None):
	result = None
	font = ImageFont.truetype("otherFiles/comicbd.ttf", 32)
	if removed_items:
		result = create_text_image('Removed Items', font)
		removed_image = None
		for item in removed_items[:10]:
			item_image = get_item_icon(item)
			removed_image = join_images_horizontal(removed_image, item_image) if removed_image else item_image
		result = join_images_vertical(result, removed_image)
		removed_image = None
		for item in removed_items[10:19]:
			item_image = get_item_icon(item)
			removed_image = join_images_horizontal(removed_image, item_image) if removed_image else item_image
		if removed_image:
			if len(removed_items) > 19:
				removed_image = join_images_horizontal(removed_image, create_text_image('+' + str(len(removed_items) - 19), font))
			result = join_images_vertical(result, removed_image)


	if items or trinket:
		items_image = None
		if items:
			for item in items:
				item_image = get_item_icon(item)
				items_image = join_images_horizontal(items_image, item_image) if items_image else item_image
		if trinket:
			items_image = join_images_horizontal(items_image, get_trinket_icon(trinket)) if items_image else item_image
		result = join_images_vertical(items_image, result) if result else items_image # Add the starting items
		result = join_images_vertical(create_text_image('Starting Items', font), result) # Add start label

	if health:
		health_icons = None
		if health[0]: # red
			for i in range(0, health[0]):
				health_icons = join_images_horizontal(health_icons, heart_icons[0]) if health_icons else heart_icons[0]
		if health[1]: # half red
				health_icons = join_images_horizontal(health_icons, heart_icons[1]) if health_icons else heart_icons[1]
		if health[2]: # empties
				health_icons = join_images_horizontal(health_icons, heart_icons[2]) if health_icons else heart_icons[2]
		if health[3]: # full soul
				health_icons = join_images_horizontal(health_icons, heart_icons[5]) if health_icons else heart_icons[5]
		if health[4]: # half soul
				health_icons = join_images_horizontal(health_icons, heart_icons[6]) if health_icons else heart_icons[6]
		if health[5]: # full black
				health_icons = join_images_horizontal(health_icons, heart_icons[7]) if health_icons else heart_icons[7]
		if health[6]: # half black
				health_icons = join_images_horizontal(health_icons, heart_icons[8]) if health_icons else heart_icons[8]
		result = join_images_vertical(health_icons, result) if result else health_icons
	result = join_images_vertical(create_text_image('#' + id, font), result) # Add the build ID
	if width and result.width < width:
		padding = int((width-result.width)/2)
		result = join_images_horizontal(result, Image.new('RGBA', (padding, 1)))
		result = join_images_horizontal(Image.new('RGBA', (padding, 1)), result)

	return result

if __name__ == '__main__':
	_raw_image_library = {} # Item images library
	items_xml = ET.parse('gameFiles/items.xml')
	items_info = items_xml.getroot()
	result = None
	heart_icons = get_heart_icons()

	# First we do all the hard work just to find out which build has maximum width
	width = 0
	for index, build in enumerate(builds):
		removed_items = build.attrib.get('removed')
		redhearts = build.attrib.get('redhearts')
		soulhearts = build.attrib.get('soulhearts')
		blackhearts = build.attrib.get('blackhearts')
		heartcontainers = build.attrib.get('heartcontainers')

		fullreds, halfred, containers, fullsouls, halfsoul, fullblacks, halfblack = 0,0,0,0,0,0,0
		if redhearts:
			fullreds = int(int(redhearts) / 2)
			halfred = int(int(redhearts) % 2)
		if heartcontainers:
			containers = int(int(heartcontainers) / 2)
		if soulhearts:
			fullsouls = int(int(soulhearts) / 2)
			halfsoul = int(int(soulhearts) % 2)
		if blackhearts:
			fullblacks = int(int(blackhearts) / 2)
			halfblack = int(int(blackhearts) % 2)

		health = (fullreds, halfred, containers, fullsouls, halfsoul, fullblacks, halfblack)
		if removed_items:
			removed_items = removed_items.split(' + ')
		build_image = draw_builds(items=build.attrib.get('items').split(' + '), removed_items=removed_items, health=health, trinket=build.attrib.get('trinket'), id=str(index+1))
		if build_image.width > width:
			width = build_image.width

	# Then we do it over again, forcing every build to have the same width
	for index, build in enumerate(builds):
		removed_items = build.attrib.get('removed')
		redhearts = build.attrib.get('redhearts')
		soulhearts = build.attrib.get('soulhearts')
		blackhearts = build.attrib.get('blackhearts')
		heartcontainers = build.attrib.get('heartcontainers')

		fullreds, halfred, containers, fullsouls, halfsoul, fullblacks, halfblack = 0,0,0,0,0,0,0
		if redhearts:
			fullreds = int(int(redhearts) / 2)
			halfred = int(int(redhearts) % 2)
		if heartcontainers:
			containers = int(int(heartcontainers) / 2)
		if soulhearts:
			fullsouls = int(int(soulhearts) / 2)
			halfsoul = int(int(soulhearts) % 2)
		if blackhearts:
			fullblacks = int(int(blackhearts) / 2)
			halfblack = int(int(blackhearts) % 2)

		health = (fullreds, halfred, containers, fullsouls, halfsoul, fullblacks, halfblack)
		if removed_items:
			removed_items = removed_items.split(' + ')
		build_image = draw_builds(items=build.attrib.get('items').split(' + '), removed_items=removed_items, health=health, trinket=build.attrib.get('trinket'), id=str(index + 1), width=width)
		ImageDraw.Draw(build_image).rectangle((0, 0, build_image.width - 1, build_image.height - 1), outline=(0, 0, 0))
		result = join_images_vertical(result, build_image) if result else build_image
		result = join_images_vertical(result, Image.new('RGBA', (10, 10)))

	result.save(target_file)

#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  

import os
import sys

from PIL import Image
from parse import parse
from plistlib import readPlist

pvr_file_ext = (".pvr", ".pvr.gz", ".pvr.ccz")
def get_image_ext(image_file):
	for ext in pvr_file_ext:
		if image_file.endswith(ext):
			return ext
	return os.path.splitext(image_file)[1]

def convert_pvr_to_png(image_file, image_ext):
	pvr_path = image_file.replace(image_ext, "")
	if os.system("TexturePacker {pvr_pathname} --sheet {pvr_path}.png --texture-format png --border-padding 0 --shape-padding 0 --disable-rotation --allow-free-size --no-trim --data {pvr_path}_temp.plist".format(pvr_pathname = image_file, pvr_path = pvr_path)) == 0:
		return True
	return False

def unpacker(plist_file, image_file):
	try:
		data = readPlist(plist_file)
	except (Exception, e):
		print ("error: read plist file failed >", plist_file)
		return 1

	# check file format
	if data.metadata.format != 2:
		print ("error: only support format : 2, current is", data.metadata.format)
		return -1

	# check imagefile
	if not image_file or image_file == "":
		file_path,_ = os.path.split(plist_file)
		image_file = os.path.join(file_path , data.metadata.textureFileName)

	# check image format
	image_ext = get_image_ext(image_file)
	if image_ext in pvr_file_ext:
		if convert_pvr_to_png(image_file, image_ext):
			image_file = image_file.replace(image_ext, ".png")
		else:
			print ("error: can't not convert pvr to png, are you sure installed TexturePacker command line tools ? More infomation:\nhttps://www.codeandweb.com/texturepacker/documentation#install-command-line")
			return -1


	# create output dir
	out_path,_ = os.path.splitext(plist_file)
	if not os.path.isdir(out_path):
		os.mkdir(out_path)

	src_image = Image.open(image_file)

	for (name,config) in data.frames.items():
		# parse config
		frame             = parse("{{{{{x:d},{y:d}}},{{{w:d},{h:d}}}}}",config.frame)
		source_color_rect = parse("{{{{{x:d},{y:d}}},{{{w:d},{h:d}}}}}",config.sourceColorRect)
		source_size       = parse("{{{w:d},{h:d}}",config.sourceSize)
		rotated           = config.rotated

		# create temp image
		src_rect = (frame["x"],frame["y"],frame["x"]+(frame["h"] if rotated else frame["w"]),frame["y"]+(frame["w"] if rotated else frame["h"]))
		temp_image = src_image.crop(src_rect)
		if rotated:
			temp_image = temp_image.rotate(90, expand=1)

		# create dst image
		dst_image = Image.new('RGBA', (source_size["w"], source_size["h"]), (0,0,0,0))
		dst_image.paste(temp_image, (source_color_rect["x"],source_color_rect["y"]), mask=0)
		dst_image.save(out_path + "/" + name)

	return 0

def main():
	if len(sys.argv) <= 1:
		print ("example: python untp.py test.plist")
		return -1

	plist_file = ""
	image_file = ""

	if len(sys.argv) >= 2:
		plist_file = sys.argv[1]

	if len(sys.argv) >= 3:
		image_file = sys.argv[2]

	return unpacker(plist_file, image_file)

if __name__ == '__main__':
	main()
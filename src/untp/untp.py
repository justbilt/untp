#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  
from __future__ import print_function

import os
import sys
import argparse
import dataparse
import tempfile
import shutil
import json

from PIL import Image

usage = """
%(prog)s ../btn.plist
%(prog)s ../btn.plist -i ../btn.png
%(prog)s ../data
%(prog)s ../data -r
"""

pvr_file_ext = (".pvr", ".pvr.gz", ".pvr.ccz")
def get_image_ext(image_file):
	for ext in pvr_file_ext:
		if image_file.endswith(ext):
			return ext
	return os.path.splitext(image_file)[1]

def convert_pvr_to_png(image_file):
	temp_dir = tempfile.mkdtemp()

	shutil.copyfile(image_file, os.path.join(temp_dir, os.path.basename(image_file)))
	image_path = os.path.join(temp_dir, "temp.png")
	plist_path = os.path.join(temp_dir, "temp.plist")

	if os.system("TexturePacker {temp_dir} --sheet {image_path} --texture-format png --border-padding 0 --shape-padding 0 --disable-rotation --allow-free-size --no-trim --data {plist_path}".format(temp_dir = temp_dir, image_path = image_path, plist_path = plist_path)) == 0:
		return image_path

	return None

def unpacker(data_file, image_file=None, output_dir=None, config=None, extra_data_receiver=None):
	# parse file
	data = dataparse.parse_file(data_file, config, extra_data_receiver)
	frame_data_list = data.get("frames") if data else None
	if not data or not frame_data_list:
		print("fail: unknown file type:" + data_file)
		return -1

	# check imagefile
	if not image_file:
		file_path,_ = os.path.split(data_file)
		image_file = os.path.join(file_path , data["texture"])

	# check image format
	image_ext = get_image_ext(image_file)
	if image_ext in pvr_file_ext:
		new_image_file = convert_pvr_to_png(image_file)
		if new_image_file:
			image_file = new_image_file
		else:
			print("fail: can't convert pvr to png, are you sure installed TexturePacker command line tools ? More infomation:\nhttps://www.codeandweb.com/texturepacker/documentation#install-command-line")
			return -1

	# create output dir
	if not output_dir:
		output_dir,_ = os.path.splitext(data_file)
	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)

	try:
		src_image = Image.open(image_file)
	except Exception, e:
		print("fail: can't open image %s " %image_file)
		return -1

	for frame_data in frame_data_list:
		temp_image = src_image.crop(frame_data["src_rect"])
		if frame_data["rotated"]:
			temp_image = temp_image.rotate(90, expand=1)

		# create dst image
		dst_image = Image.new('RGBA', frame_data["source_size"], (0,0,0,0))
		dst_image.paste(temp_image, frame_data["offset"], mask=0)

		output_path = os.path.join(output_dir, frame_data["name"])
		if not os.path.exists(os.path.dirname(output_path)):
			os.makedirs(os.path.dirname(output_path))
		dst_image.save(output_path)

	print("success:", data_file)
	return 0

# Get the all files & directories in the specified directory (path).
def unpacker_dir(path, recursive):
    for name in os.listdir(path):
        full_name = os.path.join(path, name)
        pre,ext = os.path.splitext(name)
        if ext in ('.plist', ".fnt"):
            unpacker(full_name)
        elif recursive and os.path.isdir(full_name):
	        unpacker_dir(full_name, recursive)
    
def main():

	parser = argparse.ArgumentParser(prog="untp", usage=usage)
	parser.add_argument("path", type=str, help="plist/fnt file name or directory")

	group_file = parser.add_argument_group('For file')
	group_file.add_argument("-i", "--image_file", type=str, metavar="image_file", help="specified image file for plist")
	group_file.add_argument("-o", "--output", type=str, metavar="output", help="specified output directory")

	group_dir = parser.add_argument_group('For directory')
	group_dir.add_argument("-r", "--recursive", action="store_true", default=False)

	argument = parser.parse_args()

	if os.path.isdir(argument.path):
		return unpacker_dir(argument.path, argument.recursive)
	elif os.path.isfile(argument.path):
		return unpacker(argument.path, image_file = argument.image_file, output_dir = argument.output)

if __name__ == '__main__':
	main()
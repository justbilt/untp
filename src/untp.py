#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  

import os
import sys
import xml.etree.ElementTree as ET
from PIL import Image
import parse

import plistparser

def unpacker(_plistfile, _imagefile):
	data = plistparser.parse(_plistfile)

	if data["metadata"]["format"] != 2:
		print "error: only support format : 2, current is", data["metadata"]["format"]
		return -1

	# check imagefile
	if not _imagefile or _imagefile == "":
		filepath,filename = os.path.split(_plistfile)
		_imagefile = os.path.join(filepath , data["metadata"]["textureFileName"])

	# create output dir
	outpath,_ = os.path.splitext(_plistfile)
	if not os.path.isdir(outpath):
		os.mkdir(outpath)

	src_image = Image.open(_imagefile)

	for (name,config) in data["frames"].items():
		# parse config
		frame           = parse.parse("{{{{{x:d},{y:d}}},{{{w:d},{h:d}}}}}",config["frame"])
		sourceColorRect = parse.parse("{{{{{x:d},{y:d}}},{{{w:d},{h:d}}}}}",config["sourceColorRect"])
		sourceSize      = parse.parse("{{{w:d},{h:d}}",config["sourceSize"])
		rotated         = config["rotated"]

		# create temp image
		src_rect = (frame["x"],frame["y"],frame["x"]+(frame["h"] if rotated else frame["w"]),frame["y"]+(frame["w"] if rotated else frame["h"]))
		temp_image = src_image.crop(src_rect)
		if rotated:
			temp_image = temp_image.rotate(90)

		# create dst image
		dst_image = Image.new('RGBA', (sourceSize["w"], sourceSize["h"]), (0,0,0,0))
		dst_image.paste(temp_image, (sourceColorRect["x"],sourceColorRect["y"]), mask=0)
		dst_image.save(outpath + "/" + name)

	return 0

def main():
	if len(sys.argv) <= 1:
		print "example: python untp.py test.plist"
		return -1

	plistfile = ""
	imagefile = ""

	if len(sys.argv) >= 2:
		plistfile = sys.argv[1]

	if len(sys.argv) >= 3:
		imagefile = sys.argv[2]

	return unpacker(plistfile, imagefile)

if __name__ == '__main__':
	main()
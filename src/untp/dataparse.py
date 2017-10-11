#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  

import os
import json
from parse import parse
from plistlib import readPlist
from pprint import pprint

def parse_file(_filepath, _config=None, _extra_data_receiver=None):
	path,name = os.path.split(_filepath)
	pre,ext = os.path.splitext(name)
	if ext == ".plist":
		try:
			data = readPlist(_filepath)
		except Exception:
			print("fail: read plist file failed >", _filepath)
			return
		return parse_plistdata(data)
	elif ext == ".fnt":
		with open(_filepath, "r") as f:
			data = f.read().split("\n")
			if len(data) < 5:
				print("fail: read plist file failed >", _filepath)
				return

		return parse_fntdata(data, _config if _config else {"prefix": pre}, _extra_data_receiver)



def parse_fntdata(_data, _config, _extra_data_receiver=None):
	"""
	info face="Haettenschweiler" size=60 bold=0 italic=0 charset="" unicode=0 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=2,2
	common lineHeight=64 base=53 scaleW=256 scaleH=128 pages=1 packed=0
	page id=0 file="attack_num.png"
	chars count=12
	char id=52 x=2 y=2 width=33 height=51 xoffset=0 yoffset=5 xadvance=32 page=0 chnl=0 letter="4"
	char id=48 x=37 y=2 width=29 height=50 xoffset=1 yoffset=6 xadvance=29 page=0 chnl=0 letter="0"
	char id=53 x=68 y=2 width=29 height=50 xoffset=1 yoffset=6 xadvance=28 page=0 chnl=0 letter="5"
	char id=57 x=99 y=2 width=28 height=50 xoffset=1 yoffset=6 xadvance=28 page=0 chnl=0 letter="9"
	char id=54 x=129 y=2 width=28 height=50 xoffset=1 yoffset=6 xadvance=28 page=0 chnl=0 letter="6"
	char id=56 x=159 y=2 width=28 height=50 xoffset=1 yoffset=6 xadvance=28 page=0 chnl=0 letter="8"
	char id=51 x=189 y=2 width=28 height=50 xoffset=1 yoffset=6 xadvance=28 page=0 chnl=0 letter="3"
	char id=50 x=219 y=2 width=28 height=49 xoffset=1 yoffset=7 xadvance=28 page=0 chnl=0 letter="2"
	char id=55 x=2 y=55 width=30 height=48 xoffset=1 yoffset=8 xadvance=28 page=0 chnl=0 letter="7"
	char id=49 x=34 y=55 width=20 height=48 xoffset=1 yoffset=8 xadvance=20 page=0 chnl=0 letter="1"
	char id=45 x=56 y=55 width=18 height=12 xoffset=1 yoffset=36 xadvance=19 page=0 chnl=0 letter="-"
	char id=32 x=76 y=55 width=0 height=0 xoffset=11 yoffset=73 xadvance=16 page=0 chnl=0 letter="space"
	"""
	data = {}
	frame_data_list = []

	parse_common_info = parse("common lineHeight={line_height:d} base={base:d} scaleW={scale_w:d} scaleH={scale_h:d} pages={pages:d} packed={packed:d}", _data[1])
	parse_page_info = parse("page id={id:d} file=\"{file}\"", _data[2])
	parse_char_count = parse("chars count={count:d}", _data[3])
	raw_frames_data = {}
	for index in xrange(0, parse_char_count["count"]):
		parse_frame = parse("char id={id:d} x={x:d} y={y:d} width={width:d} height={height:d} xoffset={xoffset:d} yoffset={yoffset:d} xadvance={xadvance:d} page={page:d} chnl={chnl:d} letter=\"{letter}\"", _data[index + 4])

		frame_data = {}
		frame_data["name"]        = "{prefix}_{id}.png".format(prefix= _config["prefix"], id=parse_frame["id"], letter=parse_frame["letter"])
		frame_data["source_size"] = (parse_frame["width"], parse_frame["height"])
		frame_data["rotated"]     = False
		frame_data["src_rect"]    = (parse_frame["x"], parse_frame["y"], parse_frame["x"] + parse_frame["width"], parse_frame["y"] + parse_frame["height"])
		frame_data["offset"]      = (0, 0)

		if parse_frame["width"] <= 0 or  parse_frame["height"] <= 0:
			continue

		frame_data_list.append(frame_data)

		parse_frame_named_data = parse_frame.named.copy()
		parse_frame_named_data["texture"] = frame_data["name"]

		raw_frames_data[parse_frame["id"]] = parse_frame_named_data

	data["texture"] = parse_page_info["file"]
	data["frames"] = frame_data_list

	if _extra_data_receiver != None:
		_extra_data_receiver["common"] = parse_common_info.named
		_extra_data_receiver["frames"] = raw_frames_data

	return data


def _mapping_list(_result, _name, _data):
	for i,v in enumerate(_name):
		if isinstance(v, list):
			_mapping_list(_result, v, _data[i])
		else:
			_result[v] = _data[i]

	return _result

def _parse_str(_name, _str):
	return _mapping_list({}, _name, json.loads(_str.replace("{", "[").replace("}", "]")))

def parse_plistdata(_data):
	fmt = _data.metadata.format
	# check file format
	if fmt not in (0, 1, 2, 3):
		print("fail: unsupport format " + str(fmt))
		return None

	data = {}
	frame_data_list = []

	for (name,config) in _data.frames.items():
		frame_data = {}
		if fmt == 0:
			source_size = {
				"w": config.get("originalWidth", 0),
				"h": config.get("originalHeight", 0),
			}
			rotated = False
			src_rect = (
				config.get("x", 0),
				config.get("y", 0),
				config.get("x", 0) + config.get("originalWidth", 0),
				config.get("y", 0) + config.get("originalHeight", 0),
			)
			offset = {
				"x": config.get("offsetX", False),
				"y": config.get("offsetY", False),
			}
		elif fmt == 1 or fmt == 2:
			frame         = _parse_str([["x","y"],["w","h"]], config.frame)
			center_offset = _parse_str(["x","y"], config.offset)
			source_size   = _parse_str(["w","h"], config.sourceSize)
			rotated       = config.get("rotated", False)
			src_rect      = (
				frame["x"],
				frame["y"],
				frame["x"]+(frame["h"] if rotated else frame["w"]),
				frame["y"]+(frame["w"] if rotated else frame["h"])
			)			
			offset = {
				"x": source_size["w"]/2 + center_offset["x"] - frame["w"]/2, 
				"y": source_size["h"]/2 - center_offset["y"] - frame["h"]/2,
			}
		elif fmt == 3:
			frame         = _parse_str([["x","y"],["w","h"]], config.textureRect)
			center_offset = _parse_str(["x","y"], config.spriteOffset)
			source_size   = _parse_str(["w","h"], config.spriteSourceSize)
			rotated       = config.textureRotated
			src_rect      = (
				frame["x"],
				frame["y"],
				frame["x"]+(frame["h"] if rotated else frame["w"]),
				frame["y"]+(frame["w"] if rotated else frame["h"])
			)			
			offset = {
				"x": source_size["w"]/2 + center_offset["x"] - frame["w"]/2, 
				"y": source_size["h"]/2 - center_offset["y"] - frame["h"]/2,
			}
		else:
			continue

		frame_data["name"]        = name
		frame_data["source_size"] = (int(source_size["w"]), int(source_size["h"]))
		frame_data["rotated"]     = rotated
		frame_data["src_rect"]    = [int(x) for x in src_rect ]
		frame_data["offset"]      = (int(offset["x"]), int(offset["y"]))

		frame_data_list.append(frame_data)


	data["frames"] = frame_data_list
	data["texture"] = _data.metadata.textureFileName

	return data
#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  

from parse import parse

def parsedata(_data):
	fmt = _data.metadata.format
	# check file format
	if fmt not in (2,3):
		print("fail: unsupport format " + fmt)
		return None


	frame_data_list = []

	for (name,config) in _data.frames.items():
		frame_data = {}
		if fmt == 2:
			frame         = parse("{{{{{x:g},{y:g}}},{{{w:g},{h:g}}}}}", config.frame)
			center_offset = parse("{{{x:g},{y:g}}}", config.offset)
			source_size   = parse("{{{w:g},{h:g}}}", config.sourceSize)
			rotated       = config.rotated
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
			frame         = parse("{{{{{x:g},{y:g}}},{{{w:g},{h:g}}}}}", config.textureRect)
			center_offset = parse("{{{x:g},{y:g}}}", config.spriteOffset)
			source_size   = parse("{{{w:g},{h:g}}}", config.spriteSourceSize)
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

	return frame_data_list
#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3  

import xml.etree.ElementTree as ET
import pprint
pp = pprint.PrettyPrinter(indent=4)


def parseValue(_type, _value):
	if _type == "integer":
		return int(_value)
	elif _type == "real":
		try:
			return int(_value)
		except ValueError:
			return round(float(_value), 4)
	elif _type == "string":
		return _value
	elif _type == "true":
		return True
	elif _type == "false":
		return False

	print "======================================================>>>>>>"
	print "Unknown Type:",_type, _value
	print "<<<<<<======================================================"
	
	return _value

def parseElement(_type, _value):
	if _type == "dict":
		return parseDict(_value)
	else:
		return parseValue(_type, _value.text)


def parseDict(_element):
	data = {}
	
	iterator = iter(_element)
	while True:
		try:
			key = iterator.next()
			value = iterator.next()
			if key.text == "properties":
				data[key.text] = parseProperties(value)
			else:
				data[key.text] = parseElement(value.tag, value)
		except StopIteration:
			break

	return data


def parse(_plistfile):
	tree = ET.parse(_plistfile)
	root = tree.getroot()
	return parseDict(root[0])
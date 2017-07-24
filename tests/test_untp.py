#!/usr/bin/env python  
# coding=utf-8  
# Python 2.7.3


import unittest
import os, sys, shutil
import plistlib

from PIL import Image

HERE = os.path.abspath(os.path.dirname(__file__))
TEMP_PATH = os.path.join(HERE, "temp")
DATA_PATH = os.path.join(HERE, "data")

sys.path.append(os.path.join(os.path.dirname(HERE), "src", "untp"))
import untp

def ipath(*argv):
	return os.path.join(DATA_PATH, *argv)

def opath(*argv):
	return os.path.join(TEMP_PATH, *argv)


class TestUnpackPlist(unittest.TestCase):
	"""Test test_unpack_plist.py"""

	def _cleanUp(self):
		if os.path.exists(TEMP_PATH):
			shutil.rmtree(TEMP_PATH)

	def _test_unpack(self, _plist, _output, _size_field="sourceSize"):
		data = plistlib.readPlist(_plist)
		for k,v in data.frames.iteritems():
			clip_path = os.path.join(_output, k)
			self.assertTrue(os.path.exists(clip_path))
			src_image = Image.open(clip_path)
			self.assertEqual(v[_size_field], "{%s,%d}" %(src_image.size))

	def setUp(self):
		self._cleanUp()
		os.mkdir(TEMP_PATH)

	def tearDown(self):
		self._cleanUp()

	def test_unpack_f1(self):
		"""Test unpack plist that format is 1"""
		untp.unpacker(ipath("v1.plist"), ipath("v1.png"), opath("v1"))
		self._test_unpack(ipath("v1.plist"), opath("v1"))
		
	def test_unpack_f2(self):
		"""Test unpack plist that format is 2"""
		untp.unpacker(ipath("v2.plist"), ipath("v2.png"), opath("v2"))
		self._test_unpack(ipath("v2.plist"), opath("v2"))
		
	def test_unpack_f3(self):
		"""Test unpack plist that format is 3"""
		untp.unpacker(ipath("subdir", "v3.plist"), ipath("subdir", "v3.png"), opath("v3"))
		self._test_unpack(ipath("subdir", "v3.plist"), opath("v3"), _size_field="spriteSourceSize")		
		
	def test_unpack_dir(self):
		"""Test unpack directory"""
		untp.unpacker_dir(DATA_PATH, True, output_dir=TEMP_PATH)
		self._test_unpack(ipath("v1.plist"), opath("v1"))
		self._test_unpack(ipath("v2.plist"), opath("v2"))
		self._test_unpack(ipath("subdir", "v3.plist"), opath("subdir", "v3"), _size_field="spriteSourceSize")		

	def test_unpack_fnt(self):
		"""Test unpack plist that format is 1"""
		fnt = ipath("test.fnt")
		output = opath("test")
		untp.unpacker(fnt, ipath("test.png"), output)
		with open(fnt, "r") as f:
			lines = f.read().split("\n")
			for l in lines:
				fields = l.split(" ")
				if len(fields) >= 2 and fields[0] == "char" and fields[1].startswith("id="):
					index = fields[1].replace("id=", "")
					path = os.path.join(output, "test_"+index+".png")
					self.assertTrue(os.path.exists(path))
			f.close()
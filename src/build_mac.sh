#!/bin/sh

pyinstaller ./untp.py -F --distpath ../bin

rm -rf build
rm -rf *.spec
rm -rf *.pyc
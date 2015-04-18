pyinstaller ./untp.py -F --distpath ../bin -p %PYTHONHOME%/Lib/site-packages/pil;

rmdir /s/q build
del /s/q *.spec
del /s/q *.pyc
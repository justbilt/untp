A command line tool to split TexturePacker publish file.

### install

`pip install untp`

### update

`pip install -U untp`

### usage
```
$ untp -h
usage:
untp ../btn.plist
untp ../btn.plist -i ../btn.png
untp ../data
untp ../data -r

positional arguments:
  path                  plist file name or directory

optional arguments:
  -h, --help            show this help message and exit

For file:
  -i image_file, --image_file image_file
                        specified image file for plist

For directory:
  -r, --recursive
```


---

If you have any question, pleast make a [issue](https://github.com/justbilt/untp/issues), thanks!


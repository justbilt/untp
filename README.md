[中文说明](http://blog.justbilt.com/2016/10/29/untp-2/)

A command line tool to split TexturePacker published files.

![][1]

### install

`pip install untp`

### update

`pip install -U untp`

Windows: [portable](http://7xnfpc.com1.z0.glb.clouddn.com/untp-1.1.5.zip)

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

If you have any question, just make a [issue](https://github.com/justbilt/untp/issues), thanks!


[1]: /screenshot/mac.png

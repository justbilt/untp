[中文说明](http://blog.justbilt.com/2016/10/29/untp-2/)

一个批量拆分 TexturePacker 导出的 plist 文件的工具.

![]

### 安装

`pip install untp`

### 更新

`pip install -U untp`

### 用例

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

如果你有任何问题, 请提交一个[issue](https://github.com/justbilt/untp/issues), 谢谢!


[]: /screenshot/mac.png
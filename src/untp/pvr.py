from __future__ import print_function

import tempfile
import shutil
import os
import sys
import subprocess as sp
import struct

CACHED_ENCRYPTION_KEY = {}

enclen = 1024
securelen = 512
distance = 64
DELTA = 0x9e3779b9

def long_to_uint(value):
    if value > 4294967295:
        return (value & (2 ** 32 - 1))
    else :
        return value

def int_to_byte(value):
    if value > 255 :
        return (value & 255)
    else :
        return value

def MX(z, y, sum, s_uEncryptedPvrKeyParts, p, e):
    return ((z>>5^y<<2) + (y>>3^z<<4)) ^ ((sum^y) + (s_uEncryptedPvrKeyParts[(p&3)^e] ^ z))

def _generate_key_parts(content_protection_key):
    chunks, chunk_size = len(content_protection_key), len(content_protection_key)/4
    return [int(content_protection_key[i:i+chunk_size], 16) for i in range(0, chunks, chunk_size) ]

def _generate_encryption_key(s_uEncryptedPvrKeyParts):
    s_uEncryptionKey = enclen * [0]
    rounds = 6
    sum = 0
    z = s_uEncryptionKey[enclen-1]

    while(True):
        sum = long_to_uint(sum + DELTA)
        e = long_to_uint((sum >> 2) & 3)
        for p in range(0, enclen - 1):
            y = s_uEncryptionKey[p + 1]
            s_uEncryptionKey[p] = long_to_uint(s_uEncryptionKey[p] + MX(z, y, sum, s_uEncryptedPvrKeyParts, p, e))
            z = s_uEncryptionKey[p]
        p += 1
        y = s_uEncryptionKey[0]
        s_uEncryptionKey[enclen - 1] = long_to_uint(s_uEncryptionKey[enclen - 1] + MX(z, y, sum, s_uEncryptedPvrKeyParts, p, e))
        z = s_uEncryptionKey[enclen - 1]
        rounds -= 1
        if not rounds:
            break
    
    return s_uEncryptionKey


def _pvr_head(_data):
    """
        struct CCZHeader {
            unsigned char   sig[4];             // signature. Should be 'CCZ!' 4 bytes
            unsigned short  compression_type;   // should 0
            unsigned short  version;            // should be 2 (although version type==1 is also supported)
            unsigned int    reserved;           // Reserved for users.
            unsigned int    len;                // size of the uncompressed file
        };
    """
    return {
        "sig": _data[:4],
        "compression_type": struct.unpack("H", _data[4:6])[0],
        "version": struct.unpack("H", _data[6:8])[0],
        "reserved": struct.unpack("I", _data[8:12])[0],
        "len": struct.unpack("I", _data[12:16])[0],
    }

def _decrypt_pvr_content(body, encryption_key):
    b = 0
    i = 0

    # encrypt first part completely
    for i in range(0, min(len(body), securelen)):
        num = struct.unpack("I", body[i])[0]
        body[i] = num ^ encryption_key[b]
        b += 1
        if b >= enclen:
            b = 0

    i += 1

    # encrypt second section partially
    for i in range(i, len(body), distance):
        num = struct.unpack("I", body[i])[0]
        body[i] = num ^ encryption_key[b]
        b += 1
        if b >= enclen:
            b = 0

def _decrypt_pvr(image_file, out_file, content_protection_key):
    encryption_key = CACHED_ENCRYPTION_KEY.get(content_protection_key)
    if not encryption_key:
        encryption_key = _generate_encryption_key(_generate_key_parts(content_protection_key))
        CACHED_ENCRYPTION_KEY[content_protection_key] = encryption_key
    
    with open(image_file, "rb") as fr:
        head = fr.read(12)
        byte = fr.read(4)

        head_info = _pvr_head(head + byte)
        if head_info["sig"] != "CCZp":
            return

        body = []
        tril = None
        while byte != "":
            if len(byte) < 4:
                tril = byte
            else:
                body.append(byte)
            byte = fr.read(4)

        _decrypt_pvr_content(body, encryption_key)

        with open(out_file, "wb") as fw:
            head = head[:3] + "!" + head[3+1:]
            fw.write(head)
            for num in body:
                if isinstance(num, int):
                    fw.write(struct.pack('I', num))
                else:
                    fw.write(num)
            fw.write(tril)

def _is_protectionn_pvr(image_file):
    with open(image_file, "rb") as fr:
        head_info = _pvr_head(fr.read(12 + 4))
        if head_info["sig"] == "CCZp":
            return True

    return False        

def convert_pvr_to_png(logger, image_file, protection_key=None):
    temp_dir = tempfile.mkdtemp()
    temp_pvr = os.path.join(temp_dir, os.path.basename(image_file))
    shutil.copyfile(image_file, temp_pvr)

    if _is_protectionn_pvr(temp_pvr):
        if not protection_key:
            logger("error: missing protection key for encrypted image:" + image_file)
            return None
        _decrypt_pvr(temp_pvr, temp_pvr, protection_key)

    image_path = os.path.join(temp_dir, "temp.pvr.ccz")
    plist_path = os.path.join(temp_dir, "temp.plist")

    command = "TexturePacker {temp_dir} --sheet {image_path} --texture-format png --border-padding 0 --shape-padding 0 --disable-rotation --allow-free-size --no-trim --data {plist_path}".format(temp_dir = temp_dir, image_path = image_path, plist_path = plist_path)
    child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    _, err = child.communicate()
    if err:
        logger("------------------------------")
        logger(err.strip())
        logger("error: can't convert pvr to png, are you sure installed TexturePacker command line tools ? More infomation:\nhttps://www.codeandweb.com/texturepacker/documentation#install-command-line")
        logger("------------------------------")

    if child.returncode == 0:
        return image_path

    return None


def main():
    src = sys.argv[1]
    dst = sys.argv[2]
    key = sys.argv[3]
    _decrypt_pvr(src, dst, key)

if __name__ == '__main__':
    main()
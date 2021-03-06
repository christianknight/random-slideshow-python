# Make a photo montage

import os.path
import sys
from time import strftime
from PIL import Image, ImageTk
import random

def montage_build(filenames):
    images = [Image.open(filename) for filename in filenames]

    row_size = len(filenames) // 2
    margin = 3

    width = max(image.size[0] + margin for image in images) * row_size
    height = sum(image.size[1] + margin for image in images)
    montage = Image.new(mode='RGBA', size=(width, height), color=(0,0,0,0))

    max_x = 0
    max_y = 0
    offset_x = 0
    offset_y = 0

    for i,image in enumerate(images):
        montage.paste(image, (offset_x, offset_y))

        max_x = max(max_x, offset_x + image.size[0])
        max_y = max(max_y, offset_y + image.size[1])

        if i % row_size == row_size-1:
            offset_y = max_y + margin
            offset_x = 0
        else:
            offset_x += margin + image.size[0]

    montage = montage.crop((0, 0, max_x, max_y))
    return montage

def montage_save(montage):
    basename = strftime("Montage %Y-%m-%d at %H.%M.%S.png")
    exedir = os.path.dirname(os.path.abspath(sys.argv[0]))
    filename = os.path.join(exedir, basename)
    montage.save(filename)

if __name__ == '__main__':
    montage_save(montage_build(sys.argv[1:]))
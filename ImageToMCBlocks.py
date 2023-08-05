import argparse
from PIL import Image
import os
import json
import numpy
import time
import math

BLOCKMAPCACHE = "blocks/_blockmap_cache.json"
BLACKLIST = ["bamboo_stalk.png"]

def imagetoblocks(img:Image.Image, _scale:float=1.0, width=None, height=None, quiet:bool = False) -> Image.Image:
    img = img.convert("RGBA")
    if not quiet:
        print("Finding scale")
    if width and height:
        newscale = (width, height)
    elif width:
        diff = img.height/img.width
        newscale = (width, math.floor(width*diff))
    elif height:
        diff = img.width/img.height
        newscale = (math.floor(height*diff), height)
    else:
        scale = _scale / blockmap["size"]
        newscale = (round(img.width*scale), round(img.height*scale))
    if not quiet:
        print("Rescaling source to", newscale)
    img = img.resize(newscale)
    if not quiet:
        print("Finding closest matches per pixel")
    start = time.perf_counter()
    outimg = Image.new("RGBA", (img.width*blockmap["size"], img.height*blockmap["size"]))
    n = 0
    max = (img.width*img.height)-1
    for x in range(img.width):
        for y in range(img.height):
            if not quiet:
                print(f"Proccessing block on image {n}/{max}...")
            col_a = img.getpixel((x, y))
            col = (col_a[0], col_a[1], col_a[2])
            opacity = col_a[3]
            if not opacity == 0:
                bestdiff = 1000000
                bestdiffname = ""
                for name, data in blockmap["map"].items():
                    avg = data["average"]
                    #tdiff = (abs(col[0]-avg[0]), abs(col[1]-avg[1]), abs(col[2]-avg[2]))
                    #diff = tdiff[0]+tdiff[1]+tdiff[2]
                    diff = ColorDistance(numpy.array((col[0]/255,col[1]/255,col[2]/255)), numpy.array((avg[0]/255,avg[1]/255,avg[2]/255)))
                    if diff < bestdiff:
                        bestdiff = diff
                        bestdiffname = name
                matchimg = Image.open(os.path.join("blocks", bestdiffname))
                matchimg = matchimg.crop((0, 0, blockmap["size"], blockmap["size"]))
                maskimg = Image.new("RGBA", (blockmap["size"], blockmap["size"]), (255, 255, 255, opacity))
                outimg.paste(matchimg, (x*blockmap["size"], y*blockmap["size"]), maskimg)
            n = n + 1
    if not quiet:
        print(f"Took {time.perf_counter()-start}s!")
    return outimg

def ColorDistance(rgb1,rgb2):
    '''d = {} distance between two colors(3)'''
    rm = 0.5*(rgb1[0]+rgb2[0])
    d = sum((2+rm,4,3-rm)*(rgb1-rgb2)**2)**0.5
    return d

print("Checking for blocks")
if not os.path.isdir("blocks"):
    print("ERROR: Blocks folder is missing.")
    quit()

print("Checking for cached blockmap")
if os.path.isfile(BLOCKMAPCACHE):
    print("Found cached blockmap")
    f = open(BLOCKMAPCACHE, "r")
    blockmap = json.load(f)
    f.close()
else:
    print("Cannot find cached blockmap, creating it.")
    files = os.listdir("blocks")
    blockmap = {"_": "!! Blockmap cache file for ImageToMCBlocks (github/AlignedCookie88/ImageToMCBlocks): DO NOT MODIFY",
                "map": {}}
    size = None
    for fname in files:
        if os.path.isfile(os.path.join("blocks", fname)) and fname.endswith(".png"):
            print("Proccessing block "+fname)
            if fname in BLACKLIST:
                print("Skipping block "+fname+" as it is in the hardcoded blacklist.")
                continue
            colors = []
            block = Image.open(os.path.join("blocks", fname))
            block = block.convert("RGBA")
            if size == None:
                size = block.width
            elif not size == block.width:
                if not (block.height == size*32 or block.height == size*64):
                    print("ERROR: Block sizes do not match")
                    quit()
            pix = block.load()
            transparent = False
            for x in range(size):
                for y in range(size):
                    p = pix[x, y]
                    if type(p) == int:
                        r, g, b, a = p, p, p, 255
                    elif len(p) == 3:
                        r, g, b = p
                        a = 255
                    elif len(p) == 2:
                        r, g, b, a = p[0], p[0], p[0], p[1]
                    else:
                        r, g, b, a = p
                    if not a == 255:
                        transparent = True
                        break
                    colors.append((r, g, b))
                if transparent:
                    break
            if transparent:
                print("Skipping block "+fname+" due to transparency")
            else:
                avg = [0, 0, 0]
                for c in colors:
                    avg[0] = avg[0] + c[0]
                    avg[1] = avg[1] + c[1]
                    avg[2] = avg[2] + c[2]
                avg[0] = round(avg[0] / len(colors))
                avg[1] = round(avg[1] / len(colors))
                avg[2] = round(avg[2] / len(colors))
                avg = (avg[0], avg[1], avg[2])
                blockmap["map"][fname] = {"average": avg}
            block.close()
    blockmap["size"] = size
    print("Caching generated blockmap")
    f = open(BLOCKMAPCACHE, "x")
    json.dump(blockmap, f, indent=4)
    f.close()
    print("Cached!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser("python ImageToMCBlocks.py")
    parser.add_argument("INPUT", help="The input image (including extension)")
    parser.add_argument("OUTPUT", help="The output name (including extension)")
    parser.add_argument("--scale", "-s", help="The scale of the output image relative to the input", required=False, default=1.0, type=float)
    parser.add_argument("--width", "-bw", help="The width of the image in mc blocks, scales the height relativley when --height is ommited", required=False, default=None, type=int)
    parser.add_argument("--height", "-bh", help="The height of the image in mc blocks, scales the width relativley when --width is ommited", required=False, default=None, type=int)
    args = parser.parse_args()

    img = Image.open(args.INPUT)
    outimg = imagetoblocks(img, args.scale, args.width, args.height)
    print("Saving")
    outimg.save(args.OUTPUT)
else:
    print("Running as module, skipping argument parsing & conversion")
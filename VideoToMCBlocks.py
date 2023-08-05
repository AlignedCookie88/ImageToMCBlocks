from ImageToMCBlocks import imagetoblocks
import imageio.v3 as iio
import imageio
import argparse
from PIL import Image
import numpy

parser = argparse.ArgumentParser("python VideoToMCBlocks.py")
parser.add_argument("INPUT", help="The input video (including extension)")
parser.add_argument("OUTPUT", help="The output video (including extension)")
parser.add_argument("--scale", "-s", help="The scale of the output image relative to the input", required=False, default=1.0, type=float)
parser.add_argument("--width", "-bw", help="The width of the video in mc blocks, scales the height relativley when --height is ommited", required=False, default=None, type=int)
parser.add_argument("--height", "-bh", help="The height of the video in mc blocks, scales the width relativley when --width is ommited", required=False, default=None, type=int)
args = parser.parse_args()

with iio.imopen(args.INPUT, "r", plugin="pyav") as input:
    n = 0
    meta = input.metadata()
    outvid = None
    for frame in input.read():
        n = n + 1
        print(f"Frame #{n}")
        img = Image.fromarray(frame)
        out = imagetoblocks(img, args.scale, args.width, args.height, quiet=True)
        if not outvid:
            outvid = imageio.get_writer(args.OUTPUT, "mp4", fps=meta["fps"])
        #array = numpy.array(out.getdata()).reshape(out.size[0], out.size[1], 3)
        array = numpy.array(out)
        outvid.append_data(array)
    outvid.close()
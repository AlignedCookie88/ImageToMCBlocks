# ImageToMCBlocks

Turning images into minecraft blocks since august (badly)

## Notes
- This program does not support generating structures, just `.png`s using minecraft textures

## Setup
Extract the minecraft resources and drop the `block` folder into the projects main directory. You **must** rename the folder to `blocks`!

Note: *If you drop a resourcepack's block folder here it will use the resourcepack's textures; however, all textures **must** be the same resolution.*

## Usage

`python ImageToMCBlocks.py --help` (for image conversions) or `python VideoToMCBlocks.py --help` (for video conversions) will explain it all.

## Usage as a module

The `ImageToMCBlocks.py` script can be used as a module. You can convert an image simply by using the `imagetoblocks` function. 

Usage: `imagetoblocks(img: PIL.Image.Image, scale: float = 1.0, width: int | None = None, height: int | None = None, quiet: bool = False)`

### Example
```python
# Imports
from ImageToMCBlocks import imagetoblocks
from PIL import Image

input_image = Image.open("demo1.png") # Open input file
output_image = imagetoblocks(input_image, .5, None, None, True) # Generate the output image with .5 scale without logging image generation info
output_image.save("out.png") # Save output the image
```

## Clearing the blockmap cache

To clear the blockmap cache simply delete `blocks/_blockmap_cache.json`.
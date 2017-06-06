from PIL import Image, ImageFilter, ImageEnhance
from operator import itemgetter

def processImage(image_name):
  im = Image.open(image_name)
  im = im.convert("P")

  his = im.histogram()
  values = {}

  print his

  for i in range(256):
    values[i] = his[i]

  for j,k in sorted(values.items(), key=itemgetter(1), reverse=True)[:10]:
    print j,k

  temp = {}
  im2 = Image.new("P",im.size,255)
  for x in range(im.size[1]):
    for y in range(im.size[0]):
      pix = im.getpixel((y,x))
      temp[pix] = pix
      if pix == 1: # these are the numbers to get
        im2.putpixel((y,x),0)

  width, height = im2.size
  im2 = im2.resize((width*5, height*5), Image.NEAREST)
  im2.save("output/output_" + image_name)

  return "output/output_" + image_name

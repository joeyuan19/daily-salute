from PIL import Image
img = Image.new('RGBA',(1,1))
img.putpixel((0,0),(255,255,255,0))
img.save('blank.gif')


from PIL import Image
import pytesseract
from os import chdir, listdir


def breakCaptcha(image_name):
    # pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
    img = Image.open(image_name)

    #   Perform OCR using tesseract-ocr library
    text = pytesseract.image_to_string(img)

    return text

if __name__ == "__main__":
	images = listdir("lta-images")
	chdir("lta-images")
	print "%d images in folder" % len(images)

	for img_name in images:
	    print "%s loaded" % img_name
	    answer = img_name.strip('.png')

	    """
	    img = Image.open(img_name)
	    img = img.convert('RGBA')
	    """
		                   
	    text = breakCaptcha(img_name)
	    if text == answer:
		print "Correct"
	    else:
		print "Wrong"
	    print "Output: %s Answer %s" % (text, answer)


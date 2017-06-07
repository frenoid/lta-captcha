from PIL import Image
import pytesseract
from os import chdir, listdir
from Preprocess import processImage
from captcha_solver import CaptchaSolver

def breakCaptcha(image_name):

    processed_image = processImage(image_name)
    try:
        img = Image.open(image_name)
    except IOError:
        return "Error"

    #   Perform OCR using tesseract-ocr library
    text = pytesseract.image_to_string(img)

    return text

if __name__ == "__main__":
	images = listdir("lta-images")
	chdir("lta-images")
	print "%d images in folder" % len(images)
        correct_count  = 0
        total_count = 0 

	for img_name in images:
            total_count += 1
	    print "%s loaded" % img_name
	    answer = img_name.strip('.png')

	    text = breakCaptcha(img_name)
	    if text == answer:
		# print "Correct"
                correct_count += 1
	    else:
		print "Wrong"
            try:
	        print "Output: %s Answer %s" % (text, answer)
            except UnicodeEncodeError:
                print "Wrong answer"

            print "%d out of %d is correct" % (correct_count, total_count)





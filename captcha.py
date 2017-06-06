from PIL import Image
import pytesseract
from os import chdir, listdir
from Preprocess import processImage
from captcha_solver import CaptchaSolver

def breakCaptcha(image_name):
    processed_image = processImage(image_name)

    
    # pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
    img = Image.open(image_name)

    #   Perform OCR using tesseract-ocr library
    text = pytesseract.image_to_string(img)

    """
    solver = CaptchaSolver('browser')
    raw_data = open(image_name, 'rb').read()
    text = solver.solve_captcha(raw_data)
    """

    return text

if __name__ == "__main__":
	images = listdir("lta-images")
	chdir("lta-images")
	print "%d images in folder" % len(images)
        correct_count  = 0

	for img_name in images:
	    print "%s loaded" % img_name
	    answer = img_name.strip('.png')

	    """
	    img = Image.open(img_name)
	    img = img.convert('RGBA')
	    """
		                   
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

        print "%d out of %d is correct"  % (correct_count, len(images))




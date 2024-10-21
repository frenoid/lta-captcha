import cv2
import numpy as np
from matplotlib import pyplot as plt

def getEdges(image_name):
    img = cv2.imread('captcha.png',0)
    edges = cv2.Canny(img,100,200)

    plt.subplot(121),plt.imshow(img,cmap = 'gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(edges,cmap = 'gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
    #plt.show()
    cv2.destroyAllWindows()

    cv2.imwrite('edged_image.png', edges)
    cv2.destroyAllWindows()

    return "edged_image.png"


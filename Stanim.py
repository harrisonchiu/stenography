from cv2 import cv2
import numpy as np

def createTest(out_dir, h, w, n):
    blank = np.zeros((h, w, 4), np.uint8)
    modx, mody = -1, -1
    x, y = 0, 0
    count = 0
    for times in range(n):
        for i in range(h):
            x += modx
            if x == 255 or x == 0:
                modx = modx * -1
            for j in range(w):
                if y == 255 or y == 0:
                    mody = mody * -1

                y += mody
                blank[i,j] = (x, y, 0, count)
                count += 1
        
        cv2.imwrite(out_dir, cv2.cvtColor(blank, cv2.COLOR_BGRA2BGR))

createTest("C:/Users/hchiu/Desktop/1.png",200,200,1)
"""
create an alpha channel to store index of pictures
from: www.oreilly.com/library/view/python-cookbook/0596001673/ch02s09.html
shuffle based on following algorithms 
modified so its shuffled based on a password
    - shuffles based on char of password?
modify the bits normally as it is right now in text_encode()
reformat the matrix based on the index of alpha channel
delete alpha channel

how to shuffle:
    - split image into 26 subsection matrices
    - shuffle their position based on password
    - shuffle rows or cols in each subsection based on password
    - shuffle pixel in each subsection in a row or col based on password



def best_preserve(  ):
    aux = list(data)
    random.shuffle(aux)
    for elem in aux: process(elem)
def improved(  ):
    size = len(data)
    while size:
        index = random.randrange(size)
        elem = data[index]
        data[index] = data[size-1]
        size = size - 1
        process(elem)
def faster_preserve(  ):
    aux = range(len(data))
    while aux:
        posit = random.randrange(len(aux))
        index = aux[posit]
        elem = data[index]
        # alters the auxiliary list only
        del aux[posit] 
        process(elem)




"""        
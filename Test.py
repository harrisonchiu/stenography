from cv2 import cv2
import statistics as s
import numpy as np
import time, random


def emulation(trials, image_dir, terminator, terminal_end):
    first_times = []
    sec_times = []
    thi_times = []

    for trial in range(trials):
        #
        # CODE STARTS
        #
        try:
            start1 = time.time()

            terminator = ''.join([ format(ord(i), "08b") for i in terminator ])
            terminal_end =  ''.join([ format(ord(i), "08b") for i in terminal_end ])
            image = cv2.imread(image_dir)

            data = ""
            for i in range(image.shape[0]):
                for j in range(image.shape[1]):
                    for k in range(3):
                        v = format(image[i][j][k], '08b')
                        data += v[-1]

            print("1st time:", round(time.time() - start1, 3), end=" | ")
            first_times.append(round(time.time() - start1, 3))
            start2 = time.time()

            rows = data.split(terminator)
            
            grouped = []
            for elem in rows:
                grouped.append([ int(elem[i:i+8],2) for i in range(0,len(elem),8) ])

            tupled = []
            for elem in grouped:
                tupled.append([ elem[i:i+3] for i in range(0,len(elem),3) ])

            del tupled[-1]

            px_count = 0
            width, height = len(tupled[0]), len(tupled)
            blank = np.zeros((height, width, 3), np.uint8)

            print("2nd time:", round(time.time() - start2, 3), end=" | ")
            sec_times.append(round(time.time() - start2, 3))
            start3 = time.time()

            for i in range(height):
                for j in range(width):
                    try:
                        blank[i,j] = tupled[i][j]
                
                    except IndexError:
                        print(tupled[i][j])
                        print(blank[i,j])
                        px_count += 1

            print("3rd time:", round(time.time() - start3, 3))
            thi_times.append(round(time.time() - start3, 3))

        #
        # CODE ENDS
        #
        except KeyboardInterrupt:
            break
    
    u = [1,2]
    
    # Display results
    print("Payload: [%d x %d] | Carrier: [%d x %d]" % (blank.shape[0],blank.shape[1],image.shape[0],image.shape[1]))
    print("1st Mean: %.3f | 2nd Mean: %.3f | 3rd Mean: %.3f" % (s.mean(first_times), s.mean(sec_times), s.mean(thi_times)))
    #print("1st SD: %.3f | 2nd SD: %.3f | 3rd SD: %.3f" % (s.stdev(first_times), s.stdev(sec_times), s.stdev(thi_times)))
    print()
    return s.mean(first_times), s.stdev(u), s.mean(sec_times), s.stdev(u), s.mean(thi_times), s.stdev(u)


def main():
    trials = 1
    # Sizes of images to test
    pw = [351]
    ph = [360]
    cw = [1692]
    ch = [1479]

    means1 = []
    means2 = []
    means3 = []
    sds1 = []
    sds2 = []
    sds3 = []
    for s in range(0, 15):
        # Run emulation for all sizes and get mean and SD
        emu = emulation(trials, "C:/Users/hchiu/Desktop/14.png", "TATA", "XXX")
        means1.append(emu[0])
        means2.append(emu[2])
        means3.append(emu[4])

        sds1.append(round(emu[1],3))
        sds2.append(round(emu[3],3))
        sds3.append(round(emu[5],3))

    # Report all mean and SD
    print("FINISHED")
    print(means1)
    #print(sds1)
    print()
    print(means2)
    #print(sds2)
    print()
    print(means3)
    #print(sds3)

main()
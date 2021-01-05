from cv2 import cv2
import numpy as np

import time

def search_pattern(arr, pattern):
    pattern_length = len(pattern)
    possible_matches = np.where(arr == pattern[0])[0]

    matches = []

    for possible in possible_matches:
        check = arr[possible : possible + pattern_length]

        if np.all(check == pattern):
            matches.append(possible)

    return matches


def encode(payload_dir, out_dir, enigma, terminator):
    # Read image
    image = cv2.imread(payload_dir)
    rows = image.shape[0]
    cols = image.shape[1]
    chan = image.shape[2]

    # Add termination sequence for easier decodability
    enigma += terminator

    # Image must have sufficient bytes
    enigma = "".join([ format(ord(i), "08b") for i in enigma ])
    needed_bytes = len(enigma)
    vacant_bytes = rows * cols * chan // 8

    print("[*] Bytes available: %d || Bytes needed: %d" % (vacant_bytes, needed_bytes))
    if needed_bytes > vacant_bytes:
        print("[!] Insufficient bytes: larger image or less data is needed")
        
    # Encode data for each bit in carrier image
    print("[*] Encoding data...")
    data_index = 0

    for row in range(rows):
        for col in range(cols):
            for h in range(chan):
                # Only if data is not yet encoded
                if data_index < len(enigma):
                    # Convert to 8-bits and only modify the LSB in the image (1-bit)
                    v = format(image[row][col][h], '08b')
                    image[row][col][h] = int(v[:-1] + enigma[data_index], 2)
                    data_index += 1
                else:
                    break

    # Output encoded image
    cv2.imwrite(out_dir, image)
    print("[*] Encoded")


def decode(payload_dir, terminator):
    # Read image
    image = cv2.imread(payload_dir)
    rows = image.shape[0]
    cols = image.shape[1]
    chan = image.shape[2]

    number_of_bytes = rows * cols * chan
    terminator_bytes = np.array([ord(char) for char in terminator], dtype=np.uint8)



    

    # 8bit integer array because only stores 0 and 1
    data = np.empty(number_of_bytes, dtype=np.int8) 

    start_time = time.time()

    # For each bit in image, store the LSB
    index = 0
    for row in range(rows):
        for col in range(cols):
            for h in range(chan):
                data[index] = np.unpackbits(image[row][col][h])[-1]
                index += 1

    packed = np.packbits(data)
    terminator_index = search_pattern(packed, terminator_bytes)[-1]

    decoded_data = packed[:terminator_index].tostring().decode("ascii")

    print(decoded_data)
    
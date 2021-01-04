from cv2 import cv2
#import numpy as np

def read(payload_dir):
    return cv2.imread(payload_dir)

def encode(payload_dir, out_dir, enigma, terminator):
    # Read image
    image = read(payload_dir)
    rows = image.shape[0]
    cols = image.shape[1]
    chan = image.shape[2]

    # Add termination sequence for easier decodability
    enigma += terminator

    # Image must have sufficient bytes
    enigma = ''.join([ format(ord(i), "08b") for i in enigma ])
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
    image = read(payload_dir)
    rows = image.shape[0]
    cols = image.shape[1]
    chan = image.shape[2]

    data = ""

    # For each bit in image, store the LSB
    for row in range(rows):
        for col in range(cols):
            for h in range(chan):
                v = format(image[row][col][h], "08b")
                data += v[-1]

    print(len(data), rows, cols, chan)

    # Group the 8th bits together
    all_bytes = [ data[i:i+8] for i in range(0, len(data), 8) ]

    print(len(all_bytes))

    # Translate binary to char
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-(len(terminator)):] == terminator:
            break

    decoded_data = decoded_data[:-(len(terminator))]

    # Output data
    print(decoded_data)
    
from cryptography.fernet import Fernet, InvalidToken
from cv2 import cv2
import numpy as np
import random, hashlib, time, os
import Stanim

"""=== 4-BIT IMAGE IN IMAGE STEGANOGRAPHY ==="""
def imgEncode_4bit(carrier_dir, payload_dir, out_dir): 
    # Read carrier and payload image
    image_carrier = cv2.imread(carrier_dir) 
    image_payload = cv2.imread(payload_dir)

    # Hidden data cannot exceed the capacity of carrier
    if image_payload.shape[0] > image_carrier.shape[0]:
        print('[!] Payload image is larger (width) than its carrier')
        print("Payload width: %d" % image_payload.shape[0])
        print("Carrier width: %d" % image_carrier.shape[0])
        return
    if image_payload.shape[1] > image_carrier.shape[1]:
        print('[!] Payload image is larger (height) than its carrier')
        print("Payload height: %d" % image_payload.shape[1])
        print("Carrier height: %d" % image_carrier.shape[1])
        return
    
    # Process timer
    start_time = time.time()
    print("[*] Process can take a while depending on size of images")
    print("[*] Images of 2500x2000px can take up to 90 seconds")

    # Go through each bit in payload image
    for i in range(image_payload.shape[0]): 
        for j in range(image_payload.shape[1]): 
            for k in range(3):
                # Find 8-bit values for each (B,G,R)
                v_carrier = format(image_carrier[i][j][k], '08b') 
                v_payload = format(image_payload[i][j][k], '08b') 
                
                # Taking 4 MSBs from each image
                v = v_carrier[:4] + v_payload[:4]

                # Create image matrix with bits from carrier and payload               
                image_carrier[i][j][k] = int(v, 2)
      
    # Create image with visuals of carrier and hidden data of payload
    cv2.imwrite(out_dir, image_carrier)
    print("Process took: %.2f seconds" % (time.time() - start_time))

def imgDecode_4bit(image_dir, payload_outdir):  
    # Read encoded image 
    image = cv2.imread(image_dir)
      
    # Create a blank image to modify and output later
    image_payload = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
    #image_carrier = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
    
    # Process timer
    start_time = time.time()
    print("[*] Process can take a while depending on size of images")
    print("[*] Images of 2500x2000px can take up to 90 seconds")

    # For each bit in (B,G,R) inside each pixel
    for i in range(image.shape[0]): 
        for j in range(image.shape[1]):
            for k in range(3):
                # Turn each data into 8-bit
                v = format(image[i][j][k], '08b')
                
                # Extract the MSB from encoded image
                v_payload = v[4:] + chr(random.randint(0,1) + 48) * 4
                # Extract the carrier image and purge its hidden data
                #v_carrier = v[:4] + chr(random.randint(0,1) + 48) * 4
                

                # Modify the blank images with MSB
                image_payload[i][j][k] = int(v_payload, 2)
                #image_carrier[i][j][k] = int(v_carrier, 2)
      
    # Create an image of the decoded image
    cv2.imwrite(payload_outdir, image_payload)
    #cv2.imwrite("C:/Users/hchiu/Desktop/zz.png", image_carrier)
    print("Process took: %.2f seconds" % (time.time() - start_time))

"""=== 1-BIT IMAGE IN IMAGE STEGANOGRAPHY ==="""
def imgEncode_1bit(carrier_dir, payload_dir, out_dir, terminator, terminal_end):
    # Read carrier and payload images
    image_carrier = cv2.imread(carrier_dir) 
    image_payload = cv2.imread(payload_dir)

    terminator = ''.join([ format(ord(i), "08b") for i in terminator ])
    terminal_end = ''.join([ format(ord(i), "08b") for i in terminal_end ])

    # Hidden data cannot exceed the capacity of carrier
    carrier_px = image_carrier.shape[0] * image_carrier.shape[1]
    vacant_bits = 3 * carrier_px
    payload_px = image_payload.shape[0] * image_payload.shape[1]
    payload_bits = 24*payload_px + len(terminator)*image_payload.shape[0] + len(terminal_end)
    if payload_bits > vacant_bits:
        # Warn user if unable to encode
        print('[!] Payload image is larger than its carrier')
        print("Bits to encode: %s" % (payload_bits))
        print("Bits available: %s" % (vacant_bits))
        return
    
    # Process timer
    start_time = time.time()
    print("[*] Encoding...")

    # Go through each bit in payload image
    data = ""
    for i in range(image_payload.shape[0]): 
        for j in range(image_payload.shape[1]): 
            for k in range(3):
                # Gather all its pixels in 8-bits
                data += format(image_payload[i][j][k], '08b')
        
        # Add termination sequence for decodability 
        data += terminator
    data += terminal_end

    # Go through each bit in carrier image
    data_index = 0
    for i in range(image_carrier.shape[0]):
        for j in range(image_carrier.shape[1]):
            for k in range(3):
                # Modify the LSB with 1-bit of payload image
                if data_index < len(data):
                    v_carrier = format(image_carrier[i][j][k], '08b')
                    v = v_carrier[:7] + data[data_index]
                    image_carrier[i][j][k] = int(v,2)
                    data_index += 1
                else:
                    break
    
    # Create image with visuals of carrier and hidden data of payload
    cv2.imwrite(out_dir, image_carrier)
    print("Process took: %.2f seconds" % (time.time() - start_time))

def imgDecode_1bit(image_dir, payload_outdir, terminator, terminal_end):  
    # Read encoded image 
    image = cv2.imread(image_dir)

    terminator = ''.join([ format(ord(i), "08b") for i in terminator ])
    terminal_end =  ''.join([ format(ord(i), "08b") for i in terminal_end ])

    # Process timer
    start_time = time.time()
    print("[*] Decoding...")

    # For each bit in (B,G,R) inside each pixel
    data = ""
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            for k in range(3):
                # Gather only the payload bits
                v = format(image[i][j][k], '08b')
                data += v[-1]

    """ 
    # Image matrix of payload image created from str of (B,G,R) bits
    # [ 
    # [ [B,G,R],[B,G,R],...,[B,G,R] ], (B,G,R) is the data of a pixel
    # [ [B,G,R],[B,G,R],...,[B,G,R] ], length of a row is image width
    # [    :       :           :    ], length of column is image height
    # [ [B,G,R],[B,G,R],...,[B,G,R] ],
    # ]
    """

    # Remove the part of image without the payload bits
    #payload_bits = data[:data.find(terminal_end)]

    # Split bits by the row termination sequence
    #rows = payload_bits.split(terminator)
    rows = data.split(terminator)

    # Group the bits into 8-bits
    grouped = []
    for elem in rows:
        grouped.append([ int(elem[i:i+8],2) for i in range(0,len(elem),8) ])

    # Group the 8-bits into a (B,G,R) pixel
    tupled = []
    for elem in grouped:
        tupled.append([ elem[i:i+3] for i in range(0,len(elem),3) ])

    # idk why this way is better (no cropping)
    # than removing the data after terminal end
    del tupled[-1]

    # Image matrix is completed, but it cannot create an image
    # Create a blank image copy the pixels of the image matrix
    px_count = 0
    width, height = len(tupled[0]), len(tupled)
    blank = np.zeros((height, width, 3), np.uint8)

    # For each pixel in the blank image
    for i in range(height):
        for j in range(width):
            # Replace its pixel values with the image matrix
            try:
                blank[i,j] = tupled[i][j]
        
            # Diff sizes may cause extra pixels, report to user
            except IndexError:
                print(tupled[i][j])
                print(blank[i,j])
                px_count += 1

    # Create an image of the decoded image
    cv2.imwrite(payload_outdir, blank)
    print("%d pixels were deleted, %d rows were deleted" % (px_count, px_count//width))
    print("Process took: %.2f seconds" % (time.time() - start_time))


"""=== TEXT IN IMAGE STEGANOGRAPHY ==="""
def txtEncode(payload_dir, out_dir, enigma, terminator):
    # Read image
    image = cv2.imread(payload_dir)

    # Add termination sequence for decodability
    enigma += terminator 
    data_index = 0

    # Hidden data cannot exceed the capacity of carrier
    max_bytes = image.shape[0] * image.shape[1] * 3 // 8
    print("[*] Maximum bytes to encode:", max_bytes)
    if len(enigma) > max_bytes:
        print("[!] Insufficient bytes: larger image or less data is needed")
        return
    
    print("[*] Encoding data...")

    # Turn data into 8-bits
    enigma = ''.join([ format(ord(i), "08b") for i in enigma ])

    # For each bit in carrier image
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            for k in range(3):
                # Only if data is not yet encoded
                if data_index < len(enigma):
                    # Convert to 8-bits and only modify the LSB in the image
                    v = format(image[i][j][k], '08b')
                    image[i][j][k] = int(v[:-1] + enigma[data_index], 2)
                    data_index += 1
                else:
                    break
    
    # Create image with enigma inside
    cv2.imwrite(out_dir, image)

def txtDecode(payload_dir, terminator):
    # Read image
    image = cv2.imread(payload_dir)

    print("[*] Decoding...")

    # For each (R,G,B) tuple data in each pixel
    data = ""
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            for k in range(3):

                # Store the LSB of each pixel
                v = format(image[i][j][k], '08b')
                data += v[-1]

    # Group the 8th bits together
    all_bytes = [ data[i:i+8] for i in range(0, len(data), 8) ]

    # Translate binary to char
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-(len(terminator)):] == terminator:
            break
    
    # Return decoded data
    print(decoded_data[:-(len(terminator))])


"""=== ENCRYPT DATA ==="""
# Generate new key
class Encrypt:
    def __init__(self, key_dir):
        self.key_dir = key_dir

    def genKey(self):
        # Write the new key in the file
        self.key = Fernet.generate_key()
        with open(self.key_dir, "wb") as k:
            k.write(self.key)

    def loadKey(self):
        return open(self.key_dir, "r").read()

    def encrypt(self, enigma, reuse=True):
        if not reuse:
            # If key is lost or new key is generated
            # Previous encrypted data may be undecryptable
            # Since they require the old and lost keys
            self.genKey()
        f = Fernet(self.loadKey())

        return f.encrypt(enigma)
        
    def decrypt(self, enigma):
        f = Fernet(self.loadKey())
        return f.decrypt(enigma)


"""=== CONVERT FILE TYPES ==="""
def convertImages(image_dir):
    # Convert jpg to png
    if image_dir[-3:] == "jpg":
        image = cv2.imread(image_dir)
        cv2.imwrite(image_dir[:-3] + "png", image)
        print("[JPG] image was converted to [PNG] image type")
    
    # Cause an error for main() to handle
    else:
        return 1/0


"""=== MAIN TERMINAL ==="""
# Startup messages
def startup():
    print("=== STEGANOGRAPHY TEXT/IMAGES THROUGH LSB ===")
    print("Only .PNG (lossless) files types")
    print("=== === === === === ===== === === === === ===\n")

# Menu choices
def menu():
    print("{h} - Help function")
    print("{a} - About")
    print("{0} - Convert image file types")
    print("{1} - 4-bit image-image steganography")
    print("{2} - 1-bit image-image steganography")
    print("{3} - Text-image steganography")
    print("{4} - Hash data")
    print("{5} - Encrypt text")
    print("{6} - Decrypt text")

# Process to input directories easily
def inDir(converting=False):
    #print("Enter FULL DIR WITH FILE NAME or cd shortcuts")
    cd = input("DIR > ")

    # Shortcuts to directories
    if cd[0:11] == "/s desktop ":
        f = cd[11:]
        cd = "C:/Users/hchiu/Desktop/" + f

    elif cd[0:5] == "/s d ":
        f = cd[5:]
        cd = "C:/Users/hchiu/Desktop/" + f

    elif cd[0:9] == "/s imstan ":
        f = cd[10:]
        cd = "C:/Users/hchiu/Desktop/Imstan" + f


    # Prevent backslashes errors
    if "\\" in cd:
        cd = cd.replace("\\","/")

    if not converting:
        # Warn if user uses JPG/JPEG
        if ".jpg" in cd or ".jpeg" in cd:
            print("[!] Warning, [JPG] and [JPEG] file types not compatible")
            print("[!] Process may not work")
    
    print("[*] Looking for file at", cd)
    return cd

# Main terminal
def main():
    # Error texts
    attribute_error_dir = "[!] File(s) not found, ensure correct DIR and spelling\n"
    error_input = "[!] Error input, ensure correct spelling"
    error_unexpected = "[!!] UNEXCEPTED ERROR [!!]"
    return_to_menu = "\nPress any key to return to main menu"

    # Menu traversing functions
    clear = lambda: os.system('clear') # 'CLS' or 'cls' for windows
    back = lambda: print(return_to_menu)
    error = lambda: print(attribute_error_dir + return_to_menu)
    error_in = lambda: print(error_input)
    error_unex = lambda: print(error_unexpected)
    
    # Key DIR for encryption/decryption
    local_dir = "/home/kenroku/Pictures/Stenography/" #"C:/Users/hchiu/Documents/Album/Code/"
    key_dir = local_dir + "Misc Tests/Stenography/k.key"

    # Termination sequence for text encoding and decoding
    telomeres = "TTAGGG" * 1
    tata_box = "TATA" # shorter bit for images
    terminal_end = "XXX"

    # Start Commmands
    try:
        # Command line
        cl = input(">>> ")

        # Help function for commands
        if cl == "h":
            clear()
            print("Select option from main menu by typing the letter/number")
            print("\nPREFIX SYMBOLS DEFINITION")
            print("[*] - processes, clarification, and important info\n[!] - warnings and notices")
            print("[+] - instructions for user input and possible commands")
            print("[>] - user input based on given instructions")
            print("[>>>] - terminal command line input to do processes")
            back()

        # To do/Info
        elif cl == "a":
            clear()
            print("[!] REDUCES IMAGE QUALITY [!]")
            print("[!] Does not retain steganographed text")
            print("TO-DO")
            print("# Encode an entire file of ANY type in an image")
            print("# Use N-Least Significant Bits technique to encode more data")
            print("# Encode massive amounts of data in videos and audio")
            print("# Function that estimates time for image encoding/decoding") # CANT
            print("# Obscure where data is hidden using a pre-shared key which defines where it is")
            print("# Distribute hidden data to multiple files")
            print("# basic photo editor/cropper to make ideal images")
            print("# binary file")
            print("# use math to find payload image size instead of creating image matrix")
            print("# make more efficient, (nest for loop break not efficient?)")
            print("make input on edges to make it harder to visually detect")
            print("Password by making text skip by the amount determined by one char of password")
            back()

        # Convert image file types
        elif cl == "0":
            clear()
            # Input DIR for image to convert
            print("=== CONVERTING IMAGE FILE TYPES ===")
            print("Input FULL DIR for image to be converted")
            cd_imgconvert = inDir(True)

            # Convert image type
            try:
                convertImages(cd_imgconvert)
                back()
            except ZeroDivisionError:
                error()

        # 4-bits image-image steganography
        elif cl == "1":
            clear()
            print("[+] Type [E] to encode ")
            print("[+] Type [D] to decode")
            choice = input("Encode or Decode? [E]/[D] > ").lower()

            # Encoding
            if choice == "e":
                clear()
                # Input DIR for images
                print("=== 4-BITS IMAGE-IMAGE ENCODING ===\n")
                print("[!] DEGRADES QUALITY, IDEALLY SAME IMAGE SIZE")
                print("[*] Poor obsuraction, relatively fast process")
                print("[+] Input FULL DIR for CARRIER Image")
                cd_carrier = inDir()
                print("\n[+] Input FULL DIR for PAYLOAD Image")
                cd_payload = inDir()
                print("\n[+] Input FULL DIR for OUTPUT Image")
                cd_out = inDir()

                # Encode the image into the other image
                try:
                    imgEncode_4bit(cd_carrier, cd_payload, cd_out)
                except AttributeError:
                    error()

            # Decoding
            elif choice == "d":
                clear()
                # Input DIR for images
                print("=== 4-BITS IMAGE-IMAGE DECODING ===\n")
                print("[!] OUTPUT IMAGES MAY NEED TO BE CROPPED")
                print("[+] Input FULL DIR for CARRIER Image")
                cd_carrier = inDir()
                print("\n[+] Input FULL DIR for OUTPUT Image")
                cd_out = inDir()

                # Decode an image from the image
                try:
                    imgDecode_4bit(cd_carrier, cd_out)
                except AttributeError:
                    error()

            else:
                error_in()
                back()

        # 1-bit image-image steganography
        elif cl == "2":
            clear()
            print("[+] Type [E] to encode ")
            print("[+] Type [D] to decode")
            choice = input("Encode or Decode? [E]/[D] > ").lower()

            # Encoding
            if choice == "e":
                clear()
                # Input DIR for images
                print("=== 1-BITS IMAGE-IMAGE ENCODING ===\n")
                print("[*] Relatively slow process, better obscuration")
                print("[+] Input FULL DIR for CARRIER Image")
                cd_carrier = inDir()
                print("\n[+] Input FULL DIR for PAYLOAD Image")
                cd_payload = inDir()
                print("\n[+] Input FULL DIR for OUTPUT Image")
                cd_out = inDir()

                # Encode the image into the other image
                try:
                    imgEncode_1bit(cd_carrier, cd_payload, cd_out, tata_box, terminal_end)
                except AttributeError:
                    error()
            
            # Decoding
            elif choice == "d":
                clear()
                # Input DIR for images
                print("=== 1-BITS IMAGE-IMAGE DECODING ===\n")
                print("[*] Very slow process")
                print("[+] Input FULL DIR for CARRIER Image")
                cd_carrier = inDir()
                print("\n[+] Input FULL DIR for OUTPUT Image")
                cd_out = inDir()

                # Decode an image from the image
                try:
                    imgDecode_1bit(cd_carrier, cd_out, tata_box, terminal_end)
                except AttributeError:
                    error()

            else:
                error_in()
                back()

        # Text-image steganography
        elif cl == "3":
            clear()
            print("[+] Type [E] to encode ")
            print("[+] Type [D] to decode")
            choice = input("Encode or Decode? [E]/[D] > ").lower()

            # Encoding
            if choice == "e":
                clear()
                # Input DIR for images
                print("=== TEXT-IMAGE ENCODING ===\n")
                print("[+] Input FULL DIR for CARRIER Image")
                cd_carrier = inDir()
                print("\n[+] Input FULL DIR for OUTPUT Image")
                cd_out = inDir()

                # Method of inputing hidden data
                print("\n[+] Type [Y] to encode a specific file")
                print("[+] Type [N] for manual multiline input")
                inputType = input("File? [Y]/[N] > ").lower()
                print()

                # Enter data by file
                if inputType == "y":
                    print("[+] Input FULL DIR for file of text")
                    infile_cd = inDir()
                    infile = open(infile_cd, "r")
                    enigma = infile.read()
                
                # Enter data by manual multiline input
                else:
                    print("[+] Type [$end] on its own line to finish")
                    print("=== === Data to be encoded === ===")
                    contents = []
                    while True:
                        try:
                            line = input("> ")
                            if line == "$end":
                                break
                        except EOFError:
                            break
                        contents.append(line)
                    enigma = "\n".join(contents)

                # Encode data into image
                try:
                    txtEncode(cd_carrier, cd_out, enigma, telomeres)
                except AttributeError:
                    error()

            # Decoding
            elif choice == "d":
                clear()
                # Input DIR for image
                print("=== TEXT-IMAGE DECODING ===\n")
                print("[+] Input FULL DIR for Decoding Image")
                cd_carrier = inDir()

                # Decode hidden data from image
                try:
                    txtDecode(cd_carrier, telomeres)
                except AttributeError:
                    error()

            else:
                error_in()
                back()

        # Hashing data
        elif cl == "4":
            clear()
            # Give user instructions to hash and the warnings of hashing
            print("=== HASHES ===\n")
            print("[!] Warning, hashes CANNOT BE DECRYPTED")
            print("[+] Hashing Options:")
            print("[+] [MD5], [SHA-256], [SHA-512]")
            print("[+] [SHA-3-256], [SHA-3-512], [BLAKE2s], [BLAKE2b]")
            print("=== Hash Information || Last updated: 2020-02-29 ===")
            print("MD5 obsolete\nSHA-2 may soon be obsolete\nBLAKE2 most secure and fastest\n")

            # Data to be hashed
            data = input("Data to be hashed > ").encode()

            # Can hash the data to different types
            hash_type = input("Hash type > ")
            if hash_type == "MD5":
                print("MD5:", hashlib.md5(data).hexdigest())
            elif hash_type == "SHA-256":
                print("SHA-256:", hashlib.sha256(data).hexdigest())
            elif hash_type == "SHA-512":
                print("SHA-512:", hashlib.sha512(data).hexdigest())
            elif hash_type == "SHA-3-256":
                print("SHA-3-256:", hashlib.sha3_256(data).hexdigest())
            elif hash_type == "SHA-3-512":
                print("SHA-3-512:", hashlib.sha3_512(data).hexdigest())
            elif hash_type == "BLAKE2s":
                print("BLAKE2c:", hashlib.blake2s(data).hexdigest())
            elif hash_type == "BLAKE2b":
                print("BLAKE2b:", hashlib.blake2b(data).hexdigest())
            else:
                error_in()
                back()

        # Encrypting data
        elif cl == "5" or cl == "5 new":
            clear()
            # Turn input str into utf-8 bytes and encrypt
            print("=== TEXT ENCRYPTION ===\n")
            print("[+] Type [$end] on its own line to end")
            print("=== === Data to be encrypted === ===")
            e = Encrypt(key_dir)

            # Input multilined data 
            enigma = []
            while True:
                try:
                    line = input("> ")
                    if line == "$end":
                        break
                except EOFError:
                    break
                enigma.append(line)
            enigma = "\n".join(enigma).encode()

            # Normal encryption of not generating new key
            if cl == "5":
                encrypted = e.encrypt(enigma)

            # Elevated encryption of new key
            elif cl == "5 new":
                # Give user warnings of generating new key
                print("[*] If key is lost or new key is generated")
                print("[*] Previous encrypted data may be undecryptable")
                print("[*] Since they require the old keys to decrypt")

                # Require confirmation to proceed
                confirmation = input("[+] Type [GENERATE NEW KEY] to proceed > ")
                if confirmation == "GENERATE NEW KEY":
                    encrypted = e.encrypt(enigma, False)
                else:
                    print("[!] Process aborted")

            # Return the encrypted string of data
            try:
                print(str(encrypted)[2:-1])
                back()
            except:
                error_unex()

        # Decrypting data
        elif cl == "6":
            clear()
            print("=== TEXT DECRYPTION ===")
            e = Encrypt(key_dir)

            # Decrypt input based on the given key
            try:
                print("Input text to decrypt")
                encrypted = input("> ").strip()
                decrypted = e.decrypt(encrypted.encode('utf-8'))
                print(str(decrypted)[2:-1])

            # If unable to, report to user
            except InvalidToken:
                print("[!] Cannot decrypt with the given key")
                print("[!] Key could have been changed")
                back()
            except:
                error_unex()

        # Else, return to main menu
        else:
            clear()
            startup()
            menu()
            print()
            
    # Canceling process and returning to main menu
    except KeyboardInterrupt:
        clear()
        startup()
        menu()
        print()

    main()
#startup()
#menu()
#print()
#main()


def s():
    imgEncode_1bit("/home/kenroku/Pictures/Stenography/4.png", 
                "/home/kenroku/Pictures/Stenography/5.png",
                "/home/kenroku/Pictures/Stenography/out.png",
                "TATA", "XXX")

def u():
    imgDecode_1bit("/home/kenroku/Pictures/Stenography/out.png", 
                "/home/kenroku/Pictures/Stenography/test.png",
                "TATA", "XXX")

u()
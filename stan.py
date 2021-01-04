import text

def stan():
    try:
        cl = int(input("> "))
        payload_dir = "/home/kenroku/Pictures/Stenography/1.png"
        out_dir = "/home/kenroku/Pictures/Stenography/out.png"
        enigma = "hi"
        terminator = "TATA"


        if cl == 0:
            text.encode(payload_dir, out_dir, enigma, terminator)
        elif cl == 1:
            text.decode(out_dir, terminator)
    except:
        exit()

    stan()
stan()
import text

def stan():

        cl = int(input("> "))
        payload_dir = "/home/kenroku/Pictures/Stenography/3.png"
        out_dir = "/home/kenroku/Pictures/Stenography/out.png"
        enigma = "hiTELOMERES"
        terminator = "TELOMERES"


        if cl == 0:
            text.encode(payload_dir, out_dir, enigma, terminator)
        elif cl == 1:
            text.decode(out_dir, terminator)

stan()
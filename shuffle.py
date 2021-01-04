from cv2 import cv2
import random, hashlib
import numpy as np

def get_permutation(arr, key_part):
    np.random.seed(key_part)
    permutation = list(range(len(arr)))
    np.random.shuffle(permutation)

    return permutation


def shuffle(payload_dir, out_dir, input_key):
    # Read image
    image = cv2.imread(payload_dir)


    # Hash the key to add complexity to shuffling
    # Even if shuffling algorithm uncovered, they will not know original key
    # Chosen hash algorithms and addition is arbitrary
    # key = input_key.encode()
    # hashed = hashlib.sha3_512(key).hexdigest() + hashlib.blake2b(key).hexdigest()

    """
    # Choice of seed from hash is arbitrary
    # Possible collision (multiple hashes leads to same permutation) -> not secure
    # Bad practice to use random cryptographically, but no other choice
    ## since we need cannot have truely random; we need a seed
    """

    # Shuffle the rows
    permutation = get_permutation(image, input_key)
    image[:] = [image[j] for j in permutation]

    # Return shuffled image
    cv2.imwrite(out_dir, image)


def unshuffle(payload_dir, out_dir, input_key):
    # Read shuffled image
    image = cv2.imread(payload_dir)

    # key = input_key.encode()
    # hashed = hashlib.sha3_512(key).hexdigest() + hashlib.blake2b(key).hexdigest()

    # Unshuffle the rows
    permutation = get_permutation(image, input_key)
    res = [None] * image.shape[0]
    for i, j in enumerate(permutation):
        res[j] = image[i]
    image[:] = res

    # Return unshuffled image
    cv2.imwrite(out_dir, image)


payload_dir = "/home/kenroku/Pictures/Stenography/1.png"
out1_dir = "/home/kenroku/Pictures/Stenography/out1.png"
out2_dir = "/home/kenroku/Pictures/Stenography/out2.png"
key = 1
shuffle(payload_dir, out1_dir, key)
unshuffle(out1_dir, out2_dir, key)



""" unshuffle and seeded shuffle
import random

def getperm(l):
    seed = sum(sum(a) for a in l)
    random.seed(seed)
    perm = list(range(len(l)))
    print("perm", perm)
    random.shuffle(perm)
    random.seed()
    return perm

def shuffle(l):
    perm = getperm(l)
    l[:] = [l[j] for j in perm]

def unshuffle(l):
    perm = getperm(l)
    res = [None] * len(l)
    for i, j in enumerate(perm):
        res[j] = l[i]
    l[:] = res

l=[(1,2),(3,4),(5,6),(7,8),(9,10)]   
print(l)    
shuffle(l)
print(l) # shuffled
unshuffle(l)
print(l)  # the original


"""
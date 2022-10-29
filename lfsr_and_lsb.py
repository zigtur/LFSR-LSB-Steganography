'''
Le code permet de :
	- chiffrer et cacher un message dans une image
		JPEG ne fonctionne pas
		PNG fonctionne
		BMP pas testé
	- extraire et déchiffrer le message d'une image

Technique de chiffrement = Construction d'une clé de chiffrement à partir d'un LFSR
				Le LFSR est lui-même construit à partir d'un mot de passe (c'est sûrement dégueu niveau crypto)

Technique de stegano = LSB (Least Significant Bit)


Created by : Cyberahttack - ML
Tested with : Python 3.8.10
Documentation is not needed when you have the code ;)
'''

import base64
from PIL import Image
# Convert encoding data into 8-bit binary
# form using ASCII value of characters
def genData(data):

        # list of binary codes
        # of given data
        newd = []

        for i in data:
            newd.append(format(ord(i), '08b'))
        return newd

# Pixels are modified according to the
# 8-bit binary data and finally returned
def modPix(pix, data):

    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)
    for i in range(lendata):

        # Extracting 3 pixels at a time
        pix = [value for value in imdata.__next__()[:3] +
                                imdata.__next__()[:3] +
                                imdata.__next__()[:3]]

        # Pixel value should be made
        # odd for 1 and even for 0
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pix[j]% 2 != 0):
                pix[j] -= 1

            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if(pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1
                # pix[j] -= 1
        # Eighth pixel of every set tells
        # whether to stop ot read further.
        # 0 means keep reading; 1 means thec
        # message is over.
        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if(pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1

        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

def sxor(s1,s2):
    return ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(s1,s2))

def encode_enc(newimg, data):
    print(newimg.size)
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):
        # Putting modified pixels in the new image
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

def lfsr_oper(r1, key):
    bit = sum([int(r1[i]) * int(key[i]) for i in range(len(key))]) % 2
    return bit

def lfsr(entry, data_length):
    entry_tab = []
    key = []
    # le seed est construit à partir du password et défini combien de fois le LFSR tourne avant de construire la clé qui servira à chiffrer
    seed_number = 0
    for char in entry :
        bin_letter = format(ord(char), '08b')
        seed_number += ord(char)
        for bit in bin_letter :
            entry_tab.append(bit)

    #multiplie le seed par 96
    seed_number *= 96
    len_entry = len(entry_tab)
    key_from_pass = [7,42,13,31,15,27,
                     24,39,11,9,45,21,22,14]
    tab_key = [0,entry_tab[key_from_pass.pop()],0,
               entry_tab[key_from_pass.pop()],0,
               entry_tab[key_from_pass.pop()],
               entry_tab[key_from_pass.pop()],
               0,entry_tab[key_from_pass.pop()],
               0,0,entry_tab[key_from_pass.pop()],
               0,0,0,0,0,entry_tab[key_from_pass.pop()],
               0,entry_tab[key_from_pass.pop()],
               0,0,entry_tab[key_from_pass.pop()],
               0,entry_tab[key_from_pass.pop()],
               0,0,0,entry_tab[key_from_pass.pop()],
               entry_tab[key_from_pass.pop()],
               0,entry_tab[key_from_pass.pop()],
               0,0,entry_tab[key_from_pass.pop()]]

    missing_size = len(entry_tab) - len(tab_key)
    for i in range(missing_size) :
        tab_key.insert(0,0)

    for i in range(seed_number):
        bit = lfsr_oper(entry_tab, tab_key)
        entry_tab.pop()
        entry_tab.insert(0,bit)

    bit_str = []
    for i in range(data_length*8):
        bit = lfsr_oper(entry_tab, tab_key)
        bit_str.append(entry_tab.pop())
        entry_tab.insert(0,bit)

#    print(bit_str)
    key_xor_str = ""
    for b in range(int(len(bit_str) / 8)):
        byte = bit_str[b*8:(b+1)*8]
        octet = ""
        for bit in byte :
          octet += str(bit)
        #print(type(octet))
        #print(int(octet, 2))
        key_xor_str += chr(int(octet, 2))

    return key_xor_str

# Encode data into image
def encode():
    img = input("Enter image name(with extension) : ")
    image = Image.open(img, 'r')

    data = input("Enter data to be encoded : ")
    if (len(data) == 0):
        raise ValueError('Data is empty')

    lfsr_entry = input("Enter the password (min 6 characters) : ")
    if (len(lfsr_entry) < 6):
        raise ValueError("Password is too short")

    # Construction de la clé crypto à partir du password
    lfsr_output = lfsr(lfsr_entry, len(data))

    print("data = ",str(data))
    print("clé = ",str(lfsr_output))
    data_to_insert = sxor(data,lfsr_output)
    print(data_to_insert)

    newimg = image.copy()
    encode_enc(newimg, data_to_insert)

    new_img_name = input("Enter the name of new image(with extension) : ")
    newimg.save(new_img_name, str(new_img_name.split(".")[1].upper()))

# Decode the data in the image
def decode():
    img = input("Enter image name(with extension) : ")
    image = Image.open(img, 'r')

    data = ''
    imgdata = iter(image.getdata())

    while (True):
        pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]

        # string of binary data
        binstr = ''

        for i in pixels[:8]:
            if (i % 2 == 0):
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if (pixels[-1] % 2 != 0):
            lfsr_entry = input("Enter the password (min 6 characters) : ")
            if (len(lfsr_entry) < 6):
                raise ValueError("Password is too short")
            #Reconstruction de la clé crypto à partir du password
            lfsr_output = lfsr(lfsr_entry, len(data))
            print("data = ",str(data))
            print("clé = ",str(lfsr_output))
            exported_data = sxor(data,lfsr_output)

            return exported_data

# Main Function
def main():
    a = int(input(":: Welcome to Steganography ::\n"
                        "1. Encode\n2. Decode\n"))
    if (a == 1):
        encode()

    elif (a == 2):
        print("Decoded Word :  " + decode())
    else:
        raise Exception("Enter correct input")

# Driver Code
if __name__ == '__main__' :
    # Calling main function
    main()

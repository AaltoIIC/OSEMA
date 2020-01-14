"""Function used to decrypt message encrypted with AES 128-bit CBC. Returns message as hex-string"""
def encrypt_msg(msg, key): #msg = string, key = 128-bit key as a byte-string
    #Encrypt content
    n = 16
    padded_content = msg + (n - (len(msg) % n)) * " " #pad content
    padded_content_list = [padded_content[i:i+n] for i in range(0, len(padded_content), n)] #divide into list

    iv = crypto.getrandbits(128) # hardware generated random IV (never reuse it)
    cipher = AES(shared_secret, AES.MODE_CBC, iv)
    encrypted_string = iv

    #encryption
    for block in padded_content_list:
    	ciphertext = cipher.encrypt(block.encode("ascii"))
    	encrypted_string += ciphertext
    	cipher = AES(shared_secret, AES.MODE_CBC, ciphertext)

    return ubinascii.hexlify(encrypted_string).decode("ascii")

"""Function used to encrypt message with AES 128-bit CBC"""
def encrypt_msg(msg, key): #msg = byte-string, key = 128-bit key as a byte-string
    n = 16
    encrypted_data_list = [payload[i:i+n] for i in range(0, len(payload), n)]
    cipher = AES(shared_secret, AES.MODE_CBC, encrypted_data_list[0])
    msg = ""
    for block in encrypted_data_list[1:]:
    	decrypted_msg = cipher.decrypt(block)
    	msg += decrypted_msg.decode("ascii")
    	cipher = AES(shared_secret, AES.MODE_CBC, block)
    return msg

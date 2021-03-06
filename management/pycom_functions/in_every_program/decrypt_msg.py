"""Function used to encrypt message with AES 128-bit CBC"""
def decrypt_msg(msg, key): #msg = byte-string, key = 128-bit key as a byte-string
    n = 16
    encrypted_data_list = [msg[i:i+n] for i in range(0, len(msg), n)]
    cipher = AES(key, AES.MODE_CBC, encrypted_data_list[0])
    msg = ""
    for block in encrypted_data_list[1:]:
    	decrypted_msg = cipher.decrypt(block)
    	msg += decrypted_msg.decode("ascii")
    	cipher = AES(key, AES.MODE_CBC, block)
    return msg

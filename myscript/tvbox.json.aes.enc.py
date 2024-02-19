## 解密格式：字符串以"2324"开头(此编码对应utf-8字符为"$#"）
##          开头的"2324"到"2423"(此编码对应utf-8字符为"#$")中间为密码,(aes128要求密码最多16个byte，不够就padding，padding方式为：PKCS5Padding)
##          结尾的13个byte为iv,(cbc要求iv数字最大16个byte，tvbox内置解密算法必须保证密文最后跟13个byte作为IV，需要padding)
##
## 对应的密文格式：（utf-8编码后）"2324"(utf-8解码后为字符"$#") + "xxxxxxxxxxxx"(utf-8编码后的密码字符，aes128的密码最多16个byte，两个字符为1个byte）+ "2423"(utf-8解码后为字符"#$") + 
##                              "xxxxxx"(明文字符经过utf-8编码后，再经过aes128加密后的密文) + "xxxxxxxxxxxxxxxxxxxxxxxxxx"(utf-8编码后的iv字符，13个byte，共计26个字符)

from Cryptodome.Cipher import AES

def cbc_encrypt(key_str, iv_str, plaintext_str):
    block_size = 16
    if len(key_str) < 0 or len(key_str) > 16 :
        print("length for key_str is larger than 16!")
        exit()
    if len(iv_str) < 0 or len(iv_str) > 13:
        print("length for iv_str is larger than 13")
        exit()

    # for key and iv padding
    padded_key_hexstr = padding_to_16bytes(key_str).encode().hex()
    padded_iv_hexstr = padding_to_16bytes(iv_str).encode().hex()

    # for plaintext padding
    plaintext_padding_size = block_size - len(plaintext_str.encode()) % block_size
    print("plaintext_padding_size is", plaintext_padding_size)
    # Use PKCS5Padding
    plaintext_padding_bytes = bytes([plaintext_padding_size]) * plaintext_padding_size
    padded_plaintext_bytes = plaintext_str.encode() + plaintext_padding_bytes

    # print(key_hexstr)
    # print(iv_hexstr)
    # print(padded_plaintext_bytes)

    cipher = AES.new(bytes.fromhex(padded_key_hexstr), AES.MODE_CBC, bytes.fromhex(padded_iv_hexstr))
    ciphertext_hexstr = cipher.encrypt(padded_plaintext_bytes).hex()

    return ciphertext_hexstr

def cbc_decrypt(key_str, iv_str, ciphertext_hexstr):
    block_size = 16
    if len(key_str) < 0 or len(key_str) > 16 :
        print("length for key_str is larger than 16!")
        exit()
    if len(iv_str) < 0 or len(iv_str) > 13:
        print("length for iv_str is larger than 13")
        exit()
    if len(bytes.fromhex(ciphertext_hexstr)) % block_size != 0:
        print("Length for ciphertext_bytes is ", len(bytes.fromhex(ciphertext_hexstr)), ", is not padded to 16 byte.")
        exit()

    # for key and iv padding
    padded_key_hexstr = padding_to_16bytes(key_str).encode().hex()
    padded_iv_hexstr = padding_to_16bytes(iv_str).encode().hex()
    # for ciphertext
    cipherext_bytes = bytes.fromhex(ciphertext_hexstr)

    # print(key_hexstr)
    # print(iv_hexstr)
    # print(cipherext_bytes)

    cipher = AES.new(bytes.fromhex(padded_key_hexstr), AES.MODE_CBC, bytes.fromhex(padded_iv_hexstr))
    plaintext_padded_hexstr = cipher.decrypt(cipherext_bytes).hex()

    plaintext_padding_bytes_size = int(bytes.fromhex(plaintext_padded_hexstr)[-1])
    print("plaintext_padding_bytes_size is:", plaintext_padding_bytes_size)
    plaintext_hexstr = plaintext_padded_hexstr[0 : (len(bytes.fromhex(plaintext_padded_hexstr)) - plaintext_padding_bytes_size) * 2]

    return plaintext_hexstr

# Specially for tvbox aes encryption, only
def padding_to_13bytes(iv_str):
    if len(iv_str) <= 0 or len(iv_str) > 13:
        print("length for iv_str is invalid!")
        exit()

    while len(iv_str) < 13:
        iv_str += '0'
    return iv_str

# For aes key/iv padding
def padding_to_16bytes(str):
    if len(str) <= 0 or len(str) > 16:
        print("Input str length invalid!")
        exit()
    
    while len(str) < 16:
        str += '0'
    return str

def get_enc_packed_hexstr(key_str, iv_str, ciphertext_hexstr):
    return ('$#' + key_str + '#$').encode().hex() + ciphertext_hexstr + padding_to_13bytes(iv_str).encode().hex()

def get_dec_unpack_hexstr(packed_ciphertext_hexstr):
    fixed_end_iv_bytes_size = 13
    start_idx = packed_ciphertext_hexstr.find('2324')
    if(start_idx == -1):
        print("No match found")
        exit()
    else:
        start_idx += 4

    end_idx = len(packed_ciphertext_hexstr) - fixed_end_iv_bytes_size * 2
    if end_idx < 0:
        print("Invalid ciphertext length")
        exit()

    # print("packed_ciphertext_hexstr size is:", len(packed_ciphertext_hexstr))
    # print("start_idx is ", start_idx)
    # print("end_idx is ", end_idx)
    return(packed_ciphertext_hexstr[start_idx : end_idx])

if __name__ == '__main__':
    key = '123456'
    iv = '2111111111000'

    my_dec_json_path = '../my.dec.json'
    my_enc_json_path = '../my.enc.json'

    #####################################
    ######### Encryption ################
    #####################################
    with open(my_dec_json_path, 'r', encoding = 'utf-8') as file:
        plaintext_str = file.read()
    # print(plaintext_str)

    ciphertext_hexstr = cbc_encrypt(key, iv, plaintext_str)
    packed_ciphertext_hexstr = get_enc_packed_hexstr(key, iv, ciphertext_hexstr)
    print(packed_ciphertext_hexstr)

    with open(my_enc_json_path, 'w') as file:
        file.write(packed_ciphertext_hexstr)


    # ####################################
    # ######## Decryption ################
    # ####################################
    # with open(my_enc_json_path, 'r', encoding = 'utf-8') as file:
    #     ciphertext_hexstr = file.read()
    # unpacked_plaintext_hexstr = get_dec_unpack_hexstr(ciphertext_hexstr)
    # decrypted_str = bytes.fromhex(cbc_decrypt(key, iv, unpacked_plaintext_hexstr)).decode()

    # print(decrypted_str)
    # with open('../my.test.json', 'w', encoding = 'utf-8') as file:
    #     file.write(decrypted_str)
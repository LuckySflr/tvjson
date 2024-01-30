## 解密格式：字符串以"2324"开头(此编码对应utf-8字符为"$#"）
##          开头的"2324"到"2423"(此编码对应utf-8字符为"#$")中间为密码,(aes128要求密码最多16个byte，不够就padding，padding方式为：PKCS5Padding)
##          结尾的13个byte为iv,(cbc要求iv数字最大16个byte，tvbox内置解密算法必须保证密文最后跟13个byte作为IV，需要padding)
##
## 对应的密文格式：（utf-8编码后）"2324"(utf-8解码后为字符"$#") + "xxxxxxxxxxxx"(utf-8编码后的密码字符，aes128的密码最多16个byte，两个字符为1个byte）+ "2423"(utf-8解码后为字符"#$") + 
##                              "xxxxxx"(明文字符经过utf-8编码后，再经过aes128加密后的密文) + "xxxxxxxxxxxxxxxxxxxxxxxxxx"(utf-8编码后的iv字符，13个byte，共计26个字符)

from Cryptodome.Cipher import AES

def cbc_encrypt(key_str, iv_str, plaintext_str):
    block_size = 16
    if len(key_str.encode()) > 16:
        print("length for key_str is larger than 16!")
        exit()
    if len(iv_str.encode()) > 13:
        print("length for iv_str is larger than 13")
        exit()

    padding_size = block_size - len(plaintext_str.encode('utf-8')) % block_size
    print("padding_size is", padding_size)

    padding_bytes = bytes([padding_size]) * padding_size
    padded_plaintext_bytes = plaintext_str.encode() + padding_bytes
    
    key_hexstr = key_str.encode().hex() + '00' * (block_size - len(list(key_str)))
    iv_hexstr = iv_str.encode().hex() + '00' * (block_size - len(list(iv_str)))
    # print(key_hexstr)
    # print(iv_hexstr)
    # print(padded_plaintext_bytes)

    cipher = AES.new(bytes.fromhex(key_hexstr), AES.MODE_CBC, bytes.fromhex(iv_hexstr))
    ciphertext_hexstr = cipher.encrypt(padded_plaintext_bytes).hex()

    return ciphertext_hexstr

def cbc_decrypt(key_str, iv_str, ciphertext_hexstr):
    block_size = 16
    if len(bytes.fromhex(ciphertext_hexstr)) % block_size != 0:
        print("Input decrypt ciphertext_hexstr size is not valid!")
        exit()

    key_hexstr = key_str.encode().hex() + '00' * (block_size - len(list(key_str)))
    iv_hexstr = iv_str.encode().hex() + '00' * (block_size - len(list(iv_str)))
    cipherext_bytes = bytes.fromhex(ciphertext_hexstr)

    # print(key_hexstr)
    # print(iv_hexstr)
    # print(cipherext_bytes)

    cipher = AES.new(bytes.fromhex(key_hexstr), AES.MODE_CBC, bytes.fromhex(iv_hexstr))
    plaintext_hexstr = cipher.decrypt(cipherext_bytes).hex()
    padding_size = int(bytes.fromhex(plaintext_hexstr)[-1])
    print("padding_size is:", padding_size)
    plaintext_hexstr = bytes.fromhex(plaintext_hexstr)[0:len(bytes.fromhex(plaintext_hexstr)) - padding_size].hex()

    return plaintext_hexstr

def extract(ciphertext_hexstr):
    fixed_end_iv_bytes = 13
    start_idx = ciphertext_hexstr.find('2324')
    if(start_idx == -1):
        print("No match found")
        exit()
    else:
        start_idx += 4
    end_idx = len(ciphertext_hexstr) - fixed_end_iv_bytes * 2
    if end_idx < 0:
        print("Invalid ciphertext length")
        exit()
    return(ciphertext_hexstr[start_idx:end_idx])

def iv_packed_padding(iv_hexstr):
    fixed_end_iv_bytes = 13
    if len(bytes.fromhex(iv_hexstr)) > 13:
        print("length for iv_str is larger than 13")
        exit()
    padding_size = fixed_end_iv_bytes - len(bytes.fromhex(iv_hexstr))
    padded_iv_hex_str = iv_hexstr + '00' * padding_size
    return padded_iv_hex_str

def enc_packed_str(key_str, iv_str, ciphertext_hexstr):
    return ('$#' + key_str + '#$').encode().hex() + ciphertext_hexstr + iv_packed_padding(iv_str.encode().hex())

if __name__ == '__main__':
    key = 'luckysflr'
    iv = '3456789abcdef'

    my_dec_json_path = '../my.dec.json'
    my_enc_json_path = '../my.enc.json'

    #####################################
    ######### Encryption ################
    #####################################
    with open(my_dec_json_path, 'r', encoding = 'utf-8') as file:
        plaintext_hexstr = file.read()
    # print(plaintext_hexstr)

    ciphertext_hexstr = cbc_encrypt(key, iv, plaintext_hexstr)
    print(ciphertext_hexstr)
    packed_ciphertext_hexstr = enc_packed_str(key, iv, ciphertext_hexstr)
    with open(my_enc_json_path, 'w') as file:
        file.write(packed_ciphertext_hexstr)


    # ####################################
    # ######## Decryption ################
    # ####################################
    # with open(my_enc_json_path, 'r', encoding = 'utf-8') as file:
    #     ciphertext_hexstr = file.read()
    # extract_plaintext_hexstr = extract(ciphertext_hexstr)
    # plaintext_str = bytes.fromhex(cbc_decrypt(key, iv, extract_plaintext_hexstr)).decode()

    # print(plaintext_str)
    # with open('../my.dec.json', 'w', encoding = 'utf-8') as file:
    #     file.write(plaintext_str)
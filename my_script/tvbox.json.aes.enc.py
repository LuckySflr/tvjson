## 解密格式：字符串以"2324"开头(此编码对应utf-8字符为"$#"）
##          开头的"2324"到"2423"(此编码对应utf-8字符为"#$")中间为密码,(aes128要求密码最多16个byte，不够就padding，padding方式为：PKCS5Padding)
##          结尾的13个byte为iv,(cbc要求iv数字最大16个byte，tvbox内置解密算法必须保证密文最后跟13个byte作为IV，需要padding)
##
## 对应的密文格式：（utf-8编码后）"2324"(utf-8解码后为字符"$#") + "xxxxxxxxxxxx"(utf-8编码后的密码字符，aes128的密码最多16个byte，两个字符为1个byte）+ "2423"(utf-8解码后为字符"#$") + 
##                              "xxxxxx"(明文字符经过utf-8编码后，再经过aes128加密后的密文) + "xxxxxxxxxxxxxxxxxxxxxxxxxx"(utf-8编码后的iv字符，13个byte，共计26个字符)

from Cryptodome.Cipher import AES

def cbc_encrypt(key_str, iv_str, plaintext_str):
    block_size = 16
    padding_size = block_size - len(plaintext_str.encode('utf-8')) % block_size
    print("padding_size is", padding_size)

    padding_bytes = bytes([padding_size]) * padding_size
    padded_plaintext_bytes = plaintext_str.encode() + padding_bytes
    
    key_hexstr = key_str.encode().hex() + '00' * (block_size - len(list(key_str)))
    iv_hexstr = iv_str.encode().hex() + '00' * (block_size - len(list(iv_str)))
    print(key_hexstr)
    print(iv_hexstr)
    print(padded_plaintext_bytes)

    cipher = AES.new(bytearray.fromhex(key_hexstr), AES.MODE_CBC, bytearray.fromhex(iv_hexstr))
    ciphertext_hexstr = cipher.encrypt(padded_plaintext_bytes).hex()

    return ciphertext_hexstr

def cbc_decrypt(key_str, iv_str, ciphertext_hexstr):
    block_size = 16
    if(len(bytearray.fromhex(ciphertext_hexstr)) % block_size != 0):
        exit()

    cipherext_bytes = bytearray.fromhex(ciphertext_hexstr)

    key_hexstr = key_str.encode().hex() + '00' * (block_size - len(list(key_str)))
    iv_hexstr = iv_str.encode().hex() + '00' * (block_size - len(list(iv_str)))
    print(key_hexstr)
    print(iv_hexstr)
    print(cipherext_bytes)

    cipher = AES.new(bytearray.fromhex(key_hexstr), AES.MODE_CBC, bytearray.fromhex(iv_hexstr))
    plaintext_hexstr = cipher.decrypt(cipherext_bytes).hex()
    return plaintext_hexstr

key = 'luckysflr'
iv = 'luckysflr'

my_path = '../my.json'
with open(my_path, 'r', encoding='utf-8') as file:
    content = file.read()
# content = '1234567890abcdef'

ciphertext_hexstr = cbc_encrypt(key, iv, content)
print(ciphertext_hexstr)

alltext = ('$#' + key + '#$').encode().hex() + ciphertext_hexstr + iv.encode().hex()

with open('../my.test.json', 'w') as file:
    file.write(alltext)

# ciphertext_hexstr = 'f3ed7e4405c39413218fd06014adb5ee'
# plaintext_hexstr = cbc_decrypt(key, iv, ciphertext_hexstr)
# print(plaintext_hexstr)




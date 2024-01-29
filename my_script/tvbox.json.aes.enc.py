## 解密格式：字符串以"2324"开头(此编码对应utf-8字符为"$#"）
##          开头的"2324"到"2423"(此编码对应utf-8字符为"#$")中间为密码,(aes128要求密码最多16个byte，不够就padding，padding方式为：PKCS5Padding)
##          结尾的13个byte为iv,(cbc要求iv数字最大16个byte，tvbox内置解密算法必须保证密文最后跟13个byte作为IV，需要padding)
##
## 对应的密文格式：（utf-8编码后）"2324"(utf-8解码后为字符"$#") + "xxxxxxxxxxxx"(utf-8编码后的密码字符，aes128的密码最多16个byte，两个字符为1个byte）+ "2423"(utf-8解码后为字符"#$") + 
##                              "xxxxxx"(明文字符经过utf-8编码后，再经过aes128加密后的密文) + "xxxxxxxxxxxxxxxxxxxxxxxxxx"(utf-8编码后的iv字符，13个byte，共计26个字符)

from Cryptodome.Cipher import AES
import binascii

def cbc_encrypt(key, iv, plaintext):
    block_size = 16
    padding_size = block_size - len(plaintext.encode('utf-8')) % block_size
    padding_str = str(padding_size) * padding_size
    padded_plaintext = plaintext + padding_str
    
    key_hexstr = key.encode().hex() + '00' * (block_size - len(list(key)))
    iv_hexstr = iv.encode().hex() + '00' * (block_size - len(list(iv)))
    print(key_hexstr)
    print(iv_hexstr)

    cipher = AES.new(bytearray.fromhex(key_hexstr), AES.MODE_CBC, bytearray.fromhex(iv_hexstr))
    ciphertext = cipher.encrypt(padded_plaintext.encode('utf-8'))
    # print(ciphertext.hex())
    return ciphertext


key = '123456'
iv = '1706537911728'

my_path = '../my.json'
with open(my_path, 'r', encoding='utf-8') as file:
    content = file.read()
# print(type(content))
ciphertext = cbc_encrypt(key, iv, content)
alltext = ('$#' + key + '#$').encode().hex() + ciphertext.hex() + iv.encode().hex()
with open('./newfile', 'w') as file:
    file.write(alltext)



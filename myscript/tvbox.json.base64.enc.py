import base64

my_dec_json_path = '../my.dec.json'
my_enc_json_path = '../my.enc.json'

with open(my_dec_json_path, 'r', encoding='utf-8') as file:
    content = file.read()

plaintext = content
ciphertext = base64.b64encode(plaintext.encode())
print(ciphertext)

# decodetext = base64.b64decode(ciphertext)
# print(decodetext.decode())

alltext = "sflrabcd**" + str(ciphertext, encoding = 'utf-8')

my_enc_json_path = '../my.test.json'
with open(my_enc_json_path, 'w') as file:
    file.write(alltext)
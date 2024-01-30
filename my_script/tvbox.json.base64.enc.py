import base64

my_path = '../my.json'
with open(my_path, 'r', encoding='utf-8') as file:
    content = file.read()

plaintext = content
ciphertext = base64.b64encode(plaintext.encode())
print(ciphertext)

alltext = "12345678**" + ciphertext.hex()
with open('./newfile', 'w') as file:
    file.write(alltext)
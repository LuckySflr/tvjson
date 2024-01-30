import base64

my_path = '../my.json'
with open(my_path, 'r', encoding='utf-8') as file:
    content = file.read()

plaintext = content
ciphertext = base64.b64encode(plaintext.encode())
print(ciphertext)

# decodetext = base64.b64decode(ciphertext)
# print(decodetext.decode())

alltext = "sflrabcd**" + str(ciphertext, encoding = 'utf-8')
with open('../my.test.json', 'w') as file:
    file.write(alltext)
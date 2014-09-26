import random


s = '1234567890-=!@#$%^&*()_+`~qwertyuiop[]\\asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}|ASDFGHJKL"ZXCVBNM<>?'
key_length = 256
with open('cookie_secret.txt','w') as f:
    f.write(''.join(random.choice(s) for i in range(key_length)))



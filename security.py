import random

VALID_CHARS = '1234567890-=!@#$%^&*()_+`~qwertyuiop[]\\asdfghjkl;\'zxcvbnm,./QWERTYUIOP{}|ASDFGHJKL"ZXCVBNM<>?'
HASH_LENGTH = 6
SESSION_TOKEN_LENGTH = 256

def randchar():
    return random.choice(VALID_CHARS)

def session_token():
    return ''.join(randchar() for i in xrange(256)) 

def super_hash(s):
    h = ''
    for i in s:
        for j in random_dist(HASH_LENGTH,VALID_CHARS.find(i)):
            h += VALID_CHARS[j]
    return h

def de_super_hash(h):
    s = ''
    L = len(h)
    for i in range(0,L,HASH_LENGTH):
        li = [h[i+j] for j in range(HASH_LENGTH)]
        li = [VALID_CHARS.find(j) for j in li]
        m = sum(li)/len(li)
        s += VALID_CHARS[m]
    return s

def random_dist(length,mean):
    dist = min(mean,len(VALID_CHARS)-mean)
    L = [mean]*length
    for i in range(int(len(L)/2.0)):
        r = int(dist*random.random())
        L[i] = L[i]-r
        L[-(1+i)] = L[-(1+i)]+r
    return L

def encrypt(s):
    L = len(s)
    es = ''
    for i in xrange(L):
        if i%2 == 0:
            es += s[i] + ''.join(randchar() for j in range(L-1))
        else:
            es += ''.join(randchar() for j in range(L-1)) + s[i]
    return super_hash(es)

def decrypt(hes):
    es = de_super_hash(hes)
    idx = 0
    s = ''
    L = int(len(es)**.5)
    for i in range(L):
        if i%2 == 0:
            s += es[idx]
            idx += 2*L-1
        else:
            s += es[idx]
            idx += 1
    return s

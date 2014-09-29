import psycopg2

from security import encrypt, decrypt, session_token

DB_ADDR = '127.0.0.1'

# DB Models

class PoemNotFoundException(Exception):
    pass

class Poem(object):
    @classmethod
    def load(cls,poem_id):
        poem = pullPoem(poem_id)
        if poem is None:
            raise PoemNotFoundException("Poem " + str(poem_id) + " Not found")
        return cls(poem[1],poem[2],poem[3],poem[4],new=False,poem_id=poem[0])

    @classmethod
    def getMaxID(cls):
        return getMaxID()

    @classmethod
    def getMinID(cls):
        return getMinID()

    def save(self):
        if self.new:
            self.poem_id = getMinID()-1
            insert(self)
            self.new = False
        else:
            update(self)
    
    def publish(self):
        if self.poem_id <= 0:
            self.poem_id = getMaxID()+1
        self.save()

    def saveAsDraft(self):
        self.save()
    
    def getData(self):
        return {
            'poem_id':self.poem_id,
            'poem_title':self.title,
            'poem_date':self.creation_date,
            'poem_content':self.poem,
            'poem_image_path':self.image_path,
        }
    
    def __init__(self,title,creation_date,poem,image_path,new=True,poem_id=0):
        self.new = new
        self.poem_id = poem_id
        self.title = title
        self.creation_date = creation_date
        self.poem = poem
        self.image_path = image_path


class User(object):
    @classmethod
    def login(cls,username,password):
        return login(username,password)

    @classmethod
    def logout(cls,username,token):
        return logout(username,token) is not None

    @classmethod
    def create(cls,username,password):
        create_user(username,password)

def loadpword():
    with open('db_pass.txt','r') as f:
        return ''.join(i.strip() for i in f).strip()

# DB Calls

def reset():
    reset_poems()
    reset_users()

def reset_poems():
    execute(_reset_poems)
    init_poems()

def _reset_poems(cur):
    cur.execute("""
    DROP TABLE poems
    """)

def reset_users():
    execute(_reset_users)
    init_users()

def _reset_users(cur):
    cur.execute("""
    DROP TABLE users 
    """)

def init():
    init_poems()
    init_users()

def init_poems():
    execute(_init_poems)

def _init_poems(cur):
    cur.execute("""
    CREATE TABLE poems (
        poem_id int CONSTRAINT firstkey PRIMARY KEY,
        title varchar(128),
        creation_date varchar(32),
        poem text,
        image_path varchar(128),
    )
    """)

def init_users():
    execute(_init_users)

def _init_users(cur):
    cur.execute("""
    CREATE TABLE users (
        username varchar(128),
        password text,
        token text
    )
    """)

def create_user(username,password):
    p = encrypt(password)
    execute(_create_user,username,p)

def _create_user(cur,username,password):
    cur.execute("""
    INSERT INTO users VALUES (%s,%s)
    """,(username,password))

def login(user,pword):
    return execute(_login,user,pword)

def _login(cur,user,pword):
    cur.execute("""
    SELECT password FROM users WHERE username=%s
    """,(user,))
    try:
        p = cur.fetchone()[0]
    except:
        return None,"user"
    if decrypt(p) == pword:
        token = session_token()
        cur.execute("""
        UPDATE users SET token=%s WHERE username=%s
        """,(token,user))
        return token,""
    else:
        return None,"password"

def logout(user,token):
    return execute(_logout,user,token)

def _logout(cur,user,token):
    cur.execute("""
    SELECT token FROM users WHERE username=%s
    """,(user,))
    if cur.fetchone()[0] == token:
        cur.execute("""
        UPDATE users SET token='' WHERE user=%s
        """,(user,))
        return 1
    else:
        return None

def insert(poem):
    return execute(_insert,poem) 

def _insert(cur,poem):
    cur.execute("""
    INSERT INTO poems VALUES (%s,%s,%s,%s,%s)
    """,(poem.poem_id,poem.title,poem.creation_date,poem.poem,poem.image_path))

def update(poem):
    execute(_update,poem)

def _update(cur,poem):
    cur.execute("""
    UPDATE poems 
    SET (
    title=%s,
    creation_date=%s,
    poem=%s,
    image_path=%s,
    poem_id=%s
    WHERE poem_id=%s
    """,(poem.title,poem.creation_date,poem.poem,poem.image_path,poem.poem_id,poem.poem_id))


def pullPoem(poem_id):
    try:
        return execute(_pullPoem,poem_id)
    except IndexError:
        return None

def _pullPoem(cur,poem_id):
    cur.execute("""
    SELECT * FROM poems
    WHERE poem_id=%s
    """,(poem_id,))
    return cur.fetchone()

def pullAll():
    return execute(_pullAll)

def _pullAll(cur):
    cur.execute("""
    SELECT * FROM poems
    """)
    return cur.fetchall()


def getMaxID():
    try:
        _id = execute(_getMaxID)[0]
        if _id is None:
            return 0
        return _id
    except IndexError:
        return 0

def _getMaxID(cur):
    cur.execute("""
    SELECT MAX(poem_id) FROM poems
    """)
    return cur.fetchone()

def getMinID():
    try:
        _id = execute(_getMinID)[0]
        if _id is None or _id > 0:
            return 0
        return _id
    except IndexError:
        return 0

def _getMinID(cur):
    cur.execute("""
    SELECT MIN(poem_id) FROM poems
    """)
    return cur.fetchone()

def pullAllTitlesAndDates():
    return execute(_pullAllTitlesAndDates)

def _pullAllTitlesAndDates(cur):
    cur.execute("""
    SELECT (title,creation_date) FROM poems
    """)
    return cur.fetchall()
    

def execute(f,*args):
    conn = psycopg2.connect(host=DB_ADDR,
                            database='daily_salute_db',
                            user='daily_saluter',
                            password=loadpword())
    val = None
    cur = conn.cursor()
    val = f(cur,*args)
    conn.commit()
    conn.close()
    return val




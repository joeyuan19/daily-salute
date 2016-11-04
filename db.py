import psycopg2

from security import encrypt, decrypt, session_token
from helper import avoid_incomplete_tag

DB_ADDR = '127.0.0.1'

# DB Models

class PoemNotFoundException(Exception):
    pass

class Poem(object):
    @classmethod
    def load(cls,poem_id):
        poem = pull_poem(poem_id)
        if poem is None:
            raise PoemNotFoundException("Poem " + str(poem_id) + " Not found")
        return cls(poem[1],poem[2],poem[3],new=False,_type="poem",poem_id=poem[0])

    @classmethod
    def load_draft(cls,poem_id):
        poem = pull_draft(poem_id)
        if poem is None:
            raise PoemNotFoundException("Draft " + str(poem_id) + " Not found")
        return cls(poem[1],poem[2],poem[3],new=False,_type="draft",poem_id=poem[0])

    @classmethod
    def getMaxID(cls):
        return getMaxID()

    @classmethod
    def getMaxDraftID(cls):
        return getMaxDraftID()

    @classmethod
    def getAllPoems(cls):
        return pullAllPoems()

    @classmethod
    def getAllDrafts(cls):
        return pullAllDrafts()

    @classmethod
    def getPoemPage(cls,page_no,page_size):
        return pullPoemPage(page_no,page_size)

    @classmethod
    def getDraftPage(cls,page_no,page_size):
        return pullDraftPage(page_no,page_size)

    @classmethod
    def movePoem(cls,original_id,new_id):
        movePoem(original_id,new_id)

    @classmethod
    def new(cls):
        return cls('','','','draft',new=True)

    @classmethod
    def deletePoem(cls,poem_id):
        cls.load(poem_id).delete(with_shift=True) 

    @classmethod
    def deleteDraft(cls,poem_id):
        cls.load_draft(poem_id).delete(with_shift=True) 

    def save(self,_type=None,without_assignment=False):
        if _type is not None and self._type != _type:
            self.delete()
            self.new = True
            self._type = _type
        if self.new:
            insert(self,without_assignment)
            self.new = False
        else:
            update(self)
    
    def delete(self,with_shift=False):
        delete(self,with_shift=False)
    
    def getData(self):
        return {
            'poem_id':self.poem_id,
            'poem_title':self.title,
            'poem_date':self.creation_date,
            'poem_content':self.poem,
            'poem_type':self._type,
            'poem_preview':self.get_preview(),
        }
    
    def __init__(self,title,creation_date,poem,_type,new=True,poem_id=0):
        self.new = new
        self.poem_id = poem_id
        self.title = title
        self.creation_date = creation_date
        self.poem = poem
        self._type = _type

    def get_preview(self):
        return avoid_incomplete_tag(self.poem)[:30]+'...'


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

class Content(object):
    @classmethod
    def getAbout(cls):
        return get_about()

    @classmethod
    def saveAbout(cls,about):
        save_about(about)

def loadpword():
    with open('db_pass.txt','r') as f:
        return ''.join(i.strip() for i in f).strip()

# DB Calls

def reset():
    reset_poems()
    reset_drafts()
    reset_users()
    reset_content()

def reset_poems():
    execute(_reset_poems)
    init_poems()

def _reset_poems(cur):
    cur.execute("""
    DR#OP TABLE poems
    """)

def reset_drafts():
    execute(_reset_drafts)
    init_drafts()

def _reset_drafts(cur):
    cur.execute("""
    DR#OP TABLE drafts
    """)
def reset_content():
    execute(_reset_content)
    init_content()

def _reset_content(cur):
    cur.execute("""
    DR#OP TABLE content 
    """)

def reset_users():
    execute(_reset_users)
    init_users()

def _reset_users(cur):
    cur.execute("""
    DR#OP TABLE users
    """)

def init():
    init_poems()
    init_drafts()
    init_users()

def init_poems():
    execute(_init_poems)

def _init_poems(cur):
    cur.execute("""
    CREATE TABLE poems (
        poem_id int PRIMARY KEY,
        title varchar(128),
        creation_date varchar(32),
        poem text
    )
    """)


def init_drafts():
    execute(_init_drafts)

def _init_drafts(cur):
    cur.execute("""
    CREATE TABLE drafts (
        poem_id int PRIMARY KEY,
        title varchar(128),
        creation_date varchar(32),
        poem text
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

def init_content():
    execute(_init_content)

def _init_content(cur):
    cur.execute("""
    CREATE TABLE content (
        about text
    )
    """)

def get_about():
    return execute(_get_about)

def _get_about(cur):
    cur.execute("""
    SELECT about FROM content
    """)
    return cur.fetchone()[0]

def save_about(about):
    execute(_save_about,about)

def _save_about(cur,about):
    cur.execute("""
    UPDATE content SET about=%s
    """,(about,))

def create_user(username,password):
    p = encrypt(password)
    execute(_create_user,username,p)

def _create_user(cur,username,password):
    cur.execute("""
    INSERT INTO users VALUES (%s,%s,'')
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

def delete(poem,with_shift=False):
    if poem._type == "poem":
        execute(_delete,poem) 
    elif poem._type == "draft":
        execute(_delete_draft,poem) 
    else:
        return
    if with_shift:
        shift(poem._type,poem.poem_id,-1)

def _delete(cur,poem):
    cur.execute("""
    DELETE FROM poems WHERE poem_id=%s
    """,(poem.poem_id,))

def _delete_draft(cur,poem):
    cur.execute("""
    DELETE FROM drafts WHERE poem_id=%s
    """,(poem.poem_id,))

def insert(poem,without_assignment=False):
    if poem._type == "poem":
        execute(_insert,poem,without_assignment) 
    elif poem._type == "draft":
        execute(_insert_draft,poem,without_assignment) 

def _insert(cur,poem,without_assignment=False):
    if not without_assignment:
        poem.poem_id = getMaxID()+1
    cur.execute("""
    INSERT INTO poems VALUES (%s,%s,%s,%s)
    """,(poem.poem_id,poem.title,poem.creation_date,poem.poem))

def _insert_draft(cur,poem,without_assignment=False):
    if not without_assignment:
        poem.poem_id = getMaxDraftID()+1
    cur.execute("""
    INSERT INTO drafts VALUES (%s,%s,%s,%s)
    """,(poem.poem_id,poem.title,poem.creation_date,poem.poem))

def update(poem):
    if poem._type == "poem":
        execute(_update,poem)
    elif poem._type == "draft":
        execute(_update_draft,poem)

def _update(cur,poem):
    cur.execute("""
    UPDATE poems 
    SET (title,creation_date,poem,poem_id) = (%s,%s,%s,%s)
    WHERE poem_id=%s
    """,(poem.title,
        poem.creation_date,
        poem.poem,
        poem.poem_id,
        poem.poem_id))

def _update_draft(cur,poem):
    cur.execute("""
    UPDATE drafts
    SET (title,creation_date,poem,poem_id) = (%s,%s,%s,%s)
    WHERE poem_id=%s
    """,(poem.title,
        poem.creation_date,
        poem.poem,
        poem.poem_id,
        poem.poem_id))

def pull_poem(poem_id):
    try:
        return execute(_pull_poem,poem_id)
    except IndexError:
        return None

def _pull_poem(cur,poem_id):
    cur.execute("""
    SELECT * FROM poems
    WHERE poem_id=%s
    """,(poem_id,))
    return cur.fetchone()

def pull_draft(draft_id):
    try:
        return execute(_pull_draft,draft_id)
    except IndexError:
        return None

def _pull_draft(cur,draft_id):
    cur.execute("""
    SELECT * FROM drafts
    WHERE poem_id=%s
    """,(draft_id,))
    return cur.fetchone()

def pullPoemPage(page_no,page_size):
    return execute(_pullPoemPage,page_no,page_size)

def _pullPoemPage(cur,page_no,page_size):
    cur.execute("""
    SELECT * FROM poems
    ORDER BY poem_id DESC
    LIMIT %s OFFSET %s
    """,(page_size,page_size*page_no))
    return cur.fetchall()

def pullDraftPage(page_no,page_size):
    return execute(_pullDraftPage,page_no,page_size)

def _pullDraftPage(cur,page_no,page_size):
    cur.execute("""
    SELECT * FROM drafts
    ORDER BY poem_id DESC
    LIMIT %s OFFSET %s
    """,(page_size,page_size*page_no))
    return cur.fetchall()

def pullAllPoems():
    return execute(_pullAllPoems)

def _pullAllPoems(cur):
    cur.execute("""
    SELECT * FROM poems ORDER BY poem_id DESC
    """)
    return cur.fetchall()

def pullAllDrafts():
    return execute(_pullAllDrafts)

def _pullAllDrafts(cur):
    cur.execute("""
    SELECT * FROM drafts ORDER BY poem_id DESC
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

def getMaxDraftID():
    try:
        _id = execute(_getMaxDraftID)[0]
        if _id is None:
            return 0
        return _id
    except IndexError:
        return 0

def _getMaxDraftID(cur):
    cur.execute("""
    SELECT MAX(poem_id) FROM drafts
    """)
    return cur.fetchone()

def pullAllTitlesAndDates():
    return execute(_pullAllTitlesAndDates)

def _pullAllTitlesAndDates(cur):
    cur.execute("""
    SELECT (poem_id,title,creation_date,poem) FROM poems
    """)
    return cur.fetchall()

def pullAllDraftTitlesAndDates():
    return execute(_pullAllTitlesAndDates)

def _pullAllDraftTitlesAndDates(cur):
    cur.execute("""
    SELECT (poem_id,title,creation_date,poem) FROM drafts
    """)
    return cur.fetchall()

def swap(poem_id_1,poem_id_2):
    execute(_swap,poem_id_1,poem_id_2)

def _swap(cur,poem_id_1,poem_id_2):
    poem_1 = pull(poem_id_1)
    poem_2 = pull(poem_id_2)
    poem_1.poem_id = poem_id_2
    poem_2.poem_id = poem_id_1
    update(poem_1)
    update(poem_2)

def movePoem(original_id,new_id):
    if original_id == new_id:
        return
    poem = Poem.load(original_id)
    poem.delete()
    execute(_movePoem,original_id,new_id)
    poem.poem_id = new_id
    poem.new = True
    poem.save(without_assignment=True)

def _movePoem(cur,original_id,new_id):
    if original_id > new_id:
        cur.execute("""
        UPDATE poems
        SET poem_id = poem_id-1000000000
        WHERE poem_id <= %s AND poem_id >= %s
        """,(original_id,new_id))
        cur.execute("""
        UPDATE poems
        SET poem_id = poem_id+1000000000+1
        WHERE poem_id < 0
        """)
    elif new_id > original_id:
        cur.execute("""
        UPDATE poems
        SET poem_id = poem_id-1000000000
        WHERE poem_id >= %s AND poem_id <= %s
        """,(original_id,new_id))
        cur.execute("""
        UPDATE poems
        SET poem_id = poem_id+1000000000-1
        WHERE poem_id < 0
        """)

def shift(_type,ident,amount):
    if _type == "poem":
        execute(_shift_poems,ident,amount)
    if _type == "draft":
        execute(_shift_drafts,ident,amount)

def _shift(cur,ident,amount):
    cur.execute("""
    UPDATE poems
    SET poem_id = poem_id-1000000000
    WHERE poem_id >= %s
    """,(ident,))
    cur.execute("""
    UPDATE poems
    SET poem_id = poem_id+(1000000000+%s)
    WHERE poem_id < 0
    """,(amount,))

def execute(f,*args):
    conn = psycopg2.connect(
        host=DB_ADDR,
        database='daily_salute_db',
        user='daily_saluter',
        password=loadpword())
    val = None
    cur = conn.cursor()
    val = f(cur,*args)
    conn.commit()
    conn.close()
    return val


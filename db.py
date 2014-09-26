import psycopg2

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
    
    def save(self):
        if self.new:
            insert(self)
            self.new = False
        else:
            update(self)
    
    def getData(self):
        return {
            'poem_id':self.poem_id,
            'poem_title':self.title,
            'poem_date':self.creation_date,
            'poem_content':self.poem,
            'poem_image_path':self.image_path,
        }
    
    def __init__(self,title,creation_date,poem,image_path,new=True,poem_id=-1):
        self.new = new
        self.poem_id = poem_id
        self.title = title
        self.creation_date = creation_date
        self.poem = poem
        self.image_path = image_path
    

# DB Calls

def loadpword():
    with open('db_pass.txt','r') as f:
        return ''.join(i.strip() for i in f).strip()

def reset():
    execute(_reset)
    init()

def _reset(cur):
    cur.execute("""
    DROP TABLE poems
    """)

def init():
    execute(_init)

def _init(cur):
    cur.execute("""
    CREATE TABLE poems (
        poem_id int CONSTRAINT firstkey PRIMARY KEY,
        title varchar(128),
        creation_date varchar(32),
        poem text,
        image_path varchar(128)
    )
    """)

def insert(poem):
    return execute(_insert,poem) 

def _insert(cur,poem):
    cur.execute("""
    INSERT INTO poems VALUES (%s,%s,%s,%s,%s)
    """,(getLatestID()+1,poem.title,poem.creation_date,poem.poem,poem.image_path))

def update(poem):
    execute(_update,poem)

def _update(cur,poem):
    cur.execute("""
    UPDATE poems 
    SET (
    title='%s',
    creation_date='%s',
    poem='%s',
    image_path='%s'
    WHERE poem_id=%s
    """,(poem.title,poem.creation_date,poem.poem,poem.image_path,poem.poem_id))
    
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


def getLatestID():
    try:
        _id = execute(_getLatestID)[0]
        if _id is None:
            return 0
        return _id
    except IndexError:
        return 0

def _getLatestID(cur):
    cur.execute("""
    SELECT MAX(poem_id) FROM poems
    """)
    return cur.fetchone()


def pullAllTitlesAndDates():
    pass

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




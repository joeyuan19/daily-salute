import psycopg2

DB_ADDR = 'web425.webfaction.com:5432'


def loadpword():
    with open('db_pass.txt','r') as f:
        return ''.join(i for i in f)

def init():
    execute(_init)

def _init(cur):
    cur.execute("""
    CREATE TABLE poems (
        poem_id int CONSTRAINT firstkey PRIMARY KEY,
        title varchar(128),
        creation timestamp DEFAULT now(),
        post_content text
    )
    """)

def insert(cur,poem):
    pass    

def update(cur,poem):
    pass

def pull():
    return execute(_pull)

def _pull(cur):
    cur.execute("""
    SELECT * FROM poems
    """)
    return cur.fetchall()
    
def execute(f,*args):
    conn = psycopg2.connect(host=DB_ADDR,
                            database='daily_salute_db',
                            user='daily_saluter',
                            passwd=loadpword())
    val = None
    cur = conn.cursor()
    val = f(cur,*args)
    conn.commit()
    conn.close()
    return val


init()

import sys
sys.exit()

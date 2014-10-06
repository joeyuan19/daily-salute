from db import execute


def init():
    execute(_init)

def _init(cur):
    cur.execute("""
    INSERT INTO content VALUES ('')
    """)

init()

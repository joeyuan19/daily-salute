from db import execute

def pull_password():
    execute(_pull_password)

def _pull_password(cur):
    cur.execute("""
    SELECT * FROM poems
    """)
    res = cur.fetchall()
    print res
    return res



print pull_password()



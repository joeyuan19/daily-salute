import re

def avoid_incomplete_tag(s):
    return re.sub(r'<.*?>',' ',s)

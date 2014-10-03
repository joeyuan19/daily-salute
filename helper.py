def avoid_incomplete_tag(s):
    if s.rfind('<') > s.rfind('>'):
        return s[:s.rfind('<')]
    return s

def distRuleCleanup(rule):
    cleanRule = rule
    if not rule.isalpha():
        cleanRule = '#'
    else:
        rule = unicodedata.normalize('NFKD', rule).encode('ascii', 'ignore').decode()
        if len(rule) > 0:
            cleanRule = rule
    return cleanRule
    
def stringCleanup(text):
    clean = {'\\': '-', '/': '-', '\"': '\''}
    for character, replacement in clean.items():
        text = text.replace(character, replacement)
    return text
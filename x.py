import re, sys
h = open(sys.argv[1], encoding='utf-8').read()
h = re.sub(r'(?is)<script.*?</script>', ' ', h)
h = re.sub(r'(?is)<style.*?</style>', ' ', h)
t = re.sub(r'(?s)<.*?>', '\n', h)
for line in t.split('\n'):
    s = line.strip()
    if s:
        print(s)

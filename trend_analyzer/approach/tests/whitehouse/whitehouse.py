f = open("whitehouse_raw.csv", "r")
data = []
count = 0
keys = []
vals = []
recs = []
for l in f.readlines():
    count += 1
    l = l.strip()
    record = [""] * 19
    i = 0
    quote = 0
    for c in l:
        if c == '"':
            quote = 1 - quote
        elif c == ',' and quote == 0:
            i += 1
        else:
            record[i] += c
    if i != 18:
        print i, l, record
    data.append(record)
    if count == 1: 
        header = list(record)
        continue

    rec = {}
    for i in range(0, 19):
        rec[header[i]] = record[i]

    recs.append(rec)

print count
print header

headers = header[0:3] + header[8:]

def clean(s):
    return s.replace(",", " ").replace("'", " ").replace('"', " ") 

types = ["ID", "ID", "ID", "TIME", "TIME", "CONT", "CAT/SENSITIVE", "CAT/SENSITIVE", "CAT", "CAT", "CAT/SENSITIVE", "CAT/SENSITIVE", "CAT", "TIME"]

f = open("whitehouse.csv", "w")
f.write(",".join([clean(h) for h in headers]))
f.write("\n")
f.write(",".join([clean(h) for h in types]))
f.write("\n")
for r in recs:
    vals = []
    for h in headers:
        vals.append(clean(r[h]))
    f.write(",".join(vals))
    f.write("\n")
f.close()

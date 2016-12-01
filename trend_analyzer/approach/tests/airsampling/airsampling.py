import random
f = open("airsampling_raw.csv", "r")
data = []
count = 0
keys = []
vals = []
recs = []
for l in f.readlines():
    count += 1
    l = l.strip()
    record = [""] * 14
    i = 0
    quote = 0
    for c in l:
        if c == '"':
            quote = 1 - quote
        elif c == ',' and quote == 0:
            i += 1
        else:
            record[i] += c
    if i != 13:
        print i, l, record
    data.append(record)
    if count == 1: 
        header = list(record)
        continue

    rec = {}
    for i in range(0, 14):
        rec[header[i]] = record[i]
    rec["LATITUDE"] = str(random.randrange(0, 100))
    recs.append(rec)

print count


def clean(s):
    return s.replace(",", " ").replace("'", " ").replace('"', " ") 

types = ["TIME", "CAT", "ID", "ID", "ID", "ID", "CAT", "CONT", "CAT", "CONT", "CAT", "CAT/SENSITIVE", "CONT", "CONT"]

f = open("airsampling.csv", "w")
f.write(",".join([clean(h) for h in header]))
f.write("\n")
f.write(",".join([clean(h) for h in types]))
f.write("\n")
for r in recs:
    vals = []
    for h in header:
        vals.append(clean(r[h]))
    f.write(",".join(vals))
    f.write("\n")
f.close()

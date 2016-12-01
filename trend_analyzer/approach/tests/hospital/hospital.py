f = open("hospital_raw.csv", "r")
data = []
count = 0
keys = []
vals = []
recs = []
for l in f.readlines():
    count += 1
    l = l.strip()
    record = [""] * 42
    i = 0
    quote = 0
    for c in l:
        if c == '"':
            quote = 1 - quote
        elif c == ',' and quote == 0:
            i += 1
        else:
            record[i] += c
    if i != 41:
        print i, l, record
    data.append(record)
    if count == 1: 
        header = list(record)
        continue

    rec = {}
    if len(record[3]) > 0 or len(record[4]) > 0:
        print record
    for i in [0, 1, 2] + range(5, 42):
        rec[header[i]] = record[i]

    parent = rec["Hospital Name"]
    key = "Type"
    if "HOSPITAL" in parent: value = "Hospital"
    if "HOSP" in parent or "HSPTL" in parent: value = "Hospital"
    elif "MEDICAL CENTER" in parent: value = "Medical Center"
    elif "MED CTR" in parent or "MED CENTER" in parent: value = "Medical Center"
    elif "MEDICAL CTR" in parent: value = "Medical Center"
    elif "HEALTH CTR" in parent: value = "Health Center"
    elif "HEALTH CENTER" in parent: value = "Health Center"
    elif "HEALTH SYSTEM" in parent: value = "Health System"
    elif "HEALTH" in parent: value = "Health"
    else: value = "Others"
    rec[key] = value

    parent = rec["Phone Number"]
    key = "Area Code"
    if len(parent) != 10:
        print parent
    rec[key] = parent[0:3]

    recs.append(rec)


print count

field = "Hospital Name"
vals = []
for r in recs:
    if r["Type"] == "Others":
        vals.append(r[field])
#print set(vals), len(vals)

field = "State"
vals = []
for r in recs:
    vals.append(r[field])
#print set(vals), len(set(vals))


def clean(s):
    return s.replace(",", " ").replace("'", " ").replace('"', " ") 

headers = header[0:2] + ["Type"] + header[2:3] + header[5:10] + ["Area Code"] + header[10:]
#print headers

types = ["ID"] * 2 + ["CAT"] + ["ID"] * 7 + ["CONT/SENSITIVE"] * (42 - 13) + ["CAT/SENSITIVE"] + ["CONT"] + ["CAT/SENSITIVE"]
print len(types), len(headers)

f = open("hospital.csv", "w")
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

import string
stream = open("airsampling.csv", "r")
type_line = stream.readline()
title_line = stream.readline()
print type_line,
print title_line,
line = stream.readline()
while line != "":
  line = line.rstrip("\n")
  args = line.split(",")
  for i in [0]:
    args[i] = args[i] + " -0500"
  next_line = string.join(args, ",")
  print next_line
  line = stream.readline()

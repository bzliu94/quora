import string
stream = open("hospital.csv", "r")
title_line = stream.readline()
type_line = stream.readline()
# print type_line,
# print title_line,
next_type_line = "ID,ID,CAT,ID,ID,ID,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,ID,ID,ID,ID,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CONT/SENSITIVE,CAT/SENSITIVE,CONT,CAT/SENSITIVE\n"
print next_type_line,
next_title_line = "Provider number,Hospital name,Type,Address 1,City,State,Hospital rate <= 6 (from 0-10) (%),Hospital rate 7/8 (from 0-10) (%),Hospital rate 9/10 (from 0-10) (%),No to hospital rec. (%),Prob. yes to hospital rec. (%),Def. yes to hospital rec. (%),ZIP Code,County Name,Phone Number,Area Code,Nurse S/N communicate well (%),Nurse U communicate well (%),Nurse A communicate well (%),Doctor S/N communicate well (%),Doctor U communicate well (%),Doctor A communicate well (%),S/N help received ASAP (%),U help received ASAP (%),A help received ASAP (%),Pain S/N well-controlled (%),Pain U well-controlled (%),Pain A well-controlled (%),S/N medicines explained (%),U medicines explained (%),A medicines explained (%),Rm./bathrm. S/N clean (%),Rm./bathrm. U clean (%),Rm./bathrm. A clean (%),Rm. S/N quiet at night (%),Rm. U quiet at night (%),Rm. A quiet at night (%),Given info occupy recovery (%),Not given info occupy recovery (%),Num. completed surveys,Survey response rate (%),Hospital footnote\n"
print next_title_line,

line = stream.readline()
while line != "":
  line = line.rstrip("\n")
  args = line.split(",")
  for i in range(10, 38 + 1) + [40]:
    args[i] = args[i].replace("%", "")
    args[i] = "" if (args[i] == "N/A") else args[i]
  args = args[0 : 6] + args[33 : 39] + args[6 : 33] + args[39 : 42]
  next_line = string.join(args, ",")
  print (next_line + "\n"),
  line = stream.readline()

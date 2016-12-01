pairs = [("09/27/20091 08:28 AM +0000", "09/27/2009 08:28 AM +0000"), \
("02/02/20091 08:00 AM +0000", "02/02/2009 08:00 AM +0000"), \
("04/29/20091 07:58 AM +0000", "04/29/2009 07:58 AM +0000"), \
("02/02/20091 08:00 AM +0000", "02/02/2009 08:00 AM +0000"), \
("04/29/20092 07:00 PM +0000", "04/29/2009 07:00 PM +0000"), \
("09/19/20092 07:39 AM +0000", "09/19/2009 07:39 AM +0000"), \
("09/28/20093 07:30 AM +0000", "09/28/2009 07:30 AM +0000"), \
("07/17/20094 07:30 AM +0000", "07/17/2009 07:30 AM +0000"), \
("09/16/20094 07:00 PM +0000", "09/16/2009 07:00 PM +0000"), \
("05/11/20094 07:00 PM +0000", "05/11/2009 07:00 PM +0000"), \
("09/24/20095 10:39 PM +0000", "09/24/2009 10:39 PM +0000"), \
("06/25/20095 07:45 AM +0000", "06/25/2009 07:45 AM +0000"), \
("09/24/20096 07:00 PM +0000", "09/24/2009 07:00 PM +0000"), \
("09/26/20096 07:55 AM +0000", "09/26/2009 07:55 AM +0000"), \
("07/04/20097 07:30 AM +0000", "07/04/2009 07:30 AM +0000"), \
("04/14/20098 07:45 AM +0000", "04/14/2009 07:45 AM +0000"), \
("09/30/20098 07:30 AM +0000", "09/30/2009 07:30 AM +0000"), \
("09/30/20099 07:00 PM +0000", "09/30/2009 07:00 PM +0000"), \
("03/06/20099 08:30 AM +0000", "03/06/2009 08:30 AM +0000")]

in_to_out_dict = {}

for pair in pairs:
  k, v = pair
  in_to_out_dict[k] = v

import string
stream = open("whitehouse.csv", "r")
title_line = stream.readline()
type_line = stream.readline()
print type_line,
# print title_line,
next_title_line = "Last name,First name,Middle initial,Time of arrival,Appt. start date,Total people,Visitee last name,Visitee first name,Meeting location,Meeting room,Caller last name,Caller first name,Description,Release date\n"
print next_title_line,
line = stream.readline()
while line != "":
  line = line.rstrip("\n")
  args = line.split(",")
  for i in [4]:
    if args[i] in in_to_out_dict:
      args[i] = in_to_out_dict[args[i]]
  next_line = string.join(args, ",")
  print next_line
  line = stream.readline()




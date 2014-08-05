import re

data = open("featureWeights").readlines()
data = [x.replace("\n", "") for x in data]

abstracted = []
for d in data:
  s = d.split(",")
  fstring = s[0][1:-1]
  if (re.match("H=(\w*) A=(\w*) HA=(\w*)", fstring)):
    abstracted.append("A," + s[1] + "\n")
  elif (re.match("H=(\w*) HA=(\w*)", fstring)):
    abstracted.append("B," + s[1] + "\n")
  elif (re.match("A=(\w*) HA=(\w*)", fstring)):
    abstracted.append("C," + s[1] + "\n")
  elif (re.match("H=(\w*) A=(\w*)", fstring)):
    abstracted.append("D," + s[1] + "\n")
  elif (re.match("H=(\w*)", fstring)):
    abstracted.append("E," + s[1] + "\n")
  elif (re.match("A=(\w*)", fstring)):
    abstracted.append("F," + s[1] + "\n")
  else:
    abstracted.append("G," + s[1] + "\n")

output = open("processed", "w")
output.write("type,weight\n")
for a in abstracted:
  output.write(a)
output.close()

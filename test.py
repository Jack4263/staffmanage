from datetime import date

d = str(date.today())
# print(d[2:4],end=" ")
# print(d[5:7],end=" ")
# print(d[8: ])

print(d)
print(''.join(d.split('-'))[2:])
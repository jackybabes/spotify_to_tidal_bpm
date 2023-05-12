s=lambda a,t:[c[1] for c in [([[i,j],[x,y]]) for x,i in enumerate(a) for y,j in enumerate(a) if i != j] if sum(c[0]) == t]

print(s([0,1,2], 2))
print(s([0,1,3,5,7], 12))
print(s([0,1,3,5,7,23,23,1,4,5,8,3,2,86,3,4], 90))
print(s([0,1], 2))
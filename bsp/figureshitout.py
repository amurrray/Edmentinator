newAmount = 3

print(newAmount)

theEA = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

print(theEA)

theAA = []

print(theAA)

i = 0
for x in theEA:
    theAA.append(theEA[i])
    print(theAA)
    print(len(theAA))
    i += 1
    if len(theAA) == newAmount:
        print("theAA done")
        break
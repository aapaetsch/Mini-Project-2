import sqlite3



def find_closure(attr,myFD):
	closure = attr
	nowFD = myFD[:]
	for n1 in myFD:
		n1end = True
		for i in nowFD:
			#print("i:",i)
			if (set(i[0]).issubset(closure)):
				for l in i[1]:
					if (l not in closure):
						closure.append(l)
				n1end = False
				nowFD.remove(i)
				break
		if(n1end):
			break
	closure.sort()
	return closure

def find_3NF(myFD):
	#First, make RHS of each FD into a single attribute:
	FD1 = []
	for i in myFD:
		for k in i[1]:
			FD1.append([i[0],[k]])
	print(FD1)
	#Second, eliminate redundant attributes from LHS.
	for i in FD1:
		if len(i[0])>1:
			for k in i[0]:
				Attr1 = i[0][:]
				Attr1.remove(k)
				if set(i[1]).issubset(find_closure(Attr1,FD1)):
					i[0].remove(k)
	print("NF2:")
	print(FD1)
	#Third, we delete redundant FDs.


def main():
	# connecting to a database, creating the cursor
	conn = sqlite3.connect('MiniProject2-InputExample.db')
	c = conn.cursor()
	#c.execute('PRAGMA foreign_keys=ON;')
	c.execute('''SELECT * FROM Input_FDS_R1;''')
	conn.commit()
	FD = c.fetchall()
	print(FD)
	myFD = []
	for i in range(len(FD)):
		myFD.append([])
		for j in range(len(FD[i])):
			myFD[i].append(FD[i][j].split(','))
	print(myFD)
	print(find_closure([u'A'],myFD))
	print(find_closure([u'B'],myFD))
	print(find_closure([u'C'],myFD))

	find_3NF(myFD)

	c.execute('''SELECT * FROM Input_R1;''')
	conn.commit()
	R = c.fetchall()
	print(R)



main()

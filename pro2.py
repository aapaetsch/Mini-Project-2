import sqlite3


#attr= ["A"], myFD = [[["A","B"],["C"]],[["A","C"],["D"]]]
def find_closure(attr,myFD):
	closure = attr[:]
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

def delete_redundant(FD, compare):
	all_closure = []
	for i in compare:
		closure = find_closure(i[1],FD)
		all_closure.append(closure[:])

	for i in compare:
		closure = find_closure(i[1],FD)
		all_closure2 = all_closure[:]
		all_closure2.remove(closure)
		redundant = False
		for k in all_closure2:
			if (set(closure).issubset(k)):
				redundant = True
				break
		if redundant:
			FD.remove(i)

def find_min_cover(myFD):
	#First, make RHS of each FD into a single attribute:
	FD1 = []
	for i in myFD:
		for k in i[1]:
			FD1.append([i[0],[k]])
	for i in FD1:
		clean_print(i)
	#Second, eliminate redundant attributes from LHS.
	for i in FD1:
		if len(i[0])>1:
			for k in i[0]:
				Attr1 = i[0][:]
				Attr1.remove(k)
				if set(i[1]).issubset(find_closure(Attr1,FD1)):
					i[0].remove(k)
	print "\n FD2:"
	FD1.sort()
	for i in FD1:
		clean_print(i)
	#Third, we delete redundant FDs.
	compare = [FD1[0][:]]
	need_c = False
	FD3 = FD1[:]
	for i in range(len(FD1)-1):
		if (FD1[i][0]==FD1[i+1][0]):
			compare.append(FD1[i+1])
			need_c = True
		else:
			if (need_c):
				delete_redundant(FD3,compare)
			compare = [FD1[i+1]]
			need_c = False
	if (need_c):
		delete_redundant(FD3,compare)
	return FD3

def find_3NF(myFD,R):

	FD3 = find_min_cover(myFD[:])
	print "\n FD3:"
	for i in FD3:
		clean_print(i)
	print "\n"
	print FD3
	print "\n"
	find_BCNF(FD3[:],R)
	FD4 = []
	temp_Rs = []
	for i in FD3:
		if i[0] in temp_Rs:
			for k in i[1]:
				FD4[temp_Rs.index(i[0])][1].append(k)
		else:
			FD4.append(i)
			temp_Rs.append(i[0])
	print "\n FD4:"
	for i in FD4:
		clean_print(i)

	return find_BCNF(FD4,R)


def find_BCNF(myFD,R):
	current_R = R[:]
	next_R = []
	R_F = []
	violate = True
	#print("test BCNF:")
	while violate:
		if(len(myFD)==0):
			break
		for i in myFD:
			violate = False
			if find_closure(i[0],myFD)!=current_R:
				violate = True
				next_R = current_R[:]
				for k in i[1]:
					#print(i,k,next_R)
					next_R.remove(k)
				for k in myFD:

					if (k!=i)and((not set(k[0]).issubset(next_R)) or (not set(k[1]).issubset(next_R))):

						violate = False
				if violate:

					Rn = []
					for k in i[1]:
						Rn.append(k)
					for k in i[0]:
						Rn.append(k)
					R_F.append([Rn,i])
					current_R = next_R[:]
					myFD.remove(i)
					break
	R_F.append([current_R,myFD])
	print(R_F)
	return R_F


def table_create(c, conn, attributes, columns, is_fd):
	if is_fd == False:
		name = 'Output_R1_'
	else:
		name = 'Output_FDs_R1'

	for i in columns:
		name += i[0]
	c.executescript("DROP TABLE IF EXISTS "+ name +''';

	CREATE TABLE '''+name+"(\n	"+ columns[0][0]+ columns[0][1]+");")

	for i in range(len(columns)):
		#c.execute("ALTER TABLE :name ADD COLUMN :colname", {'name':namevar,'colname':columnvar})
		c.execute("ALTER TABLE :name ADD COLUMN :col :typ;",{'name':name,'col':columns[i][0], 'typ':columns[i][1]})



def clean(item):
	isnot = ["[","]","'"," "]
	fixed = ''
	length = len(item)
	for i in range(length):
		if i != 0:
			if i != range(length):
				fixed+=","
		if item[i] not in isnot:
			fixed += item[i]
	return fixed

def clean_print(fd):
	lhs = clean(fd[0])
	rhs = clean(fd[1])
	print lhs+"|"+rhs


def f_equal(FD1,FD2):
	return set(find_min_cover(FD1))==set(find_min_cover(FD2))

def main():
	# connecting to a database, creating the cursor
	conn = sqlite3.connect('MiniProject2-InputExample.db')
	c = conn.cursor()
	#c.execute('PRAGMA foreign_keys=ON;')
	c.execute('''SELECT * FROM Input_FDS_R1;''')
	conn.commit()
	FD = c.fetchall()
	#print(FD)
	myFD = []
	for i in range(len(FD)):
		myFD.append([])
		for j in range(len(FD[i])):
			myFD[i].append(str(FD[i][j]).split(','))
	print(myFD)
	#	print(find_closure([u'A'],myFD))
#	print(find_closure([u'B'],myFD))
#print(find_closure([u'C'],myFD))



	c.execute('''pragma table_info(Input_R1);''')
	conn.commit()
	R_c = c.fetchall()
	R= []
	col = []
	for i in R_c:
		item = []
		R.append(str(i[1]))
		item.append(str(i[1]))
		item.append(str(i[2]))
		col.append(item)
	print(R)
	find_3NF(myFD[:],R[:])
	print("\n BCNF:")
	for i in myFD:
		clean_print(i)

	print(R)
	find_BCNF(myFD[:],R[:])
	print "\n HERE ARE THE COLUMNS"
	for i in col:
		clean_print(i)




main()

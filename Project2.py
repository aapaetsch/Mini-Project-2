import sqlite3
import copy
import sys

def find_closure(attr, myFD):
    closure = copy.deepcopy(attr)
    nowFD = copy.deepcopy(myFD)
    for n1 in myFD:
        n1end = True
        for i in nowFD:
            if (set(i[0]).issubset(closure)):
                for l in i[1]:
                    if l not in closure:
                        closure.append(l)
                n1end = False
                nowFD.remove(i)
                break
        if n1end:
            break
    try:
        closure.sort()
    except:
        pass
    return closure

def delete_redundant(FD, compare):
    all_closure = []
    for i in compare:
        closure = find_closure(i[1], FD)
        all_closure.append(closure[:])

    for i in compare:
        closure = find_closure(i[1], FD)
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
    #First, make RHS of each FD into a single attributes
    FD1 = []
    for i in myFD:
        for k in i[1]:
            FD1.append([i[0],[k]])
    #second eliminate redundant attributes from LHS
    for i in FD1:
        if len(i[0]) > 1:
            for k in i[0]:
                Attr1 = i[0][:]
                Attr1.remove(k)
                if set(i[1]).issubset(find_closure(Attr1, FD1)):
                    i[0].remove(k)
    FD1.sort()

    #third we delete redundant FDs
    compare = [FD1[0][:]]
    need_c = False
    FD3 = FD1[:]
    for i in range(len(FD1)-1):
        if (FD1[i][0] == FD1[i+1][0]):
            compare.append(FD1[i+1])
            need_c = True
        else:
            if need_c:
                delete_redundant(FD3, compare)
            compare = [FD1[i+1]]
            need_c = False
    if need_c:
        delete_redundant(FD3, compare)
    return FD3

def find_3NF(myFD, R):

    FD3 = find_min_cover(myFD[:])
    FD4 = []
    temp_Rs = []
    for i in FD3:
        if i[0] in temp_Rs:
            for k in i[1]:
                FD4[temp_Rs.index(i[0])][1].append(k)
        else:
            FD4.append(i)
            temp_Rs.append(i[0])

    return find_dp(FD4, R)

def find_dp(myFD, R):
    current_R = R[:]
    next_R = []
    R_F = []
    violate = True

    while violate:
        if len(myFD) == 0:
            break
        for i in myFD:
            violate = False
            if find_closure(i[0], myFD) != current_R:
                violate = True
                next_R = current_R[:]
                for k in i[1]:
                    next_R.remove(k)
                for k in myFD:
                    if (k != i) and ((not set(k[0]).issubset(next_R)) or (not set(k[1]).issubset(next_R))):
                        violate = False
                if violate:
                    Rn = []
                    for k in i[1]:
                        Rn.append(k)
                    for k in i[0]:
                        Rn.append(k)
                    R_F.append([Rn, i])
                    current_R = next_R[:]
                    myFD.remove(i)
                    break
    R_F.append([current_R, myFD])
    return R_F

def find_BCNF(myFD, R):
    current_R = R[:]
    next_R = []
    R_F = []
    violate = True
    removed = []

    while violate:
        if len(myFD) == 0:
            break
        for i in myFD:
            removed[:] = []
            violate = False
            if find_closure(i[0], myFD) != current_R:
                violate = True
                next_R = current_R[:]
                for k in i[1]:
                    removed.append(k)
                    next_R.remove(k)
            if violate:
                Rn = []
                for k in i[1]:
                    Rn.append(k)
                for k in i[0]:
                    Rn.append(k)
                R_F.append([Rn, i])
                current_R = next_R[:]
                myFD.remove(i)
                for k in myFD:
                    for j in removed:
                        if j in k[0]:
                            myFD.remove(k)
                            break
                        elif j in k[1]:
                            k[1].remove(j)
                break
    R_F.append([current_R, myFD])
    for i in range(len(R_F)):
        try:
            if len(R_F[i][1]) == 1:
                R_F[i][1] = R_F[i][1][0]
        except:
            continue

    return R_F

def table_create(c, conn, attributes, columns):
    #for the names of the outputs
    fds=[]
    #for the fd variables
    depend = []
    noFD = []
    for i in columns:
        try:
            if len(i[1]) == 0:
                noFD.append(columns.index(i))
        except:
            continue
    #for each item in the passed in schema
    for i in columns:
    	#if the lhs not in depend
    	if i[0] not in depend:
    		depend.append(i[0])
    	#flag for checking redundancy
    	in_fds = False
    	title = ''
    	for item in i[0]:
    		title += item
    	for item in i[1]:
    		title += item
    	#loop adds dependants with same i[0] to fds
    	for j in columns:
    		if i[0] == j[0] and i[1] != j[1]:
    			for item in j[1]:
    				title += item
    	for j in fds:
    		if sorted(j) == sorted(title):
    			in_fds = True
    			break
    	if in_fds == False:
    		fds.append(title)

    for i in range(len(fds)):
    	covered = []
        #HERE CAN BE CHANGED IF THE NF3 and BCNF is not needed
    	name_fd = 'Output_FDs_R1_'+fds[i]
    	name = 'Output_R1_'+fds[i]
        if i in noFD:
            for k in columns:
                if depend[i] == k[0]:
                    for item in k[0]:
                        if item not in covered:
                            covered.append(item)
        if i not in noFD:
    	    c.executescript("DROP TABLE IF EXISTS "+name_fd+''';
    	    CREATE TABLE ''' + name_fd + " (LHS TEXT, RHS TEXT);")
        c.execute("DROP TABLE IF EXISTS "+name+";")
    	primary_key = []
        if i not in noFD:
        	for k in columns:
        		if depend[i] == k[0]:
        			for item in k[0]:
        				if item not in covered:
        					primary_key.append(item)
        					covered.append(item)
        			for item in k[1]:
        				if item not in covered:
        					covered.append(item)
        			lhs = clean(k[0])
        			rhs = clean(k[1])
        			c.execute("INSERT INTO "+name_fd+" VALUES (:left, :right);", {'left':lhs, 'right':rhs})
        			conn.commit()

    	data = []
    	for x in range(len(covered)):
    		c.execute("SELECT {cl} FROM Input_R1;".format(cl=covered[x]))
    		obj = c.fetchall()
    		for item in attributes:
    			if covered[x] == item[0]:
    				for j in range(len(obj)):
    					if type(obj[j][0]) != unicode:
    						obj[j] = type(obj[j][0])(obj[j][0])
    					else:
    						obj[j] = str(obj[j][0])

    		data.append(obj)
    	data_columns = ''

    	for k in range(len(covered)):
    		data_columns += (covered[k]+' ')
    		for j in attributes:
    			if j[0] ==covered[k]:
    				data_columns += j[1]
    		if k != (len(covered)-1):
    			data_columns +=','

        data_columns += ' UNIQUE'
        pkey = ''
        if i not in noFD:
            pkey += ', PRIMARY KEY('
            for j in range(len(primary_key)):
            	pkey += primary_key[j]
            	if j != (len(primary_key)-1):
            		pkey += ','
                else:
                    pkey += ')'

        data_columns += pkey
        c.execute("CREATE TABLE "+name+" ("+data_columns+");")
        conn.commit()

        data_combined = []
        count = 0

        for j in range(len(data[0])):
    		poly_list = []
    		for d in data:
    			poly_list.append(d[count])
    		count+=1
    		data_combined.append(poly_list)
        for j in range(len(data_combined)):
        	varies = ''
        	for index in range(len(data_combined[j])):
        		varies += '?'
        		if index != (len(data_combined[j])-1):
        			varies += ','

        	try:
        		c.execute("INSERT INTO "+name+" VALUES ("+varies+");", data_combined[j])

        	except:
        		continue

def clean(item):
	isnot = ["[","'","]"," "]
	fixed = ''
	length = len(item)
	for i in range(length):
		if i != 0:
			if i != range(length):
				fixed+=","
		if item[i] not in isnot:
			fixed += str(item[i])

	return fixed

def clean_print(fd):
    lhs = clean(fd[0])
    rhs = clean(fd[1])
    if rhs != '':
        print lhs,"|",rhs

def f_equal(FD1, FD2):
    return set(find_min_cover(FD1)) == set(find_min_cover(FD2))

def is_cover(FD1, FD2):
    print FD1, FD2
    for i in range(len(FD1)):
        if not set(FD1[1]).issubset(find_closure(FD1[0], FD2)):
            return False
    return True

def is_equal(FD1, FD2):
    return is_cover(copy.deepcopy(FD1), copy.deepcopy(FD2)) and is_cover(copy.deepcopy(FD2), copy.deepcopy(FD1))

def R_F_to_FD(R_F):
    FD = []
    for i in R_F:
        if len(i) == 1:
            R_F.remove(i)
    for i in R_F:
        if len(i[1]) == 0:
            FD.append(i)
        else:
            FD.append(i[1])
    return FD
def user():
    while True:
        print '''0 - exit system
1 - compute attribute closure
2 - check if two FD's are equivilant
3 - synthesize 3nf schema
4 - decompose into BCNF'''
        entry = raw_input("Enter choice :")
        if entry == '0':
            sys.exit()
        if entry == '1' or entry == '2' or entry == '3' or entry == '4':
            return entry


def main():
    entry = raw_input("Enter the database name: ")
    if entry != '':
        conn = sqlite3.connect(entry)
    else:
        conn = sqlite3.connect('MiniProject2-InputExample.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Input_FDS_R1;")
    conn.commit()
    FD = c.fetchall()
    myFD = []
    for i in range(len(FD)):
        myFD.append([])
        for j in range(len(FD[i])):
            myFD[i].append(str(FD[i][j]).split(','))

    c.execute("PRAGMA table_info(Input_R1);")
    conn.commit()
    R_c = c.fetchall()
    R = []
    col = []
    for i in R_c:
        item = []
        R.append(str(i[1]))
        item.append(str(i[1]))
        item.append(str(i[2]))
        col.append(item)

    NF3 = R_F_to_FD(find_3NF(copy.deepcopy(myFD), R[:]))
    R_F = find_BCNF(copy.deepcopy(myFD), R[:])
    R_F = R_F_to_FD(R_F)
    for i in NF3:
        if len(i) == 0:
            NF3.remove(i)




    while True:
        enter = user()
        print ""

        if enter == '3':
            print "3NF schema"
            for i in NF3:
                clean_print(i)
            while True:
                ent = raw_input("Would you like to decompose this schema?(y/n) ")
                if ent == 'y':
                    table_create(c, conn, col, NF3)
                    conn.commit()
                    break
                elif ent == 'n':
                    break
                else:
                    print "invalid entry"
        elif enter == '4':
            print "BCNF decomposition"
            for i in R_F:
                clean_print(i)
            while True:
                ent = raw_input("would you like to decompose this schema?(y/n) ")
                if ent == 'y':
                    table_create(c, conn, col, R_F)
                    conn.commit()
                    break
                elif ent == 'n':
                    break
                else:
                    print "invalid input"
        elif enter == '1':
            attrib = raw_input("Enter a list of attributes seperated by comma: ")
            if len(attrib) == 0:
                print "No attributes entered, returning to user interface"

            else:

                attrib = attrib.split(",")
                for i in range(len(attrib)):
                    attrib[i] = attrib[i].upper()

                print "closure in list format is ",find_closure(attrib, myFD)

        elif enter == '2':
            fd1 = raw_input("Enter FD1, attributes are seperated by comma: ")
            fd2 = raw_input("Enter FD2, attributes are seperated by comma: ")
            if len(fd1) == 0 or len(fd2) == 0:
                print "No FD's entered, returning to user interface"
            else:
                fd1 = fd1.split(",")
                fd2 = fd2.split(",")
                for i in range(len(fd1)):
                    fd1[i] = fd1[i].upper()
                for i in range(len(fd2)):
                    fd2[i] = fd2[i].upper()
                for i in myFD:
                    if i[0] == fd1:
                        fd1 = i
                    if i[0] == fd2:
                        fd2 = i

                eq = is_equal(fd1, fd2)
                if eq == True:
                    print "FDs are equal"
                else:
                    print "FDs are not equal"


        print ""


main()

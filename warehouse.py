import csv
import sys
from ast import literal_eval as make_tuple
import time
import copy
import json
inf = 9999999
pathwidth = 1
shelfwidth = 1
width = pathwidth +shelfwidth
itemfile = 'warehouse-grid.csv'
itemdict = {}
orderdict = {}
weightdict = {}
startingPoint = (0,0)
endPoint = (0,0)
orderfile = "warehouse-orders-v02-tabbed.txt"
#orderfile = "5.csv"
outputFile = "output.txt"
weightfile = "item-dimensions-tabbed.txt"
userPickedItem = []
algs = "b"
keythreshold = 20000
effortflag = True
lrdiff = 'b'
def init():
    global startingPoint
    global endPoint
    global orderfile
    global outputFile
    global userPickedItem
    global algs
    global weightfile
    global effortflag
    global lrdiff
    startingPoint = make_tuple(raw_input("Hello User, where is your worker? input like this: (1,1) \n"))
    endPoint = make_tuple(raw_input("What is your worker's end location? input like this: (1,1) \n"))
    orderInput = raw_input("Do you want to specify filename to import an list of orders? (Y or N) \n")
    if orderInput == 'Y' or orderInput == 'y':
        orderfile = raw_input("Please list file of orders to be processed:\n")
    elif orderInput == 'N' or orderInput == 'n':
        orders = raw_input("Hello User, what items would you like to pick? split numbers with comma and do not use space\n")
        userPickedItem = map(lambda x: int(x), orders.split(','))
    else:
        print "invalid input"
        sys.exit()
    algs = raw_input("Which algorithm do you want to use? G (greedy algorithm) or B (branch and bound)\n")
    if algs!="g" and algs!="G" and algs !="b" and algs!="B":
        print "invalid input"
        sys.exit()
    outputFile = raw_input("Please list output file:\n")
    effortf = raw_input("Do you want to show effort for each trip? Y or N\n")
    if effortf == 'Y' or effortf =='y':
        effortflag = True
        weightfile = raw_input("Please list weight file:\n")
    elif effortf == 'N' or effortf =='n':
        effortflag = False
    else:
        print "invalid input"
        sys.exit()
    lr = raw_input("Calculate for both left and right side or just one side? L(left side) R(right side) B(both sides)\n")
    if lr == 'L' or lr == 'l':
        lrdiff = 'l'
    elif lr == 'B' or lr == 'b':
        lrdiff = 'b'
    elif lr == 'R' or lr=='r':
        lrdiff = 'r'
    else:
        print "invalid input"
        sys.exit()


# retrieve items and their positions/weights
def getItem():
    global itemdict
    global weightdict
    start = time.time()
    with open(itemfile,'r') as csvfile:
        reader = csv.reader(csvfile)
        for rows in reader:
            itemdict[int(rows[0])] = (int(float(rows[1])),int(rows[2])) # drop the decimal
    with open(weightfile,'r') as myweightfile:
        myweightfile.readline()
        for line in myweightfile.readlines():
            weightdata = line.split()
            weightdict[int(weightdata[0])] = float(weightdata[-1])
    end = time.time()
    print "time to put data into memory: " + str(end-start)
    for k in itemdict:
        v = itemdict[k]
        itemdict[k] = (width*v[0]+pathwidth,width*v[1]+pathwidth)

# retrieve items we need to gather
def getOrder():
    global orderdict
    global userPickedItem
    if (len(userPickedItem) == 0) and (orderfile != ''):
        with open(orderfile,'r') as csvfile:
            reader = csv.reader(csvfile)
            orderlist = 0
            for rows in reader:
                orderdict[orderlist] = map(lambda x: int(x), rows[0].split())
                orderlist +=1
    elif (len(userPickedItem) != 0) and (orderfile == ''):
        orderdict = {0:userPickedItem}
    else:
        print "value error"   # should not occur
        print orderdict
        print userPickedItem

# return the length to go to the next shelf
def getLength(start,end):
    if lrdiff == 'b':
        i = max(end[1],start[1])
        j = min(end[1],start[1])
        length = 0
        if (end[0] == endPoint[0] and end[1] == endPoint[1]):
            length = abs(start[0]-end[0]) + abs(start[1]-end[1])
        elif start[0] < end[0]:
            length = (end[0] - start[0]) + i-j
        elif start[0] > end[0]:
            length = (start[0] - (end[0] + shelfwidth)) + i-j
        else:
            length = i-j
        return length
    elif lrdiff == 'l':
        length = abs(start[0]-end[0]) + abs(start[1]-end[1])
        return length
    else:
        if (start[0] == startingPoint[0] and start[1] == startingPoint[1]):
            length = abs(start[0]-end[0]) +shelfwidth+ abs(start[1]-end[1])
        else:
            length = abs(start[0]-end[0]) + abs(start[1]-end[1])
        return length

def showEffort(route,cost):
    effort = 0
    start = startingPoint
    finished = 0
    missing = []
    for item in route:
        finished += getLength(start,itemdict[item])
        if item in weightdict:
            effort+=weightdict[item]*(cost-finished)
        else:
            missing.append(item)
            #print str(item) + " weight information not available"
        start = itemdict[item]
    return effort,missing

def tuplestr(location):
    mystr = '('
    mystr += str(location[0])
    mystr += ','
    mystr += str(location[1])
    mystr += ')'
    return mystr

def GUIdisplay(route,items):
    path = ''
    location = route[0]
    for i in range(len(route)-1):
        if lrdiff == 'b':
            path += tuplestr(location)+" "
            path += tuplestr((location[0],route[i+1][1]))+" "
            if location[0]<=route[i+1][0]:
                path += tuplestr((route[i+1][0],route[i+1][1]))+" "
                location = (route[i+1][0],route[i+1][1])
            else:
                path += tuplestr((route[i+1][0]+shelfwidth,route[i+1][1]))+" "
                location = (route[i+1][0]+shelfwidth,route[i+1][1])
        elif lrdiff =='l':
            path += tuplestr(location)+" "
            path += tuplestr((location[0],route[i+1][1]))+" "
            path += tuplestr((route[i+1][0],route[i+1][1]))+" "
            location = (route[i+1][0],route[i+1][1])
        else:
            path += tuplestr(location)+" "
            path += tuplestr((location[0],route[i+1][1]))+" "
            path += tuplestr((route[i+1][0]+shelfwidth,route[i+1][1]))+" "
            location = (route[i+1][0]+shelfwidth,route[i+1][1])
    path += tuplestr(location)+" "
    path += tuplestr((location[0],endPoint[1]))+" "
    path += tuplestr((endPoint[0],endPoint[1]))
    return path

def displayPath(route,items):
    path = ''
    location = route[0]
    for i in range(len(route)-1):
        if lrdiff == 'b':
            path += "From " + str(location)
            path += ", go to (%s,%s)" % (location[0],route[i+1][1])
            if location[0]<=route[i+1][0]:
                path += ", then go to (%s,%s)" % (route[i+1][0],route[i+1][1])
                location = (route[i+1][0],route[i+1][1])
            else:
                path += ", then go to (%s,%s)" % (route[i+1][0]+shelfwidth,route[i+1][1])
                location = (route[i+1][0]+shelfwidth,route[i+1][1])
            path += " pick up item %s" % items[i]
            path += " at "+ str(itemdict[items[i]]) + "\n"
        elif lrdiff =='l':
            path += "From " + str(location)
            path += ", go to (%s,%s)" % (location[0],route[i+1][1])
            path += ", then go to (%s,%s)" % (route[i+1][0],route[i+1][1])
            location = (route[i+1][0],route[i+1][1])
            path += " pick up item %s" % items[i]
            path += " at "+ str(itemdict[items[i]]) + "\n"
        else:
            path += "From " + str(location)
            path += ", go to (%s,%s)" % (location[0],route[i+1][1])
            path += ", then go to (%s,%s)" % (route[i+1][0]+shelfwidth,route[i+1][1])
            location = (route[i+1][0]+shelfwidth,route[i+1][1])
            path += " pick up item %s" % items[i]
            path += " at "+ str(itemdict[items[i]]) + "\n"
    path += "From " + str(location)
    path += ", go to (%s,%s)" % (location[0],endPoint[1])
    path += ", then go to (%s,%s)" % (endPoint[0],endPoint[1])
    return path

# grab item in a default order
def default(order):
    distance = 0
    source = startingPoint
    orderlist = orderdict[order]
    for item in orderlist:
        distance += getLength(source,itemdict[item])
        if source[0]<= itemdict[item][0]:
            source = itemdict[item]
        else:
            source = (itemdict[item][0]+shelfwidth,itemdict[item][1])
    distance += abs(source[0]-endPoint[0])+abs(source[1]-endPoint[1])
    return distance

# a single iteration in greedy algorithm
def greedyiteration(source,orderlist):
    distance = 0
    optimizedList = []
    while(len(orderlist)>0):
        distances = {}
        for item in orderlist:
            distances[getLength(source, itemdict[item])] = item
        distance += min(distances)
        nextitem = distances[min(distances)]
        orderlist.remove(nextitem)
        if source[0]<= itemdict[nextitem][0]:
            source = itemdict[nextitem]
        else:
            source = (itemdict[nextitem][0]+shelfwidth,itemdict[nextitem][1])
        optimizedList.append(nextitem)
    distance += abs(source[0]-endPoint[0])+abs(source[1]-endPoint[1])
    return distance,optimizedList

# greedy algorithm
def greedy(order):
    source = startingPoint
    orderlist = orderdict[order]
    distances = {}
    optimizedLists = {}
    s1 = time.time()
    for x in range(len(orderlist)):
#    for x in range(10):
        item = orderlist[x]
        newlist = copy.deepcopy(orderlist)
        del newlist[x]
        i,j = greedyiteration(itemdict[item],newlist)
        i += getLength(source,itemdict[item])
        distances[i]=item
        optimizedLists[item] = j
    distance = min(distances)
    optimizedList = [distances[distance]] + optimizedLists[distances[distance]]
    e1 = time.time()
    print "time for processing order: " + str(e1-s1)
    return distance,optimizedList

def lowerbound(orderlist):
    mylist = copy.deepcopy(orderlist)
    v = [startingPoint]
    distance = 0
    while (len(orderlist)!=0):
        distances = {}
        for i in v:
            for j in orderlist:
                distances[getLength(i,itemdict[j])] = j
        shortest = distances[min(distances)]
        orderlist.remove(shortest)
        v.append(itemdict[shortest])
        distance += min(distances)
    #distance += min(map(lambda x: getLength(startingPoint,itemdict[x]),origin))
    distance += min(map(lambda x: getLength(itemdict[x],endPoint), mylist))
    return distance

def reduceM(matrix):
    lb = 0
    reduced = []
    for i in range(len(matrix)):
        reduced.append(matrix[i])
        minimum = min(matrix[i])
        if minimum == 0:
            reduced[i] = matrix[i]
        elif minimum > 999999:
            reduced[i] = matrix[i]
        else:
            lb += minimum
            reduced[i] = [(v-minimum) for v in matrix[i]]

    transposed = [[reduced[j][i] for j in range(len(reduced))] for i in range(len(reduced[0]))]
    nreduced = []
    for i in range(len(transposed)):
        nreduced.append(transposed[i])
        minimum = min(transposed[i])
        if minimum == 0:
            nreduced[i] = transposed[i]
        elif minimum > 999999:
            nreduced[i] = transposed[i]
        else:
            lb += minimum
            nreduced[i] = [(v-minimum) for v in transposed[i]]
    result = [[nreduced[j][i] for j in range(len(nreduced))] for i in range(len(nreduced[0]))]
    return result,lb

def bbiteration(matrix,src,des):
    for i in range(len(matrix[src])):
        matrix[src][i] = inf
    for j in range(len(matrix)):
        matrix[j][des] = inf
    matrix[des][src] = inf
    reduced,c = reduceM(matrix)
    return reduced,c

def minkey(mydict):
    key=0
    value=inf
    for k,v in mydict.items():
        value = min(v,value)
        if value == v:
            key = k
    return key

def longestlist(mydict):
    mylist = []
    key = 0
    for k in mydict:
        if len(mydict[k]) > len(mylist):
            mylist = mydict[k]
            key = k
    return key,mylist


def maxfinishedkey(mydict):
    mylength = 0
    mykey = 0
    for k,v in mydict.items():
        mylength = max(mylength,len(v))
        if len(v) == mylength:
            mykey = k
    return mykey

# branch and bound algorithm
def bb(orderlist):
    # initialize the matrix
    pointlist = [startingPoint] + [itemdict[x] for x in orderlist]
    distances = [[inf]]*len(pointlist)
    for i in range(len(pointlist)):
        distance = [inf]*len(pointlist)
        for j in range(len(pointlist)):
            if i!=j:
                distance[j] = getLength(pointlist[i],pointlist[j])
            else:
                distance[j] = inf
        distances[i] = distance
    # first reduction
    #print distances
    reduced,lb = reduceM(distances)
    #set source
    src = 0
    indexlist = range(1,len(reduced))
    newMatrix = copy.deepcopy(reduced)
    costdict = {}
    ordersd = {}
    matrixdict = {}
    totalkeys = 0
    for j in indexlist:
        temp = newMatrix[src][j]
        tempM = copy.deepcopy(newMatrix)
        newM,c = bbiteration(tempM,src,j)
        totalkeys +=1
        costdict[totalkeys] = c+lb+temp
        matrixdict[totalkeys] = newM
        ordersd[totalkeys] = [j]
    #treef = open('tree.txt','w')
    while max(map(lambda x:len(x),ordersd.values())) < len(indexlist) or costdict[maxfinishedkey(ordersd)] > min(costdict.values()):
#    while max(map(lambda x:len(x),ordersd.values())) < len(indexlist):
        mykey = minkey(costdict)
        mylb = costdict[mykey]
        myMatrix = matrixdict[mykey]
        myorders = ordersd[mykey]
        src = myorders[-1]
        myresults = {}
        for j in [x for x in indexlist if x not in myorders]:
            temporders = copy.deepcopy(myorders)
            temp = myMatrix[src][j]
            tempM = copy.deepcopy(myMatrix)
            newM,c = bbiteration(tempM,src,j)
            totalkeys +=1
            costdict[totalkeys] = c+mylb+temp
            matrixdict[totalkeys] = newM
            ordersd[totalkeys] = temporders + [j]
        del costdict[mykey]
        del ordersd[mykey]
        del matrixdict[mykey]
        #treef.write(str(mykey) + "\n")
        #treef.write(str(mylb) + "\n")
        #treef.write(str(myorders) + "\n")
        #treef.write(str(costdict) + "\n")
        if totalkeys > keythreshold:
            break

    mykey = 0
    finalindexlist = []
    bbcost = 0
    if totalkeys > keythreshold:

        mykey,finalindexlist = longestlist(ordersd)
        startindex = len(finalindexlist)
        for leftitem in indexlist:
            if leftitem not in finalindexlist:
                finalindexlist.append(leftitem)
        bbcost += getLength(startingPoint,itemdict[orderlist[finalindexlist[0]-1]])
        for ii in range(0,len(finalindexlist)-1):
            bbcost += getLength(itemdict[orderlist[finalindexlist[ii]-1]],itemdict[orderlist[finalindexlist[ii+1]-1]])
        bbcost += getLength(itemdict[orderlist[finalindexlist[-1]-1]],startingPoint)
    else:
        for k in ordersd:
            if len(ordersd[k]) == len(indexlist):
                mykey = k
        finalindexlist = ordersd[mykey]
        bbcost = costdict[mykey]
        #print matrixdict[mykey]
    optimizedList = []
    #treef.write(str(finalindexlist) + "\n")
    #treef.close()
    for i in finalindexlist:
        optimizedList.append(orderlist[i-1])
    return bbcost,optimizedList


# compare time and distance of default list and optimized list
def compareOrder():
    f = open(outputFile,'w')
    xxx = 0
    yyy = 999
    GUIdict = {}
    for order in range(len(orderdict)):
        f.write("\n====================================")
        f.write("\n##Order Number##\n")
        f.write(str(order+1))
        f.write("\n##Worker Start Location##\n")
        f.write(str(startingPoint))
        f.write("\n##Worker End Location##\n")
        f.write(str(endPoint))
        f.write("\n##Original Parts Order##\n")
        map(lambda x:f.write(str(x)+" "),orderdict[order])

        # defalut order
        defaultdistance = default(order)
        dflist = orderdict[order]
        effort,missing = showEffort(dflist,defaultdistance)
        f.write("\n##Original Parts Total Distance##\n")
        f.write(str(defaultdistance))
        if effortflag is True:
            f.write("\nEffort\n")
            f.write(str(effort)+"\n")
            if len(missing)!=0:
                f.write(str(missing) +"weight information missing\n")


        # lower bound
        lblist = copy.deepcopy(orderdict[order])
        lbdistance = lowerbound(lblist)
        f.write("\n##Lower Bound Distance##\n")
        f.write(str(lbdistance)+"\n")
        distance = 0
        #branch and bound
        if algs == "B" or algs =="b":
            bbstart = time.time()
            bblist = copy.deepcopy(orderdict[order])
            distance,optimizedList = bb(bblist)
            routelist = [startingPoint] + [itemdict[x] for x in optimizedList]
            for point in range(len(routelist)-1):
                if routelist[point][0]>routelist[point+1][0]:
                    distance+=1
            if startingPoint != endPoint:
                if itemdict[optimizedList[-1]][0] >= itemdict[optimizedList[-2]][0]:
                    distance = distance - getLength(itemdict[optimizedList[-1]],startingPoint) + getLength(itemdict[optimizedList[-1]],endPoint)
                else:
                    distance = distance - getLength((itemdict[optimizedList[-1]][0]+1,itemdict[optimizedList[-1]][1]),startingPoint) + getLength((itemdict[optimizedList[-1]][0]+1,itemdict[optimizedList[-1]][1]),endPoint)
            effort,missing = showEffort(optimizedList,distance)
        # write to file
            print "branch and bound time: " + str(time.time()-bbstart)
            f.write("\n##BB Algs Optimized Parts Order##\n")
            map(lambda x:f.write(str(x)+" "),optimizedList)
            f.write("\n##Optimized Path##\n")
            route = [startingPoint]+map(lambda x: itemdict[x], optimizedList)
            f.write(displayPath(route,optimizedList))
            f.write("\n##Optimized Parts Total Distance##\n")
            f.write(str(distance))
            if effortflag is True:
                f.write("\nEffort\n")
                f.write(str(effort)+"\n")
                GUIdict[str(order+1)] = {"path":GUIdisplay(route,optimizedList),"text":displayPath(route,optimizedList),"effort":str(effort)}
                if len(missing)!=0:
                    f.write(str(missing) +"weight information missing\n")
                    GUIdict[str(order+1)]["effort"] += "\n" + str(missing) +"weight information missing\n"
            else:
                GUIdict[str(order+1)] = {"path":GUIdisplay(route,optimizedList),"text":displayPath(route,optimizedList)}


        # grab item in an optimized order(grab the nearest item).
        if algs == "G" or algs =="g":
            distance,optimizedList = greedy(order)
            effort,missing = showEffort(optimizedList,distance)
            # write to file
            f.write("\n##Greedy Optimized Parts Order##\n")
            map(lambda x:f.write(str(x)+" "),optimizedList)
            f.write("\n##Optimized Path##\n")
            route = [startingPoint]+map(lambda x: itemdict[x], optimizedList)
            f.write(displayPath(route,optimizedList))
            f.write("\n##Optimized Parts Total Distance##\n")
            f.write(str(distance))
            if effortflag is True:
                f.write("\nEffort\n")
                f.write(str(effort) +"\n")
                GUIdict[str(order+1)] = {"path":GUIdisplay(route,optimizedList),"text":displayPath(route,optimizedList),"effort":str(effort)}
                if len(missing)!=0:
                    f.write(str(missing) +"weight information missing\n")
                    GUIdict[str(order+1)]["effort"] += "\n" + str(missing) +"weight information missing\n"
            else:
                GUIdict[str(order+1)] = {"path":GUIdisplay(route,optimizedList),"text":displayPath(route,optimizedList)}

        with open('GUI.txt', 'w') as GUIfile:
            GUIfile.write(json.dumps(GUIdict))
        print ("%s order(s) processed" % (order+1))


        if lbdistance > distance:
            print "smaller than lowerbound! Check! "
            print order
        xxx =max(xxx,(distance-lbdistance))
        yyy =min(yyy,(distance-lbdistance))
    f.close()
    print "max larger than lower bound: " +str(xxx)
    print "min larger than lower bound: " +str(yyy)

def main():
    init()
    s = time.time()
    itemdict = getItem()
    orderdict = getOrder()
    e = time.time()
    print "time for pre-processing: "+str(e-s)
    compareOrder()

if __name__ == '__main__':
    main()

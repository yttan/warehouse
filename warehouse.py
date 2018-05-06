import csv
import sys
from ast import literal_eval as make_tuple
import time
import copy
inf = 9999999
pathwidth = 1
shelfwidth = 1
width = pathwidth +shelfwidth
itemfile = 'warehouse-grid.csv'
itemdict = {}
orderdict = {}
startingPoint = (0,0)
endPoint = (0,0)
#orderfile = "warehouse-orders-v01.csv"
orderfile = "10.csv"
outputFile = "output.txt"
userPickedItem = []
algs = "b"
def init():
    global startingPoint
    global endPoint
    global orderfile
    global outputFile
    global userPickedItem
    global algs
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

# retrieve items and their positions
def getItem():
    global itemdict
    start = time.time()
    with open(itemfile,'r') as csvfile:
        reader = csv.reader(csvfile)
        for rows in reader:
            itemdict[int(rows[0])] = (int(float(rows[1])),int(rows[2])) # drop the decimal
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
    i = max(end[1],start[1])
    j = min(end[1],start[1])
    length = 0
    if (end[0] == 0 and end[1] == 0):
        length = start[0] + start[1]
    elif start[0] < end[0]:
        length = (end[0] - start[0]) + i-j
    elif start[0] > end[0]:
        length = (start[0] - (end[0] + shelfwidth)) + i-j
    else:
        length = i-j
    return length


def displayPath(route,items):
    path = ''
    location = route[0]
    for i in range(len(route)-1):
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
    for k in mydict:
        if value > mydict[k]:
            value = mydict[k]
            key = k
    return key

def maxfinishedkey(mydict):
    mylength = 0
    mykey = 0
    for k in mydict:
        if mylength < len(mydict[k]):
            mylength = len(mydict[k])
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
    while max(map(lambda x:len(x),ordersd.values())) < len(indexlist) or costdict[maxfinishedkey(ordersd)] > min(costdict.values()):
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
    mykey = 0
    for k in ordersd:
        if len(ordersd[k]) == len(indexlist):
            mykey = k
    finalindexlist = ordersd[mykey]
    optimizedList = []
    for i in finalindexlist:
        optimizedList.append(orderlist[i-1])
    return costdict[mykey],optimizedList

# compare time and distance of default list and optimized list
def compareOrder():
    f = open(outputFile,'w')
    xxx = 0
    yyy = 999
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
        f.write("\n##Original Parts Total Distance##\n")
        f.write(str(defaultdistance))

        # lower bound
        lblist = copy.deepcopy(orderdict[order])
        lbdistance = lowerbound(lblist)

        f.write("\n##Lower Bound Distance##\n")
        f.write(str(lbdistance))
        distance = 0
        #branch and bound
        if algs == "B" or algs =="b":
            bblist = copy.deepcopy(orderdict[order])
            distance,optimizedList = bb(bblist)
            routelist = [startingPoint] + [itemdict[x] for x in optimizedList]
            for point in range(len(routelist)-1):
                if routelist[point][0]>routelist[point+1][0]:
                    distance+=1
        # write to file
            f.write("\n##BB Algs Optimized Parts Order##\n")
            map(lambda x:f.write(str(x)+" "),optimizedList)
            f.write("\n##Optimized Path##\n")
            route = [startingPoint]+map(lambda x: itemdict[x], optimizedList)
            f.write(displayPath(route,optimizedList))
            f.write("\n##Optimized Parts Total Distance##\n")
            f.write(str(distance))

        # grab item in an optimized order(grab the nearest item).
        if algs == "b" or algs =="g":
            distance,optimizedList = greedy(order)
            # write to file
            f.write("\n##Greedy Optimized Parts Order##\n")
            map(lambda x:f.write(str(x)+" "),optimizedList)
            f.write("\n##Optimized Path##\n")
            route = [startingPoint]+map(lambda x: itemdict[x], optimizedList)
            f.write(displayPath(route,optimizedList))
            f.write("\n##Optimized Parts Total Distance##\n")
            f.write(str(distance))

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
    #init()
    s = time.time()
    itemdict = getItem()
    orderdict = getOrder()
    e = time.time()
    print "time for pre-processing: "+str(e-s)
    compareOrder()

if __name__ == '__main__':
    main()

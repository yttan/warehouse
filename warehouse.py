import csv
import sys
from ast import literal_eval as make_tuple
import time
pathwidth = 1
shelfwidth = 1
width = pathwidth +shelfwidth
itemfile = 'warehouse-grid.csv'

itemdict = {}
orderdict = {}

startingPoint = (0,0)
endPoint = (0,0)
orderfile = ''
outputFile = ''
userPickedItem = []

def init():
    global startingPoint
    global endPoint
    global orderfile
    global outputFile
    global userPickedItem
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
    if start[0] < end[0]:
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

    path += "From " + str(route[-1])
    path += ", go to (%s,%s)" % (route[-1][0],endPoint[1])
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
def single(source,orderlist):
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
        newlist = orderlist[:]
        newlist.remove(item)
        i,j = single(itemdict[item],newlist)
        i += getLength(source,itemdict[item])
        distances[i]=item
        optimizedLists[item] = j
    distance = min(distances)
    optimizedList = optimizedLists[distances[distance]]
    e1 = time.time()
    print "time for processing order: " + str(e1-s1)
    return distance,optimizedList

def lowerbound(orderlist):
    mylist = orderlist[:]
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
        lblist = orderdict[order][:]
        lbdistance = lowerbound(lblist)

        f.write("\n##Lower Bound Distance##\n")
        f.write(str(lbdistance))

        # grab item in an optimized order(grab the nearest item).
        distance,optimizedList = greedy(order)
        # write to file
        f.write("\n##Optimized Parts Order##\n")
        map(lambda x:f.write(str(x)+" "),optimizedList)
        f.write("\n##Optimized Path##\n")
        route = [startingPoint]+map(lambda x: itemdict[x], optimizedList)
        f.write(displayPath(route,optimizedList))
        f.write("\n##Optimized Parts Total Distance##\n")
        f.write(str(distance))
        print ("%s order(s) processed" % (order+1))
        #if defaultdistance < distance:
        #    print "!!!!!!!!!!!"
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

import numpy as np
def datagen(duedates,w):
    #normalise to first due:
    first = duedates[0] # or min if not sorted
    norm_duedates = [i for i in duedates] 
    # print(norm_duedates)
    res = np.zeros(shape=(len(norm_duedates), len(norm_duedates)))
    for idx,i in enumerate(norm_duedates):
        for idy,j in enumerate(norm_duedates[idx:]):
            res[idx,idy+idx] = (j-i)*w[idx+idy]
    # print(res) 
    return res
def split2dict(a,splits,minlbl,la):
    res = {}
    cchecks = (a[0],) + splits
    # subarrays = np.split(matrix, splits, axis=1)
    # res = []

    curr = 0
    for idx,t in enumerate(la):
        if curr>=len(minlbl) or t != minlbl[curr] :
            res[minlbl[curr-1]].append(t)
        else:

            res[minlbl[curr]]=[t]

            curr+=1

        # print(splits[idx+1])
        # res[minlbl[idx]]= [i for i,j in zip(la,a) if (splits[idx]<j and j <splits[idx+1])]
        pass
    return res
def calccost(matrix,splits):
    # for i in sorted(splits):
    subarrays = np.split(matrix, splits, axis=1)
    cost = 0
    for m,s in zip(subarrays,[0]+splits):
       cost+=m[[s]].sum() 
    return cost
def algorithm(c,a,p,w,lc,la,v=False):
    if len(c) < p:
        return c, 0, split2dict(a,tuple(c),lc,la)
    m = datagen(a,w)
    from itertools import combinations

    combinations_costs = {}
    i = 0
    if v : print("generating combos ...",end = '\r')
    from math import comb

    count = comb(len(c), p-1)

    combos = combinations(range(len(c)), p-1)
    if v : print("evaluating combos...",end='\r')

    for combo in combos:
        i+=1
        if (i%10000)==0: print(f" ~{i} of {count} ({int(i/count*100)}%) ",end='\r')
        times = tuple([c[i] for i in combo])
        
        min_indices = [a.index(t) for t in times]
        combinations_costs[times]=(calccost(m,(min_indices)))
        if v : print(f"Combo:{combo} -> Timestamps:{times} -> Min Indices:{min_indices} : Cost:{combinations_costs[times]}")

    min_key = min(combinations_costs, key=combinations_costs.get)
    if v : print(f"MINKEY: {min_key}")
    if v : print(f"IMPORTANT : {[(i,j) for i,j in zip(c,lc)]}")

    if True:
        min_lbl = [lc[0]]
        visitied = []
        for i,j in zip(c,lc):
            if i in min_key and i not in visitied:

                min_lbl.append(j)
                visitied.append(i)

        if v : print("MIN_LBL:",min_lbl)
        projects = (a[0],)+min_key if min_key[0]!=a[0]else min_key
        return projects, combinations_costs[min_key],split2dict(a,min_key,min_lbl,la)
    return min_key, combinations_costs[min_key]

def grouping_algo(fleet): # Aircraft-level Task Grouping Algorithn
    res = {}

    for idx,plane in enumerate(fleet):
        print(f"{idx+1}/{len(fleet)}")

        a = [t["max_util"]-t["curr_util"] for t in plane["events"]]
        la = [t["taskID"] for t in plane["events"]]
        ld = [t["duration"]for t in plane["events"]]
        w = [t["importance"] for t in plane["events"]]
        x,imp,labels,durations = a,w,la,ld #TODO
        durations = [max(1,int(i)) for i in durations]
        if len(x) == 0 :
            print("skip")
            continue
        x_sorted,imp_sorted,labels_sorted,durations_sorted = map(list, zip(*sorted(zip(x,imp,labels,durations))))

        minx = x_sorted[0]
        important_x = [i for i,j,l in zip(x_sorted,imp_sorted,labels_sorted) if (j>=data["threshold"] or i==minx)]
        important_l = [l for i,j,l in zip(x_sorted,imp_sorted,labels_sorted) if (j>=data["threshold"] or i==minx)]
        if len(important_x) == 0:
            print("Boom not important")
            continue
        x,cost,labeledout =  algorithm(important_x,x_sorted,data["max_projects"],imp_sorted,important_l,labels_sorted) 



        res[plane["aircraftID"]] = {"split":x,"cost":cost,"labeledout":labeledout}
    return res
# _______________New Code : _________________

def _cost(l):
    if len(l) == 0:
        return 0
    ex_date = min(l,key=lambda x : x[1])[1]
    return sum (i[2]*(i[1]-ex_date) for i in l)
def cost(l1,l2):
    return _cost(l1)+_cost(l2)

def split(l,horison):
    x0 = l[0]
    l3 = []
    l1 = []
    l2 = []
    #~print(l)
    l.sort(key=lambda x: x[1])
    #~print ("sort l")
    #~print(l)
    for idx,x in enumerate(l):
        # #~print(i,x)
        if not any([i[0] == x[0] for i in l1]):
            l1.append(x)
            continue
        else:
            l2 = l[idx:] 
            break
    wp1_time = l1[0][1]
    #~print("first split")
    #~print(l1)
    #~print(l2)
    for t in l1:
        for x in l2:
            if t[0] == x[0] : x[1]-= (t[1]-wp1_time)
    l2.sort(key=lambda x: x[1])
    #~print("time update")
    #~print(l1)
    #~print(l2)    
    l3 = [i  for i in l2 if i[1] > horison]
    l2 = [i  for i in l2 if i not in  l3]
    #~print("check horison")
    #~print(l1)
    #~print(l2)
    #~print(l3)

    
    for t in l2:
        for x in l2:
            if t[0] == x[0] and t[1] != x[1] and not (x in l1 or t in l1):
                if x[1]<=t[1]:
                    l1.append(x)
                else:
                    l1.append(t)

    l2 = [i  for i in l2 if i not in  l1]
    
    #~print("move duplicates back to l1")
    #~print(l1)
    #~print(l2)
    #~print(l3)
    l2.sort(key=lambda x: x[1])
    l2buff = []
    for t in l3:
        for i in l2:
            if i[0] == t[0]  and  t[1] - (i[1] - min(l2,key=lambda x:x[1])[1]) <= horison:
                l1.append(i)
                l2buff.append(t)
    l2 = [i  for i in l2 if i not in  l1]+ l2buff
    l3 = [i for i in l3 if i not in l2]
    # if len(l2)!=0:
    #     wp2_time = min(l2,key=lambda x:x[1])[1]
    #     for i in l3:
    #         for j in l2:    
    #             if i[0] == j[0]:
    #                 i[1]-= j[1]-wp2_time
    # #print("Recalculating ooh tasks")
    # print(l1)
    # print(l2)
    # print(l3)
    # wp2_time = l2[0][1]
    # print("\nRESULT")
    # print("l1",l1)
    # print("l2",l2)
    # print("Optimizing")
    # intialise min and pointer
    min_cost = cost(l1,l2)
    l1_tonos = l1.copy()
    l2_tonos = l2.copy()
    l3_tonos = l3.copy()
    #~print("min cost =",min_cost)
    for idx,t in enumerate(l1[::-1]):
        #~print(f"task : {t}")
        if any(i[0]==t[0] for i in l2):
            #~print(f" task {t[0]} found in l2. Abort")
            break # TODO replace with continue and skip element ?
        l1_prop = l1[:-idx-1]
        l2_prop = l2+l1[-idx-1:]
        l3_prop = l3.copy()
        # fix l3
        l2buff = []
        for t in l3_prop:
            for i in l2_prop:
                if i[0] == t[0]  and  t[1] - (i[1] - min(l2_prop,key=lambda x:x[1])[1]) <= horison:
                    l1_prop.append(i.copy())
                    l2buff.append(t.copy())
        for i in l2buff:
            for j in l1_prop:
                if i[0] == j[0]:
                    i[1]-= j[1]-wp1_time 
        l2_prop = [i  for i in l2_prop if i not in  l1_prop]+ l2buff
        l3_prop = [i for i in l3_prop if i not in l2_prop]
        curr_cost = cost(l1_prop,l2_prop)

        #~print (f"spliting: l1 = {l1_prop} l2 = {l2_prop} : cost = {curr_cost}")

        if curr_cost<min_cost:
            min_cost = curr_cost
            l1_tonos ,l2_tonos,l3_tonos= l1_prop,l2_prop,l3_prop
            #~print (f"   Min found :l1 = {l1_tonos} l2 = {l2_tonos} : cost = {min_cost}")
    l1 = l1_tonos
    l2 = l2_tonos
    l3 = l3_tonos
    #~print("RESULT")
    #~print("l1",l1)
    #~print("l2",l2)
    #~print("l3",l3)

    #   if cost (l1,l2) < cost : min = cost, pointer = ti

    if len(l2)!=0:
        wp2_time = min(l2,key=lambda x:x[1])[1]
        for i in l3:
            for j in l2:    
                if i[0] == j[0]:
                    i[1]-= j[1]-wp2_time
    #~print("Recalculating ooh tasks")
    #~print(l1)
    #~print(l2)
    #~print(l3)

    return l1,l2,l3

def algorithmv2(tasks,horison):
    #l = {TaskID:duedate}
    lo1 = [[k,v[0]-v[1],v[2]] for k,v in tasks.items()]
    lo2 = [[k,2*v[0]-v[1],v[2]] for k,v in tasks.items()]
    l = lo1+lo2
    l1,l2,l3 = split(l,horison)
    # print(l1,l2,l3)
    labeledout = {}
    l1_def = min(l1,key=lambda x : x[1])
    if len(l2) !=0:
        l2_def = min(l2,key=lambda x : x[1])
        split_dates = [l1_def[1],l2_def[1]]
        labeledout = {l1_def[0]:[i[0] for i in l1],l2_def[0]:[i[0] for i in l2]}
    else:
        split_dates = [l1_def[1]]
        labeledout = {l1_def[0]:[i[0] for i in l1]}

    return split_dates,labeledout

def grouping_algov2(fleet,horison): # Aircraft-level Task Grouping Algorithn
    res = {}
    for idx,plane in enumerate(fleet):
        print(f"{idx+1}/{len(fleet)}",end = "")

        a = [(t["max_util"],t["curr_util"],t["importance"]) for t in plane["events"]]
        la = [t["taskID"] for t in plane["events"]]
        
        # ld = [t["duration"]for t in plane["events"]]
        # w = [t["importance"] for t in plane["events"]]
        # x,imp,labels,durations = a,w,la,ld #TODO
        # durations = [max(1,int(i)) for i in durations]

        # important_x = [i for i,j,l in zip(x_sorted,imp_sorted,labels_sorted) if (j>=data["threshold"] or i==minx)]
        # important_l = [l for i,j,l in zip(x_sorted,imp_sorted,labels_sorted) if (j>=data["threshold"] or i==minx)]
        # # print(len(important_x))
        # if len(important_x) == 0:
        #     print("Boom not important")
        #     continue
        # x,cost,labeledout =  algorithm(important_x,x_sorted,data["max_projects"],imp_sorted,important_l,labels_sorted) 
        tasks = {j:i for i,j in zip(a,la)}
        x,labeledout = algorithmv2(tasks,horison)


        if len(x) == len (labeledout) :
            res[plane["aircraftID"]] = {"split":x,"labeledout":labeledout}
            print()
        else:
            print(x , labeledout)
            print ("skip")
    return res

if __name__=="__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filename', help='file containing initial data (e.g. test.json)',required=True)
    parser.add_argument('-t','--horison', help='time horison',type=int)
    parser.add_argument('-w','--max_projects', help='projects per season',type=int)
    parser.add_argument('-o','--outfile', help='prefix for output file (defaults to \'out\')',default="out")
    args = parser.parse_args()
    data = json.load(open(args.filename,'r'))
    horison = data["sim_days"]
    fleet = data["fleet"]
    if args.horison :
        horison = args.horison
    groupings = grouping_algov2(fleet,horison=horison)

    json.dump(groupings,open(args.outfile+"_grouping.json",'w'),indent=4)
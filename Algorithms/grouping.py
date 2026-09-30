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
        # print("a",c,len(c))
        # print("la",lc,len(lc))
        # print("min_key",min_key,len(min_key))
        # print("min_lbl",min_lbl,len(min_lbl)) 
        if v : print("MIN_LBL:",min_lbl)
        projects = (a[0],)+min_key if min_key[0]!=a[0]else min_key
        return projects, combinations_costs[min_key],split2dict(a,min_key,min_lbl,la)
    return min_key, combinations_costs[min_key]

def grouping_algo(data): # Aircraft-level Task Grouping Algorithn
    res = {}

    for idx,plane in enumerate(data["fleet"]):
        print(f"{idx+1}/{len(data['fleet'])}")

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
        # print(len(important_x))
        if len(important_x) == 0:
            print("Boom not important")
            continue
        x,cost,labeledout =  algorithm(important_x,x_sorted,data["max_projects"],imp_sorted,important_l,labels_sorted) 



        res[plane["aircraftID"]] = {"split":x,"cost":cost,"labeledout":labeledout}
    return res

if __name__=="__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filename', help='file containing initial data (e.g. test.json)',required=True)
    parser.add_argument('-o','--outfile', help='prefix for output file (defaults to \'out\')',default="out")
    args = parser.parse_args()
    data = json.load(open(args.filename,'r'))
    groupings = grouping_algo(data)
    json.dump(groupings,open(args.outfile+"_grouping.json",'w'),indent=4)
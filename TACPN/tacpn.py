def tacpn_prep(data,T_dc=0,crew_count=100,): # generates  input JSON file  for TACPN_generator script
  
    res = {}
    tasks = max([len(i["events"]) for i in data["fleet"]])
    aircrafts = [f"{planeID2PID(a['aircraftID'])}" for a in data["fleet"]]
    lifespan= T_dc + data["sim_days"]
    res_tasks = []
    for t in range(1,tasks+1):
        task = {}
        task["guard"]=[T_dc,lifespan]
        task["timer_invariants"] = {}
        for idx,a in enumerate(data["fleet"]):
            for event in a["events"]:
                if int(''.join(filter(str.isdigit, event["taskID"]))) == t and event["max_util"] - event["curr_util"]>=0:
                    if int(event["max_util"] - event["curr_util"] + T_dc)<T_dc:
                        print(f"{event['max_util']} - {event['curr_util']} + {T_dc} = {int(event['max_util'] - event['curr_util'] + T_dc)} < {T_dc}")
                    task["timer_invariants"][f"{planeID2PID(a['aircraftID'])}"] = int(event["max_util"] - event["curr_util"] + T_dc)
                else:
                    task["timer_invariants"][f"{planeID2PID(a['aircraftID'])}"]= lifespan #probably
        res_tasks.append(task)
    res["aircraft"] = aircrafts
    res["flying_invariants"]={i:lifespan for i in aircrafts}
    res["tasks"] = res_tasks    
    res["crew_count"] = crew_count
    res["hangar_count"] = data["hangar_capacity"]
    res["lifespan"] = lifespan
    
    return res
def tacpn_prep_v2(fleet,taskmap,T_dc=0,capacity=1,lifespan=365,):
    # create task list mapping
    res = {}
    tasks = []
    res ["aircraft"] = []
    res ["flying_invariants"] = {
        i:lifespan for i in fleet
    }
    res["crew_count"]=capacity
    res["hangar_count"]=capacity
    res["lifespan"] = lifespan+T_dc
    res["tasks"] = []
    for a in fleet:
        res["aircraft"].append(a)
        for t in fleet[a]:
            if t not in tasks:
                tasks.append(t)
    for t in tasks:
        datum = {"guard":[T_dc,lifespan+T_dc],"timer_invariants":{}}
        for a in fleet:
            if t not in fleet[a]:
                datum["timer_invariants"][a] = lifespan+T_dc
            else:
                datum["timer_invariants"][a] = taskmap[a][t]+T_dc
        res["tasks"].append(datum)
    return res,tasks
if __name__ == "__main__":
    import json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-g','--grouping', help='file containing flp schedule (e.g. output of FLP.py)')
    parser.add_argument('-d','--data', help='file containing initial data (e.g. test.json): used ONLY for hangar capacity and task due dates')
    parser.add_argument('-t','--taskmap', help='taskmap : overrides value set in data file if provided')
    parser.add_argument('-f','--fleet', help='fleet : overrides value set in grouping file if provided')
    parser.add_argument('-c','--capacity', help='capacity : overrides value set in data file if provided',type=int)
    parser.add_argument('--tdc', help='T_dc',type=int,default=0)
    parser.add_argument('--lifespan', help='capacity : overrides value set in data file if provided',type=int)
    parser.add_argument('-o','--outfile', help='prefix for output file (defaults to \'out\')',default="out")
    args = parser.parse_args()
    capacity = 1
    lifespan = 365
    if args.data:
        data = json.load(open(args.data,'r'))
        capacity = data["hangar_capacity"]
        lifespan = data["sim_days"]
    if args.capacity :
        capacity = args.capacity
    if args.lifespan :
        lifespan = args.lifespan
    if not args.taskmap:
        taskmap = {}
        if args.data:
            data = json.load(open(args.data,'r'))
            for a in data["fleet"]:
                taskmap [a["aircraftID"]] = {}
                for e in a["events"]:
                    taskmap [a["aircraftID"]][e["taskID"]] = e["max_util"]-e["curr_util"]
        else:
            import sys
            sys.exit("No data or taskmap files specified. Check -h ")
    else:
        taskmap = json.load(open(args.taskmap,'r'))
    if not args.fleet:
        fleet = {}
        if args.grouping:
            grouping = json.load(open(args.grouping,'r'))
            for a in grouping:
                fleet[a] = []
                for p in grouping[a]["labeledout"]:
                    fleet[a]+= grouping[a]["labeledout"][p]
        else:
            import sys
            sys.exit("No grouping or fleet files specified. Check -h ")
    else:
        fleet = json.load(open(args.fleet,'r'))
    res,tasks = tacpn_prep_v2(fleet,taskmap,args.tdc,capacity,lifespan)
    json.dump(res,open(args.outfile+"_tacpn_config.json",'w'),indent=4)
    json.dump(tasks,open(args.outfile+"_tacpn_taskmap.json",'w'),indent=4)
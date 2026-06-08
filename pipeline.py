#!.venv/bin/python
try:
    from termcolor import colored as co
except:
    def co(s,col):
        return s
import json
VERBOSE = False
INTER_CLEAN = False
def printv(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)
        return True
    return False
def grouping_algo(data):
    from Scheduling.algorithm import algorithm
    print(co("\n[GROUPING] Grouping Algorithm ... ","green"),end = '')
    res = {}

    printv("\nCalculating Groupings ....")
    for idx,plane in enumerate(data["fleet"]):
        printv(f"{idx+1}/{len(data['fleet'])}")

        a = [t["max_util"]-t["curr_util"] for t in plane["events"]]
        la = [t["taskID"] for t in plane["events"]]
        ld = [t["duration"]for t in plane["events"]]
        w = [t["importance"] for t in plane["events"]]
        x,imp,labels,durations = a,w,la,ld #TODO
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
        x,cost,labeledout =  algorithm(important_x,x_sorted,data["max_projects"],imp_sorted,important_l,labels_sorted,v=VERBOSE) 



        res[plane["aircraftID"]] = {"split":x,"cost":cost,"labeledout":labeledout}
    printv(f'grouping algo result : \n{json.dumps(res, indent=4)}')
    print(co("Done","red"))
    return res

def tokenise(ac,tasks,fcpd=1,fhpd=1,years=1,year_dur=365,p=2,bop=[],bot=[]):
    res  = {}
    res["active_fleet"]= {
        "tokens": [[]],
        "timestamps": [0]
    }
    res["specs"]= {
        "tokens": [],
        "timestamps": [0]
    }
    spec_1 = []
    spec_2 = []
    for task in tasks:
        try:
            if task["max_util"]-task["curr_util"] >= 0:
                res["active_fleet"]["tokens"][0].append([task["taskID"],int(task["curr_util"]),int(task["curr_util"]),int(task["curr_util"])])#replace with other clocks when we have good fhpd fcpd needed
                #TODO:modify to take into account both interval_value AND interval_value_next
                spec_1.append([task["taskID"],int(task["max_util"]),int(task["max_util"]),int(task["max_util"])])#replace with other clocks when we have good fhpd fcpd needed
                spec_2.append(task["duration"])#replace with other clocks when we have good fhpd fcpd needed
                

        except KeyError:
            pass
    res["specs"]["tokens"]=[[spec_1,spec_2]]
    flights_tokens = []
    flights_timestamps = []
    for day in range(year_dur*years):
        flights_tokens.append([f"#{day}",fcpd,fhpd])
        flights_timestamps.append(day)
    res["flights"]={
        "tokens":flights_tokens,    
        "timestamps":flights_timestamps
    }
    wps = []
    wps_t = []
    for year in range(years):
        wps.append([f"#{year}",p])
        wps_t.append(year_dur*year)
    res["workgroup"] = {
        "tokens" : wps,
        "timestamps" : wps_t
    }
    res["blackout_periods"]= {
        "tokens": [(f"#{idx}",i) for idx,i in enumerate(bop)],
        "timestamps": bot
    }
    return res
# def alp_tcpn_prep(data,fleet_grouping):
#     for plane in data:
def initial_marking(data):
    print(co("\n[ALP] Initial Markings generation ... ","green"),end = '')
    res = {}
    printv("\nCalculating Groupings ....")
    for idx,plane in enumerate(data["fleet"]):
        printv(f"{idx+1}/{len(data['fleet'])}")

        if "blackout-durations" in data :res[plane["aircraftID"]] = tokenise(plane["aircraftID"],plane["events"],fcpd=plane["fpd"],year_dur=data["sim_days"],p=data["max_projects"],bot=data["blackout-days"],bop=data["blackout-durations"])
        else:res[plane["aircraftID"]] = tokenise(plane["aircraftID"],plane["events"],fcpd=plane["fpd"],year_dur=data["sim_days"],p=data["max_projects"],bot=data["blackout-days"],bop=[1 for _ in data["blackout-days"]])
    printv(f'Initial Markings : \n{json.dumps(res, indent=4)}')
    print(co("Done","red"))
    return res
def alp_tcpn(initial_marking,grouping):

    import subprocess
    pID = ""
    json.dump(initial_marking,open(f"dataset_initial_marking.json",'w'))
    json.dump(grouping,open(f"curr_grouping.json",'w'))

    result = subprocess.run(["python", "Modified/vp1_custom_grouping.py","pipeline","-ijx"],capture_output=True, text=True) 
        
    printv(result.stderr)
    # strr = result.stdout.replace("status",'"status"').replace('wps','"wps"').replace("'",'"').replace(",\n }","\n   }").replace(",\n     ]","\n     ]").replace(",\n]","\n]")
    tcpnresult=json.loads(result.stdout)
    alts = []
    for r in tcpnresult:
        if r["status"]=="SAFE":
            alts.append({"wps":r["wps"]})
    printv(alts)
    return alts

    durations = [x["duration"]for x in wps]
    timestamps_real = [x["timestamp"] for x in wps]
    ends_real = [i+x for i,x in zip(timestamps_real,durations)]
    timezero = max(ends_real)

    rev_times = [timezero-x-d for x,d in zip(times,durations)]
    wps_resc = wps.copy()
    for idx,proj in enumerate(wps):
        wps_resc[idx]["timestamp"] = rev_times[idx]

    return rev_times,wps_resc


def flp_algo(alts,cap,bo_days):
    from Scheduling.FLP import task,schedule,solve
    tasks_list = []
    print(co(f"\n[FLP] Preparing optimal Schedule... ","green"),end = '')

    for plane in alts:
        if len(alts[plane]) > 1:
            printv("multiple alts selecting first")
        tcpn = alts[plane][0]
        tmp=tcpn["wps"].copy()

        for i in tmp:
            tasks_list.append((plane,i))
    tasks = []
    # timezero = 0
    # for _,i in tasks_list:
    #         if i['duration'] + i['timestamp'] > timezero :
    #             timezero =  i['duration'] + i['timestamp']    
    for plane,i in tasks_list:
            tasks.append(task(f"{plane}: {i['tasks']}",i['timestamp'],i['duration']))
    schd = schedule(tasks,bo=bo_days)


    printv("\n  Initial schedule ")
    if printv():schd.print()
    print(co("Done","red"))

    print(co(f"\n[FLP] Running Fleet Level Planning Algorithm... ","green"),end = '')

    solve(schd,cap)

    print(co("Done","red"))
    printv("\n  Resulting schedule ")
    schd.print(bohash=True)
    return [schd]


def list2tasks(l):
    res = []
    for idx,i in enumerate(l):
        if i ==1:
            res.append(f"t{idx+1}")
    return res
def planeID2PID(planeID):
    return int(planeID.split("_")[-1])

def tracegen_prepv2(sched_l):
    print(co("\n[TACPN] Preparing schedule for trace generation ...","green"),end = "")
    input_json = []
    for idx,sched in enumerate(sched_l):
        alt = {"ID":f"Alt{idx+1}","Schedule":[]}
        timezero = sched.timezero
        for project in sched.tasks:
            flag = False
            planeid = project.id.split(': ')[0]
            projects = eval(project.id.split(': ')[1])
            duration = project.d
            date = project.i 
            for plane in alt["Schedule"]:
                if planeID2PID(planeid) == plane["PID"]:
                    plane["P"].append(list2tasks(projects))
                    plane["T"].append(date)
                    plane["D"].append(duration)
                    flag = True
                    break
            if not flag:
                alt["Schedule"].append({
                    "PID" : planeID2PID(planeid),
                    "P":[list2tasks(projects)],
                    "T":[date],
                    "D":[duration]   

                })
        input_json.append(alt)
    printv("\n schedule json:")
    printv(input_json)
    print(co("Done","red"))
    return input_json   
def tracegen_run(input_json,outfile,T_horizon_nominal,T_dc):
    print(co(f"\n[TACPN] Generation TACPN traces... ","green"),end = '')

    from TACPN.Trace_generator.trace_gen_zerotimes import DictObject, HandleAlt
    alts = [DictObject(**alt) for alt in input_json]
    for alt in alts:
        printv(f"\n     generating trace for {alt.ID}...",end = '')
        trace = HandleAlt(alt,T_dc,T_horizon_nominal,save=False)
        with open(f'{outfile}_{alt.ID}.trc','w') as f:
            f.write(trace)
        printv("Done")
    print(co("Done","red"))

def read_input(filename):
    print(co("[Misc] Parsing Data ... ","blue"),end = '')
    data = json.load(open(filename,'r'))
    printv(f"Parsed {filename} : \n {json.dumps(data, indent=4)}")
    print(co("Done","red"))
    return data


def main(filename,outfile):
    data = read_input(args.filename)
    groupings = grouping_algo(data)
    initial_markings = initial_marking(data)
    fleet_alt_tcpn_res = {}
    for idx,plane in enumerate(data["fleet"]):
        pID = plane["aircraftID"]
        print(co(f"\n[ALP] TCPN for {pID} ({idx}/{len(data['fleet'])}) ... ","green"),end = '')
        fleet_alt_tcpn_res[pID]=alp_tcpn(initial_markings[pID],groupings[pID]["labeledout"])
        print(co("Done","red"))
    if "blackout-durations" in data:
        bo_days= {i:j for i,j in zip(data["blackout-days"],data["blackout-durations"])}
    else:bo_days= {i:1 for i in data["blackout-days"]}
    flp_res = flp_algo(fleet_alt_tcpn_res,data["hangar_capacity"],bo_days)
   
    flp_rev_res = flp_res.copy()
    # if printv():flp_rev_res.print()

    sched_out = tracegen_prepv2(flp_rev_res)
    json.dump(sched_out,open(f"{outfile}_scheduling_output.json",'w'))
    tracegen_run(sched_out,outfile,T_horizon_nominal=data["sim_days"],T_dc=100)
    if not INTER:
        import os
        printv("Cleanning intermediate files ...")
        os.remove("curr_grouping.json")
        os.remove("dataset_initial_marking.json")
        printv("Done")
        # print(f'{json.dumps(fleet_alt_tcpn_res, indent=4)}')
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filename', help='filename of initial data json',required=True)
    parser.add_argument('-v','--verbose', help='increase output verbosity',action='store_true')
    parser.add_argument('-i','--intermediate', help='Keep Intermediate Files',action='store_true')
    parser.add_argument('-o','--outfile', help='Name of Outfile',default="out")
    args = parser.parse_args()
    VERBOSE = args.verbose
    INTER = args.intermediate

    main(args.filename,args.outfile)



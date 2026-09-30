import json

def tokenise(ac,tasks,fcpd=1,fhpd=1,years=1,year_dur=365,p=2,bop=[],bot=[]): # Create TCPN compatible tokens from input variables
    # ac := "Plane ID",tasks := "Tasks object",fcpd := "Flight Cycles / day",fhpd := "Flight Hours / day",years := "Number of seasons ",year_dur := "season duration",p := "Number of projects / season",bot := "black-out days (dates)",bop := black-out days (duration)

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

def initial_marking(data): # Generates initial marking (tokens) for Aircraft-level Planning TCPN
    res = {}
    for idx,plane in enumerate(data["fleet"]):
        if "blackout-durations" in data :res[plane["aircraftID"]] = tokenise(plane["aircraftID"],plane["events"],fcpd=plane["fpd"],year_dur=data["sim_days"],p=data["max_projects"],bot=data["blackout-days"],bop=data["blackout-durations"])
        else:res[plane["aircraftID"]] = tokenise(plane["aircraftID"],plane["events"],fcpd=plane["fpd"],year_dur=data["sim_days"],p=data["max_projects"],bot=data["blackout-days"],bop=[1 for _ in data["blackout-days"]])
    return res
def alp_tcpn(initial_marking,grouping): # Runs the Aircraft-level Planning TCPN component for a specific scenario

    import subprocess
    pID = ""

    json.dump(initial_marking,open(f"dataset_initial_marking.json",'w'))
    json.dump(grouping,open(f"curr_grouping.json",'w'))

    result = subprocess.run(["python", "TCPN/vp1_custom_grouping.py","pipeline","-ijx"],capture_output=True, text=True) 
        
    # strr = result.stdout.replace("status",'"status"').replace('wps','"wps"').replace("'",'"').replace(",\n }","\n   }").replace(",\n     ]","\n     ]").replace(",\n]","\n]")
    print(result.stderr,end="")
    # print(result.stdout)
    tcpnresult=json.loads(result.stdout)
    alts = []
    for r in tcpnresult:
        if r["status"]=="SAFE":
            alts.append({"wps":r["wps"]})
    return alts,result.stdout

def map_maker (ac_token):
    
    return [i[0] for i in ac_token]

if __name__=="__main__":
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filename', help='file containing initial data (e.g. test.json)',required=True)
    parser.add_argument('-g','--grouping', help='file containing decided_grouping (result of grouping.py)',required=True)
    parser.add_argument('-o','--outfile', help='prefix for output files (defaults to \'out\')',default="out")
    parser.add_argument('-i','--intermediate', help='keep intermediate marking files',action='store_true')


    args = parser.parse_args()
    data = json.load(open(args.filename,'r'))
    groupings = json.load(open(args.grouping,'r'))
    initial_markings = initial_marking(data)
    if args.intermediate:
        json.dump(initial_markings,open(args.outfile+"_intital_markings.json",'w'),indent=4)
    fleet_alt_tcpn_res = {}
    # Run ALP for each aircraft in the Fleet
    fleetsize = len(data["fleet"])
    for idx,plane in enumerate(data["fleet"]):
        pID = plane["aircraftID"]
        print (f"{pID} ({idx+1}/{fleetsize}) ",end=" ")

        alp_res,stdout = alp_tcpn(initial_markings[pID],groupings[pID]["labeledout"])
        if len(alp_res)!=0:
            for fstate in alp_res: 
                for wp in fstate["wps"]:
                    wp["map"] = map_maker(initial_markings[pID]["active_fleet"]["tokens"][0])
            fleet_alt_tcpn_res[pID]=alp_res
            if args.intermediate:
                json.dump(eval(stdout),open(args.outfile+f"_{pID}_alp_out.json",'w'),indent=4)
  
            print("ok")
        else:
            print("No feasible Schedule")
            if args.intermediate:
                json.dump(eval(stdout),open(args.outfile+f"_{pID}_alp_out.json",'w'),indent=4)

    json.dump(fleet_alt_tcpn_res,open(args.outfile+f"_fleet_alp_res.json",'w'),indent=4)    
    os.remove("curr_grouping.json")
    os.remove("dataset_initial_marking.json")
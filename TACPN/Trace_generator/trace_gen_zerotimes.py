
# DISCLAIMER: THIS WORKS ONLY FOR HANGAR CAPACITY (BAY+CREW ) ===1
# Otherwise it may not work
import json
import sys
import argparse
import math
VERBOSE = False
def printv(*args, **kwargs):
    if VERBOSE:print(*args, **kwargs)

def read_alts(filename):
    alts = json.load(open(filename,'r'))
    return alts

class DictObject:
    def __init__(self, **entries):
        self.__dict__.update(entries)
    def __repr__(self):
        return f"*{self.__dict__}*"

def start_trans(global_time,pid,tasks,diff):
    curr_age=diff

    pid = int(pid[-1])-1
    printv(pid)
    if pid == 0:
        plane_id = ""
    else:
        plane_id = f"__{pid-1}"
    res =f"""
      <transition id="ComposedModel_T_enter{plane_id}">
    <token age="{curr_age}" place="ComposedModel_Shared_P_flying__{pid}"/>
    <token age="0" place="ComposedModel_Shared_P_ground_capacity"/>
  </transition>"""
    for t in tasks:
        tid = t[-1]
        res+=f"""
    <transition id="ComposedModel_T_maint_{tid}{plane_id}">
    <token age="{global_time}" place="ComposedModel_Shared_P_timer_{tid}__{pid}"/>
    <token age="0" place="ComposedModel_Shared_P_crew"/>
    <token age="0" place="ComposedModel_P_bay__{pid}"/>
    </transition>
    <transition id="ComposedModel_T_return_{tid}{plane_id}">
    <token age="0" place="ComposedModel_P_inter_{tid}__{pid}"/>
    </transition>"""
        curr_age = 0
    return res


def end_trans(diff,pid):
    pid = int(pid[-1])-1
    printv(pid)
    if pid == 0:
        plane_id = ""
    else:
        plane_id = f"__{pid-1}"
    return f"""
  <transition id="ComposedModel_T_exit{plane_id}">
    <token age="{diff}" place="ComposedModel_P_bay__{pid}"/>
  </transition>"""
def delay(diff):
    return f"<delay>{diff}</delay>"

def delayto(global_time,goal_time):
    return f"<delay>{goal_time-global_time}</delay>\n"

def HandleAlt(alt,T_dc,T_horizon_nominal,save=True):
    Important_dates_unsorted = set()
    log = {}
    res = ""
    for p in alt.Schedule:
        for idx,d in enumerate(p["T"]):
            printv(f"idx = {idx}, d = {d}")
            printv(f"   adding {d+T_dc} in Idu")
            Important_dates_unsorted.add(d+T_dc)

            if d+T_dc not in log : log[d+T_dc] = []
            log[d+T_dc].append((f"P{p['PID']}","start",p["P"][idx]))
            printv(f"   adding (P{p['PID']}, 'start', {p['P'][idx]} ) in log[{d+T_dc}]({log[d+T_dc]})")
            
            end = d+p["D"][idx]+T_dc
            printv(f"   adding {end} in Idu")
            Important_dates_unsorted.add(end)
            if end not in log : log[end] = []
            printv(f"   adding (P{p['PID']}, 'end', {p['P'][idx]} ) in log[{end}]({log[end]})")
            log[end].append((f"P{p['PID']}","end",p["P"][idx]))

    Important_dates = sorted(Important_dates_unsorted)
    prev = 0
    for i in Important_dates:

        printv(i,log[i])
    res+="""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<trace>"""
    for i in Important_dates:
        res+=delay(i-prev)
        for action in log[i]: # 2 loops for priority of exit over enter: possibly better if i sorted based on action type?
            if action[1] == "end" :
                res+=end_trans(i-prev,action[0])
        for action in log[i]:
            if action[1] == "start" :
                res+=start_trans(i,action[0],action[-1],i-prev)
        prev = i
    res+="</trace>"
    printv(res)
    if save:
        with open(args.filename.replace('.json',f'_{alt.ID}.trc'),'w') as f:
            f.write(res)
    return res
def main():
    alts = [DictObject(**alt) for alt in read_alts(args.filename)]
    T_horizon_nominal = 45
    T_dc = 100
    for alt in alts:
        print(alt.ID)
        HandleAlt(alt,T_dc,T_horizon_nominal)
        print("Done")
if __name__=="__main__":
    parser = argparse.ArgumentParser(
                    prog='Trace Generator',
                    description='Generate trace for TACPN from a given set of alternative schedules',
    )
    parser.add_argument('filename')           # positional argument
    parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag
    args = parser.parse_args()
    if args.verbose : VERBOSE = True
    main()

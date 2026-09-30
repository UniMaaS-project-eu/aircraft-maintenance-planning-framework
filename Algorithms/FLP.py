class task:
    def __init__(self,name,s,d,mapping):
        self.id = name
        self.s = int(s)
        self.d = int(d) 
        self.i = int(s) 
        self.map = mapping
    def schedule(self,i):
        self.i = i 
    def delay(self,x):
        self.i += x
    def __repr__(self):
        return f"{self.id}"

class schedule:
    def __init__(self,tasks,bo={}):
        self.tasks = tasks
        self.timezero = self.last_day()
        self.r2sim = {}
        self.sim2r = {}
        self.bo = bo
        self.truncated = False
        last = 0
        lasts = 0
        for t in range(self.last_day()+1):
            res = t
            for b in [b for b in self.bo if b<t ]:
                new_last = b+bo[b]
                if t<b+bo[b]:
                    res = b-(t-res)
                    break
                    
                else:
                    res -= bo[b]
            self.r2sim[t] = res
        for x,y in self.r2sim.items():
            self.sim2r[y]=x

    def flip_time(self):
        for t in self.tasks:
            t.i = self.timezero - t.i -t.d
            t.s = self.timezero - t.s -t.d
        bo = {}
        for b in self.bo:
            bo[self.timezero - b - self.bo[b]] = self.bo[b]
        self.bo = bo

            
    def last_day(self):
        max_d = 0
        for task in self.tasks:
            if task.i + task.d > max_d:
                max_d = task.i + task.d
        return int(max_d)
    def day(self,d):
        res = []
        for task in self.tasks:
            if task.i<=d<task.i+task.d:
                res.append(task)
        return res
    def trunc(self):
        if not self.truncated :
            for t in self.tasks:
                t.s = self.r2sim[t.s]
                t.i = self.r2sim[t.i]
    def restore(self):
        if not self.truncated :
            for t in self.tasks:
                if t.i in self.sim2r:
                    t.s = self.sim2r[t.s]
                    t.i = self.sim2r[t.i]
                elif t.i > max(self.sim2r):
                    diff =  self.sim2r[max(self.sim2r)]-max(self.sim2r)
                    t.s = self.sim2r[t.s]
                    t.i+=diff

    def apply_delays(self,flipped=False):
        for t in self.tasks:
            for b in self.bo:
                if flipped:
                    overlap = min(t.i,b) - max(t.i+t.d,b+self.bo[b])
                else:
                    overlap = min(t.i+t.d,b+self.bo[b])-max(t.i,b)  

                if overlap >0:
                    t.d += self.bo[b]
    def blackoutdays(self):
        res = []
        for b in self.bo:
            for i in range(b,b+self.bo[b]):
                res.append(i)
        return res
    def print(self,bohash=False):
        days = []
        for i in range(self.last_day()):
            days.append(self.day(i))

        flag = True
        print(self.tasks)
        task_id_length=max([len(t.id) for t in self.tasks])
        for i,d in enumerate(days):
            if len(d)!=0 or i in self.blackoutdays():
                flag = True
                if bohash:
                    if i in self.blackoutdays():
                        delimeter  = "="
                        print( f"{i}", delimeter.join([delimeter*task_id_length for x in self.tasks ]))
                    
                    else:
                        delimeter  = " "
                        print( f"{i}", delimeter.join([f"{x}" if x in d else delimeter*task_id_length for x in self.tasks ]))
                else:
                 delimeter  = f"=" if i  in self.blackoutdays() else " "
                 print( f"{i}", delimeter.join([f"{x}" if x in d else delimeter*task_id_length for x in self.tasks ]))
            elif flag:
                print(" ...")
                flag = False

def conflict(l,capacity):
    import itertools

    combinations = list(itertools.combinations(l, len(l)-capacity))
    actions = {}
    for comb in combinations:
        n = l.copy()
        for x in comb:
            n.remove(x)
        lasttoend = min(n, key=lambda p: p.i+p.d)
        actions[comb] = [abs(lasttoend.i+lasttoend.d - x.i)for x in comb]
    tomove = min(actions, key=lambda x:sum(actions[x])+sum(i.i-i.s for i in x))
    for x,y in zip(tomove,actions[tomove]):
        x.delay(y)
    return min(l, key=lambda p: p.i).i
    
def _solve(schedule,start,capacity):
    for d in range(start,schedule.last_day()):
        day = schedule.day(d)
        if len(day)>capacity:
            c_start = conflict(day,capacity)
            return(_solve(schedule,c_start,capacity))
    return schedule
def solve(sched,capacity):
    sched.trunc()
    sched.flip_time()
    _solve(sched,0,capacity)
    sched.flip_time()
    sched.restore()
    sched.apply_delays()

def flp_algo(alts,cap,bo_days): # Flight-level Planning Algorithm
    tasks_list = []

    for plane in alts:
        if len(alts[plane]) > 1:
            print("multiple alts selecting first")

        if len( alts[plane]) == 0 :
            continue
        tcpn = alts[plane][0]
        tmp=tcpn["wps"].copy()

        for i in tmp:
            tasks_list.append((plane,i))
    tasks = []
    if len(tasks_list) == 0:
        return [None]
    # timezero = 0
    # for _,i in tasks_list:
    #         if i['duration'] + i['timestamp'] > timezero :
    #             timezero =  i['duration'] + i['timestamp']    
    for plane,i in tasks_list:
            tasks.append(task(f"{plane}: {i['tasks']}",i['timestamp'],i['duration'],i['map']))
    # print(tasks)
    schd = schedule(tasks,bo=bo_days)

    # if printv():schd.print()

    solve(schd,cap)

    # schd.print(bohash=True)
    return schd
def list2tasks(l,map=None): # Converts boolean lists of task inclusion into lists of included tasks. E.g. [1,0,0,1] -> [t1,t4]
    res = []
    for idx,i in enumerate(l):
        if i ==1:
            if map:
                res.append(map[idx])
            else:
                res.append(f"t{idx+1}")
    return res
def tracegen_prepv2(sched): # Prepares input for the TACPN trace generation ( Aggregation and JSON serialization) 
# def tracegen_prepv2(sched_l): # Prepares input for the TACPN trace generation ( Aggregation and JSON serialization) 
    # input_json = []
    # for idx,sched in enumerate(sched_l):
        # alt = {"ID":f"Alt{idx+1}","Schedule":[]}
        alt = {"Schedule":[]}
        timezero = sched.timezero
        for project in sched.tasks:
            flag = False
            planeid = project.id.split(': ')[0]
            projects = eval(project.id.split(': ')[1])
            duration = project.d
            date = project.i 
            for plane in alt["Schedule"]:
                if planeid == plane["PID"]:
                    plane["P"].append(list2tasks(projects,project.map))
                    plane["T"].append(date)
                    plane["D"].append(duration)
                    flag = True
                    break
            if not flag:
                alt["Schedule"].append({
                    "PID" : planeid,
                    "P":[list2tasks(projects,project.map)],
                    "T":[date],
                    "D":[duration]   

                })
    #     input_json.append(alt)
    # return input_json   
        return alt
if __name__ == "__main__":
    import json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filename', help='file containing alp result for fleet (e.g. output of alp.py)',required=True)
    parser.add_argument('-d','--data', help='file containing initial data (e.g. test.json): used ONLY for hangar capacity and blackout days')
    parser.add_argument('-c','--capacity', help='capacity : overrides value set in data file if provided',type=int)
    parser.add_argument('-b','--blackout_days', help='blackout-days provided either as list (e.g. [1,23,24, 35]) or data-duration pairs (e.g. {"1":1, "23":2, "35":1})')

    parser.add_argument('-o','--outfile', help='prefix for output file (defaults to \'out\')',default="out")
    args = parser.parse_args()
    bo_days = {}
    capacity = 1
    if args.data:
        data = json.load(open(args.data,'r'))
        if "blackout-durations" in data:
            bo_days= {i:j for i,j in zip(data["blackout-days"],data["blackout-durations"])}
        else:bo_days= {i:1 for i in data["blackout-days"]}
        capacity = data["hangar_capacity"]
    if blackout_days := args.blackout_days:
        bos = json.loads(blackout_days)
        if type(bos) == list:
            bo_days= {i:1 for i in bos}
        if type(bos) == dict:
            bo_days = {int(i):j for i,j in bos.items()}
    if args.capacity :
        capacity = args.capacity
    alts = json.load(open(args.filename,'r'))
    json.dump(tracegen_prepv2(flp_algo(alts,capacity,bo_days)),open(args.outfile+"_flp_schedule.json",'w'),indent=4)
class task:
    def __init__(self,name,s,d):
        self.id = name
        self.s = s
        self.d = d 
        self.i = s 
    def schedule(self,i):
        self.i = i 
    def delay(self,x):
        self.i += x
    def __repr__(self):
        return f"{self.id}"

class schedule:
    def __init__(self,tasks,timezero = 0,bo={}):
        self.tasks = tasks
        self.timezero = timezero
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
        return max_d
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
                    t.d += overlap
    def print(self):
        days = []
        for i in range(self.last_day()):
            days.append(self.day(i))

        flag = True
        for i,d in enumerate(days):
            if len(d)!=0 or i in self.bo:
                flag = True
                asterisc = f"({self.bo[i]})" if i  in self.bo else ""
                print( f"{i}{asterisc}", " ".join([f"{x}" if x in d else "     " for x in self.tasks ]))
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

if __name__ == "__main__":
    tasks = []
    for i,(x,y) in enumerate([(25,7),(25,6)]):
        tasks.append(task(f"task{i}",x,y))
    schd = schedule(tasks,timezero = 32,bo={21:2,30:1})
    schd.print()
    print("\n\n")
    solve(schd,1)

    schd.print()

    

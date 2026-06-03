from cpnpy.cpn.cpn_imp import CPN, Place, Transition, Arc, Marking, EvaluationContext
from cpnpy.cpn.colorsets import ColorSetParser
from argparse import ArgumentParser
import json

# Create CPN
cpn = CPN()


# Define color sets
cs_defs = """
colset INT = int timed;
colset TIME = time;
colset STRING = string;

colset task = product(product(INT, STRING), product(INT, INT));
colset airplane = list task timed;

colset flight = product( STRING, product(INT, INT)) timed;

colset spec_element = product( INT, product(INT, INT));
colset spec = product(list spec_element, list INT);

colset log = STRING;
colset tok = STRING timed;
colset wg = product(STRING , INT) timed;

"""
parser = ColorSetParser()
colorsets = parser.parse_definitions(cs_defs)
airplane =colorsets["airplane"]
flight =colorsets["flight"]
spec =colorsets["spec"]
tok =colorsets["tok"]
wg =colorsets["wg"]
log =colorsets["log"]


# Evaluation context with a user-defined function
user_code = """
import math
import json
grouping = json.load(open('curr_grouping.json','r'))


def grouping2vec(a,s):
    grouping = json.load(open('curr_grouping.json','r'))
    th1_vec=TH1(a,s)
    if any(TH1(a,s)):
        dom = a[th1_vec.index(True)][0]
    else:
        dom = 2
    res = []
    for i in a:
        if dom != 2 and i[0] in grouping[dom]: res.append(True)
        else:res.append(False)
    return res
def th1(a,s):
    return any(i>=(j) for i,j in zip(a[1:],s[1:]))
def th2(a,s):
    return any(i>0.1*(j) for i,j in zip(a[1:],s[1:]))
def th_error(a,s):
    return any([i>=j for i,j in zip(a[1:],s[1:])])
def next_grouping(a,s,gr):
    deadline = []
    labels = []
    for i,j in zip(a,s):
        if i[0] in gr:
            deadline.append(min([(y-x) for x,y in zip(i[1:],j[1:])]))
            labels.append(i[0])
    deadline_sorted, labels_sorted = zip(*sorted(zip(deadline, labels)))
    return labels_sorted[0]
def TH1(a,s):
    grouping = json.load(open('curr_grouping.json','r'))
    next = next_grouping(a,s,grouping)
    # res = [th1(i,j) if (i[0] == next) else False for i,j in zip(a,s) ]
    # if any(res): print(res)
    return [th1(i,j) if (i[0] == next) else False for i,j in zip(a,s) ]
def TH2(a,s):
    return grouping2vec(a,s)

    #return [th2(i,j) for i,j in zip(a,s)]
def e(a,s):
    return any(TH1(a,s[0]))

def add(x,y):
    # normalize inputs as tuples
    x = tuple(x)
    y = tuple(y)
    return tuple([i+j for i,j in zip(x,y)])

def fl(a,f):
    a = [tuple(i) for i in a]
    f = tuple(f)
    return tuple([(i[0],) + add(f[1:], i[1:-1]) + (i[-1]+1,) for i in a])

def reset(a,s,d):
    a = [tuple(i) for i in a]
    s = [tuple(i) for i in s]
    return tuple([
        (i[0],0,0,0) if th else tuple(i[:-1]) + (i[-1]+d,)
        for i,th in zip(a,TH2(a,s))
    ])

def expire(a,s):
    a = [tuple(i) for i in a]
    s = [tuple(i) for i in s[0]]
    return any([th_error(i,j) for i,j in zip(a,s)])

def Duration(th,d):
    return  sum([i*j for i,j in zip(th,d)])
"""
context = EvaluationContext(user_code=user_code)


# PLACES
active_fleet = Place("active_fleet", airplane)
cpn.add_place(active_fleet)

flights = Place("flights", flight)
cpn.add_place(flights)

specs = Place("specs", spec)
cpn.add_place(specs)

workgroup = Place("workgroup", wg)
cpn.add_place(workgroup)

logs = Place("logs", log)
cpn.add_place(logs)

unsafe = Place("unsafe", tok )
cpn.add_place(unsafe)

# svc_days = Place("svc_days", tok )
# cpn.add_place(svc_days)

blackout_periods = Place("blackout_periods", wg )
cpn.add_place(blackout_periods)

svc_delay = Place("svc_delay", wg )
cpn.add_place(svc_delay)

in_svc = Place("in_svc", tok )
cpn.add_place(in_svc)

under_maintenance = Place("under_maintenance", airplane )
cpn.add_place(under_maintenance)

# TRANSITIONS
fly = Transition("fly", variables= ["a","f","s","w"], guard="(not e(a,s) or (e(a,s) and w[-1] <= 0)) and not expire(a,s)",transition_delay=0)
cpn.add_transition(fly)

maintenance = Transition("maintenance", variables=["a","w","s"],guard="e(a,s) and w[-1]>0",transition_delay=0)
cpn.add_transition(maintenance)

expire = Transition("expire", variables=["a","s"],guard="expire(a,s) ",transition_delay=0)
cpn.add_transition(expire)

cleanup_wg = Transition("cleanup_wg", variables=["w","w0"],guard="w0[-1] <= w[-1]")
cpn.add_transition(cleanup_wg)

cleanupfl = Transition("cleanupfl", variables= ["f"])
cpn.add_transition(cleanupfl)

block_maintenance = Transition("block_maintenance", variables= ["b","w"])
cpn.add_transition(block_maintenance)

delay_maintenance = Transition("delay_maintenance", variables= ["b","x","t"])
cpn.add_transition(delay_maintenance)

exit_maintenance = Transition("exit_maintenance", variables= ["a","x","t"])
cpn.add_transition(exit_maintenance)

# Arcs
am = Arc(active_fleet, maintenance, "[a]")
cpn.add_arc(am)

# ma = Arc(maintenance, active_fleet, "[reset(a,s[0],Duration(TH2(a,s[0]),s[1]))] @+Duration(TH2(a,s[0]),s[1])")
# cpn.add_arc(ma)

sm = Arc(specs,maintenance,"[s]")
cpn.add_arc(sm)

ms = Arc(maintenance,specs,"[s]")
cpn.add_arc(ms)

af = Arc(active_fleet,fly,"[a]")
cpn.add_arc(af)

fa = Arc(fly,active_fleet,"[fl(a,f)] @+1")
cpn.add_arc(fa)

ff = Arc(flights,fly,"[f]")
cpn.add_arc(ff)

wm = Arc(workgroup,maintenance,"[w]")
cpn.add_arc(wm)

mw = Arc(maintenance,workgroup,"[(w[0],w[1]-1)] @+Duration(TH2(a,s[0]),s[1])")
cpn.add_arc(mw)

wf = Arc(workgroup,fly,"[w]")
cpn.add_arc(wf)

fw = Arc(fly,workgroup,"[w]")
cpn.add_arc(fw)

ml = Arc(maintenance,logs,"[f'Plane: {a}, Tasks: {TH2(a,s[0])}, Duration: {Duration(TH2(a,s[0]),s[1])}']")
cpn.add_arc(ml)

sf = Arc(specs,fly,"[s]")
cpn.add_arc(sf)

fs = Arc(fly,specs,"[s]")
cpn.add_arc(fs)



ae = Arc(active_fleet,expire,"[a]")
cpn.add_arc(ae)

se = Arc(specs,expire,"[s]")
cpn.add_arc(se)

eu = Arc(expire,unsafe,"'☠️'")
cpn.add_arc(eu)



fc = Arc(flights,cleanupfl,"[f]")
cpn.add_arc(fc)

# sc = Arc(svc_days,cleanupfl,"[t]")
# cpn.add_arc(sc)
sc = Arc(active_fleet,cleanupfl,"INHIBITOR")
cpn.add_arc(sc)
mc = Arc(under_maintenance,cleanupfl,"INHIBITOR")
cpn.add_arc(mc)
# msd = Arc(maintenance,svc_days,"['❎']*Duration(TH2(a,s[0]),s[1])")
# cpn.add_arc(msd)

wc = Arc(workgroup,cleanup_wg,"[w,w0]")
cpn.add_arc(wc)

cw = Arc(cleanup_wg,workgroup,"[w]")
cpn.add_arc(cw)

wbm = Arc(workgroup,block_maintenance,"[w]")
cpn.add_arc(wbm)

bmw = Arc(block_maintenance,workgroup,"[(w[0],0)]")
cpn.add_arc(bmw)

bmw2 = Arc(block_maintenance,workgroup,"[w]@+b[-1]")
cpn.add_arc(bmw2)

bbm = Arc(blackout_periods,block_maintenance,"[b]")
cpn.add_arc(bbm)

bdm = Arc(blackout_periods,delay_maintenance,"[b]")
cpn.add_arc(bdm)

sddm = Arc(svc_delay,delay_maintenance,"[x]")
cpn.add_arc(sddm)

dmsd = Arc(delay_maintenance,svc_delay,"[x+b[-1]]")
cpn.add_arc(dmsd)

isdm = Arc(in_svc,delay_maintenance,"[t]")
cpn.add_arc(isdm)

dmis = Arc(delay_maintenance,in_svc,"[t]")
cpn.add_arc(dmis)

sdem = Arc(svc_delay,exit_maintenance,"[x]")
cpn.add_arc(sdem)

emsd = Arc(exit_maintenance,svc_delay,"[0]")
cpn.add_arc(emsd)

isem = Arc(in_svc,exit_maintenance,"[t]")
cpn.add_arc(isem)

mis = Arc(maintenance,in_svc,"['🔧']")
cpn.add_arc(mis)

umem = Arc(under_maintenance,exit_maintenance,"[a]")
cpn.add_arc(umem)

mum = Arc(maintenance,under_maintenance,"[reset(a,s[0],Duration(TH2(a,s[0]),s[1]))] @+Duration(TH2(a,s[0]),s[1])")
cpn.add_arc(mum)

ema = Arc(exit_maintenance,active_fleet,"[a]@+x")
cpn.add_arc(ema)

# emsd = Arc(exit_maintenance,svc_days,"['❎']*x")
# cpn.add_arc(emsd)

in1 = Arc(in_svc,block_maintenance,"INHIBITOR")
cpn.add_arc(in1)


in2 = Arc(blackout_periods,exit_maintenance,"INHIBITOR")
cpn.add_arc(in2)

in3 = Arc(blackout_periods,maintenance,"INHIBITOR")
cpn.add_arc(in3)


# Generate Initial Marking

marking = Marking()
# schedule =[(f"#{i}",1,2) for i in range(20)]
# marking.set_tokens("active_fleet", [(('t1',0, 0, 0),('t2',0, 0, 0),('t3',0, 0, 0))])  
# marking.set_tokens("flights", schedule,timestamps=(range(len(schedule))))  
# marking.set_tokens("specs", [((('t1',5,15,20),('t2',6,13,20),('t3',20,30,50)),(4,4,9))])  
# marking.set_tokens("workgroup", [('2025',2),('2026',2)], timestamps=[0,25])  


parser = ArgumentParser()
parser.add_argument('mode')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-o', '--file')
parser.add_argument('-j', '--no_json', action='store_true')
parser.add_argument('-i', '--no_img', action='store_true')
parser.add_argument('-x', '--no_nx', action='store_true')
parser.add_argument('--interactive_viewer', action='store_true')
parser.add_argument('--nx_draw', action='store_true')
parser.add_argument('--nx_draw_pruned', action='store_true')
parser.add_argument('--fullmarking', action='store_true')
parser.add_argument('-q', '--quiet', action='store_true')
parser.add_argument('-g', '--grouping')
# parser.add_argument('-f', '--filename')

args = parser.parse_args()


from util import prettymarking,json2marking,custom_marking

file = args.file if args.file is not None else "dataset_initial_marking.json"
from json import load
mj = load(open(file,"r"))
mj = json2marking(mj)
for place in mj:
    marking.set_tokens(place,mj[place]["tokens"],timestamps=mj[place]["timestamps"])
    
marking.set_tokens("svc_delay",[0])
# schedule =[(f"#{i}",1,2) for i in range(365)]
# marking.set_tokens("flights", schedule,timestamps=(range(len(schedule))))  
if args.grouping :
    import os
    os.system(f"cp {args.grouping} curr_grouping.json")
gfile = "curr_grouping.json"


if not args.no_json:
    from cpnpy.cpn.exporter import export_cpn_to_json
    exported_json = export_cpn_to_json(cpn, marking, context, "vp1.json", "usercode_vp1.py")
    if not args.quiet:print ("exporeded JSON")


if not args.no_img:
    from cpnpy.visualization.visualizer import CPNGraphViz
    viz = CPNGraphViz().apply(cpn, marking, format="png")
    path = viz.save("vp1")
    if not args.quiet:print("Saved vizualisation to:", path)

# if not args.quiet:
#     print("Initial marking:")
#     print(prettymarking(marking))  

if args.mode == "manual":
    def sequeun(cpn,marking,context):
        transitions = cpn.transitions
        for t in transitions:
            print (t.name,end=' : ')
            if cpn.is_enabled(t,marking,context):
                print("OK",end = '')
                cpn.fire_transition(t,marking,context)
            print("\n")
        cpn.advance_global_clock(marking)
        print (f"time:{marking.global_clock}\n marking:{custom_marking(marking,args)}")
        if not args.no_img:
            viz = CPNGraphViz().apply(cpn, marking, format="png")
            path = viz.save("vizout")

    prev_clock = None
    while (input("?\r") != 'x' and prev_clock != marking.global_clock):
        prev_clock = marking.global_clock
        print("\n\n")

        sequeun(cpn,marking,context)
        
    if len(marking.get_multiset("unsafe").tokens) != 0:
        print("UNSAFE") 
    else:print("SAFE") 

if args.mode == "sim":
    def sequeun(cpn,marking,context):
        transitions = cpn.transitions
        print(f"Firing ... ",end = '\r')
        for t in transitions:
            if cpn.is_enabled(t,marking,context):
                cpn.fire_transition(t,marking,context)
        cpn.advance_global_clock(marking)
        print(f"Visualising ... ",end = '\r')
        if args.verbose:print (f"time:{marking.global_clock}\n marking:{prettymarking(marking)}")
        if not args.no_img:
            viz = CPNGraphViz().apply(cpn, marking, format="png")
            path = viz.save("vizout")
        print(f"                                                        ",end = '\r')
        

    prev_clock = None
    if not args.quiet:print("Running....")
    while (prev_clock != marking.global_clock):
        prev_clock = marking.global_clock
        if args.verbose:print("\n\n")
        print([i.name for i in cpn.transitions if cpn.is_enabled(i,marking,context)])
        sequeun(cpn,marking,context)
        
    if not args.quiet:
        print("Final marking:")
        print(prettymarking(marking)) 
    # else:
    #     for tok in marking.get_multiset("logs").tokens:
    #         print (tok)
    if len(marking.get_multiset("unsafe").tokens) != 0:
        print("UNSAFE") 
    else:print("SAFE") 

if args.mode == "statespace":
    if args.verbose:print ("STATE SPACE")
    from cpnpy.analysis.analyzer import StateSpaceAnalyzer 
    if args.verbose:print ("creating analyzer ...")  

    analyzer = StateSpaceAnalyzer(cpn, marking, context) 
    if args.verbose:print ("OK")  
    
    if args.verbose:print ("analyzing ...")  
    report = analyzer.summarize()
    if args.verbose:print ("OK")  

    print("=== State Space Report ===")
    for key, val in report.items():
        print(f"{key}: {val}")
    

    RG = analyzer.RG
    if (not args.no_nx )or args.interactive_viewer:
        from pickle import dump
        dump(RG,open("vp1RG.pkl","wb"))    
    if (args.interactive_viewer):
        from util import interactive_viewer as IV
        IV(RG)
    if (args.nx_draw):
        from util import nx_draw as draw
        # from util import nx_draw as draw
        draw(RG,with_t_labels=True)
    terminals = [node for node in RG.nodes if RG.out_degree(node) == 0]
    for terminal in terminals:
        safe = True
        for t in terminal[1]:  
            if t[0] == "unsafe" and t[1][0][0] == "☠️":
                safe = False
                break
        print( "SAFE" if safe else "UNSAFE")
        Plane = "Plane"
        Duration = "Duration"
        Tasks = "Tasks"
        for t in terminal[1]: 
            if t[0] == "logs":
                for log in t[1]:
                    marking = eval("{"+log[0].replace("True","1").replace("False","0")+"}")
                    timestamp = log[-1]
                    print ("{"+f" tasks: {marking['Tasks']}, duration : {marking['Duration']} , timestamp : {timestamp} "+"}")

if args.mode == "res":

    if args.verbose:print ("STATE SPACE")
    from cpnpy.analysis.analyzer import StateSpaceAnalyzer 
    if args.verbose:print ("creating analyzer ...")  

    analyzer = StateSpaceAnalyzer(cpn, marking, context) 
    if args.verbose:print ("OK")  
    
    if args.verbose:print ("analyzing ...")  
    report = analyzer.summarize()
    if args.verbose:print ("OK")  



    RG = analyzer.RG
    if (not args.no_nx )or args.interactive_viewer:
        from pickle import dump
        dump(RG,open("vp1RG.pkl","wb"))    
    if (args.interactive_viewer):
        from util import interactive_viewer as IV
        IV(RG)
    if (args.nx_draw):
        from util import nx_draw as draw
        if args.verbose:print("visualising....")
        draw(RG,with_t_labels=True,filename=f"RG/{file.split('/')[-1].replace('.json','')}")
    if (args.nx_draw_pruned):
        from util import nx_draw_pruned as draw
        if args.verbose:print("visualising....")
        draw(RG,with_t_labels=True,filename=f"RG/{file.split('/')[-1].replace('.json','')}")
    terminals = [node for node in RG.nodes if RG.out_degree(node) == 0]
    print("[")
    for terminal in terminals:
        print(" {")
        safe = True
        for t in terminal[1]:  
            if t[0] == "unsafe" and t[1][0][0] == "☠️":
                safe = False
                break
        print( "    status : "+("'SAFE'" if safe else "'UNSAFE'" )+",")
        Plane = "Plane"
        Duration = "Duration"
        Tasks = "Tasks"
        for t in terminal[1]: 
            if t[0] == "logs":
                print("    wps:[")
                for log in t[1]:
                    marking = eval("{"+log[0].replace("True","1").replace("False","0")+"}")
                    timestamp = log[-1]
                    print ("        {"+f" 'tasks': {marking['Tasks']}, 'duration' : {marking['Duration']} , 'timestamp' : {timestamp} "+"},")
                print("     ]")
        print(" },")
    print("]")

if args.mode == "pipeline":

    if args.verbose:print ("STATE SPACE")
    from cpnpy.analysis.analyzer import StateSpaceAnalyzer 
    if args.verbose:print ("creating analyzer ...")  

    analyzer = StateSpaceAnalyzer(cpn, marking, context) 
    if args.verbose:print ("OK")  
    
    if args.verbose:print ("analyzing ...")  
    report = analyzer.summarize()
    if args.verbose:print ("OK")  



    RG = analyzer.RG
    if (not args.no_nx )or args.interactive_viewer:
        from pickle import dump
        dump(RG,open("vp1RG.pkl","wb"))    
    if (args.interactive_viewer):
        from util import interactive_viewer as IV
        IV(RG)
    if (args.nx_draw):
        from util import nx_draw as draw
        if args.verbose:print("visualising....")
        draw(RG,with_t_labels=True,filename=f"RG/{file.split('/')[-1].replace('.json','')}")
    if (args.nx_draw_pruned):
        from util import nx_draw_pruned as draw
        if args.verbose:print("visualising....")
        draw(RG,with_t_labels=True,filename=f"RG/{file.split('/')[-1].replace('.json','')}")
    terminals = [node for node in RG.nodes if RG.out_degree(node) == 0]
    # print("[")
    terminals_res = []
    for terminal in terminals:
               
        # print(" {")
        terminal_res = {}
        safe = True
        for t in terminal[1]:  
            if t[0] == "unsafe" and t[1][0][0] == "☠️":
                safe = False
                break
        # print( "    status : "+('"SAFE"' if safe else '"UNSAFE"' )+",")
        terminal_res["status"] = "SAFE" if safe else "UNSAFE"
        Plane = "Plane"
        Duration = "Duration"
        Tasks = "Tasks"
        wps = []
        for t in terminal[1]: 
            if t[0] == "logs":
                
                # print("    wps:[")
                for log in t[1]:
                    marking = eval("{"+log[0].replace("True","1").replace("False","0")+"}")
                    timestamp = log[-1]
                    # print ("        {"+f" 'tasks': {marking['Tasks']}, 'duration' : {marking['Duration']} , 'timestamp' : {timestamp} "+"},")
                    wps.append({"tasks":marking['Tasks'],"duration":marking['Duration'],"timestamp":timestamp})
                    # print(wps[-1])
                # print("     ]")
        terminal_res["wps"] =wps
        # print(" },")
        terminals_res.append(terminal_res)
    # print("]")
    print(json.dumps(terminals_res))
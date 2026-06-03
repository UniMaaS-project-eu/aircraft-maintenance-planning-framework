from cpnpy.cpn.cpn_imp import CPN, Place, Transition, Arc, Marking, EvaluationContext
from cpnpy.cpn.colorsets import ColorSetParser
from argparse import ArgumentParser
print("APLOMA")

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
colset wp = product(STRING , INT) timed;
"""
parser = ColorSetParser()
colorsets = parser.parse_definitions(cs_defs)
tok =colorsets["tok"]
wp =colorsets["wp"]
log =colorsets["log"]


# Evaluation context with a user-defined function
user_code = """
"""
context = EvaluationContext(user_code=user_code)


# PLACES
pending = Place("pending", wp)
cpn.add_place(pending)
maintenance = Place("maintenance", wp)
cpn.add_place(maintenance)
logs = Place("logs", log)
cpn.add_place(logs)
capacity = Place("capacity", tok)
cpn.add_place(capacity)
unsafe = Place("unsafe", tok)
cpn.add_place(unsafe)

# TRANSITIONS

execute = Transition("execute", variables= ["w","c"])
cpn.add_transition(execute)
end = Transition("end", variables= ["w"])
cpn.add_transition(end)
expire = Transition("expire", variables= ["w"])
cpn.add_transition(expire)
reschedule = Transition("reschedule", variables= ["w"])
cpn.add_transition(reschedule)
# Arcs
cpn.add_arc(Arc(pending, execute, "[w]"))
cpn.add_arc(Arc(pending, reschedule, "[w]"))
cpn.add_arc(Arc(reschedule, pending, "[w]@+1"))
cpn.add_arc(Arc(capacity, execute, "[c]"))
cpn.add_arc(Arc(execute, maintenance, "[w]@+w[-1]"))
cpn.add_arc(Arc(end, capacity, "['c']"))
cpn.add_arc(Arc(maintenance, end, "[w]"))
cpn.add_arc(Arc(capacity, reschedule, "INHIBITOR"))
cpn.add_arc(Arc(execute, logs, "[f'{w}']"))


# Generate Initial Marking
import datagen 
from sys import argv
import os
# print(argv[-1])
planes =  [p for p in argv[1:] if os.path.isfile(p)]
work_packages , optimal = datagen.datagen(planes)
marking = Marking()
marking.set_tokens("pending", work_packages,timestamps=optimal)  
marking.set_tokens("capacity", ['c']*2)  


parser = ArgumentParser()
# parser.add_argument('mode')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-o', '--file')
parser.add_argument('-j', '--no_json', action='store_true')
parser.add_argument('-i', '--no_img', action='store_true')
parser.add_argument('-x', '--no_nx', action='store_true')
parser.add_argument('--interactive_viewer', action='store_true')
parser.add_argument('--nx_draw', action='store_true')
parser.add_argument('--fullmarking', action='store_true')
parser.add_argument('-q', '--quiet', action='store_true')
parser.add_argument("paths", nargs="+", help="Directories or globbed paths")
args = parser.parse_args()


from util import prettymarking,json2marking,custom_marking

# file = args.file if args.file is not None else "dataset_initial_marking.json"
# from json import load
# mj = load(open(file,"r"))
# mj = json2marking(mj)
# for place in mj:
#     marking.set_tokens(place,mj[place]["tokens"],timestamps=mj[place]["timestamps"])
# marking.set_tokens("svc_delay",[0])
# # schedule =[(f"#{i}",1,2) for i in range(365)]
# # marking.set_tokens("flights", schedule,timestamps=(range(len(schedule))))  


if not args.no_json:
    from cpnpy.cpn.exporter import export_cpn_to_json
    exported_json = export_cpn_to_json(cpn, marking, context, "vp1.json", "usercode_vp1.py")
    if not args.quiet:print ("exporeded JSON")


if not args.no_img:
    from cpnpy.visualization.visualizer import CPNGraphViz
    viz = CPNGraphViz().apply(cpn, marking, format="png")
    path = viz.save("vp1")
    if not args.quiet:print("Saved vizualisation to:", path)

if not args.quiet:
    print("Initial marking:")
    print(prettymarking(marking))  


if args.verbose:print ("STATE SPACE")
from cpnpy.analysis.analyzer import StateSpaceAnalyzer 
if args.verbose:print ("creating analyzer ...")  

analyzer = StateSpaceAnalyzer(cpn, marking, context) 
if args.verbose:print ("OK")  
    
if args.verbose:print ("analyzing ...")  
report = analyzer.summarize()
if args.verbose:print ("OK")  

# print("=== State Space Report ===")
# for key, val in report.items():
#     print(f"{key}: {val}")
    

RG = analyzer.RG
if (not args.no_nx )or args.interactive_viewer:
    from pickle import dump
    dump(RG,open("vp1RG.pkl","wb"))    

if (args.nx_draw):
    from util import nx_draw as draw
    draw(RG)
terminals = [node for node in RG.nodes if RG.out_degree(node) == 0]
results = []
for terminal in terminals:
    for t in terminal[1]: 
        if t[0] == "logs":
            datum = {}
            for log in t[1]:
                datum[eval(log[0])[0]] = log[-1]
            # print(datum)
            results.append([datum[key] for key in sorted(datum.keys(), reverse=False)])
minval = 0
minidx = results[0]
for r in results:
    val = sum(j-i for i,j in zip(r,optimal))
    if val < minval:
        minval = val
        minidx = r
sortedresults = sorted(results,key=lambda x : sum(i-j for i,j in zip(x,optimal)))
print("RESULTS(sorted):")
print (sortedresults)
# print (sortedresults[0])
# print (f"optimal :{optimal} vs given : {sortedresults[0]}")


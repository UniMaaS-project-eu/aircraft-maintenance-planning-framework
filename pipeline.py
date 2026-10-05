from os import system 
from os.path import isfile
def grouping(filename,prefix):
    system(f"python Algorithms/groupingv2.py -f {filename} -o {prefix}") 
    # result = run(["python", "Algorithms/groupingv2.py","-f",filename,"-o",prefix],capture_output=True, text=True) 
    # print (result.stderr)

def alp(filename,prefix):
    grouping_file = prefix+"_grouping.json"
    if not isfile(grouping_file):
        grouping(filename,prefix)
    system(f"python TCPN/alp.py -f {filename} -g {grouping_file} -o {prefix} -i") 
    # result = run(["python", "TCPN/alp.py","-f",filename,"-g",grouping_file,"-o",prefix],capture_output=True, text=True) 
    # print (result.stderr)
def flp(filename,prefix):
    alp_file = prefix+"_fleet_alp_res.json"
    if not isfile(alp_file):
        alp(filename,prefix)
    system(f"python Algorithms/FLP.py -f {alp_file} -d {filename} -o {prefix}") 
    # result = run(["python", "Algorithms/FLP.py","-f",alp_file,"-d",filename,"-o",prefix],capture_output=True, text=True) 
    # print (result.stderr)
def tacpngen(filename,prefix):
    flp_file = prefix+"_flp_schedule.json"
    if not isfile(flp_file):
        flp(filename,prefix)
    system(f"python TACPN/tacpn.py -s {flp_file } -d {filename} -o {prefix}") 
    # result = run(["python", "TACPN/tacpn.py","-s",flp_file,"-d",filename,"-o",prefix],capture_output=True, text=True) 
    # print (result.stderr)   
def tacpn(filename,prefix):
    config_file = prefix+"_tacpn_config.json"
    if not isfile(config_file):
        tacpngen(filename,prefix)
    system(f"python TACPN/TACPN_generator/tacpn_generator_aegean.py {config_file}") 
    # result = run(["python", "TACPN/TACPN_generator/tacpn_generator_aegean.py",config_file],capture_output=True, text=True) 
    # print (result.stderr)  
def tracegen(filename,prefix):
    config_file = prefix+"_flp_schedule.json"
    if not isfile(config_file):
        flp(filename,prefix)
    system(f"python TACPN/Trace_generator/trace_gen_zerotimes.py {config_file} -d {filename}") 
    # result = run(["python", "TACPN/TACPN_generator/tacpn_generator_aegean.py",config_file],capture_output=True, text=True) 
    # print (result.stderr)  

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filename', help='file containing initial data (e.g. test.json)',required=True)
    parser.add_argument('-o','--outfile', help='prefix for output files (defaults to \'out\')',default="out")
    parser.add_argument('--grouping', help='run grouping ',action='store_true')
    parser.add_argument('--alp', help='run alp(tcpn) ',action='store_true')
    parser.add_argument('--flp', help='run flp ',action='store_true')
    parser.add_argument('--tacpngen', help='run tacpn config generation ',action='store_true')
    parser.add_argument('--tacpn', help='run tacpn generation ',action='store_true')
    parser.add_argument('--tracegen', help='run tacpn trace generation ',action='store_true')
    parser.add_argument('-a','--all', help='run whole pipeline ',action='store_true')
    
    args = parser.parse_args()
    if args.grouping:
        grouping(filename=args.filename,prefix=args.outfile)
    if args.alp:
        alp(filename=args.filename,prefix=args.outfile)
    if args.flp:
        flp(filename=args.filename,prefix=args.outfile)
    if args.tacpngen:
        tacpngen(filename=args.filename,prefix=args.outfile)   
    if args.tracegen:
        tracegen(filename=args.filename,prefix=args.outfile)
    if args.tacpn or args.all:
        tacpn(filename=args.filename,prefix=args.outfile)
    
    print("Done")
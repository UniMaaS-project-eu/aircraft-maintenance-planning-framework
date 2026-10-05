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


def render_gantt(
    schedule_data,
    title: str = "Schedule",
    height_per_aircraft: int = 55,
    show_task_labels: bool = False,
    ) :
    import plotly.graph_objects as go
    import plotly.colors as pc
    schedule = schedule_data.get("Schedule", [])

    if not isinstance(schedule, list):
        raise ValueError("'Schedule' must be a list.")

    # ---------------------------------------------------------------
    # Colors
    # ---------------------------------------------------------------

    pids = [item["PID"] for item in schedule]

    palette = (
        pc.qualitative.Plotly
        + pc.qualitative.D3
        + pc.qualitative.Set3
        + pc.qualitative.Safe
    )

    pid_colors = {
        pid: palette[i % len(palette)]
        for i, pid in enumerate(pids)
    }

    fig = go.Figure()

    # ---------------------------------------------------------------
    # Add blocks
    # ---------------------------------------------------------------

    for item in schedule:

        pid = item["PID"]

        P = item.get("P", [])
        T = item.get("T", [])
        D = item.get("D", [])

        if not (len(P) == len(T) == len(D)):
            raise ValueError(
                f"{pid}: P, T and D must have the same length. "
                f"Got P={len(P)}, T={len(T)}, D={len(D)}."
            )

        for i, (tasks, start, duration) in enumerate(zip(P, T, D)):

            if isinstance(tasks, list):
                task_list = tasks
            else:
                task_list = [tasks]

            # -------------------------------------------------------
            # Store the P IDs directly in customdata.
            #
            # This is important because plotly_click will give us
            # customdata for the clicked block.
            # -------------------------------------------------------
            task_str = "\n".join(
                task
                for task in task_list
            ) 

            fig.add_trace(
                go.Bar(
                    x=[duration],
                    y=[pid],
                    base=[start],
                    orientation="h",

                    width=1,

                    marker=dict(
                        color=pid_colors[pid],
                        line=dict(
                            color="rgba(255,255,255,0.8)",
                            width=1,
                        ),
                    ),

                    text=[
                        str(task_list[0])
                        if show_task_labels and len(task_list) == 1
                        else (
                            f"{len(task_list)} tasks"
                            if show_task_labels
                            else ""
                        )
                    ],

                    textposition="inside",
                    # Everything needed when this block is clicked.
                    customdata=[[
                        pid,
                        i,
                        start,
                        duration,
                        task_str,
                    ]],

                    # Hover is deliberately minimal.
                    # The actual information is shown on CLICK.
                    hovertemplate=(
                        "<br>%{y}"
                        "<br>Start: %{base}"
                        "<br>Duration: %{customdata[3]}"
                        "<br>End: %{x}"
                        # "<br>%{customdata[4]}"
                        "<extra></extra>"
                    ),

                    showlegend=False,
                )
            )

    # ---------------------------------------------------------------
    # Layout
    # ---------------------------------------------------------------

    fig.update_layout(
        title=title,

        height=max(
            250,
            len(schedule) * height_per_aircraft
        ),

        barmode="overlay",
        bargap=0,

        clickmode="event+select",

        xaxis=dict(
            title="Time",
            showgrid=True,
            zeroline=True,
        ),

        yaxis=dict(
            title="PID",
            type="category",
            categoryorder="array",
            categoryarray=pids,
            autorange="reversed",
        ),

        plot_bgcolor="white",

        margin=dict(
            l=120,
            r=40,
            t=70,
            b=60,
        ),
    )

    return fig


def render(filename,prefix):
    import json

    config_file = prefix+"_flp_schedule.json"
    if not isfile(config_file):
        flp(filename,prefix)
    schedule = json.load(open(config_file,'r'))
    render_gantt(schedule,show_task_labels=True).show()   


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
    parser.add_argument('--render', help='render flp output using plottly',action='store_true')
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
    if args.tracegen or args.all:
        tracegen(filename=args.filename,prefix=args.outfile)
    if args.tacpn:
        tacpn(filename=args.filename,prefix=args.outfile)
    if args.render:
        render(filename=args.filename,prefix=args.outfile)
    
    print("Done")
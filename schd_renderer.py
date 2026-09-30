from __future__ import annotations

from typing import Any, Dict
import plotly.graph_objects as go
import plotly.colors as pc


def render_gantt(
    schedule_data: Dict[str, Any],
    title: str = "Schedule",
    height_per_aircraft: int = 55,
    show_task_labels: bool = False,
) -> go.Figure:

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



if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filename', help='file containing initial data (e.g. test.json)',required=True)
    args = parser.parse_args()
    schedule = json.load(open(args.filename,'r'))
    render_gantt(schedule,show_task_labels=True).show()   

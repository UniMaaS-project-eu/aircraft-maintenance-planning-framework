# Installation
```
git clone https://github.com/UniMaaS-project-eu/aircraft-maintenance-planning-framework
cd aircraft-maintenance-planning-framework
./install.sh
```
> For colored output, remove comment from `termcolor` in [requirements.txt](requirements.txt)

# Usage
```
usage: pipeline.py [-h] -f FILENAME [-o OUTFILE] [--grouping] [--alp] [--flp] [--tacpngen] [--tacpn] [-a]

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        file containing initial data (e.g. test.json)
  -o OUTFILE, --outfile OUTFILE
                        prefix for output files (defaults to 'out')
  --grouping            run grouping
  --alp                 run alp(tcpn)
  --flp                 run flp
  --tacpngen            run tacpn config generation
  --tacpn               run tacpn generation
  -a, --all             run tacpn generation

```
> note: In case of errors make sure that you use the included virtual environment (`source .venv/bin/activate`)


# Example 
Running the framework using [an example scenario](examples/test.json):

`pipeline.py -f examples/test.json -o test`


Content of `test_grouping.json`:
```json
{
    "aircraft_1": {
        "split": [
            4,
            25
        ],
        "cost": 13.0,
        "labeledout": {
            "task1": [
                "task1",
                "task2"
            ],
            "task3": [
                "task3",
                "task4"
            ]
        }
    },
    "aircraft_2": {
        "split": [
            3,
            25
        ],
        "cost": 28.0,
        "labeledout": {
            "task1": [
                "task1"
            ],
            "task3": [
                "task3",
                "task2",
                "task4"
            ]
        }
    }
}
```

Content of `test_fleet_alp_res.json`:
```json
{
    "aircraft_1": [
        {
            "wps": [
                {
                    "tasks": [1,1,0,0],
                    "duration": 1,
                    "timestamp": 4,
                    "map": [
                        "task1",
                        "task2",
                        "task3",
                        "task4"
                    ]
                },
                {
                    "tasks": [0,0,1,1],
                    "duration": 5,
                    "timestamp": 25,
                    "map": [
                        "task1",
                        "task2",
                        "task3",
                        "task4"
                    ]
                }
            ]
        }
    ],
    "aircraft_2": [
        {
            "wps": [
                {
                    "tasks": [1,0,0,0],
                    "duration": 1,
                    "timestamp": 3,
                    "map": [
                        "task1",
                        "task2",
                        "task3",
                        "task4"
                    ]
                },
                {
                    "tasks": [0,1,1,1],
                    "duration": 5,
                    "timestamp": 25,
                    "map": [
                        "task1",
                        "task2",
                        "task3",
                        "task4"
                    ]
                }
            ]
        }
    ]
}
```
Content of `test_flp_schedule.json`:
```json
{
    "Schedule": [
        {
            "PID": "aircraft_1",
            "P": [
                ["task1","task2"],
                ["task3","task4"]
            ],
            "T": [4,20],
            "D": [1,5]
        },
        {
            "PID": "aircraft_2",
            "P": [
                ["task1"],
                ["task2","task3","task4"]
            ],
            "T": [3,25],
            "D": [1,5]
        }
    ]
}

```

Content of `test_tacpn_config.json`:
```json
{
    "aircraft": [
        "aircraft_1",
        "aircraft_2"
    ],
    "flying_invariants": {
        "aircraft_1": 45,
        "aircraft_2": 45
    },
    "crew_count": 1,
    "hangar_count": 1,
    "lifespan": 45,
    "tasks": [
        {
            "guard": [0,45],
            "timer_invariants": {
                "aircraft_1": 4,
                "aircraft_2": 3
            }
        },
        {
            "guard": [0,45],
            "timer_invariants": {
                "aircraft_1": 12,
                "aircraft_2": 37
            }
        },
        {
            "guard": [0,45],
            "timer_invariants": {
                "aircraft_1": 25,
                "aircraft_2": 25
            }
        },
        {
            "guard": [0,45],
            "timer_invariants": {
                "aircraft_1": 30,
                "aircraft_2": 41
            }
        }
    ]
}
```

TACPN trace generation still unter maintenance

<!-- 
Content of `test_Alt1.trc`:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<trace><delay>103</delay>
      <transition id="ComposedModel__T_enter__0">
    <token age="103" place="ComposedModel__Shared__P_flying__1"/>
    <token age="0" place="ComposedModel__Shared__P_ground_capacity"/>
  </transition>
    <transition id="ComposedModel__T_maint_1__0">
    <token age="103" place="ComposedModel__Shared__P_timer_1__1"/>
    <token age="0" place="ComposedModel__Shared__P_crew"/>
    <token age="0" place="ComposedModel__P_bay__1"/>
    </transition>
    <transition id="ComposedModel__T_return_1__0">
    <token age="0" place="ComposedModel__P_inter_1__1"/>
    </transition><delay>1</delay>
  <transition id="ComposedModel__T_exit__0">
    <token age="1" place="ComposedModel__P_bay__1"/>
  </transition>
      <transition id="ComposedModel__T_enter">
    <token age="1" place="ComposedModel__Shared__P_flying__0"/>
    <token age="0" place="ComposedModel__Shared__P_ground_capacity"/>
  </transition>
    <transition id="ComposedModel__T_maint_1">
    <token age="104" place="ComposedModel__Shared__P_timer_1__0"/>
    <token age="0" place="ComposedModel__Shared__P_crew"/>
    <token age="0" place="ComposedModel__P_bay__0"/>
    </transition>
    <transition id="ComposedModel__T_return_1">
    <token age="0" place="ComposedModel__P_inter_1__0"/>
    </transition>
    <transition id="ComposedModel__T_maint_2">
    <token age="104" place="ComposedModel__Shared__P_timer_2__0"/>
    <token age="0" place="ComposedModel__Shared__P_crew"/>
    <token age="0" place="ComposedModel__P_bay__0"/>
    </transition>
    <transition id="ComposedModel__T_return_2">
    <token age="0" place="ComposedModel__P_inter_2__0"/>
    </transition><delay>2</delay>
  <transition id="ComposedModel__T_exit">
    <token age="2" place="ComposedModel__P_bay__0"/>
  </transition><delay>13</delay>
      <transition id="ComposedModel__T_enter">
    <token age="13" place="ComposedModel__Shared__P_flying__0"/>
    <token age="0" place="ComposedModel__Shared__P_ground_capacity"/>
  </transition>
    <transition id="ComposedModel__T_maint_3">
    <token age="119" place="ComposedModel__Shared__P_timer_3__0"/>
    <token age="0" place="ComposedModel__Shared__P_crew"/>
    <token age="0" place="ComposedModel__P_bay__0"/>
    </transition>
    <transition id="ComposedModel__T_return_3">
    <token age="0" place="ComposedModel__P_inter_3__0"/>
    </transition>
    <transition id="ComposedModel__T_maint_4">
    <token age="119" place="ComposedModel__Shared__P_timer_4__0"/>
    <token age="0" place="ComposedModel__Shared__P_crew"/>
    <token age="0" place="ComposedModel__P_bay__0"/>
    </transition>
    <transition id="ComposedModel__T_return_4">
    <token age="0" place="ComposedModel__P_inter_4__0"/>
    </transition><delay>6</delay>
  <transition id="ComposedModel__T_exit">
    <token age="6" place="ComposedModel__P_bay__0"/>
  </transition>
      <transition id="ComposedModel__T_enter__0">
    <token age="6" place="ComposedModel__Shared__P_flying__1"/>
    <token age="0" place="ComposedModel__Shared__P_ground_capacity"/>
  </transition>
    <transition id="ComposedModel__T_maint_2__0">
    <token age="125" place="ComposedModel__Shared__P_timer_2__1"/>
    <token age="0" place="ComposedModel__Shared__P_crew"/>
    <token age="0" place="ComposedModel__P_bay__1"/>
    </transition>
    <transition id="ComposedModel__T_return_2__0">
    <token age="0" place="ComposedModel__P_inter_2__1"/>
    </transition>
    <transition id="ComposedModel__T_maint_3__0">
    <token age="125" place="ComposedModel__Shared__P_timer_3__1"/>
    <token age="0" place="ComposedModel__Shared__P_crew"/>
    <token age="0" place="ComposedModel__P_bay__1"/>
    </transition>
    <transition id="ComposedModel__T_return_3__0">
    <token age="0" place="ComposedModel__P_inter_3__1"/>
    </transition>
    <transition id="ComposedModel__T_maint_4__0">
    <token age="125" place="ComposedModel__Shared__P_timer_4__1"/>
    <token age="0" place="ComposedModel__Shared__P_crew"/>
    <token age="0" place="ComposedModel__P_bay__1"/>
    </transition>
    <transition id="ComposedModel__T_return_4__0">
    <token age="0" place="ComposedModel__P_inter_4__1"/>
    </transition><delay>8</delay>
  <transition id="ComposedModel__T_exit__0">
    <token age="8" place="ComposedModel__P_bay__1"/>
  </transition></trace>
``` -->
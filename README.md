# Installation
```
git clone https://github.com/UniMaaS-project-eu/aircraft-maintenance-planning-framework
cd aircraft-maintenance-planning-framework
./install.sh
```
> For colored output, remove comment from `termcolor` in [requirements.txt](requirements.txt)

# Usage
```
usage: pipeline.py [-h] -f FILENAME [-v] [-i] [-o OUTFILE]

options:
  -f FILENAME, --filename FILENAME  file containing initial data (e.g. test.json)
  -o OUTFILE, --outfile OUTFILE     prefix for output files (defaults to 'out')
  -i, --intermediate    Keep Intermediate output files 
  -v, --verbose         increase output verbosity
  -h, --help            show this help message and exit

```
> note: In case of errors make sure that you use the included virtual environment (`source .venv/bin/activate`)


# Example 
Running the framework using [test.json](test.json):

`pipeline.py -f test.json -o test`


```
[Misc] Parsing Data ... Done

[GROUPING] Grouping Algorithm ... Done

[ALP] Initial Markings generation ... Done

[ALP] TCPN for aircraft_1 (0/2) ... Done

[ALP] TCPN for aircraft_2 (1/2) ... Done

[FLP] Preparing optimal Schedule... Done

[FLP] Running Fleet Level Planning Algorithm... Done
 ...
3                                                   aircraft_2: [1, 0, 0, 0]                         
4 aircraft_1: [1, 1, 0, 0]                                                                           
5 aircraft_1: [1, 1, 0, 0]                                                                           
 ...
19                          aircraft_1: [0, 0, 1, 1]                                                  
20                          aircraft_1: [0, 0, 1, 1]                                                  
21                          aircraft_1: [0, 0, 1, 1]                                                  
22                          aircraft_1: [0, 0, 1, 1]                                                  
23                          aircraft_1: [0, 0, 1, 1]                                                  
24                          aircraft_1: [0, 0, 1, 1]                                                  
25                                                                            aircraft_2: [0, 1, 1, 1]
26                                                                            aircraft_2: [0, 1, 1, 1]
27                                                                            aircraft_2: [0, 1, 1, 1]
28                                                                            aircraft_2: [0, 1, 1, 1]
29                                                                            aircraft_2: [0, 1, 1, 1]
30 ===================================================================================================
31                                                                            aircraft_2: [0, 1, 1, 1]
32                                                                            aircraft_2: [0, 1, 1, 1]

[TACPN] Preparing schedule for trace generation ...Done

[TACPN] Generation TACPN traces... Done

```

Content of `test_scheduling_output.json`:
```json
[{
    "ID": "Alt1",
    "Schedule": [{
        "PID": 1,
        "P": [
            ["t1", "t2"],
            ["t3", "t4"]
        ],
        "T": [4, 19],
        "D": [2, 6]
    }, {
        "PID": 2,
        "P": [
            ["t1"],
            ["t2", "t3", "t4"]
        ],
        "T": [3, 25],
        "D": [1, 8]
    }]
}]
```

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
```
# data_acquisition

_Instructions in development..._

### Setting up environment

    conda env create -f setup/env.yml
    conda activate data_acquisition


### Installing Vicon Datastream SDK

[See Installation Guide here](https://docs.vicon.com/display/DSSDK111/Vicon+DataStream+SDK+Quick+Start+Guide+for+Python)

[Download the Datastream SDK software here](https://www.vicon.com/software/datastream-sdk/)

- Proceed to set local vicon path in yaml file
- start Vicon application (shogun) 

![Pipeline](/img/pipeline.jpg)


TODO: 
- Program pedal and connect to hot keys
- Read hot keys from yaml file 
- connect Client to output 
- make main file 
- how to integrate with handengine 

Notes 
- The facewear and hand engine systems are integrated with Vicon 
- so the pedal can issue commands to shogun and this script simultaneously
- can we then store the data directly from hand engine in a list 
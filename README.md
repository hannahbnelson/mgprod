# mgprod
This code is meant to generate Monte Carlo events using [MadGraph](https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/ManualAndHelp) as generator and [Lobster](http://lobster.readthedocs.io/en/latest/) to manage the workflow steps: LHE,GEN-SIM,DIGI,RECO,MAOD.

## Setup
In order to setup your area, run the setup scripts located in the scripts directory.

    cd lobster_workflow
    ./scripts/setup_cmssw.sh

This setup script is simply to make sure that the correct CMSSW releases are present when running lobster and should only have to be run once.

## Introduction to producing samples
The production is split into two main steps, each with its own corresponding lobster configuration. It is assumed that the following commands are run in the `lobster_workflow` directory.

Make sure to activate your lobster virtual environment before trying to run any of the lobster configs (Note: This implies that you must also have already done `cmsenv` in an appropriate CMSSW release before activating the virtual environment).

    source ~/.lobster/bin/activate

The first step produces LHE level events and uses [lobster_LHE_config.py](lobster_workflow/lobster_LHE_config.py). This step runs on pre-made gridpack tarballs, which were produced using the [CMSSW genproductions workflow](https://github.com/cms-sw/genproductions/tree/mg26x/bin/MadGraph5_aMCatNLO), and are located somewhere on `/hadoop` or in a local `/afs` area. The gridpacks directory can contain any number of gridpacks and can be filtered to only run over a certain sub-set of gridpacks using the whitelists in the lobster configs. For the whitelists to work, it is assumed that the gridpacks are named with the following convention: `p_c_r_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz`, where `p`,`c`,`r` correspond respectively to process, coefficient (or group) tag, and run tag.

To start production of the LHE events run:

    lobster process lobster_LHE_config.py

Make sure to have a `work_queue_factory` running, otherwise lobster won't have any workers to process the tasks.

    nohup work_queue_factory -T condor -M "lobster_${USER}_EFT_LHE.*" -d all -o /tmp/${USER}_lobster_factory.debug -C REPLACEME >& /tmp/${USER}_lobster_factory.log &

Make sure to replace the `REPLACEME` with a path to your own `work_queue_factory` config file (e.g. `/afs/crc.nd.edu/user/a/awightma/Public/worker_factories/factory_T3_12c.json`). **Note:** It is _very_ important for this step that all the workers which are used by the lobster master come from the T3 resources, otherwise the tasks will take significantly longer to finish.

The second step runs on the output produced in the first step and uses [lobster_postLHE_config.py](lobster_workflow/lobster_postLHE_config.py). You will need to change the `input_path` and (possibly) `input_path_full` variables to point to the output directory where you placed the LHE step root files. Similar to before, run the following:

    lobster process lobster_postLHE_config.py

On the condorfe submit nodes run:

    nohup work_queue_factory -T condor -M "lobster_${USER}_EFT_postLHE.*" -d all -o /tmp/${USER}_lobster_factory.debug -C REPLACEME --runos=rhel6 >& /tmp/${USER}_lobster_factory.log &

Again replacing the `REPLACEME` string with a path to your own factory config file. For the postLHE step, the lobster workers can come from either the CRC or T3 resources.

Both lobster configs sport particular run setups to try and better facilitate the transition from the first step to the second. Currently, these options are: `local`, `mg_studies` (which uses the `grp_tag` variable for directory naming) and ,`full_production` (which uses the `production_tag` variable for directory naming). Each of which sets up a particular and separate directory structure in your user area on `/hadoop`. Feel free to modify, or add your own setups, these are simply to make specifying the output from the LHE step and the input to the postLHE step as easy as possible.

## Notes on the production of NAOD samples

To generate NAOD files that include the EFT weights, we cannot use a generic CMSSW release. We need to include the code that puts the weight information into the NAOD files, so execute the following commands to set up the appropriate CMSSW release and include the necessary packages: 
```
cmsrel CMSSW_10_6_19_patch2
cd CMSSW_10_6_19_patch2/src/
export SCRAM_ARCH=slc7_amd64_gcc700
cmsenv

git cms-addpkg PhysicsTools/NanoAOD
git remote add eftfit https://github.com/GonzalezFJR/cmssw.git
git fetch eftfit
```
The `NanoAOD/plugins/GenWeightsTableProducer.cc` script requires `WCFit` and `WCPoint`, so clone the `EFTGenReader` inside of `CMSSW_10_6_19_patch2/src/`:
```
cd CMSSW_10_6_19_patch2/src/ # Or whatever cd gets you into this directory
git clone https://github.com/TopEFT/EFTGenReader.git
```
Finally, we will also need the `NanoAODTools` (described [here](https://twiki.cern.ch/twiki/bin/viewauth/CMS/NanoAODTools#Quickly_make_plots_with_NanoAODT)) in order to get the script we need to merge non-EDM NAOD root files. Follow these steps to clone the repository inside of `PhysicsTools`:
```
cd CMSSW_10_6_19_patch2/src
cmsenv
git cms-init   #not really needed unless you later want to add some other cmssw stuff
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
scram b
```
At this point, you should have all of the necessary code in order to produce the EFT NAOD files. At this point, do a `scram b` in the `CMSSW_10_6_19_patch2/src` to make sure everyting is compiled. 

Finally, edit the `PATH_TO_NAOD_CMSSW` global variable in your lobster config to point to your new `CMSSW_10_6_19_patch2` directory.

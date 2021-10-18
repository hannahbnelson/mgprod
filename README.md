# mgprod
This code is meant to generate Monte Carlo events using [MadGraph](https://cp3.irmp.ucl.ac.be/projects/madgraph/wiki/ManualAndHelp) as generator and [Lobster](http://lobster.readthedocs.io/en/latest/) to manage the workflow steps.

## Setup
In order to setup your area, run the setup scripts located in the scripts directory.

    cd lobster_workflow
    ./scripts/setup_cmssw.sh

This setup script is simply to make sure that the correct CMSSW releases are present when running lobster and should only have to be run once. However, please note that the script may need to be edited, depending on MC samples you are trying to produce. If the release that you need for your samples is not in the script, you will need to add it to the script and rerun, or just set up the release manually.

## Introduction to producing samples
The production is split into multiple steps, each with its own corresponding lobster configuration. It is assumed that the following commands are run in the `lobster_workflow` directory. For information about how to use lobster, please see the [lobster tutorial](https://indico.cern.ch/event/1012446/) from February of 2021, especially the slides from the "How to Lobster" section, which provide a thorough introduction.

Make sure to activate your lobster virtual environment before trying to run any of the lobster configs (Note: This implies that you must also have already done `cmsenv` in an appropriate CMSSW release before activating the virtual environment).

    source ~/.lobster/bin/activate

### The LHE step
The first step is to produce LHE level events. The lobster config for this step is `lobster_LHE_config.p`. This step runs on pre-made gridpack tarballs, which were produced using the [CMSSW genproductions workflow](https://github.com/cms-sw/genproductions/tree/mg26x/bin/MadGraph5_aMCatNLO), and are located somewhere on `/hadoop` or in a local `/afs` area. The gridpacks directory can contain any number of gridpacks and can be filtered to only run over a certain sub-set of gridpacks using the whitelists in the lobster configs. For the whitelists to work, it is assumed that the gridpacks are named with the following convention: `p_c_r_slc6_amd64_gcc630_CMSSW_9_3_0_tarball.tar.xz`, where `p`,`c`,`r` correspond respectively to process, coefficient (or group) tag, and run tag.

To start production of the LHE events run:

    lobster process lobster_LHE_config.py

Make sure to have a `work_queue_factory` running, otherwise lobster won't have any workers to process the tasks. For information about how to do this, please see the "How to Lobster" slides from the lobster tutorial mentioned above. 

**Note:** It is _very_ important for this step that all the workers which are used by the lobster master come from the T3 resources, otherwise the tasks will take significantly longer to finish.

## The post-LHE steps

The second step runs on the LHE output produced in the first step. Any step after the LHE step can be run on either the T3 resources or the general CRC resources. There are currently several scripts with different purposes that can be run on the LHE output.  

* `lobster_postLHE_config.py`: This script includes GEN-MAOD steps. It was designed to produce the 2017 MC used in TOP-19-001. It is not set up to produce UL MC.
* `lobster_GEN_config.py`: This script runs only the GEN step, and is also not set up to produce UL MC.
* `lobster_postLHE_UL_config.py`: This script produced UL MC. It can produce the GEN-NAOD steps, but it can be used to run only the GEN step, the GEN-MAOD steps, or the full GEN-NAOD steps by setting the `STEPS` variable to `throughGEN`, `throughMAOD`, or `throughNAOD`.

All of these lobster configs will need to be edited before you run them. You will need to edit the code to point to the input files you are interested in, and also tell the code how to name the output files. Depending on the config and your intentions, you may need to make additional edits as well.

These lobster configs feature particular run setups to try and better facilitate the transition from the first step to the second. Currently, these options are: `local`, `mg_studies` (which uses the `grp_tag` variable for directory naming) and ,`full_production` (which uses the `production_tag` variable for directory naming). Each of which sets up a particular and separate directory structure in your user area on `/hadoop`. Feel free to modify, or add your own setups, these are simply to make specifying the output from the LHE step and the input to the postLHE step as easy as possible.

### Additional notes on the production of NAOD samples

The NAOD step can be run as part of the "postLHE" step as described above, or as a standalone workflow. One befit of running it as a standalone workflow (that takes as input the MAOD files produced by the `postLHE` step) is that it makes it cleaner and more straightforward to rerun the NAOD step. The `lobster_NAOD_UL_config.py` config is designed to run on the MAOD output of the `lobster_postLHE_UL_config.py` step to produce UL NAOD.

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
At this point, you should have all of the necessary code in order to produce the EFT NAOD samples. Before moving on, do a `scram b` in the `CMSSW_10_6_19_patch2/src` to make sure everyting is compiled. 

Finally, edit the `PATH_TO_NAOD_CMSSW` global variable in your lobster config to point to your new `CMSSW_10_6_19_patch2` directory.

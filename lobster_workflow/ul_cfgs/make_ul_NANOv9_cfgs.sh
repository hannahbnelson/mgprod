#!/bin/bash

export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh

setup_rel(){

    printf "\nSet up CMSSW release for $1...\n"
    if [ -r $1/src ] ; then
        echo release $1 already exists
    else
        scram p CMSSW $1
    fi
    cd $1/src
    eval `scram runtime -sh`
  
    scram b
    cd ../..
  
    printf "CMSSW base: $CMSSW_BASE\n"
}


# Set up the v9 rel
REL=CMSSW_10_6_26
setup_rel $REL


# UL16 NAOD
(
    CFG_NAME=UL16_NAOD_cfg.py
    FIN=MAOD-00000.root
    FOUT=NAOD-00000.root

    # cfg url: https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/TOP-RunIISummer20UL16NanoAODv9-00001
    # cmsDriver from url: cmsDriver.py  --python_filename TOP-RunIISummer20UL16NanoAODv9-00001_1_cfg.py --eventcontent NANOEDMAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:TOP-RunIISummer20UL16NanoAODv9-00001.root --conditions 106X_mcRun2_asymptotic_v17 --step NANO --filein "dbs:/TTZToQQ_Dilept_TuneCP5_13TeV-amcatnlo-pythia8/RunIISummer20UL16MiniAODv2-106X_mcRun2_asymptotic_v17-v1/MINIAODSIM" --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec --mc -n $EVENTS || exit $? ;

    printf "\n --- START cfg $CFG_NAME ---\n"
    cmsDriver.py step1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 106X_mcRun2_asymptotic_v17 --step NANO --era Run2_2016,run2_nanoAOD_106Xv2 --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
    printf "\n --- END cfg $CFG_NAME ---\n"
)

# UL16APV NAOD
(
    CFG_NAME=UL16APV_NAOD_cfg.py
    FIN=MAOD-00000.root
    FOUT=NAOD-00000.root

    # cfg url: https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/TOP-RunIISummer20UL16NanoAODAPVv9-00001
    # cmsDriver from url: cmsDriver.py  --python_filename TOP-RunIISummer20UL16NanoAODAPVv9-00001_1_cfg.py --eventcontent NANOEDMAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:TOP-RunIISummer20UL16NanoAODAPVv9-00001.root --conditions 106X_mcRun2_asymptotic_preVFP_v11 --step NANO --filein "dbs:/ST_t-channel_muDecays_anomwtbLVRT_LV2RT2_TuneCP5_13TeV-comphep-pythia8/RunIISummer20UL16MiniAODAPVv2-106X_mcRun2_asymptotic_preVFP_v11-v1/MINIAODSIM" --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec --mc -n $EVENTS || exit $? ;

    printf "\n --- START cfg $CFG_NAME ---\n"
    cmsDriver.py step1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 106X_mcRun2_asymptotic_preVFP_v11 --step NANO --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
    printf "\n --- END cfg $CFG_NAME ---\n"
)

# UL17 NAOD
(
    CFG_NAME=UL17_NAOD_cfg.py
    FIN=MAOD-00000.root
    FOUT=NAOD-00000.root

    # cfg url: https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/TOP-RunIISummer20UL17NanoAODv9-00001
    # cmsDriver from url: cmsDriver.py  --python_filename TOP-RunIISummer20UL17NanoAODv9-00001_1_cfg.py --eventcontent NANOEDMAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:TOP-RunIISummer20UL17NanoAODv9-00001.root --conditions 106X_mc2017_realistic_v9 --step NANO --filein "dbs:/TAToTTQ_MA-200to700GeV_TuneCP5_13TeV_G2HDM-rtc08-madgraphMLM-pythia8/RunIISummer20UL17MiniAODv2-rp_106X_mc2017_realistic_v9-v2/MINIAODSIM" --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec --mc -n $EVENTS || exit $? ;

    printf "\n --- START cfg $CFG_NAME ---\n"
    cmsDriver.py step1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 106X_mc2017_realistic_v9 --step NANO --era Run2_2017,run2_nanoAOD_106Xv2  --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
    printf "\n --- END cfg $CFG_NAME ---\n"
)

# UL18 NAOD
(
    CFG_NAME=UL18_NAOD_cfg.py
    FIN=MAOD-00000.root
    FOUT=NAOD-00000.root

    # cfg url: https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/TOP-RunIISummer20UL18NanoAODv9-00001
    # cmsDriver from url: cmsDriver.py  --python_filename TOP-RunIISummer20UL18NanoAODv9-00001_1_cfg.py --eventcontent NANOEDMAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:TOP-RunIISummer20UL18NanoAODv9-00001.root --conditions 106X_upgrade2018_realistic_v16_L1v1 --step NANO --filein "dbs:/TTToHadronic_mtop171p5_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM" --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec --mc -n $EVENTS || exit $? ;

    printf "\n --- START cfg $CFG_NAME ---\n"
    cmsDriver.py step1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 106X_upgrade2018_realistic_v16_L1v1 --step NANO --era Run2_2018,run2_nanoAOD_106Xv2  --filein file:$FIN --fileout file:$FOUT --python_filename $CFG_NAME --no_exec
    printf "\n --- END cfg $CFG_NAME ---\n"
)

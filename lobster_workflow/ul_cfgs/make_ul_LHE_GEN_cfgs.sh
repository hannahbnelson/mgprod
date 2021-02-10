#!/bin/bash

export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh

FDIR=../../../fragments # Dir of fragments, relative to CMSSW/src

setup_rel(){

    printf "\nSet up CMSSW release for $1...\n"
    if [ -r $1/src ] ; then
        echo release $1 already exists
    else
        scram p CMSSW $1
    fi
    cd $1/src
    eval `scram runtime -sh`

    mkdir -p ./Configuration/GenProduction/python/ # Make a directory for the fragment if it does not already exist
    cp $FDIR/$2 ./Configuration/GenProduction/python/ # Copy the fragment to the  directory

    scram b
    cd ../..

    printf "CMSSW base: $CMSSW_BASE\n"
}

make_ul16_gen_cfg(){
    cfgname=$1
    fin=$2
    fout=$3
    fragment=$4
    printf "$cfgname , $fin , $fout , $fragment"
    cmsDriver.py Configuration/GenProduction/python/$fragment --mc --eventcontent RAWSIM --datatier GEN --conditions 106X_mcRun2_asymptotic_v13 --beamspot Realistic25ns13TeV2016Collision --step GEN --geometry DB:Extended --era Run2_2016  --fileout file:$fout --filein file:$fin --python_filename $cfgname --no_exec

}

make_ul16apv_gen_cfg(){
    cfgname=$1
    fin=$2
    fout=$3
    fragment=$4
    printf "$cfgname , $fin , $fout , $fragment"
    cmsDriver.py Configuration/GenProduction/python/$fragment --mc --eventcontent RAWSIM --datatier GEN --conditions 106X_mcRun2_asymptotic_preVFP_v8 --beamspot Realistic25ns13TeV2016Collision --step GEN --geometry DB:Extended --era Run2_2016_HIPM  --fileout file:$fout --filein file:$fin --python_filename $cfgname --no_exec
}

make_ul17_gen_cfg(){
    cfgname=$1
    fin=$2
    fout=$3
    fragment=$4
    printf "$cfgname , $fin , $fout , $fragment"
    cmsDriver.py Configuration/GenProduction/python/$fragment --mc --eventcontent RAWSIM --datatier GEN --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN --geometry DB:Extended --era Run2_2017 --fileout file:$fout --filein file:$fin --python_filename $cfgname --no_exec
}

make_ul18_gen_cfg(){
    cfgname=$1
    fin=$2
    fout=$3
    fragment=$4
    printf "$cfgname , $fin , $fout , $fragment"
    cmsDriver.py Configuration/GenProduction/python/$fragment --mc --eventcontent RAWSIM --datatier GEN --conditions 106X_upgrade2018_realistic_v4 --beamspot Realistic25ns13TeVEarly2018Collision --step GEN --geometry DB:Extended --era Run2_2018 --fileout file:$fout --filein file:$fin --python_filename $cfgname --no_exec 
}


# UL16 LHE and GEN
(
    # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL16pLHEGEN
    REL=CMSSW_10_6_19_patch3

    # GEN ttHJet
    FRAGMENT=ttHJets_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul16_gen_cfg "UL16_GEN_ttHJet_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # GEN ttlnuJet
    FRAGMENT=ttlnuJets_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul16_gen_cfg "UL16_GEN_ttlnuJet_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # GEN ttlnu (no matching)
    FRAGMENT=ttlnu_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul16_gen_cfg "UL16_GEN_ttlnu_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # LHE
    FRAGMENT=ttHJets_custom_ND-fragment.py
    lheout=LHE-00000.root
    lhecfgname=UL16_LHE_cfg.py
    cmsDriver.py Configuration/GenProduction/python/$FRAGMENT --mc --eventcontent LHE --datatier LHE --conditions 106X_mcRun2_asymptotic_v13 --beamspot Realistic25ns13TeV2016Collision --step LHE --era Run2_2016 --fileout file:$lheout --python_filename $lhecfgname --no_exec

)

# UL16APV LHE and GEN
(
    # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL16pLHEGENAPV
    REL=CMSSW_10_6_19_patch3

    # GEN ttHJet
    FRAGMENT=ttHJets_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul16apv_gen_cfg "UL16APV_GEN_ttHJet_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # GEN ttlnuJet
    FRAGMENT=ttlnuJets_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul16apv_gen_cfg "UL16APV_GEN_ttlnuJet_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # GEN ttlnu (no matching)
    FRAGMENT=ttlnu_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul16apv_gen_cfg "UL16APV_GEN_ttlnu_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # LHE
    FRAGMENT=ttHJets_custom_ND-fragment.py
    #FRAGMENT=ttlnuJets_custom_ND-fragment.py # All the fragments seem to result in same cfg
    #FRAGMENT=ttlnu_custom_ND-fragment.py # All the fragments seem to result in same cfg
    lheout=LHE-00000.root
    lhecfgname=UL16APV_LHE_cfg.py
    cmsDriver.py Configuration/GenProduction/python/$FRAGMENT --mc --eventcontent LHE --datatier LHE --conditions 106X_mcRun2_asymptotic_preVFP_v8 --beamspot Realistic25ns13TeV2016Collision --step LHE --era Run2_2016_HIPM --fileout file:$lheout --python_filename $lhecfgname --no_exec

)

# UL17 LHE and GEN
(
    # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL17pLHEGEN
    # LHE cmsDriver: cmsDriver.py NameOfFragment --mc --eventcontent LHE --datatier LHE --conditions 106X_mc2017_realistic_v6 --step NONE --era Run2_2017  --filein file:step-1.root --fileout file:step0.root
    # GEN cmsDriver: cmsDriver.py NameOfFragment --mc --eventcontent RAWSIM --datatier GEN --conditions 106X_mc2017_realistic_v6 --beamspot Realistic25ns13TeVEarly2017Collision --step GEN --geometry DB:Extended --era Run2_2017  --fileout file:step1.root
    REL=CMSSW_10_6_19_patch3

    # GEN ttHJet
    FRAGMENT=ttHJets_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul17_gen_cfg "UL17_GEN_ttHJet_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # GEN ttlnuJet
    FRAGMENT=ttlnuJets_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul17_gen_cfg "UL17_GEN_ttlnuJet_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # GEN ttlnu (no matching)
    FRAGMENT=ttlnu_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul17_gen_cfg "UL17_GEN_ttlnu_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # LHE
    FRAGMENT=ttHJets_custom_ND-fragment.py
    #FRAGMENT=ttlnuJets_custom_ND-fragment.py # All the fragments seem to result in same cfg
    #FRAGMENT=ttlnu_custom_ND-fragment.py # All the fragments seem to result in same cfg
    lheout=LHE-00000.root
    lhecfgname=UL17_LHE_cfg.py
    cmsDriver.py Configuration/GenProduction/python/$FRAGMENT --mc --eventcontent LHE --datatier LHE --conditions 106X_mc2017_realistic_v6 --step LHE --era Run2_2017  --fileout file:$lheout --python_filename $lhecfgname --no_exec

)

# UL18 LHE and GEN
(
    # cfg url: https://twiki.cern.ch/twiki/bin/view/CMS/RunIISummer20UL18pLHEGEN
    REL=CMSSW_10_6_19_patch3

    # GEN ttHJet
    FRAGMENT=ttHJets_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul18_gen_cfg "UL18_GEN_ttHJet_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # GEN ttlnuJet
    FRAGMENT=ttlnuJets_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul18_gen_cfg "UL18_GEN_ttlnuJet_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # GEN ttlnu (no matching)
    FRAGMENT=ttlnu_custom_ND-fragment.py
    setup_rel $REL $FRAGMENT
    make_ul18_gen_cfg "UL18_GEN_ttlnu_cfg.py" "LHE-00000.root" "GEN-00000.root" $FRAGMENT

    # LHE
    FRAGMENT=ttHJets_custom_ND-fragment.py
    lheout=LHE-00000.root
    lhecfgname=UL18_LHE_cfg.py
    cmsDriver.py Configuration/GenProduction/python/$FRAGMENT --mc --eventcontent LHE --datatier LHE --conditions 106X_upgrade2018_realistic_v4 --step LHE --era Run2_2018 --fileout file:$lheout --python_filename $lhecfgname --no_exec

)

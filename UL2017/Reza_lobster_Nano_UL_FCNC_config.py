import datetime
import os
import sys
import shutil

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, Dataset,ParentDataset, StorageConfiguration, Workflow

sys.path.append(os.getcwd())
from helpers.utils import regex_match, run_process

MODIFIED_CFG_DIR = "python_cfgs/modified"
timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')
input_path = "/store/user/"
input_path_full = "/hadoop" + input_path

master_label = 'CRC_EFT_postLHE_crc_{tstamp}'.format(tstamp=timestamp_tag)
#master_label = 'EFT_ALL_postLHE_{tstamp}'.format(tstamp=timestamp_tag)
#master_label = 'EFT_T3_postLHE_{tstamp}'.format(tstamp=timestamp_tag)
#master_label = 'EFT_testNAOD_T3_postLHE_{tstamp}'.format(tstamp=timestamp_tag)

########## Set up the lobster cfg ##########

# Note: Should not have to modify things outside of this section, unless you want to:
#    - Hardcode lhe dirs to use
#    - Modify gen cfgs

# Specify what kind of output to make
#STEPS = 'throughGEN'
STEPS = 'throughNAOD'
#STEPS = 'throughNAOD'

PATH_TO_NAOD_CMSSW = "/afs/crc.nd.edu/user/r/rgoldouz/MakeLobsterJobs/UL/mgprod/lobster_workflow/CMSSW_10_6_19_patch2"

# Specfy the run setup
RUN_SETUP = 'UL_production'
#RUN_SETUP = 'mg_studies'
#RUN_SETUP = 'testing'

# Specify the UL year
#UL_YEAR = 'UL16'
#UL_YEAR = 'UL16APV'
UL_YEAR = 'UL17'
#UL_YEAR = 'UL18'

# Name the output
out_ver = "v1"   # The version index for the OUTPUT directory
#out_tag = "FullR2Studies/ULChecks/ttXJet-tXq_testUpdateGenproddim6TopMay20GST_GEN_ULCheck"
out_tag = "FullR2Studies/ValidationChecks/ttXJet_dim6TopMay20GST_run0StartPt_qCutScan_GEN_"
#out_tag = "ForPhenoJhepReviewStudies/ttZJet_sampleForDoubleCheckingQcut_dim6TopMay20GST_GEN_"
prod_tag = "Round1/Batch3"


# Append UL year to out tag
out_tag = out_tag + UL_YEAR

# Only run over lhe steps from specific processes/coeffs/runs
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []  # (i.e. MG starting points)

# Specify the input directories. Note: The workflows in each of the input directories should all be uniquely named w.r.t each other
input_dirs = [
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_testUpdateGenproddim6TopMay20GST_ULCheck-UL16/v1"),
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_testUpdateGenproddim6TopMay20GST_ULCheck-UL16APV/v1"),
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_testUpdateGenproddim6TopMay20GST_ULCheck-UL17/v1"),
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_testUpdateGenproddim6TopMay20GST_ULCheck-UL18/v1"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL17/Round1/Batch1/LHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL17/Round1/Batch2/LHE_step/v1/"),
    os.path.join(input_path_full,"rgoldouz/FullProduction/FullR2/UL17/Round1/Batch3/postLHE_step/v1/"),
]



########## Select input directories according to whitelists ##########

lhe_dirs = []
for path in input_dirs:
    for fd in os.listdir(path):
        if fd.find('mAOD_step_') < 0:
            continue
        arr = fd.split('_')
        p,c,r = arr[1],arr[2],arr[3]
        if len(regex_match([p],process_whitelist)) == 0:
            continue
        elif len(regex_match([c],coeff_whitelist)) == 0:
            continue
        elif len(regex_match([r],runs_whitelist)) == 0:
            continue
        relpath = os.path.relpath(path,input_path_full)
        lhe_dirs.append(os.path.join(relpath,fd))

'''
# Hardcode the lhe dirs by hand
lhe_dirs = [
    # For Full R2
    #"kmohrman/LHE_step/FullR2Studies/ValidationChecks/ttHJet-ttlnuJet-ttllJet-ttbarJet-tllq-tHq_dim6TopMay20GST_all22WCsStartPtCheck_UL17/v1/lhe_step_ttHJet_all22WCsStartPtCheckdim6TopMay20GST_run0",
    #"kmohrman/LHE_step/FullR2Studies/ValidationChecks/ttHJet-ttlnuJet-ttllJet-ttbarJet-tllq-tHq_dim6TopMay20GST_all22WCsStartPtCheck_UL17/v1/lhe_step_ttlnuJet_all22WCsStartPtCheckdim6TopMay20GST_run0",
    #"kmohrman/LHE_step/FullR2Studies/ValidationChecks/ttHJet-ttlnuJet-ttllJet-ttbarJet-tllq-tHq_dim6TopMay20GST_all22WCsStartPtCheck_UL17/v1/lhe_step_ttllNuNuJetNoHiggs_all22WCsStartPtCheckdim6TopMay20GST_run0",
    #"kmohrman/LHE_step/FullR2Studies/ValidationChecks/ttHJet-ttlnuJet-ttllJet-ttbarJet-tllq-tHq_dim6TopMay20GST_all22WCsStartPtCheck_UL17/v1/lhe_step_tllq4fNoSchanWNoHiggs0p_all22WCsStartPtCheckdim6TopMay20GST_run0",
    #"kmohrman/LHE_step/FullR2Studies/ValidationChecks/ttHJet-ttlnuJet-ttllJet-ttbarJet-tllq-tHq_dim6TopMay20GST_all22WCsStartPtCheck_UL17/v1/lhe_step_tHq4f_all22WCsStartPtCheckdim6TopMay20GST_run0",
    #"kmohrman/LHE_step/FullR2Studies/ValidationChecks/ttHJet-ttlnuJet-ttllJet-ttbarJet-tllq-tHq_dim6TopMay20GST_all22WCsStartPtCheck_UL17/v1/lhe_step_ttbarJet_all22WCsStartPtCheckdim6TopMay20GST_run0",
    #"kmohrman/LHE_step/FullR2Studies/ValidationChecks/ttHJet-ttlnuJet-ttbarJet-tllq-tHq_dim6TopMay20GST_all22WCsStartPtCheckV2_UL17/v1/lhe_step_tllq4fNoSchanWNoHiggs0p_all22WCsStartPtCheckV2dim6TopMay20GST_run0"
    "kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_testUpdateGenproddim6TopMay20GST_ULCheck-UL17/v1/lhe_step_tllq4fNoSchanWNoHiggs0p_testUpdateGenproddim6TopMay20GST_run1"
]
'''


########## Set up output based on run setup ##########

if RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
elif RUN_SETUP == 'UL_production':
    # For Large MC production
    output_path  = "/store/user/$USER/FullProduction/FullR2/{ul}/{tag}/postLHE_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/FullR2/{ul}/{tag}/postLHE_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/FullProduction/FullR2/{ul}/{tag}/postLHE_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=out_ver)
elif RUN_SETUP == 'testing':
    # For test runs (where you do not intend to keep the output)
    grp_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
else:
    print "Unknown run setup, {setup}".format(setup=RUN_SETUP)
    raise ValueError


########## Configure storage ##########

storage = StorageConfiguration(
    input=[
        "hdfs://eddie.crc.nd.edu:19000"  + input_path,
        "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + input_path,
        "srm://T3_US_NotreDame"          + input_path,
    ],
    output=[
        "hdfs://eddie.crc.nd.edu:19000"  + output_path,
        # ND is not in the XrootD redirector, thus hardcode server.
        "root://deepthought.crc.nd.edu/" + output_path, # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + output_path,
        "srm://T3_US_NotreDame"          + output_path,
        "file:///hadoop"                 + output_path,
    ],
    disable_input_streaming=False,
)


########## Resources for each step ##########

# Worker Res.:
#   Cores:  12    | 4
#   Memory: 16000 | 8000
#   Disk:   13000 | 6500

gen_resources = Category(
    name='gen',
    cores=1,
    memory=2000,
    disk=1000,
    tasks_min=12,
    tasks_max=3000,
    mode='fixed'
)
sim_resources = Category(
    name='sim',
    cores=6,
    memory=3000,
    disk=3000,
    tasks_min=12,
    mode='fixed'
)
digi_resources = Category(
    name='digi',
    cores=6,
    memory=7800,
    disk=6000,
    mode='fixed'
)
hlt_resources = Category(
    name='hlt',
    cores=2,
    memory=5000,
    disk=6000,
    mode='fixed'
)
reco_resources = Category(
    name='reco',
    cores=3,
    memory=5000,
    disk=3000,
    mode='fixed'
)
maod_resources = Category(
    name='maod',
    cores=2,
    memory=3500,
    disk=2000,
    mode='fixed'
)
naod_resources = Category(
    name='naod',
    cores=2,
    memory=3500,
    disk=2000,
    mode='fixed'
)


########## Set up dictionary for cfg files ##########

wf_steps = ['gen','sim','digi','hlt','reco','maod','naod']
ul_base = 'ul_cfgs'

ul_cfg_map = {
    'UL16' : {
        'all_procs' : {
            'sim'  : os.path.join(ul_base,'UL16_SIM_cfg.py'),
            'digi' : os.path.join(ul_base,'UL16_DIGI_cfg.py'),
            'hlt'  : os.path.join(ul_base,'UL16_HLT_cfg.py'),
            'reco' : os.path.join(ul_base,'UL16_RECO_cfg.py'),
            'maod' : os.path.join(ul_base,'UL16_MAOD_cfg.py'),
            'naod' : os.path.join(ul_base,'UL16_NAOD_cfg.py'),
        }
    },
    'UL16APV' : {
        'all_procs' : {
            'sim'  : os.path.join(ul_base,'UL16APV_SIM_cfg.py'),
            'digi' : os.path.join(ul_base,'UL16APV_DIGI_cfg.py'),
            'hlt'  : os.path.join(ul_base,'UL16APV_HLT_cfg.py'),
            'reco' : os.path.join(ul_base,'UL16APV_RECO_cfg.py'),
            'maod' : os.path.join(ul_base,'UL16APV_MAOD_cfg.py'),
            'naod' : os.path.join(ul_base,'UL16APV_NAOD_cfg.py'),
        }
    },
    'UL17' : {
        'all_procs' : {
            'gen': os.path.join(ul_base,'UL17_GEN_FCNC_cfg.py'),
            'sim'  : os.path.join(ul_base,'UL17_SIM_cfg.py'),
            'digi' : os.path.join(ul_base,'UL17_DIGI_cfg.py'),
            'hlt'  : os.path.join(ul_base,'UL17_HLT_cfg.py'),
            'reco' : os.path.join(ul_base,'UL17_RECO_cfg.py'),
            'maod' : os.path.join(ul_base,'UL17_MAOD_cfg.py'),
            'naod' : os.path.join(ul_base,'UL17_NAOD_cfg.py'),
        }
    },
    'UL18' : {
        'all_procs' : {
            'sim'  : os.path.join(ul_base,'UL18_SIM_cfg.py'),
            'digi' : os.path.join(ul_base,'UL18_DIGI_cfg.py'),
            'hlt'  : os.path.join(ul_base,'UL18_HLT_cfg.py'),
            'reco' : os.path.join(ul_base,'UL18_RECO_cfg.py'),
            'maod' : os.path.join(ul_base,'UL18_MAOD_cfg.py'),
            'naod' : os.path.join(ul_base,'UL18_NAOD_cfg.py'),
        }
    }

}
gen_ul_cfg_map = {
    'UL16' : {
        'ttHJet' : {
            'gen': os.path.join(ul_base,'UL16_GEN_ttHJet_cfg.py'),
        },
        'ttlnuJet' : {
            'gen': os.path.join(ul_base,'UL16_GEN_ttlnuJet_cfg.py'),
        },
        'ttllNuNuJetNoHiggs' : {
            'gen': os.path.join(ul_base,'UL16_GEN_ttlnuJet_cfg.py'),
        },
        'tllq4fNoSchanWNoHiggs0p' : {
            'gen': os.path.join(ul_base,'UL16_GEN_ttlnu_cfg.py'),
        },
        'tHq4f' : {
            'gen': os.path.join(ul_base,'UL16_GEN_ttlnu_cfg.py'),
        }
    },
    'UL16APV' : {
        'ttHJet' : {
            'gen': os.path.join(ul_base,'UL16APV_GEN_ttHJet_cfg.py'),
        },
        'ttlnuJet' : {
            'gen': os.path.join(ul_base,'UL16APV_GEN_ttlnuJet_cfg.py'),
        },
        'ttllNuNuJetNoHiggs' : {
            'gen': os.path.join(ul_base,'UL16APV_GEN_ttlnuJet_cfg.py'),
        },
        'tllq4fNoSchanWNoHiggs0p' : {
            'gen': os.path.join(ul_base,'UL16APV_GEN_ttlnu_cfg.py'),
        },
        'tHq4f' : {
            'gen': os.path.join(ul_base,'UL16APV_GEN_ttlnu_cfg.py'),
        }
    },
    'UL17' : {
        'ttHJet' : {
            'gen': os.path.join(ul_base,'UL17_GEN_ttHJet_cfg.py'),
        },
        'ttlnuJet' : {
            'gen': os.path.join(ul_base,'UL17_GEN_ttlnuJet_cfg.py'),
        },
        'ttllNuNuJetNoHiggs' : {
            'gen': os.path.join(ul_base,'UL17_GEN_ttlnuJet_cfg.py'),
        },
        'tllq4fNoSchanWNoHiggs0p' : {
            'gen': os.path.join(ul_base,'UL17_GEN_ttlnu_cfg.py'),
        },
        'tHq4f' : {
            'gen': os.path.join(ul_base,'UL17_GEN_ttlnu_cfg.py'),
        },
        'FCNC' : {
            'gen': os.path.join(ul_base,'UL17_GEN_FCNC_cfg.py'),
        }
    },
    'UL18' : {
        'ttHJet' : {
            'gen': os.path.join(ul_base,'UL18_GEN_ttHJet_cfg.py'),
        },
        'ttlnuJet' : {
            'gen': os.path.join(ul_base,'UL18_GEN_ttlnuJet_cfg.py'),
        },
        'ttllNuNuJetNoHiggs' : {
            'gen': os.path.join(ul_base,'UL18_GEN_ttlnuJet_cfg.py'),
        },
        'tllq4fNoSchanWNoHiggs0p' : {
            'gen': os.path.join(ul_base,'UL18_GEN_ttlnu_cfg.py'),
        },
        'tHq4f' : {
            'gen': os.path.join(ul_base,'UL18_GEN_ttlnu_cfg.py'),
        }
    },
}
# Put the gen configs into the ul cfg map
fragment_map = ul_cfg_map[UL_YEAR]
for k,v in gen_ul_cfg_map[UL_YEAR].iteritems():
    fragment_map[k] = v


########## Specify CMSSW rel for each step ##########

rel_map = {
    'UL16' : {
        'gen' : 'CMSSW_10_6_19_patch3',
        'sim' : 'CMSSW_10_6_17_patch1',
        'digi': 'CMSSW_10_6_17_patch1',
        'hlt' : 'CMSSW_8_0_33_UL',
        'reco': 'CMSSW_10_6_17_patch1',
        'maod': 'CMSSW_10_6_20',
        'naod': 'CMSSW_10_6_19_patch2',
    },
    'UL16APV' : {
        'gen' : 'CMSSW_10_6_19_patch3',
        'sim' : 'CMSSW_10_6_17_patch1',
        'digi': 'CMSSW_10_6_17_patch1',
        'hlt' : 'CMSSW_8_0_33_UL',
        'reco': 'CMSSW_10_6_17_patch1',
        'maod': 'CMSSW_10_6_20',
        'naod': 'CMSSW_10_6_19_patch2',
    },
    'UL17' : {
        'gen' : 'CMSSW_10_6_19_patch3',
        'sim' : 'CMSSW_10_6_17_patch1',
        'digi': 'CMSSW_10_6_17_patch1',
        'hlt' : 'CMSSW_9_4_14_UL_patch1',
        'reco': 'CMSSW_10_6_17_patch1',
        'maod': 'CMSSW_10_6_20',
        'naod': 'CMSSW_10_6_19_patch2',
    },
    'UL18' : {
        'gen' : 'CMSSW_10_6_19_patch3',
        'sim' : 'CMSSW_10_6_17_patch1',
        'digi': 'CMSSW_10_6_17_patch1',
        'hlt' : 'CMSSW_10_2_16_UL',
        'reco': 'CMSSW_10_6_17_patch1',
        'maod': 'CMSSW_10_6_20',
        'naod': 'CMSSW_10_6_19_patch2',
    },

}


########## Optionally modify the GEN cfgs ##########

gs_mods_dict = {}
gs_mods_dict["base"] = {}
gs_mods_dict["base"]["base"] = []
'''
# Example of q cut variation
gs_mods_dict["ttHJet"] = {}
gs_mods_dict["ttHJet"]['qCut15'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 15.|g']
gs_mods_dict["ttHJet"]['qCut20'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 20.|g']
gs_mods_dict["ttHJet"]['qCut25'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 25.|g']
gs_mods_dict["ttlnuJet"] = {}
gs_mods_dict["ttlnuJet"]['qCut15'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 15.|g']
gs_mods_dict["ttlnuJet"]['qCut20'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 20.|g']
gs_mods_dict["ttlnuJet"]['qCut25'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 25.|g']
gs_mods_dict["ttbarJet"] = {}
gs_mods_dict["ttbarJet"]['qCut15'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 15.|g']
gs_mods_dict["ttbarJet"]['qCut20'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 20.|g']
gs_mods_dict["ttbarJet"]['qCut25'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 25.|g']
gs_mods_dict["ttllNuNuJetNoHiggs"] = {}
gs_mods_dict["ttllNuNuJetNoHiggs"]['qCut15'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 15.|g']
gs_mods_dict["ttllNuNuJetNoHiggs"]['qCut20'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 20.|g']
gs_mods_dict["ttllNuNuJetNoHiggs"]['qCut25'] = ['s|JetMatching:qCut = 20.|JetMatching:qCut = 25.|g']
'''

# Turn matching off here, since we are using a fragment wiht matching turned on
gs_mods_dict["ttH"] = {}
gs_mods_dict["ttH"]["MatchOff"] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']
gs_mods_dict["ttHTOll"] = {}
gs_mods_dict["ttHTOll"]["MatchOff"] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']


########## Generate workflows ##########

wf = []
print "Generating workflows:"
for idx,lhe_dir in enumerate(lhe_dirs):
    # Raise exception if trying to make UL sample but the UL year is not in the path anywhere
    if ( (UL_YEAR not in lhe_dir) or ((UL_YEAR == "UL16") and ("APV" in lhe_dir)) ):
        print "\nWARNING: UL year selected, but lhe dir path does not contain this UL year in it anywhere, are you sure you have the right path? Please double check."
        print "\tUL Year:" , UL_YEAR, "\n\tPath:" , lhe_dir, "\nExiting...\n"
        raise Exception
    print "\t[{0}/{1}] LHE Input: {dir}".format(idx+1,len(lhe_dirs),dir=lhe_dir)
    head,tail = os.path.split(lhe_dir)
    arr = tail.split('_')
    p,c,r = arr[1],arr[2],arr[3]
    #print("p c r:",p,c,r)
    wf_fragments = {}
    for step in wf_steps:
        wf_fragments[step] = fragment_map["all_procs"][step]
    label_tag = c + '_' + r 
    gen = Workflow(
        label='gen_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['gen']),
        sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['gen']),
        merge_size=-1,  # Don't merge files we don't plan to keep
        cleanup_input=False, # Do not accidently clean up the LHE files!!!
        globaltag=False,
        outputs=['GEN-00000.root'],
        dataset=Dataset(
            files=lhe_dir,
            files_per_task=1,
            patterns=["*.root"]
        ),
        category=gen_resources
    )

    sim = Workflow(
        label='sim_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['sim']),
        sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['sim']),
        merge_size=-1,  # Don't merge files we don't plan to keep
        cleanup_input=True,
        #cleanup_input=False,
        globaltag=False,
        outputs=['SIM-00000.root'],
        dataset=ParentDataset(
            parent=gen,
            units_per_task=1
        ),
        category=sim_resources
    )

    digi = Workflow(
        label='digi_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['digi']),
        sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['digi']),
        merge_size=-1,  # Don't merge files we don't plan to keep
        cleanup_input=True,
        #cleanup_input=False,
        outputs=['DIGI-00000.root'],
        dataset=ParentDataset(
            parent=sim,
            units_per_task=1
        ),
        category=digi_resources
    )

    hlt = Workflow(
        label='hlt_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['hlt']),
        sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['hlt']),
        merge_size=-1, # Don't merge files we don't plan to keep
        cleanup_input=True,
        #cleanup_input=False,
        outputs=['HLT-00000'],
        dataset=ParentDataset(
            parent=digi,
            units_per_task=1
        ),
        category=hlt_resources
    )

    reco = Workflow(
        label='reco_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['reco']),
        sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['reco']),
        merge_size=-1,  # Don't merge files we don't plan to keep
        cleanup_input=True,
        #cleanup_input=False,
        outputs=['RECO-00000.root'],
        dataset=ParentDataset(
            parent=hlt,
            units_per_task=2
        ),
        category=reco_resources
    )

    maod = Workflow(
        label='mAOD_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['maod']),
        sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['maod']),
        merge_size='256M',
        #merge_size=-1,
        cleanup_input=True,
        #cleanup_input=False,
        outputs=['MAOD-00000.root'],
        dataset=ParentDataset(
            parent=reco,
            units_per_task=3
        ),
        category=maod_resources
    )

    naod = Workflow(
        label='nAOD_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['naod']),
        sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['naod']),
        merge_size='256M',
        merge_command='python haddnano.py @outputfiles @inputfiles',
        extra_inputs=[os.path.join(PATH_TO_NAOD_CMSSW,'src/PhysicsTools/NanoAODTools/scripts/haddnano.py')],
        cleanup_input=False, # Leave the MAOD files
        outputs=['NAOD-00000.root'],
        dataset=ParentDataset(
            parent=maod,
            units_per_task=3
        ),
        category=naod_resources
    )
    Justnaod = Workflow(
        label='nAOD_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['naod']),
        sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['naod']),
        merge_size='256M',
        merge_command='python haddnano.py @outputfiles @inputfiles',
        extra_inputs=[os.path.join(PATH_TO_NAOD_CMSSW,'src/PhysicsTools/NanoAODTools/scripts/haddnano.py')],
        cleanup_input=False, # Leave the MAOD files
        outputs=['NAOD-00000.root'],
        dataset=Dataset(
            files=lhe_dir,
            files_per_task=1,
        ),
        category=naod_resources
    )
    wf.extend([Justnaod])
    # Specify which steps to run
#    if (STEPS == 'throughGEN'):
#        wf.extend([gen])
#    elif (STEPS == 'throughMAOD'):
#        wf.extend([gen,sim,digi,hlt,reco,maod])
#    elif (STEPS == 'throughNAOD'):
#        wf.extend([gen,sim,digi,hlt,reco,maod,naod])
#    else:
#        print "\nUnknown steps" , STEPS , "exiting...\n"
#        raise Exception

config = Config(
    label=master_label,
    workdir=workdir_path,
    plotdir=plotdir_path,
    storage=storage,
    workflows=wf,
    advanced=AdvancedOptions(
        dashboard = False,
        bad_exit_codes=[127, 160],
        log_level=1,
        payload=10,
        xrootd_servers=[
#                       'ndcms.crc.nd.edu',
                       'cmsxrootd.fnal.gov',
                       'deepthought.crc.nd.edu']
    )
)

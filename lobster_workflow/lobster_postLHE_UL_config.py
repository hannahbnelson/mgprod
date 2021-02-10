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

# Specfy the run setup
#RUN_SETUP = 'full_production'
#RUN_SETUP = 'mg_studies'
RUN_SETUP = 'testing'

# Specify the UL year
#UL_YEAR = 'UL16'
UL_YEAR = 'UL16APV'
#UL_YEAR = 'UL17'
#UL_YEAR = 'UL18'

# Speciy the LHE sample
# Note: The workflows in each of the input directories should all be uniquely named w.r.t each other
input_dirs = [
    #os.path.join(input_path_full,"kmohrman/LHE_step/2019_04_19/ttXJetTests-HanV4Model-xqcut10/v1")
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_ULCheck-UL16/v1"),
    os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_ULCheck-UL16APV/v1"),
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_ULCheck-UL17/v1"),
    #os.path.join(input_path_full,"kmohrman/LHE_step/FullR2Studies/ULChecks/ttXJet-tXq_ULCheck-UL18/v1"),
]

# Name the output
out_ver = "v1"   # The version index for the OUTPUT directory
#out_tag = "Round6/Batch9"                               # For 'full_production' setup
out_tag = "2019_04_19/TEST"

# Only run over lhe steps from specific processes/coeffs/runs
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []  # (i.e. MG starting points)

master_label = 'EFT_ALL_postLHE_{tstamp}'.format(tstamp=timestamp_tag)

if RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/postLHE_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
elif RUN_SETUP == 'full_production':
    # For Large MC production
    output_path  = "/store/user/$USER/FullProduction/{tag}/postLHE_step/{ver}".format(tag=out_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/{tag}/postLHE_step/{ver}".format(tag=out_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/FullProduction/{tag}/postLHE_step/{ver}".format(tag=out_tag,ver=out_ver)
elif RUN_SETUP == 'testing':
    grp_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/postLHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
else:
    print "Unknown run setup, {setup}".format(setup=RUN_SETUP)
    raise ValueError

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

lhe_dirs = []
for path in input_dirs:
    for fd in os.listdir(path):
        if fd.find('lhe_step_') < 0:
            continue
        arr = fd.split('_')
        p,c,r = arr[2],arr[3],arr[4]
        if len(regex_match([p],process_whitelist)) == 0:
            continue
        elif len(regex_match([c],coeff_whitelist)) == 0:
            continue
        elif len(regex_match([r],runs_whitelist)) == 0:
            continue
        relpath = os.path.relpath(path,input_path_full)
        lhe_dirs.append(os.path.join(relpath,fd))

# Specify lhe dirs by hand
#lhe_dirs = [
#    #"kmohrman/LHE_step/FullR2Studies/PreliminaryStudies/tHq4f_testOldGenprod-HanV4/v1/lhe_step_tHq4f_testOldGenprodHanV4_run2"
#    "kmohrman/LHE_step/FullR2Studies/PreliminaryStudies/ttHJet_testOldGenprod-testModels/v1/lhe_step_ttHJet_testOldGenproddim6TopMay20GST_run1", # 100k
#]

#################################################################
# Worker Res.:
#   Cores:  12    | 4
#   Memory: 16000 | 8000
#   Disk:   13000 | 6500
#################################################################
# Need to be careful with using 'runtime' setting, as it can cause us to exceed the workers resources

gen_resources = Category(
    name='gen',
    cores=1,
    memory=600,
    disk=1000,
    tasks_min=12,
    tasks_max=3000,
    mode='fixed'
)

sim_resources = Category(
    name='sim',
    #cores=12,
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

# Not sure what to put for this... same as digi???
hlt_resources = Category(
    name='hlt',
    cores=2,
    memory=3000,
    disk=6000,
    mode='fixed'
)

reco_resources = Category(
    name='reco',
    cores=3,
    memory=3500,
    disk=3000,
    mode='fixed'
)

maod_resources = Category(
    name='maod',
    cores=2,
    memory=2500,
    disk=2000,
    mode='fixed'
)

naod_resources = Category(
    name='naod',
    cores=2,
    memory=2500,
    disk=2000,
    mode='fixed'
)

#################################################################

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

# Put the gen configs into the ul cfg map
fragment_map = ul_cfg_map[UL_YEAR]
for k,v in gen_ul_cfg_map[UL_YEAR].iteritems():
    fragment_map[k] = v

#print("Fragement map!")
#for k,v in fragment_map.iteritems():
    #print k,":",v

gs_mods_dict = {}

gs_mods_dict["base"] = {}
gs_mods_dict["base"]["base"] = []
#gs_mods_dict["ttHJet"] = {}
#gs_mods_dict["ttHJet"]['qCut15'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 15|g']
#gs_mods_dict["ttHJet"]['qCut19'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 19|g']
#gs_mods_dict["ttHJet"]['qCut25'] = ['s|JetMatching:qCut = 19|JetMatching:qCut = 25|g']

# Don't need to turn off matching for single top samples since using cfg with matching already turned off
#gs_mods_dict["tllq4fNoSchanWNoHiggs0p"] = {}
#gs_mods_dict["tllq4fNoSchanWNoHiggs0p"]['MatchOff'] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']

# Don't need to turn off matching for single top samples since using cfg with matching already turned off
#gs_mods_dict["tHq4f"] = {}
#gs_mods_dict["tHq4f"]['MatchOff'] = ['s|JetMatching:merge = on|JetMatching:merge = off|g']

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
    p,c,r = arr[2],arr[3],arr[4]
    #print("p c r:",p,c,r)
    if p in gs_mods_dict:
        gs_mods = gs_mods_dict[p]
    else:
        gs_mods = gs_mods_dict["base"]
    for mod_tag,sed_str_list in gs_mods.iteritems():
        wf_fragments = {}
        for step in wf_steps:
            if step == 'gen':
                template_loc = fragment_map[p][step]
            else:
                template_loc = fragment_map["all_procs"][step]
            #print "template loc !!", template_loc
            # Only the GEN-SIM step can be modified
            if step == 'gen':
                head,tail = os.path.split(template_loc)
                # This should be a unique identifier within a single lobster master to ensure we dont overwrite a cfg file too early
                cfg_tag = '{tag}-{idx}'.format(tag=mod_tag,idx=idx)
                tail = tail.replace("cfg.py","{tag}_cfg.py".format(tag=cfg_tag))
                mod_loc = os.path.join(MODIFIED_CFG_DIR,tail)
                shutil.copy(template_loc,mod_loc)
                for sed_str in sed_str_list:
                    if sed_str:
                        run_process(['sed','-i','-e',sed_str,mod_loc])
            else:
                mod_loc = template_loc
            wf_fragments[step] = mod_loc
        if mod_tag == 'base': mod_tag = ''
        label_tag = "{p}_{c}{mod}_{r}".format(p=p,c=c,r=r,mod=mod_tag)

        #print "\nThis is the wf_fragments:",wf_fragments,"\n"

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
                #files_per_task=2,
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
            cleanup_input=True,
            outputs=['MAOD-00000.root'],
            dataset=ParentDataset(
                parent=reco,
                units_per_task=3
            ),
            category=maod_resources
        )

        # No idea about these settings... just go with same as maod?
        naod = Workflow(
            label='nAOD_step_{tag}'.format(tag=label_tag),
            command='cmsRun {cfg}'.format(cfg=wf_fragments['naod']),
            sandbox=cmssw.Sandbox(release=rel_map[UL_YEAR]['naod']),
            merge_size='256M',
            cleanup_input=False,
            outputs=['NAOD-00000.root'],
            dataset=ParentDataset(
                parent=maod,
                units_per_task=3
            ),
            category=naod_resources
        )

        wf.extend([gen])
        #wf.extend([gen,sim,digi,hlt,reco,maod])
        #wf.extend([gen,sim,digi,hlt,reco,maod,naod])

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
        xrootd_servers=['ndcms.crc.nd.edu',
                       'cmsxrootd.fnal.gov',
                       'deepthought.crc.nd.edu']
    )
)

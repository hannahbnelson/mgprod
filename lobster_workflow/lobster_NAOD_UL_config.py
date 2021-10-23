import datetime
import os
import sys
import shutil

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, Dataset,ParentDataset, StorageConfiguration, Workflow

sys.path.append(os.getcwd())
from helpers.utils import regex_match, run_process

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')
input_path = "/store/user/"
input_path_full = "/hadoop" + input_path

#master_label = 'EFT_testNAOD_T3_postLHE_{tstamp}'.format(tstamp=timestamp_tag)
master_label = 'EFT_testNAOD_crc_postLHE_{tstamp}'.format(tstamp=timestamp_tag)


########## Set up the lobster cfg ##########

# Note: Should not have to modify things outside of this section, unless you want to:
#    - Hardcode maod dirs to use

PATH_TO_NAOD_CMSSW = "/afs/crc.nd.edu/user/k/kmohrman/CMSSW_Releases/CMSSW_10_6_19_patch2"
#PATH_TO_NAOD_CMSSW = "CMSSW_10_6_19_patch2"

# Specfy the run setup
#RUN_SETUP = 'full_production'
#RUN_SETUP = 'mg_studies'
RUN_SETUP = 'testing'

# Specify the UL year
#UL_YEAR = 'UL16'
#UL_YEAR = 'UL16APV'
UL_YEAR = 'UL17'
#UL_YEAR = 'UL18'

# Name the output
out_ver = "v1"   # The version index for the OUTPUT directory
out_tag = "FullR2Studies/ValidationChecks/ttXJet_dim6TopMay20GST_run0StartPt_qCutScan_GEN_"
prod_tag = "Round1/Batch1"

# Append UL year to out tag
out_tag = out_tag + UL_YEAR

# Only run over moad steps from specific processes/coeffs/runs
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []  # (i.e. MG starting points)

# Specify the input directories. Note: The workflows in each of the input directories should all be uniquely named w.r.t each other
input_dirs = [
    os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL17/Round1/Batch1/postLHE_step/v2/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL17/Round1/Batch2/postLHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL17/Round1/Batch3/postLHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL17/Round1/Batch4/postLHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL18/Round1/Batch1/postLHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL18/Round1/Batch2/postLHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL18/Round1/Batch3/postLHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL18/Round1/Batch4/postLHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL16/Round1/Batch1/postLHE_step/v1/"),
    #os.path.join(input_path_full,"kmohrman/FullProduction/FullR2/UL16APV/Round1/Batch1/postLHE_step/v1/"),
]



########## Select input directories according to whitelists ##########

maod_dirs = []
for path in input_dirs:
    for fd in os.listdir(path):
        if fd.find('mAOD_step_') < 0:
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
        maod_dirs.append(os.path.join(relpath,fd))

'''
# Hardcode the maod dirs by hand
# Do not include a trailing slash, as we're not expecting it when we use os.path.split later on
maod_dirs = [
    "kmohrman/postLHE_step/FullR2Studies/ULChecks/ttXJet-tXq_testFullULWFonCRC_ULCheck_UL17/v6/mAOD_step_ttHJet_testUpdateGenproddim6TopMay20GST_run1"
    #"kmohrman/FullProduction/FullR2/UL17/Round1/Batch1/postLHE_step/v1/mAOD_step_ttHJet_all22WCsStartPtCheckdim6TopMay20GST_run0"
]
'''


########## Set up output based on run setup ##########

if RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/naodOnly_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/naodOnly_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/naodOnly_step/{tag}/{ver}".format(tag=out_tag,ver=out_ver)
elif RUN_SETUP == 'full_production':
    # For Large MC production
    output_path  = "/store/user/$USER/FullProduction/FullR2/{ul}/{tag}/naodOnly_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/FullR2/{ul}/{tag}/naodOnly_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/FullProduction/FullR2/{ul}/{tag}/naodOnly_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=out_ver)
elif RUN_SETUP == 'testing':
    # For test runs (where you do not intend to keep the output)
    grp_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/naodOnly_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    workdir_path = "/tmpscratch/users/$USER/naodOnly_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
    plotdir_path = "~/www/lobster/naodOnly_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=out_ver)
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

naod_resources = Category(
    name='naod',
    cores=2,
    memory=3500,
    disk=2000,
    mode='fixed'
)


########## Set up dictionary for cfg files ##########

wf_steps = ['naod']
ul_base = 'ul_cfgs'

ul_cfg_map = {
    'UL16' : {
        'all_procs' : {
            'naod' : os.path.join(ul_base,'UL16_NAOD_cfg.py'),
        }
    },
    'UL16APV' : {
        'all_procs' : {
            'naod' : os.path.join(ul_base,'UL16APV_NAOD_cfg.py'),
        }
    },
    'UL17' : {
        'all_procs' : {
            'naod' : os.path.join(ul_base,'UL17_NAOD_cfg.py'),
        }
    },
    'UL18' : {
        'all_procs' : {
            'naod' : os.path.join(ul_base,'UL18_NAOD_cfg.py'),
        }
    }

}

fragment_map = ul_cfg_map[UL_YEAR]


########## Generate workflows ##########

wf = []
print "Generating workflows:"
for idx,maod_dir in enumerate(maod_dirs):
    # Raise exception if trying to make UL sample but the UL year is not in the path anywhere
    if ( (UL_YEAR not in maod_dir) or ((UL_YEAR == "UL16") and ("APV" in maod_dir)) ):
        print "\nWARNING: UL year selected, but moad dir path does not contain this UL year in it anywhere, are you sure you have the right path? Please double check."
        print "\tUL Year:" , UL_YEAR, "\n\tPath:" , maod_dir, "\nExiting...\n"
        raise Exception
    print "\t[{0}/{1}] LHE Input: {dir}".format(idx+1,len(maod_dirs),dir=maod_dir)
    head,tail = os.path.split(maod_dir)
    arr = tail.split('_')
    p,c,r = arr[2],arr[3],arr[4]
    #print("p c r:",p,c,r)
    wf_fragments = {}
    for step in wf_steps:
        template_loc = fragment_map["all_procs"][step]
        wf_fragments[step] = template_loc
        label_tag = "{p}_{c}_{r}".format(p=p,c=c,r=r)

    naod = Workflow(
        label='nAOD_step_{tag}'.format(tag=label_tag),
        command='cmsRun {cfg}'.format(cfg=wf_fragments['naod']),
        sandbox=cmssw.Sandbox(release=PATH_TO_NAOD_CMSSW),
        #merge_size='256M',
        merge_size='1000M',
        merge_command='python haddnano.py @outputfiles @inputfiles',
        extra_inputs=[os.path.join(PATH_TO_NAOD_CMSSW,'src/PhysicsTools/NanoAODTools/scripts/haddnano.py')],
        cleanup_input=False, # Leave the MAOD files
        outputs=['NAOD-00000.root'],
        dataset=Dataset(
            files=maod_dir,
            files_per_task=1,
            patterns=["*.root"]
        ),
        category=naod_resources
    )

    wf.extend([naod])

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

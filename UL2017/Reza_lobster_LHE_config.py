#IMPORTANT: The workers that are submitted to this lobster master, MUST come from T3 resources

import datetime
import os
import sys

from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, MultiProductionDataset, StorageConfiguration, Workflow

#sys.path.append(os.getcwd())
sys.path.append('/afs/crc.nd.edu/user/r/rgoldouz/MakeLobsterJobs/UL/mgprod/lobster_workflow')
from helpers.utils import regex_match

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

#events_per_gridpack = 5e5
#events_per_gridpack = 100e3
events_per_gridpack = 5e5
events_per_lumi = 500

#RUN_SETUP = 'local'
RUN_SETUP = 'UL_production'
#RUN_SETUP = 'mg_studies'
#RUN_SETUP = 'lobster_test'

#UL_YEAR = 'UL16'
#UL_YEAR = 'UL16APV'
UL_YEAR = 'UL17'
#UL_YEAR = 'UL18'
if ((UL_YEAR != 'UL16') and (UL_YEAR != 'UL16APV') and (UL_YEAR != 'UL17') and (UL_YEAR != 'UL18')):
    UL_YEAR = "NONE"

version = "v1"
#grp_tag = "FullR2Studies/PreliminaryStudies/tHq4f_testOldGenprod-HanV4"
#grp_tag = "FullR2Studies/ULChecks/ttH-ttHJet_dim6TopMay20GST_JustctGctp-check-dim6syntaxes_"
grp_tag = "FullR2Studies/ValidationChecks/ttbarJet_dim6TopMay20GST_1dAxisScans-2heavy-2heavy2light_"
#grp_tag = "ForPhenoJhepReviewStudies/ttZJet_sampleForDoubleCheckingQcut_dim6TopMay20GST_"

prod_tag = "Round1/Batch3"

if (UL_YEAR != "NONE"):
    grp_tag = grp_tag + UL_YEAR

print grp_tag

# Only run over gridpacks from specific processes/coeffs/runs
#process_whitelist = ['^ttllNuNuNoHiggs$','^ttH$','^ttlnu$']
#coeff_whitelist   = ['^NoDim6$']
#runs_whitelist    = ['^run0$']    # (i.e. MG starting points)
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []    # (i.e. MG starting points)

master_label = 'T3_EFT_{tstamp}'.format(tstamp=timestamp_tag)

#if RUN_SETUP == 'local':
#    # Overwrite the input path to point to a local AFS file directory with the desired gridpacks
#    input_path      = "/afs/crc.nd.edu/user/a/awightma/Public/git_repos/mgprod/lobster_workflow/local_gridpacks/
#    input_path_full = input_path
#    test_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
#    output_path  = "/store/user/$USER/tests/{tag}".format(tag=test_tag)
#    workdir_path = "/tmpscratch/users/$USER/tests/{tag}".format(tag=test_tag)
#    plotdir_path = "~/www/lobster/tests/{tag}".format(tag=test_tag)
#    inputs = [
#        "file://" + input_path,    # For running on gridpacks in a local directory
#    ]
#elif RUN_SETUP == 'mg_studies':

if RUN_SETUP == 'mg_studies':
    # For MadGraph test studies
    output_path  = "/store/user/$USER/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
    plotdir_path = "~/www/lobster/LHE_step/{tag}/{ver}".format(tag=grp_tag,ver=version)
elif RUN_SETUP == 'UL_production':
    # For Large MC production
    output_path  = "/store/user/$USER/FullProduction/FullR2/{ul}/{tag}/LHE_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/FullProduction/FullR2/{ul}/{tag}/LHE_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=version)
    plotdir_path = "~/www/lobster/FullProduction/FullR2/{ul}/{tag}/LHE_step/{ver}".format(ul=UL_YEAR,tag=prod_tag,ver=version)
elif RUN_SETUP == 'lobster_test':
    # For lobster workflow tests
    grp_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
    output_path  = "/store/user/$USER/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
    workdir_path = "/tmpscratch/users/$USER/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
    plotdir_path = "~/www/lobster/LHE_step/tests/{tag}/{ver}".format(tag=grp_tag,ver=version)
else:
    print "Unknown run setup, %s" % (RUN_SETUP)
    raise ValueError

input_path = "/store/user/"
input_path_full = "/hadoop" + input_path

storage = StorageConfiguration(
    input = [
        "hdfs://eddie.crc.nd.edu:19000"  + input_path,
        "root://deepthought.crc.nd.edu/" + input_path,  # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + input_path,
        "srm://T3_US_NotreDame"          + input_path,
    ],
    output=[
        "hdfs://eddie.crc.nd.edu:19000"  + output_path,
         #ND is not in the XrootD redirector, thus hardcode server.
        "root://deepthought.crc.nd.edu/" + output_path, # Note the extra slash after the hostname!
        "gsiftp://T3_US_NotreDame"       + output_path,
        "srm://T3_US_NotreDame"          + output_path,
        "file:///hadoop"                 + output_path,
    ],
    disable_input_streaming=True,
)

gridpack_list = [
    #"kmohrman/gridpack_scans/ForPhenoJhepReviewStudies/ttWJet_cbWCheck1dForPhenodim6TopMay20GSTAxisScan_run1_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",
]

FullR2_gridpack_list = [
    "rgoldouz/gridpack_scans/tuFCNC_tllProduction_noH_NRF2_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz",
    "rgoldouz/gridpack_scans/tuFCNC_ullDecay_noH_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz"    ,
    "rgoldouz/gridpack_scans/tuFCNC_tHProduction_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz",
    "rgoldouz/gridpack_scans/tuFCNC_uHDecay_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz",
]

if RUN_SETUP == 'UL_production':
    gridpack_list = FullR2_gridpack_list

wf_steps = ['lhe']
fragment_map = {
    'default': {
        'lhe': 'python_cfgs/LHE/HIG-RunIIFall17wmLHE-00000_1_cfg.py',
    },
}
ul_fragment_map = {
    'UL16' : {
        'lhe' : 'ul_cfgs/UL16_LHE_cfg.py',
    },
    'UL16APV' : {
        'lhe' : 'ul_cfgs/UL16APV_LHE_cfg.py',
    },
    'UL17' : {
        'lhe' : 'ul_cfgs/UL17_LHE_cfg.py',
    },
    'UL18' : {
        'lhe' : 'ul_cfgs/UL18_LHE_cfg.py',
    },
}

event_multiplier = {
    'default': 1.0,
    'tllProduction': 10.0,
    'ullDecay': 4.0,
    'tHProduction': 2.0,
    'uHDecay': 1.0,
}

cat_dict = {}

wf = []
print "Generating workflows:"
for idx,gridpack in enumerate(gridpack_list):
    head,tail = os.path.split(gridpack)
    arr = tail.split('_')
    p,c,r = arr[0],arr[1],arr[2]
    c = c.replace('-','')   # Lobster doesn't like labels with dashes in them

    label='lhe_step_{p}_{c}'.format(p=p,c=c)
    cat_name = 'lhe_{p}_{c}'.format(p=p,c=c)
    print "Label and cat name:", label,cat_name
    if not cat_name in cat_dict:
        cat_dict[cat_name] = Category(
            name=cat_name,
            #mode='fixed',
            cores=1,
            memory=1200,
            disk=2900
        )
    cat = cat_dict[cat_name]

    wf_fragments = {}
    for step in wf_steps:
        if (UL_YEAR == "NONE"):
            if fragment_map.has_key(p) and fragment_map[p].has_key(step):
                wf_fragments[step] = fragment_map[p][step]
            else:
                wf_fragments[step] = fragment_map['default'][step]
        else:
            wf_fragments[step] = ul_fragment_map[UL_YEAR][step]
    #print wf_fragments
    multiplier = event_multiplier['default']
    if event_multiplier.has_key(c):
        multiplier = event_multiplier[c]
    nevents = int(multiplier*events_per_gridpack)
    print "\t[{0}/{1}] Gridpack: {gp} (nevts {events})".format(idx+1,len(gridpack_list),gp=gridpack,events=nevents)
    if (UL_YEAR == "NONE"):
        rel = 'CMSSW_9_3_1'
    else:
        rel = 'CMSSW_10_6_19_patch3'
    lhe = Workflow(
        label=label,
        command='cmsRun {cfg}'.format(cfg=wf_fragments['lhe']),
        sandbox=cmssw.Sandbox(release=rel),
        merge_size=-1,  # Don't merge the output files, to keep individuals as small as possible
        cleanup_input=False,
        globaltag=False,
        #outputs=['HIG-RunIIFall17wmLHE-00000ND.root'],
        outputs=['LHE-00000.root'],
        dataset=MultiProductionDataset(
            gridpacks=gridpack,
            events_per_gridpack=nevents,
            events_per_lumi=events_per_lumi,
            lumis_per_task=1,
            randomize_seeds=True
        ),
        category=cat
    )
    wf.extend([lhe])

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

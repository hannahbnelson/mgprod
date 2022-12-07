#IMPORTANT: The workers that are submitted to this lobster master, MUST come from T3 resources

import datetime
import os
import sys
from os import path
from lobster import cmssw
from lobster.core import AdvancedOptions, Category, Config, MultiProductionDataset, StorageConfiguration, Workflow

sys.path.append(os.getcwd())
from helpers.utils import regex_match

timestamp_tag = datetime.datetime.now().strftime('%Y%m%d_%H%M')

events_per_gridpack = 100e3
events_per_lumi = 500

RUN_SETUP = 'UL_production'
UL_YEAR = 'UL17'
version = "v1"
prod_tag = "nanoGen"

# Only run over gridpacks from specific processes/coeffs/runs
# process_whitelist = ['^ttllNuNuNoHiggs$','^ttH$','^ttlnu$']
# coeff_whitelist   = ['^NoDim6$']
# runs_whitelist    = ['^run0$']    # (i.e. MG starting points)
process_whitelist = []
coeff_whitelist   = []
runs_whitelist    = []    # (i.e. MG starting points)

master_label = 'EFT_CRC_full_{tstamp}'.format(tstamp=timestamp_tag)

grp_tag = "lobster_{tstamp}".format(tstamp=timestamp_tag)
output_path  = "/store/user/$USER/NanoGen/{tag}".format(tag=grp_tag)
workdir_path = "/tmpscratch/users/$USER/NanoGen/{tag}".format(tag=grp_tag)
plotdir_path = "~/www/lobster/NanoGen/{tag}".format(tag=grp_tag)

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
    "hnelson2/gridpack_scans/MLsamples/ttHJetgg_ctGTesting01AxisScan_run0_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz",
]

nanoGen = Category(
            name="nanoGen",
            cores=1,
            memory=1500,
            disk=2900
        )

wf = []

cmsswSSource = '/afs/crc.nd.edu/user/h/hnelson2/cmssw/CMSSW_10_6_26'
cmsRun_config = '/afs/crc.nd.edu/user/h/hnelson2/mgprod/lobster_workflow/ul_cfgs/nanoGen2017_LO_cfg.py'

print "Generating workflows:"

for gridpack in gridpack_list.items():
    GN = Workflow(
        label='NanoGen_{tag}'.format(tag=key),
        command='cmsRun {cfg}'.format(cfg=cmsRun_config),
        sandbox=cmssw.Sandbox(release=cmsswSSource),
        merge_size= '256M',
        merge_command='python haddnano.py @outputfiles @inputfiles',
        extra_inputs=['/afs/crc.nd.edu/user/h/hnelson2/cmssw/CMSSW_10_6_26/src/PhysicsTools/NanoAODTools/scripts/haddnano.py'],
        cleanup_input=False,
        globaltag=False,
        outputs=['nanoGen.root'],
        dataset=MultiProductionDataset(
            gridpacks=gridpack,
            events_per_gridpack=events_per_gridpack,
            events_per_lumi=events_per_lumi,
            lumis_per_task=1,
            randomize_seeds=True
        ),
        category=nanoGen
    )
    wf.extend([GN])

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

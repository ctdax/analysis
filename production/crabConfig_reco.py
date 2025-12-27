import sys
from CRABClient.UserUtilities import config

Type='reco'
inputDataset='/gensim_gluino1800_0p1mm_lightDecay_10000Events/cthompso-gensim_gluino1800_0p1mm_lightDecay_10000Events-03adeb32831e36d194df00404504a695/USER'
maxEvents=10000
mass=1800
ctau='0p1'
quarkDecay='light'
njobs=100
memory=3000

config = config()

config.section_('General')
config.General.requestName = f'{Type}_noPU_gluino{mass}_{ctau}mm_{quarkDecay}Decay_{maxEvents}Events'
config.General.workArea = '/eos/user/c/cthompso/crab_projects'
config.General.transferOutputs = True
config.General.instance = 'prod'

config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = f'{Type}.py'
config.JobType.allowUndistributedCMSSW = True
config.JobType.maxMemoryMB = memory
config.JobType.outputFiles = []

config.section_('Data')
config.Data.inputDataset = inputDataset
config.Data.inputDBS = 'https://cmsweb.cern.ch/dbs/prod/phys03/DBSReader'
config.Data.splitting = 'FileBased'
config.Data.totalUnits = 100
config.Data.unitsPerJob = 1
config.Data.outputDatasetTag = config.General.requestName
config.Data.outLFNDirBase = '/store/user/cthompso/HSCP'
config.Data.publication = True

config.section_('Site')
config.Site.whitelist = ['T2_DE_DESY','T2_FR_IPHC','T2_CH_CERN','T2_IT_Bari','T1_IT_*','T2_US_*','T3_US_*']
config.Site.storageSite = 'T3_US_FNALLPC'
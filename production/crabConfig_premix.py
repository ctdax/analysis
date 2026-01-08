import sys
from CRABClient.UserUtilities import config

Type='premix'
inputDataset='/gensim_noPU_gluino1800_1000mm_heavyDecay_10000Events/cthompso-reco_noPU_gluino1800_1000mm_heavyDecay_10000Events-0a7623ffb3e17311de012aded75a5bb5/USER'
maxEvents=10000
mass=1800
ctau='1000'
quarkDecay='heavy'
njobs=200
memory=3000

config = config()

config.section_('General')
config.General.requestName = f'{Type}_gluino{mass}_{ctau}mm_{quarkDecay}Decay_{maxEvents}Events'
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
config.Data.totalUnits = njobs
config.Data.unitsPerJob = 1
config.Data.outputDatasetTag = config.General.requestName
config.Data.outLFNDirBase = '/store/user/cthompso/HSCP'
config.Data.publication = True

config.section_('Site')
config.Site.whitelist = ['T2_DE_DESY','T2_FR_IPHC','T2_CH_CERN','T2_IT_Bari','T1_IT_*','T2_US_*','T3_US_*']
config.Site.storageSite = 'T3_US_FNALLPC'
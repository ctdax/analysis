import sys
from CRABClient.UserUtilities import config

Type='gensim'
maxEvents=10000
mass=1800
ctau=1000
quarkDecay='heavy'
njobs=100
memory=3000

config = config()

config.section_('General')
config.General.requestName = f'{Type}_noPU_gluino{mass}_{ctau}mm_{quarkDecay}Decay_{maxEvents}Events'
config.General.workArea = '/eos/user/c/cthompso/crab_projects'
config.General.transferOutputs = True
config.General.instance = 'prod'

config.section_('JobType')
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = f'{Type}.py'
config.JobType.allowUndistributedCMSSW = True
config.JobType.maxMemoryMB = memory
config.JobType.pyCfgParams = [f'maxEvents={maxEvents}',f'mass={mass}',f'ctau={ctau}',f'quarkDecay={quarkDecay}',f'outputFile={Type}.root']
config.JobType.outputFiles = []

config.section_('Data')
config.Data.splitting = 'EventBased'
config.Data.totalUnits = maxEvents
config.Data.unitsPerJob = njobs
config.Data.outputDatasetTag = config.General.requestName
config.Data.outLFNDirBase = '/store/user/cthompso/HSCP'
config.Data.outputPrimaryDataset = f'{Type}_noPU_gluino{mass}_{ctau}mm_{quarkDecay}Decay_{maxEvents}Events'
config.Data.publication = True

config.section_('Site')
config.Site.whitelist = ['T2_DE_DESY','T2_FR_IPHC','T2_CH_CERN','T2_IT_Bari','T1_IT_*','T2_US_*','T3_US_*']
config.Site.storageSite = 'T3_US_FNALLPC'
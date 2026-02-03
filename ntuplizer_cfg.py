import os
import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
from FWCore.ParameterSet.VarParsing import VarParsing
from HSCPAnalysis.Ntuplizer.input_parser import xparser

options = VarParsing('analysis')

# defaults
options.maxEvents = -1 # -1 means all events
options.register ('outputEvery', 500, VarParsing.multiplicity.singleton, VarParsing.varType.int, "")
options.register ('isAOD', True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "")
options.register ('isData', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "")
options.register ('year', 2018, VarParsing.multiplicity.singleton, VarParsing.varType.int, "")
options.register ('era', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "")

options.register ('triggerFilter', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "")

options.register ('doCrab', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "")
#
options.parseArguments()
xparser = xparser(options.year, options.era, options.doCrab)
#
GTAG = ''
# to be changed : adapt the GTAG depending on the era
if options.isData:
    if (options.year==2018 or options.year==2017):
        GTAG = '106X_dataRun2_v36'
    elif options.year==2024:
        GTAG = '150X_dataRun3_v2'
        # GTAG = '140X_dataRun3_v20'
    elif options.year==2023:
        GTAG = '130X_dataRun3_PromptAnalysis_v1'
    elif options.year==2022:
        if (options.era=="C" or options.era=="D" or options.era=="E"):
            GTAG = '124X_dataRun3_v15'
        elif (options.era=="F" or options.era=="G"):
            GTAG = '130X_dataRun3_PromptAnalysis_v1'
else:
    if options.year==2017:
        GTAG = '106X_mc2017_realistic_v10'
    elif options.year==2018:
        GTAG = '106X_upgrade2018_realistic_v16_L1v1'

    elif options.year==2024:
        GTAG = '150X_mcRun3_2024_realistic_v2'
    elif options.year==2023:
        if (options.era=="C"):
            GTAG = '130X_mcRun3_2023_realistic_v14'
        elif (options.era=="D"):
            GTAG = '130X_mcRun3_2023_realistic_postBPix_v2'
    elif options.year==2022:
        if (options.era=="C" or options.era=="D"):
            GTAG = '130X_mcRun3_2022_realistic_v5'
        if (options.era=="E" or options.era=="F" or options.era=="G"):
            GTAG = '130X_mcRun3_2022_realistic_postEE_v6'


isAOD = options.isAOD

## print configuration
###############################################################
print('\n')
print('CMSSW version     : {}'.format(os.environ['CMSSW_VERSION']))
print('SCRAM ARCH        : {}'.format(os.environ['SCRAM_ARCH']))
print('Global Tag        : {}'.format(GTAG))
print('is AOD            : {}'.format(options.isAOD))
print('is Data           : {}'.format(options.isData))
print('Year              : {}'.format(options.year))
print('Era (even on MC!) : {}'.format(options.era))
print('TriggerFilter     : {}'.format(options.triggerFilter))
print('Output File       : {}'.format(options.outputFile))
print('Input Files       : {}'.format(options.inputFiles))
print('\n')
#_____________________________________________________________#

if options.isData and options.era=='':
    raise RuntimeError("For data, you must provide an era corresponding to the dataset (2017: B,C,D,E,F ; 2018: A,B,C,D ; 2022: C,D,E,F,G ; 2023: C,D ; 2024: C,D,E,F,G,H,I)")


process = cms.Process("HSCPAnalysis")

#if options.isData: process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load("HSCPAnalysis.Ntuplizer.metFilters_cff")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = options.outputEvery
process.MessageLogger.cerr.threshold = "INFO"
#process.MessageLogger.PrimaryVertices = dict(limit = 0)

process.options   = cms.untracked.PSet(wantSummary = cms.untracked.bool(False))

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

# Define files of dataset
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(options.inputFiles),
                            inputCommands = cms.untracked.vstring("keep *", "drop *_MEtoEDMConverter_*_*")
)
# Number of events to be skipped (0 by default)
process.source.skipEvents = cms.untracked.uint32(0)
# Register fileservice for output file
process.TFileService = cms.Service(
    "TFileService", fileName=cms.string(options.outputFile)
)

## Conditions data
###############################################################
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, GTAG, '')
### this is necessary to get the simulation geometry
if not options.isData:
    process.GlobalTag.toGet = cms.VPSet(
    cms.PSet(record = cms.string("GeometryFileRcd"),
            tag = cms.string("XMLFILE_Geometry_101YV4_Extended2018_mc"),
            label = cms.untracked.string('Extended'),
            )
    )

if options.isData:
    lumiToProcess = xparser.getLS()
    import FWCore.PythonUtilities.LumiList as LumiList
    process.source.lumisToProcess = LumiList.LumiList(filename = lumiToProcess).getVLuminosityBlockRange()

###############################################################

triggerList = ["HLT_PFMET120_PFMHT120_IDTight_v",
               "HLT_PFHT500_PFMET100_PFMHT100_IDTight_v",
               "HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60_v",
               "HLT_MET105_IsoTrk50_v",
               "HLT_Mu50_v",
               "HLT_IsoMu24_v",
               "HLT_IsoMu27_v"] #2018 + 2022-2024 
if options.year == 2017:
    triggerList = ["HLT_PFMET120_PFMHT120_IDTight_v",
               "HLT_PFHT500_PFMET100_PFMHT100_IDTight_v",
               "HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60_v",
               "HLT_MET105_IsoTrk50_v",
               "HLT_Mu50_v",
               "HLT_IsoMu27_v"]
 
###############################################################

triggerFilter=options.triggerFilter

if not options.isData and isAOD:
   process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
   process.genParticlesSkimmed = cms.EDFilter("GenParticleSelector",
        filter = cms.bool(False),
        src = cms.InputTag("genParticles"),
        cut = cms.string('pt > 5.0')
   )

########################################################################
K,C,SF0,SF1 = 1,1,1,1
IasTemplate = ''
if options.isData:
    if options.year == 2017:
        K = 2.54
        C = 3.14
        SF0 = 1.0
        SF1 = 0.990
    if options.year == 2018:
        K = 2.55
        C = 3.14
        SF0 = 1.0
        SF1 = 1.035
    if options.year == 2024:
        K = 2.8202
        C = 2.9784
        SF0 = 1.0
        SF1 = 1.0
else:
    if options.year == 2017:
        K = 2.48
        C = 3.19
        SF0 = 1.009
        SF1 = 1.044
    if options.year == 2018:
        K = 2.49
        C = 3.18
        SF0 = 1.006
        SF1 = 1.097
IasTemplate = xparser.getIasTemplate(options.isData)

########################################################################
        
SF_dEdx_Run3_bool = False
if (options.isData and (options.year == 2022 or options.year == 2023 or options.year == 2024)): SF_dEdx_Run3_bool = True

########################################################################

# from HSCPAnalysis.Ntuplizer.HSCParticleProducer_cff import *
if isAOD:
    process.load("HSCPAnalysis.Ntuplizer.HSCParticleProducer_cff")
    process.HSCParticleProducer.filter = False

    process.load("HSCPAnalysis.Ntuplizer.HSCPFullAODAnalyzer_cfi")
    myprocess=process.HSCPFullAODAnalyzer
else:
    # Load HSCProducer
    process.load("HSCPAnalysis.Ntuplizer.HSCPMiniAODProducer_cff")
    process.HSCPMiniAODProducer.filter = False

    process.load("HSCPAnalysis.Ntuplizer.HSCPMiniAODAnalyzer_cfi")
    myprocess=process.HSCPMiniAODAnalyzer
    # myprocess.AddElectronCollection = True

##myprocess.TapeRecallOnly = True
myprocess.AddStripClusterInfo = True
myprocess.AddExtraDeDxEstimators = True
myprocess.TriggerPaths = triggerList
myprocess.TriggerFilter = triggerFilter
myprocess.DeDxK = K
myprocess.DeDxC = C
myprocess.DeDxSF_0 = SF0
myprocess.DeDxSF_1 = SF1
myprocess.DeDxTemplate = IasTemplate
myprocess.SF_dEdx_Run3 = xparser.getRun3dEdxSF()
myprocess.Do_SF_dEdx_Run3 = SF_dEdx_Run3_bool
if not options.isData:
    myprocess.puWeights = xparser.getPU()

#if options.year==2024: myprocess.NoiseFilters=("TriggerResults","","RECO")

#process.endjob_step = cms.EndPath(process.endOfProcess)

process.HSCPTuplePath = cms.Path()
if isAOD:
    process.HSCPTuplePath += process.HSCParticleProducerSeq + process.metFilters
    if not options.isData:
        process.HSCPTuplePath += process.genParticlesSkimmed
    process.HSCPTuplePath += process.HSCParticleProducer
    process.HSCPTuplePath += process.HSCPFullAODAnalyzer
else:
    process.HSCPTuplePath += process.HSCPMiniAODProducerSeq
    process.HSCPTuplePath += process.HSCPMiniAODProducer
    process.HSCPTuplePath += process.HSCPMiniAODAnalyzer

process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
#process.endPath1 = cms.EndPath(process.Out)
process.schedule = cms.Schedule(process.HSCPTuplePath,process.endjob_step)
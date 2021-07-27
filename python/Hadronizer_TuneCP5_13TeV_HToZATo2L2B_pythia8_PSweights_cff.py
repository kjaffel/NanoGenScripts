import FWCore.ParameterSet.Config as cms
externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring(''),
    nEvents = cms.untracked.uint32(1000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *
# https://github.com/cms-sw/cmssw/blob/master/Configuration/Generator/python/Pythia8CommonSettings_cfi.py
# https://github.com/cms-sw/cmssw/blob/master/Configuration/Generator/python/MCTunes2017/PythiaCP5Settings_cfi.py
# https://github.com/cms-sw/cmssw/blob/master/Configuration/Generator/python/PSweightsPythia/PythiaPSweightsSettings_cfi.py

generator = cms.EDFilter("Pythia8HadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    PythiaParameters = cms.PSet(
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        pythia8CommonSettingsBlock,
        processParameters = cms.vstring(
            'Higgs:useBSM = on',# allow BSM Higgs production
            '35:onMode = off' , # turn off all h2 decays
            '35:onIfMatch = 36 23', # turn on only h2 to h3 Z
            '35:isResonance = true',
            #'35:doForceWidth = on',
            '36:onMode = off' , # turn off all h3 decays
            '36:onIfAny = 5',   # turn on only h3 to b b~
            '36:isResonance = true',
            #'36:doForceWidth = on',
            #'36:mWidth =0.01410862'
            #'23:onMode = off' , # turn off all Z decays
            #'23:onIfAny = 11 13 15',  # turn on only decays Z to leptons
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'pythia8PSweightsSettings',
                                    'processParameters'
                                    )
    )
)
ProductionFilterSequence = cms.Sequence(generator)

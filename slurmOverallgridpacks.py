import glob
import random
import os, os.path
import datetime
import argparse
from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

def SlurmRunNanoGEN(path= None, outputDIR=None, decay_in=None, idx=None, randomseed=None):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(config.cmsswDir, outputDIR)
    config.sbatch_time = '07:59:00'
    sbatch_memPerCPU = '7000'
    #config.environmentType = 'cms'
    config.inputSandboxContent = ["gridpackTolheToNanoGen.sh"]
    config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ["cmssw", "fragment", "gridpack_path","NanoGEN", "randomseed"]
    config.inputParams = []
    
    for gridpack_path in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "*_tarball.tar.xz")):
        
        dumpOutputs = os.path.join(config.stageoutDir, "outputs","%s"%gridpack_path.split('/')[-1].split('_slc7')[0])
        if not os.path.exists(dumpOutputs):
            os.makedirs(dumpOutputs)

        NanoGEN = os.path.join(dumpOutputs, "nanogen__%s.root"%idx)

        if "bbH" in NanoGEN:
            fragment = "Hadronizer_TuneCP5_13TeV_aMCatNLO_2p_LHE_pythia8_cff.py"
        elif "W1JetsToLNu_14TeV_5f_NLO_FXFX" in NanoGEN:
            fragment = "Hadronizer_TuneCP5_14TeV_aMCatNLO_FXFX_5f_max2j_LHE_pythia8_cff.py" 
        else:
            if decay_in =='pythia8':
                if "AToZHTo2L2B" in NanoGEN:
                    fragment ="Hadronizer_TuneCP5_13TeV_AToZHTo2L2B_pythia8_PSweights_cff.py"
                else:
                    fragment = "Hadronizer_TuneCP5_13TeV_HToZATo2L2B_pythia8_PSweights_cff.py"
            else:
                fragment ="Hadronizer_TuneCP5_13TeV_generic_LHE_pythia8_PSweights_cff.py" 
        
        cmssw = config.cmsswDir
        config.inputParams.append([cmssw, fragment, gridpack_path, NanoGEN, randomseed])
    config.payload = \
    """
            echo " Gridpack Path      :" ${gridpack_path}
            echo " Output file        :" ${NanoGEN}
            echo " Slurm_JobID_TaskID :" ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
            echo " Random seed        :" ${randomsee}
            echo " Gen-Fragment       :" ${fragment} 
            echo "**********************************************************************"
            cat  ${cmssw}/python/${fragment}
            echo "**********************************************************************"
            bash gridpackTolheToNanoGen.sh ${fragment} ${NanoGEN} ${gridpack_path} ${randomseed}
    """
    submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
    submitWorker()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ZA NanoGen Production', formatter_class=argparse.RawTextHelpFormatter)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    parser.add_argument("-p", "--path"  , default=None, required=True, help="path to gridpacks")
    parser.add_argument("-o", "--output", default=None, help="output dir")
    parser.add_argument("--decay_in"    , default=None, required=True, choices=['pythia8', 'madspin'], help="mandatory as pythia8 fragment will be different according where the decay is specified")
    
    options = parser.parse_args()
    if options.output is None:
        options.output = options.path 
    
    for i in range(10):
        random.seed(i)
        randomseed = random.randint(25, 50)
        SlurmRunNanoGEN( path=options.path, outputDIR=options.output, decay_in=options.decay_in, idx=i, randomseed=int(randomseed))

import glob
import os, os.path
import datetime
import argparse
from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

def SlurmRunNano(path= None, outputDIR=None):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(config.cmsswDir, outputDIR)
    config.sbatch_time = '0-06:00'
    sbatch_memPerCPU = '2000'
    #config.environmentType = 'cms'
    config.inputSandboxContent = ["gridpackTolheToNanoGen.sh"]
    config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ["gridpack_path","NanoGEN"]
    config.inputParams = []
    
    # PATH_wheretolook ="/home/ucl/cp3/kjaffel/ZAPrivateProduction/genproductions/bin/MadGraph5_aMCatNLO/"
    # PATH_wheretolook ="/home/ucl/cp3/kjaffel/ZAPrivateProduction/CMSSW_11_2_0_pre7/src/Configuration/NanoGenScripts/lxplus-ver2021.0316/BENCHMARKS/"
    # PATH_wheretolook ="/home/ucl/cp3/kjaffel/ZAPrivateProduction/CMSSW_11_2_0_pre7/src/Configuration/NanoGenScripts/compare_bbHwidths/"
    
    for gridpack_path in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "*_tarball.tar.xz")):
        config.inputParams.append([gridpack_path, "%s%s"%(gridpack_path.split('/')[-1].split('_slc7')[0], ".root")])
    config.payload = \
    """
            if [[ "${NanoGEN}" == *"bbH"* ]]; then
                eval fragment="Hadronizer_TuneCP5_13TeV_aMCatNLO_2p_LHE_pythia8_cff.py"
            else
                eval fragment="Hadronizer_TuneCP5_13TeV_generic_LHE_pythia8_PSweights_cff.py"
            fi
            cat python/${fragment}
            echo ${gridpack_path}
            echo ${NanoGEN}
            echo ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
            
            bash gridpackTolheToNanoGen.sh ${fragment} ${NanoGEN} ${gridpack_path}
    """
    submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
    submitWorker()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ZA NanoGen Production', formatter_class=argparse.RawTextHelpFormatter)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    parser.add_argument("-p", "--path", default=None, help="path to gridpacks")
    parser.add_argument("-o", "--output", default=os.makedirs("." + current_time), help="output dir")
    options = parser.parse_args()
    SlurmRunNano( path=options.path, outputDIR=options.output)

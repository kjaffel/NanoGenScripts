#!/bin/env python
import os, glob, ROOT, subprocess
import argparse

def system(command):
  return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)

# Check if valid ROOT file exists
def isValidRootFile(fname):
  if not os.path.exists(os.path.expandvars(fname)): return False
  f = ROOT.TFile(fname)
  if not f: return False
  try:
    return not (f.IsZombie() or f.TestBit(ROOT.TFile.kRecovered) or f.GetListOfKeys().IsEmpty())
  finally:
    f.Close()

def domerge( mainOutputDir=None):
    for smppath in glob.glob(os.path.join(mainOutputDir, 'outputs', '*_pythia8')):
        smpNm = smppath.split('/')[-1]
        for slurmDIR in glob.glob(os.path.join(mainOutputDir, 'outputs', smpNm)):
            targetFile   = os.path.join(mainOutputDir, 'outputs','%s.root'%smpNm)
            filesToMerge = glob.glob(os.path.join(slurmDIR, '*.root'))
        
            if os.path.exists(targetFile): # if existing target file exists and looks ok, skip
                if isValidRootFile(targetFile): continue
                else: os.system('rm %s' % targetFile)
    
            for f in filesToMerge:
                if not isValidRootFile(f):
                    print ('WARNING: something wrong with %s' % f)
        
            if len(filesToMerge)>100:
                print ('A lot of files to merge, this might take some time...')
            print( system('hadd %s %s' % (targetFile, ' '.join(filesToMerge))) )

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='ZA NanoGen Production', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-p", "--path"  , default=None, required=True, help="path to gridpacks")
    options = parser.parse_args()
    
    domerge( mainOutputDir=options.path) 

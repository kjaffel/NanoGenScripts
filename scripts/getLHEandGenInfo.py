#!usr/bin/python
import os
import optparse 
import sys 
import subprocess
import datetime 
import re
from subprocess import check_output
import ROOT
import numpy as nn
from random import randint

basedir_path = os.path.dirname(os.path.realpath(__file__))
print basedir_path

madgraph_dir = "genproductions/bin/MadGraph5_aMCatNLO"

usage = ""
parser = optparse.OptionParser(usage='\nExample: python %prog -i gridpacks/gridpack_name_without_tar -n gridpack_name -t /tmp/kjaffel --getGenInfo --createLHE --EOSdir  \n1) enter in a CMSSW area and do cmsenv \n2) Copy by hand new gridpacks (typically created in genproductions/bin/MadGraph5_aMCatNLO) in a new directory (i.e. gridpacks/TrijetRes_g_ggg_BP2_test) \n3) Launch the script %prog: the code creates a root file with the gen info of the produced samples (if --getGenInfo is enabled) and/or create an LHE file (if --createLHE is enabled)')
parser.add_option("-i","--inputGridpackDir",action="store",type="string",dest="INPUTGRIDPACKDIR",default="")
parser.add_option("-n","--genProcessName",action="store",type="string",dest="GENPROCESSNAME",default="")
parser.add_option("-t","--tmpDir",action="store",type="string",dest="TMPDIR",default="")
parser.add_option("--getGenInfo",action="store_true",dest="GENINFO")
parser.add_option("--createLHE",action="store_true",dest="CREATELHE")
parser.add_option("--numberOfLHEevents",action="store",type="string",dest="NEVENTSLHE",default="10")
parser.add_option("--numberOfCPUforLHE",action="store",type="string",dest="NCPULHE",default="2")
parser.add_option("--EOSdir",action="store",type="string",dest="EOSDIR",default="")

(options, args) = parser.parse_args()
INPUTGRIDPACKDIR = options.INPUTGRIDPACKDIR
GENPROCESSNAME = options.GENPROCESSNAME
TMPDIR = options.TMPDIR
GENINFO = options.GENINFO
CREATELHE = options.CREATELHE
NEVENTSLHE = options.NEVENTSLHE
NCPULHE = options.NCPULHE
EOSDIR = options.EOSDIR

if not options.INPUTGRIDPACKDIR:   
    parser.error('ERROR: Input gridpack directory is not given')
if not options.GENPROCESSNAME:   
    parser.error('ERROR: Gen process name is not given')
if not options.TMPDIR:   
    parser.error('ERROR: Tmp directory is not given')
if CREATELHE:
    if not EOSDIR:
         parser.error('ERROR: Eos directory is not given')

proc = subprocess.Popen(["ls %s | grep %s | grep tarball" % (INPUTGRIDPACKDIR,GENPROCESSNAME)], stdout=subprocess.PIPE, shell=True)
(gridpacklist, err) = proc.communicate()
gridpacklist = gridpacklist.splitlines()
#print gridpacklist

if GENINFO or CREATELHE:
    #create dir on eos
    print("eos mkdir %s/%s" % (EOSDIR,GENPROCESSNAME))
    os.system("eos mkdir %s/%s" % (EOSDIR,GENPROCESSNAME))

if GENINFO:
    # create root file
    f = ROOT.TFile("%s/tree_%s.root" % (INPUTGRIDPACKDIR,GENPROCESSNAME), "recreate")
    t = ROOT.TTree("geninfotree", "tree title")

    xsec = nn.zeros(1, dtype=float)
    gkkmass = nn.zeros(1, dtype=float)
    gkkwidth = nn.zeros(1, dtype=float)
    gkkbr = nn.zeros(1, dtype=float)
    rmass = nn.zeros(1, dtype=float)
    rwidth = nn.zeros(1, dtype=float)
    rbr = nn.zeros(1, dtype=float)
    
    t.Branch('xsec', xsec, 'xsec/D')
    t.Branch('gkkmass', gkkmass, 'gkkmass/D')
    t.Branch('gkkwidth', gkkwidth, 'gkkwidth/D')
    t.Branch('gkkbr', gkkbr, 'gkkbr/D')
    t.Branch('rmass', rmass, 'rmass/D')
    t.Branch('rwidth', rwidth, 'rwidth/D')
    t.Branch('rbr', rbr, 'rbr/D')

# loop over gripacks
for gridpack in gridpacklist:
    gridpacktmpdirname = gridpack.split("_tarball.tar.xz")[0]
    gridpacktmpdir = TMPDIR+"/"+gridpacktmpdirname
    print("mkdir -p %s" % gridpacktmpdir)
    os.system("mkdir -p %s" % gridpacktmpdir)
    print("cp %s/%s %s" % (INPUTGRIDPACKDIR,gridpack,gridpacktmpdir))
    os.system("cp %s/%s %s" % (INPUTGRIDPACKDIR,gridpack,gridpacktmpdir))

    if GENINFO:
        #copy gridpacks
        print("eos cp %s/%s %s/%s/%s" % (INPUTGRIDPACKDIR,gridpack,EOSDIR,GENPROCESSNAME,gridpack))
        os.system("eos cp %s/%s %s/%s/%s" % (INPUTGRIDPACKDIR,gridpack,EOSDIR,GENPROCESSNAME,gridpack))

    os.chdir(gridpacktmpdir)
    print("tar -xavf %s" % gridpack)
    os.system("tar -xavf %s" % gridpack)

    # extract gen info from gridpacks
    if GENINFO:

        # xsection (pb)
        reader = subprocess.Popen(["grep Cross-section gridpack_generation.log"], stdout=subprocess.PIPE, shell=True)
        (xsection, err) = reader.communicate()
        if xsection:
            xsectionpb = float(xsection.split()[2])
        else:
            xsectionpb = 0
        print "xsection (pb) = "+str(xsectionpb)

        # KK gluon mass (GeV)
        reader = subprocess.Popen(["grep mgkk process/madevent/Cards/param_card.dat"], stdout=subprocess.PIPE, shell=True)
        (mgkk, err) = reader.communicate()
        if mgkk:
            mgkkGeV = float(mgkk.split()[1])
        else:
            mgkkGeV = 0
        print "KK gluon mass (GeV) = "+str(mgkkGeV)

        # KK gluon width (GeV)
        reader = subprocess.Popen(["grep \"DECAY  9000021\" process/madevent/Cards/param_card.dat"], stdout=subprocess.PIPE, shell=True)
        (wgkk, err) = reader.communicate()
        if wgkk:
            wgkkGeV = float(wgkk.split()[2])
        else:
            wgkkGeV = 0
        print "KK gluon width (GeV) = "+str(wgkkGeV)

        # Radion mass (GeV)
        reader = subprocess.Popen(["grep mr process/madevent/Cards/param_card.dat"], stdout=subprocess.PIPE, shell=True)
        (mr, err) = reader.communicate()
        if mr:
            mrGeV = float(mr.split()[1])
        else:
            mrGeV = 0
        print "Radion mass (GeV) = "+str(mrGeV)

        # Radion width (GeV)
        reader = subprocess.Popen(["grep \"DECAY  9000025\" process/madevent/Cards/param_card.dat"], stdout=subprocess.PIPE, shell=True)
        (wr, err) = reader.communicate()
        if wr:
            wrGeV = float(wr.split()[2])
        else:
            wrGeV = 0
        print "Radion width (GeV) = "+str(wrGeV)

        # BR (KK gluon -> Radion gluon)
        reader = subprocess.Popen(["grep \"21  9000025\" process/madevent/Cards/param_card.dat"], stdout=subprocess.PIPE, shell=True)
        (brgkk, err) = reader.communicate()
        if brgkk:
            brgkk = float(brgkk.split()[0])
        else:
            brgkk = 0
        print "BR (KK gluon -> Radion gluon) = "+str(brgkk)

        # BR (Radion -> gluon gluon)
        reader = subprocess.Popen(["grep \"21  21\" process/madevent/Cards/param_card.dat"], stdout=subprocess.PIPE, shell=True)
        (brr, err) = reader.communicate()
        if brr:
            brr = float(brr.split()[0])
        else:
            brr = 0
        print "BR (Radion -> gluon gluon) = "+str(brr)

        # fill root tree
        xsec[0] = xsectionpb
        gkkmass[0] = mgkkGeV
        gkkwidth[0] = wgkkGeV
        gkkbr[0] = brgkk
        rmass[0] = mrGeV
        rwidth[0] = wrGeV
        rbr[0] = brr
        t.Fill()

    # create LHE file
    if CREATELHE:
        SEEDLHE = randint(1, 100000) 
        print("./runcmsgrid.sh %s %s %s" % (NEVENTSLHE, SEEDLHE, NCPULHE))
        os.system("./runcmsgrid.sh %s %s %s" % (NEVENTSLHE, SEEDLHE, NCPULHE))        
        #copy LHE
        print("eos cp cmsgrid_final.lhe %s/%s/%s.lhe" % (EOSDIR,GENPROCESSNAME,gridpacktmpdirname))
        os.system("eos cp cmsgrid_final.lhe %s/%s/%s.lhe" % (EOSDIR,GENPROCESSNAME,gridpacktmpdirname))

    os.chdir(basedir_path)
    
    #clean tmp directory
    print("rm -rf %s" % (gridpacktmpdir))
    os.system("rm -rf %s" % (gridpacktmpdir))

if GENINFO:
    f.Write()
    f.Close()
    #copy file with geninfo on eos
    print("eos cp %s/tree_%s.root %s/%s/tree_%s.root" % (INPUTGRIDPACKDIR,GENPROCESSNAME,EOSDIR,GENPROCESSNAME,GENPROCESSNAME))
    os.system("eos cp %s/tree_%s.root %s/%s/tree_%s.root" % (INPUTGRIDPACKDIR,GENPROCESSNAME,EOSDIR,GENPROCESSNAME,GENPROCESSNAME))

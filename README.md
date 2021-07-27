# ZANanoGEN:
## Setup CMSSW area :
To set up in a new CMSSW area:
```bash
cmsrel CMSSW_10_6_19_patch2
cd CMSSW_10_6_19_patch2/src
cmsenv
mkdir Configuration
git clone https://github.com/kjaffel/NanoGenScripts -o Configuration/NanoGenScripts
scram b
```
or inside an existing CMSSW area
```bash
cd $CMSSW_BASE/src
mkdir -p Configuration
git clone https://github.com/kjaffel/NanoGenScripts -o Configuration/NanoGenScripts
scram b
```
## gridpacks -> LHE -> GEN:[slurm]
At this stage I am assuming that you manage to generate gridpacks stored by default in :`genproductions/bin/MadGraph5_aMCatNLO/`

```bash
./loadgridpacksfromlxplus.sh
```
```python
python slurmOverallgridpacks.py --path --output
```
- ``-p``/``--path`` : path to `` _tarball.tar.xz`` gridpacks
- ``-o``/``--output``:  output dir by default will be tha same as the output
- ``--decay_in:`` need to be ``madspin`` or ``pythia8`` accordingly the gen-fragment will change   
```python
scripts/mergeOutput.py --path slurm_dir 
```
## LHE -> GEN:
If you have lhe files:
Go to folderName/Events/run_01. In there should be a file named unweighted_events.lhe.gz . To unzip it, use:
```
zcat unweighted_events.lhe.gz > unweighted_events.lhe
or gunzip unweighted_events.lhe.gz
```
You should now have unweighted_events.lhe, which is the file to be used in further analysis.
```bash
./Configuration/NanoGenScripts/lheToNanoGen.sh <fragment> <lhe> <output>
```
where `<fragment>` is a fragment with an externalLHEProducer and hadronizer settings compatible with the process in the LHE file.

## Get gridpack and fragments for a dataset: [snippets/1488](https://gitlab.cern.ch/-/snippets/1488)
```python
python getGenInfo.py --cernSSOcookies=prodcookies.pkl /HToZATo2L2B_MH-500_MA-300_13TeV-madgraph-pythia8/RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8-v1/NANOAODSIM
```
This (python3) script assumes you have a grid proxy (to query DAS) and kerberos token (to get a session cookie for McM - set up with kinit username@CERN.CH).
It also depends on cerndb/cern-sso-python with a patch, which can be installed with
```bash
pip install git+https://github.com/pieterdavid/cern-sso-python.git@addverifyarg 
```
## Useful Links:
- [NanoGen twiki page](https://twiki.cern.ch/twiki/bin/viewauth/CMS/NanoGen)
- [Kenneth Long's repo](https://github.com/kdlong/WMassNanoGen) 
- [Pieter David repo](https://github.com/pieterdavid/NanoGenScripts)

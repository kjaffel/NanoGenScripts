#!/usr/bin/env bash
if [ $# != 3 ]; then
  echo "Need exactly three arguments: fragment, LHE file, and output file"
  exit 1
fi
if [ -z "${CMSSW_BASE}" ]; then
  echo "Need to set up a CMSSW release first"
  exit 1
fi
fragment="Configuration/NanoGenScripts/python/${1}"
lheInput=$(realpath "${2}")
nEvents=$(grep '<event>' "${lheInput}" | wc -l)
output=$(realpath "${3}")
startdir=$(pwd)
tmpdir=$(mktemp -d)
pushd "${tmpdir}"
cp "$lheInput" "cmsgrid_final.lhe"

cmsDriver.py "${fragment}" --filein "file:${lheInput}" --fileout "file:${output}" --mc --eventcontent NANOAODSIM --datatier NANOAOD  --conditions auto:mc --step GEN,NANOGEN -n "${nEvents}" --customise_commands 'process.nanoAOD_step.remove(process.rivetProducerHTXS); process.nanoAOD_step.remove(process.HTXSCategoryTable)'; "process.externalLHEProducer.scriptName = cms.FileInPath('Configuration/NanoGenScripts/data/ignore.sh')"

popd
if [ -d "${tmpdir}" ]; then
  rm -rf "${tmpdir}"
fi

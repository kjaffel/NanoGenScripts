#!/usr/bin/env bash
if [ $# != 4 ]; then
  echo "Need exactly four arguments: fragment, and output file and the gridpack path and randomseed"
  exit 1
fi
if [ -z "${CMSSW_BASE}" ]; then
  echo "Need to set up a CMSSW release first"
  exit 1
fi
fragment="Configuration/NanoGenScripts/python/${1}"
echo "The path to the gridpack should be in the fragment: ${fragment} or changed through customise commands as the case here !!"
output=$(realpath "${2}")
startdir=$(pwd)
tmpdir=$(mktemp -d)
pushd "${tmpdir}"
nEvents=2000
randomseed=${4}

cmsDriver.py "${fragment}" --fileout "file:${output}" --mc --eventcontent NANOAODSIM --datatier NANOAOD --conditions auto:mc --step LHE,GEN,NANOGEN -n "${nEvents}" --customise_commands "process.nanoAOD_step.remove(process.rivetProducerHTXS); process.nanoAOD_step.remove(process.HTXSCategoryTable) ;process.externalLHEProducer.args = cms.vstring('${3}'); process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=${randomseed}"

popd
#if [ -d "${tmpdir}" ]; then
#  rm -rf "${tmpdir}"
#fi

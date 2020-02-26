#!/bin/bash
echo "Run script starting"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc820
eval `scramv1 project CMSSW CMSSW_11_0_0_pre13`

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_11_0_0_pre13/src/; cd ../CMSSW_11_0_0_pre13/src/
eval `scramv1 runtime -sh`

echo python hhAll_preselection_eosFiles_switched.py $*
python hhAll_preselection_eosFiles_switched.py $*

cp HHpreselection*.root ../../

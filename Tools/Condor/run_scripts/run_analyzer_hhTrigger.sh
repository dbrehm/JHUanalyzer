#!/bin/bash
echo "Run script starting"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc820
eval `scramv1 project CMSSW_11_0_0`

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * ../CMSSW_11_0_0/src/; cd ../CMSSW_11_0_0/src/
eval `scramv1 runtime -sh`

echo python hhTrigger.py $*
python hhTrigger.py $*

cp HHtrigger*.root ../../

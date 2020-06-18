import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser

from JHUanalyzer.Analyzer.analyzer import analyzer, Group, VarGroup, CutGroup, Nminus1, SetCFunc
from JHUanalyzer.Tools.Common import openJSON,CutflowHist
from JHUanalyzer.Analyzer.Cscripts import CommonCscripts, CustomCscripts
commonc = CommonCscripts()
customc = CustomCscripts()

parser = OptionParser()

parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-c', '--config', metavar='FILE', type='string', action='store',
                default   =   'config.json',
                dest      =   'config',
                help      =   'Configuration file in json format that is interpreted as a python dictionary')
parser.add_option('-y', '--year', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'year',
                help      =   'Year (16,17,18)')
parser.add_option('-d', '--doublebtagger', metavar='F', type='string', action='store',
                default   =   'btagHbb',
                dest      =   'doublebtagger',
                help      =   'Variable name in NanoAOD for double b tagger to be used. btagHbb (default), deepTagMD_HbbvsQCD, deepTagMD_ZHbbvsQCD, btagDDBvL')
parser.add_option('-J', '--JES', metavar='F', type='string', action='store',
                default   =   'nom',
                dest      =   'JES',
                help      =   'nom, up, or down')
parser.add_option('-R', '--JER', metavar='F', type='string', action='store',
                default   =   'nom',
                dest      =   'JER',
                help      =   'nom, up, or down')
parser.add_option('-a', '--JMS', metavar='F', type='string', action='store',
                default   =   'nom',
                dest      =   'JMS',
                help      =   'nom, up, or down')
parser.add_option('-b', '--JMR', metavar='F', type='string', action='store',
                default   =   'nom',
                dest      =   'JMR',
                help      =   'nom, up, or down')

(options, args) = parser.parse_args()

start_time = time.time()

a = analyzer(options.input)
if '_loc.txt' in options.input: setname = options.input.split('/')[-1].split('_loc.txt')[0]
elif '.root' in options.input: setname = options.input.split('/')[-1].split('_hh'+options.year+'.root')[0]
else: setname = ''

if os.path.exists(options.config):
    print 'JSON config imported'
    c = openJSON(options.config)
    if setname != '' and not a.isData: 
        xsec = c['XSECS'][setname]
        lumi = c['lumi']
    else: 
        xsec = 1.
        lumi = 1.

##JECs for actual values.
lead = {}
sublead = {}
if not a.isData:
    if options.JES != 'nom':
        lead['JEScorr'] = 'FatJet_corr_JES_Total'+options.JES.capitalize()+"[0]"
        sublead['JEScorr'] = 'FatJet_corr_JES_Total'+options.JES.capitalize()+"[1]"
    else:
        lead['JEScorr'] = "1.0"
        sublead['JEScorr'] = "1.0"
    lead['JERcorr'] = 'FatJet_corr_JER_'+options.JER+"[0]"
    sublead["JERcorr"] = 'FatJet_corr_JER_'+options.JER+"[1]"
    lead["JMScorr"] = 'FatJet_corr_JMS_'+options.JMS+"[0]"
    sublead["JMScorr"] = 'FatJet_corr_JMS_'+options.JMS+"[1]"
    lead["JMRcorr"] = 'FatJet_groomed_corr_JMR_'+options.JMR+"[0]"
    sublead["JMRcorr"] = 'FatJet_groomed_corr_JMR_'+options.JMR+"[1]"
if not a.isData:
    lead['pt'] = "*"+lead['JEScorr']+"*"+lead['JERcorr']
    sublead['pt'] = "*"+sublead['JEScorr']+"*"+sublead['JERcorr']
    lead['SDmass'] = "*"+lead['JEScorr']+"*"+lead['JERcorr']
    sublead['SDmass'] = "*"+sublead['JEScorr']+"*"+sublead['JERcorr']
    if 'ttbar' not in setname:
        lead['SDmass'] += "*"+lead['JMScorr']+"*"+lead['JMRcorr']
        sublead['SDmass'] += "*"+sublead['JMScorr']+"*"+sublead['JMRcorr']
###Apply corrections
# if not a.isData:
#     mass0 = "FatJet_msoftdrop_nom[0]"+lead['SDmass']
#     mass1 = "FatJet_msoftdrop_nom[1]"+sublead['SDmass']
#     pt0 = "FatJet_pt_nom[0]"+lead['pt']
#     pt1 = "FatJet_pt_nom[1]"+sublead['pt']
# else:
#     mass0 = "FatJet_msoftdrop_nom[0]"
#     mass1 = "FatJet_msoftdrop_nom[1]"
#     pt0 = "FatJet_pt_nom[0]"
#     pt1 = "FatJet_pt_nom[1]"
# eta0 = "FatJet_eta[0]"
# eta1 = "FatJet_eta[1]"
# phi0 = "FatJet_phi[0]"
# phi1 = "FatJet_phi[1]"

if not a.isData:
    mass1 = "FatJet_msoftdrop_nom[0]"+lead['SDmass']
    mass0 = "FatJet_msoftdrop_nom[1]"+sublead['SDmass']
    pt1 = "FatJet_pt_nom[0]"+lead['pt']
    pt0 = "FatJet_pt_nom[1]"+sublead['pt']

else:
    mass1 = "FatJet_msoftdrop_nom[0]"
    mass0 = "FatJet_msoftdrop_nom[1]"
    pt1 = "FatJet_pt_nom[0]"
    pt0 = "FatJet_pt_nom[1]"

eta0 = "FatJet_eta[1]"
eta1 = "FatJet_eta[0]"
phi0 = "FatJet_phi[1]"
phi1 = "FatJet_phi[0]"

print("mass 0 = "+ mass0)
print("mass 1 = "+ mass1)
print("pt 0 = "+ pt0)
print("pt 1 = "+ pt1)

cutsDict = {
    'doubleBtag':[0.8,1.0],
    'doubleBtagTight':[0.8,1.0],
    'doubleBtagLoose':[0.3,1.0],
    'DeepDBtag':[0.3,1.0],
    'DeepDBtagTight':[0.86,1.0],
    'DeepDBtagLoose':[0.7,1.0],
    'dak8MDZHbbtag':[0.95,1.0],
    'dak8MDZHbbtagTight':[0.95,1.0],
    'dak8MDZHbbtagLoose':[0.8,1.0],
    'dak8MDHbbtag':[0.9,1.0],
    'dak8MDHbbtagTight':[0.9,1.0],
    'dak8MDHbbtagLoose':[0.8,1.0]
}

doubleB_titles = {'btagHbb':'Double b',
                  'deepTagMD_HbbvsQCD': 'DeepAK8 MD Hbb',
                  'deepTagMD_ZHbbvsQCD': 'DeepAK8 MD ZHbb',
                  'btagDDBvL': 'Deep Double b'}
doubleB_abreviations = {'btagHbb':'doubleB',
                  'deepTagMD_HbbvsQCD': 'dak8MDHbb',
                  'deepTagMD_ZHbbvsQCD': 'dak8MDZHbb',
                  'btagDDBvL': 'DeepDB'}
doubleB_name = options.doublebtagger
doubleB_title = doubleB_titles[doubleB_name]
doubleB_short = doubleB_abreviations[doubleB_name]

SetCFunc(commonc.deltaPhi)
SetCFunc(commonc.vector)
SetCFunc(commonc.invariantMass)
SetCFunc(commonc.invariantMassThree)
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/pdfweights.cc","pdfweights")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/hemispherize.cc","hemispherize")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/triggerlookup.cc","triggerlookup")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/btagsf.cc","btagsf")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/ptwlookup.cc","ptwlookup")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/topCut.cc","topCut")

colnames = a.BaseDataFrame.GetColumnNames()
# Start an initial group of cuts
triggerGroup = VarGroup('triggerGroup')
trigOR = ""
if '16' in options.output: 
    trigList = ["HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30"]
    for i,t in enumerate(trigList):
            if t in colnames: 
                if not trigOR: trigOR = "("+t+"" # empty string == False
                else: trigOR += " || "+t+""
            else:
                print "Trigger %s does not exist in TTree. Skipping." %(t)
    triggerGroup.Add("triggers",""+trigOR+")")
else: 
    trigList = ["HLT_PFHT1050","HLT_AK8PFJet400_TrimMass30"]
    for i,t in enumerate(trigList):
        if t in colnames: 
            if not trigOR: trigOR = "("+t+"" # empty string == False
            else: trigOR += " || "+t+""
        else:
            print "Trigger %s does not exist in TTree. Skipping." %(t)
    triggerGroup.Add("triggers",""+trigOR+")")

if options.year =='16':
    triggerGroup.Add("numerator","(triggers) && HLT_Mu50")
if options.year == '17'  or options.year == '18':
    triggerGroup.Add("numerator","(triggers) && HLT_Mu50")
triggerGroup.Add("denominator","HLT_Mu50")

newcolumns = VarGroup("newcolumns")
newcolumns.Add("pt0",""+pt0+"")
newcolumns.Add("pt1",""+pt1+"")
newcolumns.Add("mh",""+mass0+"")
newcolumns.Add("mh1",""+mass1+"")
newcolumns.Add("lead_vect","analyzer::TLvector("+pt0+","+eta0+","+phi0+","+mass0+")")
newcolumns.Add("sublead_vect","analyzer::TLvector("+pt1+","+eta1+","+phi1+","+mass1+")")
newcolumns.Add("mhh","analyzer::invariantMass(lead_vect,sublead_vect)")
newcolumns.Add("mreduced","mhh - (mh-125.0) - (mh1-125.0)")

bbColumn = VarGroup("bbColumn")
bbColumn.Add("Hemispherized","analyzer::Hemispherize(FatJet_pt_nom,FatJet_eta,FatJet_phi,FatJet_msoftdrop_nom,nFatJet,Jet_pt,Jet_eta,Jet_phi,Jet_mass,nJet,Jet_btagDeepB)")

mbbColumn = VarGroup("mbbColumn")
mbbColumn.Add("b_lead_vect","analyzer::TLvector(Jet_pt[Hemispherized[0]],Jet_eta[Hemispherized[0]],Jet_phi[Hemispherized[0]],Jet_mass[Hemispherized[0]])")
mbbColumn.Add("b_sublead_vect","analyzer::TLvector(Jet_pt[Hemispherized[1]],Jet_eta[Hemispherized[1]],Jet_phi[Hemispherized[1]],Jet_mass[Hemispherized[1]])")
mbbColumn.Add("mbb","analyzer::invariantMass(b_lead_vect,b_sublead_vect)")
mbbColumn.Add("topMassVec","analyzer::topCut(Hemispherized[0],Hemispherized[1],Jet_pt,Jet_eta,Jet_phi,Jet_mass,nJet)")
mbbColumn.Add("topMass","topMassVec[0]")
mbbColumn.Add("topDeltaR","topMassVec[1]")

mred21Column = VarGroup("mred21Column")
mred21Column.Add("mreduced21","analyzer::invariantMassThree(sublead_vect,b_lead_vect,b_sublead_vect) - (mh1-125.0) - (mbb-125)")

slim_skim = CutGroup('slim_skim')
# slim_skim.Add("triggers","triggers == 1")
slim_skim.Add("nFatJets","nFatJet > 0")

filters = CutGroup('filters')
filters.Add("Flag_goodVertices","Flag_goodVertices == 1")
filters.Add("Flag_globalSuperTightHalo2016Filter","Flag_globalSuperTightHalo2016Filter == 1")
filters.Add("Flag_HBHENoiseFilter","Flag_HBHENoiseFilter == 1")
filters.Add("Flag_HBHENoiseIsoFilter","Flag_HBHENoiseIsoFilter == 1")
filters.Add("Flag_EcalDeadCellTriggerPrimitiveFilter","Flag_EcalDeadCellTriggerPrimitiveFilter == 1")
filters.Add("Flag_BadPFMuonFilter","Flag_BadPFMuonFilter == 1")

#### 1+1 cut groups

preselection11 = CutGroup('preselection11')
preselection11.Add("nFatJets","nFatJet > 1")
preselection11.Add("pt0",""+pt0+" > 200")
preselection11.Add("pt1",""+pt1+" > 200")
preselection11.Add("eta0","abs("+eta0+") < 2.4")
preselection11.Add("eta1","abs("+eta1+") < 2.4")
preselection11.Add("jetID","((FatJet_jetId[0] & 2) == 2) && ((FatJet_jetId[1] & 2) == 2)")
# preselection11.Add("PV","PV_npvsGood > 0")
preselection11.Add("deltaEta","abs("+eta0+" - "+eta1+") < 1.3")
# preselection11.Add("tau21","(FatJet_tau2[0]/FatJet_tau1[0] < 0.55) && (FatJet_tau2[1]/FatJet_tau1[1] < 0.55)")
# Cut on new column
preselection12 = CutGroup('preselection12')
preselection12.Add("msoftdrop_1","(110 < mh1) && (mh1 < 140)")
# preselection12.Add("cut_mreduced","mreduced > 750.")

cand21String = "((!(nFatJet > 1) || !(pt0 > 300 && pt1 > 300) || !(abs("+eta0+") < 2.4 && abs("+eta1+") < 2.4) || !(abs("+eta0+" - "+eta1+") < 1.3) || !(mreduced > 750.) || !((110 < mh1) && (mh1 < 140))) == 1)"


preselection21 = CutGroup('preselection21')
preselection21.Add("candidate21","("+cand21String+")")
preselection21.Add("nFatJets21","nFatJet > 0")
preselection21.Add("nJets21","nJet >= 2")

preselection22 = CutGroup('preselection22')
preselection22.Add("bb_pairs_check","(Hemispherized[0] != 0) && (Hemispherized[1] != 0)")
preselection22.Add("eta","abs("+eta0+") < 2.4")
preselection22.Add("b_eta","abs(Jet_eta[Hemispherized[0]]) < 2.0 && abs(Jet_eta[Hemispherized[1]]) < 2.0")
preselection22.Add("pt","(pt1 > 300)")
preselection22.Add("b_pt","Jet_pt[Hemispherized[0]] > 30 && Jet_pt[Hemispherized[1]] > 30")
preselection22.Add("jetID","((FatJet_jetId[1] & 2) == 2)")
# preselection22.Add("DeepCSV","(0.4184 < Jet_btagDeepB[Hemispherized[0]] && Jet_btagDeepB[Hemispherized[0]] < 1) && (0.4184 < Jet_btagDeepB[Hemispherized[1]] && Jet_btagDeepB[Hemispherized[1]] < 1)")
# preselection22.Add("DeepCSV","(0.6324 < Jet_btagDeepB[Hemispherized[0]] && Jet_btagDeepB[Hemispherized[0]] < 1) && (0.6324 < Jet_btagDeepB[Hemispherized[1]] && Jet_btagDeepB[Hemispherized[1]] < 1)")
# preselection22.Add("deltaEta21","abs("+eta1+" - (Jet_eta[Hemispherized[0]]+Jet_eta[Hemispherized[1]])) < 1.3")


preselection23 = CutGroup('preselection23')
# preselection23.Add("mbbCut","90.0 < mbb && mbb < 140.0")
preselection23.Add("mbbCut","105.0 < mbb && mbb < 135.0")
# preselection23.Add("topMass","topMass > 200.0 || topMass < 140.0")
preselection23.Add("topMass","topMass > 200.0")
# preselection23.Add("topMass","topMass > 220.0")
preselection23.Add("topDeltaR","topDeltaR > 1.0")

# Apply all groups in list order to the base RDF loaded in during analyzer() initialization
slimandskim = a.Apply([triggerGroup,slim_skim,filters])

print("Doing 1+1 preselection.")
presel11 = slimandskim.Apply([preselection11,newcolumns,preselection12])

num = presel11.Cut("num","numerator==1")
den = presel11.Cut("den","denominator==1")

print("Doing 2+1 preselection.")
presel21 = slimandskim.Apply([newcolumns,preselection21,bbColumn,preselection22,mbbColumn,mred21Column])

num21 = presel21.Cut("num21","numerator==1")
den21 = presel21.Cut("den21","denominator==1")

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()

hnum = num.DataFrame.Histo1D(("hnum","hnum", 28 ,700 ,3500),"mreduced")
hden = den.DataFrame.Histo1D(("hden","hden", 28 ,700 ,3500),"mreduced")

hnum21 = num21.DataFrame.Histo1D(("hnum21","hnum21", 13 ,700 ,2000),"mreduced21")
hden21 = den21.DataFrame.Histo1D(("hden21","hden21", 13 ,700 ,2000),"mreduced21")

hnum.Write()
hden.Write()

hnum21.Write()
hden21.Write()

out_f.Close()

print "Total time: "+str((time.time()-start_time)/60.) + ' min'

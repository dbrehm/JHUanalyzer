import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from JHUanalyzer.Analyzer.analyzer import analyzer,openJSON,CutflowHist,CutGroup
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
if '.root' in options.input: setname = options.input.split('/')[-1].split('_hh'+options.year+'.root')[0]
else: setname = ''

print("Setname = "+setname)
print("Is Data = "+str(a.isData))
if os.path.exists(options.config):
    print 'JSON config imported'
    c = openJSON(options.config)
    if setname != '' and not a.isData: 
        xsec = c['XSECS'][setname]
        lumi = c['lumi']
    else: 
        xsec = 1.
        lumi = 1.

cutsDict = {
    'doubleBtag':[0.8,1.0],
    'doubleBtagTight':[0.8,1.0],
    'doubleBtagLoose':[0.3,1.0],
    'DeepDBtag':[0.86,1.0],
    'DeepDBtagTight':[0.86,1.0],
    #'DeepDBtagTight':[0.6,1.0],
    'DeepDBtagLoose':[0.7,1.0],
    #'DeepDBtagLoose':[0.3,1.0],
    'dak8MDZHbbtag':[0.95,1.0],
    'dak8MDZHbbtagTight':[0.95,1.0],
    'dak8MDZHbbtagLoose':[0.8,1.0],
    'dak8MDHbbtag':[0.9,1.0],
    'dak8MDHbbtagTight':[0.9,1.0],
    'dak8MDHbbtagLoose':[0.8,1.0],
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
###These have been switched to swap the preselection and alphabet fatjets
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


print("mass 0 = "+ mass0)
print("mass 1 = "+ mass1)
print("pt 0 = "+ pt0)
print("pt 1 = "+ pt1)


### The following loads the btag calibration code in c++ so that it is available to RDF
ROOT.gInterpreter.Declare('string year = string(TPython::Eval("options.year"));')
btagLoadCode = '''
    string btagfilename;
    if (year == "16"){
          btagfilename = "JHUanalyzer/SFs/DeepCSV_2016LegacySF_V1.csv";
      }else if (year == "17"){
          btagfilename = "JHUanalyzer/SFs/DeepCSV_94XSF_V4_B_F.csv";
      }else if (year ==  "18"){
          btagfilename = "JHUanalyzer/SFs/DeepCSV_102XSF_V1.csv";
      }
    BTagCalibration calib("DeepCSV", btagfilename);

    BTagCalibrationReader reader(BTagEntry::OP_LOOSE,  // operating point
                             "central",             // central sys type
                             {"up", "down"});      // other sys types

    reader.load(calib,                // calibration instance
            BTagEntry::FLAV_B,    // btag flavour
            "incl");
'''
if not a.isData:
    ROOT.gInterpreter.ProcessLine(btagLoadCode)
    print ("Btag files load time: "+str((time.time()-start_time)/60.) + ' min')

a.SetCFunc(commonc.deltaPhi)
a.SetCFunc(commonc.vector)
a.SetCFunc(commonc.invariantMass)
customc.Import("pdfweights","JHUanalyzer/Corrections/pdfweights.cc")
customc.Import("hemispherize","JHUanalyzer/Corrections/hemispherize.cc")
customc.Import("triggerlookup","JHUanalyzer/Corrections/triggerlookup.cc")
customc.Import("btagsf","JHUanalyzer/Corrections/btagsf.cc")
customc.Import("ptwlookup","JHUanalyzer/Corrections/ptwlookup.cc")
customc.Import("topCut","JHUanalyzer/Corrections/topCut.cc")
a.SetCFunc(customc.ptwlookup)
a.SetCFunc(customc.btagsf)
a.SetCFunc(customc.pdfweights)
a.SetCFunc(customc.triggerlookup)
a.SetCFunc(customc.hemispherize)
a.SetCFunc(commonc.invariantMassThree)
a.SetCFunc(customc.topCut)



if options.year == '16':
    a.SetTriggers(["HLT_HT650","HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30"])
if options.year == '17'  or options.year == '18':
    a.SetTriggers(["HLT_PFHT1050","HLT_AK8PFJet400_TrimMass30"])

# a.SetVar("lead_vect","analyzer::TLvector("+pt0+",FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])")
# a.SetVar("sublead_vect","analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])")
# a.SetVar("mhh","analyzer::invariantMass(analyzer::TLvector("+pt0+",FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0]),analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1]))")
a.SetVar("mreduced","analyzer::invariantMass(analyzer::TLvector("+pt0+",FatJet_eta[0],FatJet_phi[0],"+mass0+"),analyzer::TLvector("+pt1+",FatJet_eta[1],FatJet_phi[1],"+mass1+"))- ("+mass0+"-125.0) - ("+mass1+"-125.0)")
a.SetVar("pt0",""+pt0+"")
a.SetVar("pt1",""+pt1+"")
a.SetVar("mh",""+mass0+"")
a.SetVar("mh1",""+mass1+"")

####Testing for corrections adding.#######

a.SetVar("Hemispherized","analyzer::Hemispherize(FatJet_pt_nom,FatJet_eta,FatJet_phi,FatJet_msoftdrop_nom,nFatJet,Jet_pt,Jet_eta,Jet_phi,Jet_mass,nJet,Jet_btagDeepB)")
# a.SetVar("b_lead_vect","analyzer::TLvector(Jet_pt[Hemispherized[0]],Jet_eta[Hemispherized[0]],Jet_phi[Hemispherized[0]],Jet_mass[Hemispherized[0]])")
# a.SetVar("b_sublead_vect","analyzer::TLvector(Jet_pt[Hemispherized[1]],Jet_eta[Hemispherized[1]],Jet_phi[Hemispherized[1]],Jet_mass[Hemispherized[1]])")

# a.SetVar("hemisphere1Check","Hemispherized[0]")
# a.SetVar("hemisphere2Check","Hemispherized[1]")

a.SetVar("mbb","analyzer::invariantMass(analyzer::TLvector(Jet_pt[Hemispherized[0]],Jet_eta[Hemispherized[0]],Jet_phi[Hemispherized[0]],Jet_mass[Hemispherized[0]]),analyzer::TLvector(Jet_pt[Hemispherized[1]],Jet_eta[Hemispherized[1]],Jet_phi[Hemispherized[1]],Jet_mass[Hemispherized[1]]))")
a.SetVar("mreduced21","analyzer::invariantMassThree(analyzer::TLvector("+pt1+",FatJet_eta[0],FatJet_phi[0],"+mass1+"),analyzer::TLvector(Jet_pt[Hemispherized[0]],Jet_eta[Hemispherized[0]],Jet_phi[Hemispherized[0]],Jet_mass[Hemispherized[0]]),analyzer::TLvector(Jet_pt[Hemispherized[1]],Jet_eta[Hemispherized[1]],Jet_phi[Hemispherized[1]],Jet_mass[Hemispherized[1]])) - (mh-125.0) - (analyzer::invariantMass(analyzer::TLvector(Jet_pt[Hemispherized[0]],Jet_eta[Hemispherized[0]],Jet_phi[Hemispherized[0]],Jet_mass[Hemispherized[0]]),analyzer::TLvector(Jet_pt[Hemispherized[1]],Jet_eta[Hemispherized[1]],Jet_phi[Hemispherized[1]],Jet_mass[Hemispherized[1]]))- 125)")
a.SetVar("topMassVec","analyzer::topCut(Hemispherized[0],Hemispherized[1],Jet_pt,Jet_eta,Jet_phi,Jet_mass,nJet)")
a.SetVar("topMass","topMassVec[0]")
a.SetVar("topDeltaR","topMassVec[1]")

### Btagging correction code
if not a.isData:
    a.SetVar("btagscalefactor","analyzer::BtagSF(reader,analyzer::TLvector(Jet_pt[Hemispherized[0]],Jet_eta[Hemispherized[0]],Jet_phi[Hemispherized[0]],Jet_mass[Hemispherized[0]]),analyzer::TLvector(Jet_pt[Hemispherized[1]],Jet_eta[Hemispherized[1]],Jet_phi[Hemispherized[1]],Jet_mass[Hemispherized[1]]))")

    #### Trigger correction code

    triggerFile = ROOT.TFile("TriggerWeights.root","READ")
    triggerHistTight = triggerFile.Get(doubleB_name+'tight'+options.year)
    # triggerHistLoose = triggerFile.Get(doubleB_name+'11'+options.year)
    triggerHist21 = triggerFile.Get(doubleB_name+'21'+options.year)
    ROOT.gInterpreter.ProcessLine("auto tHistT = "+doubleB_name+"tight"+options.year+";")
    a.SetVar("triggerTight","analyzer::TriggerLookup(mreduced,tHistT)")
    # ROOT.gInterpreter.ProcessLine("auto tHistL = "+doubleB_name+"loose"+options.year+";")
    a.SetVar("triggerLoose","analyzer::TriggerLookup(mreduced,tHistT)")
    ROOT.gInterpreter.ProcessLine("auto tHist21 = "+doubleB_name+"21"+options.year+";")
    a.SetVar("trigger21","analyzer::TriggerLookup(mreduced21,tHist21)")

    # ### Pileup reweighting code
    # if options.year == '16':
    #     pufile_mc_name="JHUanalyzer/PileupFiles/pileup_profile_Summer16.root" 
    #     pufile_data_name="JHUanalyzer/PileupFiles/PileupData_GoldenJSON_Full2016.root" 
    # elif options.year == '17':
    #     pufile_data_name="JHUanalyzer/PileupFiles/PileupHistogram-goldenJSON-13tev-2018-99bins_withVar.root" 
    #     pufile_mc_name="JHUanalyzer/PileupFiles/mcPileup2017.root"
    # elif options.year == '18':
    #     pufile_data_name="JHUanalyzer/PileupFiles/PileupHistogram-goldenJSON-13tev-2018-100bins_withVar.root"
    #     pufile_mc_name="JHUanalyzer/PileupFiles/mcPileup2018.root"
    # ###NOMINAL
    # puFile_data = ROOT.TFile(pufile_data_name,"READ")
    # puHist_data = puFile_data.Get('pileup')
    # puHist_data.Scale(1/puHist_data.Integral())

    # puFile_mc = ROOT.TFile(pufile_mc_name,"READ")
    # puHist_mc = puFile_mc.Get('pu_mc')
    # puHist_mc.Scale(1/puHist_mc.Integral())

    # puWeights = puHist_data.Clone()
    # puWeights.Divide(puHist_mc)
    # puWeights.Sumw2()

    # ROOT.gInterpreter.ProcessLine("auto puWeightNom = pileup;")
    # ###UP
    # puFile_data_up = ROOT.TFile(pufile_data_name,"READ")
    # puHist_data_up = puFile_data_up.Get('pileup_plus')
    # puHist_data_up.Scale(1/puHist_data_up.Integral())

    # puWeights_up = puHist_data_up.Clone()
    # puWeights_up.Divide(puHist_mc)
    # puWeights_up.Sumw2()

    # ROOT.gInterpreter.ProcessLine("auto puWeightUp = pileup_plus;")
    # ###DOWN
    # puFile_data_down = ROOT.TFile(pufile_data_name,"READ")
    # puHist_data_down = puFile_data_down.Get('pileup_minus')
    # puHist_data_down.Scale(1/puHist_data_down.Integral())

    # puWeights_down = puHist_data.Clone()
    # puWeights_down.Divide(puHist_mc)
    # puWeights_down.Sumw2()

    # ROOT.gInterpreter.ProcessLine("auto puWeightDown = pileup_minus;")

    # a.makePUWeight('PV_npvsGood')
    # a.SetVar("puWeight",'puw[0]')
    # a.SetVar("puWeightUp",'puw[1]')
    # a.SetVar("puWeightDown",'puw[2]')


## top reweighting code if necessary
if not a.isData and 'ttbar' in options.output:
    a.SetVar("topptvector","analyzer::PTWLookup(nGenPart, GenPart_pdgId, GenPart_statusFlags, GenPart_pt, GenPart_eta, GenPart_phi, GenPart_mass, analyzer::TLvector("+pt0+",FatJet_eta[0],FatJet_phi[0],"+mass0+"), analyzer::TLvector("+pt1+",FatJet_eta[1],FatJet_phi[1],"+mass1+"))")
    a.SetVar("topptvectorcheck","topptvector[0]")

#### B tag SF
if "btagHbb" in options.doublebtagger:
    if options.year == '16':
        a.SetVar("dbSFnomloose","1.03*("+pt0+"<350)+1.03*("+pt0+">350)")
        a.SetVar("dbSFuploose","1.09*("+pt0+"<350)+1.09*("+pt0+">350)")
        a.SetVar("dbSFdownloose","0.90*("+pt0+"<350)+0.90*("+pt0+">350)") 
        a.SetVar("dbSFnomtight","0.95*("+pt0+"<350)+0.95*("+pt0+">350)")
        a.SetVar("dbSFuptight","1.02*("+pt0+"<350)+1.02*("+pt0+">350)")
        a.SetVar("dbSFdowntight","0.82*("+pt0+"<350)+0.82*("+pt0+">350)") 
    if options.year == '17':
        a.SetVar("dbSFnomloose","0.96*("+pt0+"<350)+0.95*("+pt0+">350)")
        a.SetVar("dbSFuploose","0.99*("+pt0+"<350)+1.01*("+pt0+">350)")
        a.SetVar("dbSFdownloose","0.93*("+pt0+"<350)+0.91*("+pt0+">350)") 
        a.SetVar("dbSFnomtight","0.85*("+pt0+"<350)+0.8*("+pt0+">350)")
        a.SetVar("dbSFuptight","0.89*("+pt0+"<350)+0.87*("+pt0+">350)")
        a.SetVar("dbSFdowntight","0.81*("+pt0+"<350)+0.76*("+pt0+">350)") 
    if options.year == '18':
        a.SetVar("dbSFnomloose","0.93*("+pt0+"<350)+0.98*("+pt0+">350)")
        a.SetVar("dbSFuploose","0.97*("+pt0+"<350)+1.03*("+pt0+">350)")
        a.SetVar("dbSFdownloose","0.89*("+pt0+"<350)+0.94*("+pt0+">350)") 
        a.SetVar("dbSFnomtight","0.89*("+pt0+"<350)+0.84*("+pt0+">350)")
        a.SetVar("dbSFuptight","0.97*("+pt0+"<350)+0.89*("+pt0+">350)")
        a.SetVar("dbSFdowntight","0.85*("+pt0+"<350)+0.79*("+pt0+">350)")
elif "deepTagMD_HbbvsQCD" in options.doublebtagger:
    a.SetVar("dbSFnomloose","1.1*("+pt0+"<350)+1.1*("+pt0+">350)")
    a.SetVar("dbSFuploose","1.3*("+pt0+"<350)+1.3*("+pt0+">350)")
    a.SetVar("dbSFdownloose","0.9*("+pt0+"<350)+0.9*("+pt0+">350)") 
    a.SetVar("dbSFnomtight","1.1*("+pt0+"<350)+1.1*("+pt0+">350)")
    a.SetVar("dbSFuptight","1.3*("+pt0+"<350)+1.3*("+pt0+">350)")
    a.SetVar("dbSFdowntight","0.9*("+pt0+"<350)+0.9*("+pt0+">350)")
    # if options.year == '16':
    #     a.SetVar("dbSFnomloose","1*(300<"+pt0+"<400)+0.97*(400<"+pt0+"<500)+0.91*(500<"+pt0+"<600)+0.95*("+pt0+">600)")
    #     a.SetVar("dbSFuploose","1.06*(300<"+pt0+"<400)+1*(400<"+pt0+"<500)+0.96*(500<"+pt0+"<600)+0.99*("+pt0+">600)")
    #     a.SetVar("dbSFdownloose","0.94*(300<"+pt0+"<400)+0.94*(400<"+pt0+"<500)+0.86*(500<"+pt0+"<600)+0.91*("+pt0+">600)")
    #     a.SetVar("dbSFnomtight","1*(300<"+pt0+"<400)+0.97*(400<"+pt0+"<500)+0.91*(500<"+pt0+"<600)+0.95*("+pt0+">600)")
    #     a.SetVar("dbSFuptight","1.06*(300<"+pt0+"<400)+1*(400<"+pt0+"<500)+0.96*(500<"+pt0+"<600)+0.99*("+pt0+">600)")
    #     a.SetVar("dbSFdowntight","0.94*(300<"+pt0+"<400)+0.94*(400<"+pt0+"<500)+0.86*(500<"+pt0+"<600)+0.91*("+pt0+">600)")
    # if options.year == '17':
    #     a.SetVar("dbSFnomloose","1.05*(300<"+pt0+"<400)+1.01*(400<"+pt0+"<500)+1.06*(500<"+pt0+"<600)+1.13*("+pt0+">600)")
    #     a.SetVar("dbSFuploose","1.07*(300<"+pt0+"<400)+1.04*(400<"+pt0+"<500)+1.09*(500<"+pt0+"<600)+1.18*("+pt0+">600)")
    #     a.SetVar("dbSFdownloose","1.03*(300<"+pt0+"<400)+0.98*(400<"+pt0+"<500)+1.03*(500<"+pt0+"<600)+1.08*("+pt0+">600)")
    #     a.SetVar("dbSFnomtight","1.05*(300<"+pt0+"<400)+1.01*(400<"+pt0+"<500)+1.06*(500<"+pt0+"<600)+1.13*("+pt0+">600)")
    #     a.SetVar("dbSFuptight","1.07*(300<"+pt0+"<400)+1.04*(400<"+pt0+"<500)+1.09*(500<"+pt0+"<600)+1.18*("+pt0+">600)")
    #     a.SetVar("dbSFdowntight","1.03*(300<"+pt0+"<400)+0.98*(400<"+pt0+"<500)+1.03*(500<"+pt0+"<600)+1.08*("+pt0+">600)")
    # if options.year == '18':
    #     a.SetVar("dbSFnomloose","1.35*(300<"+pt0+"<400)+1.22*(400<"+pt0+"<500)+1.31*(500<"+pt0+"<600)+1.30*("+pt0+">600)")
    #     a.SetVar("dbSFuploose","1.38*(300<"+pt0+"<400)+1.25*(400<"+pt0+"<500)+1.35*(500<"+pt0+"<600)+1.34*("+pt0+">600)")
    #     a.SetVar("dbSFdownloose","1.32*(300<"+pt0+"<400)+1.19*(400<"+pt0+"<500)+1.27*(500<"+pt0+"<600)+1.26*("+pt0+">600)")
    #     a.SetVar("dbSFnomtight","1.35*(300<"+pt0+"<400)+1.22*(400<"+pt0+"<500)+1.31*(500<"+pt0+"<600)+1.30*("+pt0+">600)")
    #     a.SetVar("dbSFuptight","1.38*(300<"+pt0+"<400)+1.25*(400<"+pt0+"<500)+1.35*(500<"+pt0+"<600)+1.34*("+pt0+">600)")
    #     a.SetVar("dbSFdowntight","1.32*(300<"+pt0+"<400)+1.19*(400<"+pt0+"<500)+1.27*(500<"+pt0+"<600)+1.26*("+pt0+">600)")
else:
    a.SetVar("dbSFnomloose","1*("+pt0+"<350)+1*("+pt0+">350)")
    a.SetVar("dbSFuploose","1*("+pt0+"<350)+1*("+pt0+">350)")
    a.SetVar("dbSFdownloose","1*("+pt0+"<350)+1*("+pt0+">350)") 
    a.SetVar("dbSFnomtight","1*("+pt0+"<350)+1*("+pt0+">350)")
    a.SetVar("dbSFuptight","1*("+pt0+"<350)+1*("+pt0+">350)")
    a.SetVar("dbSFdowntight","1*("+pt0+"<350)+1*("+pt0+">350)")
#### make final weights for histos
#### Pileup here taken from TTree branch
if not a.isData:
    if 'ttbar' in options.input:
        a.SetVar("finalweightTight","dbSFnomtight*(dbSFnomtight)*topptvector[0]*triggerTight[0]*puWeight")
        a.SetVar("finalweightLoose","dbSFnomloose*(dbSFnomloose)*topptvector[0]*triggerLoose[0]*puWeight")
        a.SetVar("finalweightTightFailFullSF","dbSFnomtight*(1-dbSFnomtight)*topptvector[0]*triggerTight[0]*puWeight")
        a.SetVar("finalweightLooseFailFullSF","dbSFnomloose*(1-dbSFnomloose)*topptvector[0]*triggerLoose[0]*puWeight")
        a.SetVar("finalweightTightFailHalfSF","dbSFnomtight*topptvector[0]*triggerTight[0]*puWeight")
        a.SetVar("finalweightLooseFailHalfSF","dbSFnomloose*topptvector[0]*triggerLoose[0]*puWeight")

        a.SetVar("finalweight21","dbSFnomloose*topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")
        a.SetVar("finalweight21FailFullSF","(1-dbSFnomloose)*topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")
        a.SetVar("finalweight21FailHalfSF","topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")

    else:
        a.SetVar("finalweightTight","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight")
        a.SetVar("finalweightLoose","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight")
        a.SetVar("finalweightTightFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight")
        a.SetVar("finalweightLooseFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight")
        a.SetVar("finalweightTightFailHalfSF","dbSFnomtight*triggerTight[0]*puWeight")
        a.SetVar("finalweightLooseFailHalfSF","dbSFnomloose*triggerLoose[0]*puWeight")

        a.SetVar("finalweight21","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")
        a.SetVar("finalweight21FailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")
        a.SetVar("finalweight21FailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")


### Here I make the weights for the shape based uncertainties. This cannot be done inline with the Histo1D calls so it is done here.

if not a.isData:

    if 'ttbar' in options.input:
        a.SetVar("topptweight_tight_up","dbSFnomtight*(dbSFnomtight)*topptvector[1]*triggerTight[0]*puWeight")
        a.SetVar("topptweight_tight_down","dbSFnomtight*(dbSFnomtight)*topptvector[2]*triggerTight[0]*puWeight")
        a.SetVar("topptweight_loose_up","dbSFnomloose*(dbSFnomloose)*topptvector[1]*triggerLoose[0]*puWeight")
        a.SetVar("topptweight_loose_down","dbSFnomloose*(dbSFnomloose)*topptvector[2]*triggerLoose[0]*puWeight")

        a.SetVar("topptweight_tight_upFailFullSF","dbSFnomtight*(1-dbSFnomtight)*topptvector[1]*triggerTight[0]*puWeight")
        a.SetVar("topptweight_tight_downFailFullSF","dbSFnomtight*(1-dbSFnomtight)*topptvector[2]*triggerTight[0]*puWeight")
        a.SetVar("topptweight_loose_upFailFullSF","dbSFnomloose*(1-dbSFnomloose)*topptvector[1]*triggerLoose[0]*puWeight")
        a.SetVar("topptweight_loose_downFailFullSF","dbSFnomloose*(1-dbSFnomloose)*topptvector[2]*triggerLoose[0]*puWeight")

        a.SetVar("topptweight_tight_upFailHalfSF","(dbSFnomtight)*topptvector[1]*triggerTight[0]*puWeight")
        a.SetVar("topptweight_tight_downFailHalfSF","(dbSFnomtight)*topptvector[2]*triggerTight[0]*puWeight")
        a.SetVar("topptweight_loose_upFailHalfSF","(dbSFnomloose)*topptvector[1]*triggerLoose[0]*puWeight")
        a.SetVar("topptweight_loose_downFailHalfSF","(dbSFnomloose)*topptvector[2]*triggerLoose[0]*puWeight")

        a.SetVar("Pdfweight",'analyzer::PDFweight(LHEPdfWeight)')
        a.SetVar("Pdfweight_tight_up",'dbSFnomtight*(dbSFnomtight)*Pdfweight[0]*topptvector[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_tight_down",'dbSFnomtight*(dbSFnomtight)*Pdfweight[1]*topptvector[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_loose_up",'dbSFnomloose*(dbSFnomloose)*Pdfweight[0]*topptvector[0]*triggerLoose[0]*puWeight')
        a.SetVar("Pdfweight_loose_down",'dbSFnomloose*(dbSFnomloose)*Pdfweight[1]*topptvector[0]*triggerLoose[0]*puWeight')

        a.SetVar("Pdfweight_tight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*Pdfweight[0]*topptvector[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_tight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*Pdfweight[1]*topptvector[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_loose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*Pdfweight[0]*topptvector[0]*triggerLoose[0]*puWeight')
        a.SetVar("Pdfweight_loose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*Pdfweight[1]*topptvector[0]*triggerLoose[0]*puWeight')

        a.SetVar("Pdfweight_tight_upFailHalfSF",'(dbSFnomtight)*Pdfweight[0]*topptvector[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_tight_downFailHalfSF",'(dbSFnomtight)*Pdfweight[1]*topptvector[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_loose_upFailHalfSF",'(dbSFnomloose)*Pdfweight[0]*topptvector[0]*triggerLoose[0]*puWeight')
        a.SetVar("Pdfweight_loose_downFailHalfSF",'(dbSFnomloose)*Pdfweight[1]*topptvector[0]*triggerLoose[0]*puWeight')

        a.SetVar("pileupweight_tight_up",'dbSFnomtight*(dbSFnomtight)*puWeightUp*topptvector[0]*triggerTight[0]')
        a.SetVar("pileupweight_tight_down",'dbSFnomtight*(dbSFnomtight)*puWeightDown*topptvector[0]*triggerTight[0]')
        a.SetVar("pileupweight_loose_up",'dbSFnomloose*(dbSFnomloose)*puWeightUp*topptvector[0]*triggerLoose[0]')
        a.SetVar("pileupweight_loose_down",'dbSFnomloose*(dbSFnomloose)*puWeightDown*topptvector[0]*triggerLoose[0]')

        a.SetVar("pileupweight_tight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*puWeightUp*topptvector[0]*triggerTight[0]')
        a.SetVar("pileupweight_tight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*puWeightDown*topptvector[0]*triggerTight[0]')
        a.SetVar("pileupweight_loose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*puWeightUp*topptvector[0]*triggerLoose[0]')
        a.SetVar("pileupweight_loose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*puWeightDown*topptvector[0]*triggerLoose[0]')

        a.SetVar("pileupweight_tight_upFailHalfSF",'(dbSFnomtight)*puWeightUp*topptvector[0]*triggerTight[0]')
        a.SetVar("pileupweight_tight_downFailHalfSF",'(dbSFnomtight)*puWeightDown*topptvector[0]*triggerTight[0]')
        a.SetVar("pileupweight_loose_upFailHalfSF",'(dbSFnomloose)*puWeightUp*topptvector[0]*triggerLoose[0]')
        a.SetVar("pileupweight_loose_downFailHalfSF",'(dbSFnomloose)*puWeightDown*topptvector[0]*triggerLoose[0]')

        a.SetVar("triggertight_up",'dbSFnomtight*(dbSFnomtight)*triggerTight[1]*topptvector[0]*puWeight')
        a.SetVar("triggertight_down",'dbSFnomtight*(dbSFnomtight)*triggerTight[2]*topptvector[0]*puWeight')
        a.SetVar("triggerloose_up",'dbSFnomloose*(dbSFnomloose)*triggerLoose[1]*topptvector[0]*puWeight')
        a.SetVar("triggerloose_down",'dbSFnomloose*(dbSFnomloose)*triggerLoose[2]*topptvector[0]*puWeight')

        a.SetVar("triggertight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*triggerTight[1]*topptvector[0]*puWeight')
        a.SetVar("triggertight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*triggerTight[2]*topptvector[0]*puWeight')
        a.SetVar("triggerloose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*triggerLoose[1]*topptvector[0]*puWeight')
        a.SetVar("triggerloose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*triggerLoose[2]*topptvector[0]*puWeight')

        a.SetVar("triggertight_upFailHalfSF",'(dbSFnomtight)*triggerTight[1]*topptvector[0]*puWeight')
        a.SetVar("triggertight_downFailHalfSF",'(dbSFnomtight)*triggerTight[2]*topptvector[0]*puWeight')
        a.SetVar("triggerloose_upFailHalfSF",'(dbSFnomloose)*triggerLoose[1]*topptvector[0]*puWeight')
        a.SetVar("triggerloose_downFailHalfSF",'(dbSFnomloose)*triggerLoose[2]*topptvector[0]*puWeight')

        a.SetVar("dbsftight_up",'dbSFuptight*(dbSFuptight)*triggerTight[0]*topptvector[0]*puWeight')
        a.SetVar("dbsftight_down",'dbSFdowntight*(dbSFdowntight)*triggerTight[0]*topptvector[0]*puWeight')
        a.SetVar("dbsfloose_up",'dbSFuploose*(dbSFuploose)*triggerLoose[0]*topptvector[0]*puWeight')
        a.SetVar("dbsfloose_down",'dbSFdownloose*(dbSFdownloose)*triggerLoose[0]*topptvector[0]*puWeight')

        a.SetVar("dbsftight_upFailFullSF",'dbSFuptight*(1-dbSFuptight)*triggerTight[0]*topptvector[0]*puWeight')
        a.SetVar("dbsftight_downFailFullSF",'dbSFdowntight*(1-dbSFdowntight)*triggerTight[0]*topptvector[0]*puWeight')
        a.SetVar("dbsfloose_upFailFullSF",'dbSFuploose*(1-dbSFuploose)*triggerLoose[0]*topptvector[0]*puWeight')
        a.SetVar("dbsfloose_downFailFullSF",'dbSFdownloose*(1-dbSFdownloose)*triggerLoose[0]*topptvector[0]*puWeight')

        a.SetVar("dbsftight_upFailHalfSF",'(dbSFuptight)*triggerTight[0]*topptvector[0]*puWeight')
        a.SetVar("dbsftight_downFailHalfSF",'(dbSFdowntight)*triggerTight[0]*topptvector[0]*puWeight')
        a.SetVar("dbsfloose_upFailHalfSF",'(dbSFuploose)*triggerLoose[0]*topptvector[0]*puWeight')
        a.SetVar("dbsfloose_downFailHalfSF",'(dbSFdownloose)*triggerLoose[0]*topptvector[0]*puWeight')

#### Now do 2+1 weights
        a.SetVar("topptweight_up","dbSFnomloose*topptvector[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")
        a.SetVar("topptweight_down","dbSFnomloose*topptvector[2]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")

        a.SetVar("topptweight_upFailFullSF","(1-dbSFnomloose)*topptvector[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")
        a.SetVar("topptweight_downFailFullSF","(1-dbSFnomloose)*topptvector[2]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")

        a.SetVar("topptweight_upFailHalfSF","topptvector[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")
        a.SetVar("topptweight_downFailHalfSF","topptvector[2]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]")

        a.SetVar("pileupweight_up",'dbSFnomloose*puWeightUp*topptvector[0]*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("pileupweight_down",'dbSFnomloose*puWeightDown*topptvector[0]*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("pileupweight_upFailFullSF",'(1-dbSFnomloose)*puWeightUp*topptvector[0]*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("pileupweight_downFailFullSF",'(1-dbSFnomloose)*puWeightDown*topptvector[0]*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("pileupweight_upFailHalfSF",'puWeightUp*topptvector[0]*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("pileupweight_downFailHalfSF",'puWeightDown*topptvector[0]*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("Pdfweight_up",'dbSFnomloose*Pdfweight[0]*topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("Pdfweight_down",'dbSFnomloose*Pdfweight[1]*topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("Pdfweight_upFailFullSF",'(1-dbSFnomloose)*Pdfweight[0]*topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("Pdfweight_downFailFullSF",'(1-dbSFnomloose)*Pdfweight[1]*topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("Pdfweight_upFailHalfSF",'Pdfweight[0]*topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("Pdfweight_downFailHalfSF",'Pdfweight[1]*topptvector[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("btagsfweight_up",'dbSFnomloose*puWeight*topptvector[0]*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]')
        a.SetVar("btagsfweight_down",'dbSFnomloose*puWeight*topptvector[0]*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]')

        a.SetVar("btagsfweight_upFailFullSF",'(1-dbSFnomloose)*puWeight*topptvector[0]*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]')
        a.SetVar("btagsfweight_downFailFullSF",'(1-dbSFnomloose)*puWeight*topptvector[0]*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]')

        a.SetVar("btagsfweight_upFailHalfSF",'puWeight*topptvector[0]*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]')
        a.SetVar("btagsfweight_downFailHalfSF",'puWeight*topptvector[0]*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]')

        a.SetVar("trigger_up",'dbSFnomloose*trigger21[1]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("trigger_down",'dbSFnomloose*trigger21[2]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("trigger_upFailFullSF",'(1-dbSFnomloose)*trigger21[1]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("trigger_downFailFullSF",'(1-dbSFnomloose)*trigger21[2]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("trigger_upFailHalfSF",'trigger21[1]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("trigger_downFailHalfSF",'trigger21[2]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("dbsfup",'dbSFuploose*trigger21[0]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("dbsfdown",'dbSFdownloose*trigger21[0]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("dbsfupFailFullSF",'(1-dbSFuploose)*trigger21[0]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("dbsfdownFailFullSF",'(1-dbSFdownloose)*trigger21[0]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("dbsfupFailHalfSF",'trigger21[0]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("dbsfdownFailHalfSF",'trigger21[0]*topptvector[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

    else:
        a.SetVar("Pdfweight",'analyzer::PDFweight(LHEPdfWeight)')
        a.SetVar("Pdfweight_tight_up",'dbSFnomtight*(dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_tight_down",'dbSFnomtight*(dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_loose_up",'dbSFnomloose*(dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight')
        a.SetVar("Pdfweight_loose_down",'dbSFnomloose*(dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight')

        a.SetVar("Pdfweight_tight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_tight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_loose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight')
        a.SetVar("Pdfweight_loose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight')

        a.SetVar("Pdfweight_tight_upFailHalfSF",'(dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_tight_downFailHalfSF",'(dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight')
        a.SetVar("Pdfweight_loose_upFailHalfSF",'(dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight')
        a.SetVar("Pdfweight_loose_downFailHalfSF",'(dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight')

        a.SetVar("pileupweight_tight_up",'dbSFnomtight*(dbSFnomtight)*puWeightUp*triggerTight[0]')
        a.SetVar("pileupweight_tight_down",'dbSFnomtight*(dbSFnomtight)*puWeightDown*triggerTight[0]')
        a.SetVar("pileupweight_loose_up",'dbSFnomloose*(dbSFnomloose)*puWeightUp*triggerLoose[0]')
        a.SetVar("pileupweight_loose_down",'dbSFnomloose*(dbSFnomloose)*puWeightDown*triggerLoose[0]')

        a.SetVar("pileupweight_tight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*puWeightUp*triggerTight[0]')
        a.SetVar("pileupweight_tight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*puWeightDown*triggerTight[0]')
        a.SetVar("pileupweight_loose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*puWeightUp*triggerLoose[0]')
        a.SetVar("pileupweight_loose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*puWeightDown*triggerLoose[0]')

        a.SetVar("pileupweight_tight_upFailHalfSF",'(dbSFnomtight)*puWeightUp*triggerTight[0]')
        a.SetVar("pileupweight_tight_downFailHalfSF",'(dbSFnomtight)*puWeightDown*triggerTight[0]')
        a.SetVar("pileupweight_loose_upFailHalfSF",'(dbSFnomloose)*puWeightUp*triggerLoose[0]')
        a.SetVar("pileupweight_loose_downFailHalfSF",'(dbSFnomloose)*puWeightDown*triggerLoose[0]')

        a.SetVar("triggertight_up",'dbSFnomtight*(dbSFnomtight)*triggerTight[1]*puWeight')
        a.SetVar("triggertight_down",'dbSFnomtight*(dbSFnomtight)*triggerTight[2]*puWeight')
        a.SetVar("triggerloose_up",'dbSFnomloose*(dbSFnomloose)*triggerLoose[1]*puWeight')
        a.SetVar("triggerloose_down",'dbSFnomloose*(dbSFnomloose)*triggerLoose[2]*puWeight')

        a.SetVar("triggertight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*triggerTight[1]*puWeight')
        a.SetVar("triggertight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*triggerTight[2]*puWeight')
        a.SetVar("triggerloose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*triggerLoose[1]*puWeight')
        a.SetVar("triggerloose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*triggerLoose[2]*puWeight')

        a.SetVar("triggertight_upFailHalfSF",'(dbSFnomtight)*triggerTight[1]*puWeight')
        a.SetVar("triggertight_downFailHalfSF",'(dbSFnomtight)*triggerTight[2]*puWeight')
        a.SetVar("triggerloose_upFailHalfSF",'(dbSFnomloose)*triggerLoose[1]*puWeight')
        a.SetVar("triggerloose_downFailHalfSF",'(dbSFnomloose)*triggerLoose[2]*puWeight')

        a.SetVar("dbsftight_up",'dbSFuptight*(dbSFuptight)*triggerTight[0]*puWeight')
        a.SetVar("dbsftight_down",'dbSFdowntight*(dbSFdowntight)*triggerTight[0]*puWeight')
        a.SetVar("dbsfloose_up",'dbSFuploose*(dbSFuploose)*triggerLoose[0]*puWeight')
        a.SetVar("dbsfloose_down",'dbSFdownloose*(dbSFdownloose)*triggerLoose[0]*puWeight')

        a.SetVar("dbsftight_upFailFullSF",'dbSFuptight*(1-dbSFuptight)*triggerTight[0]*puWeight')
        a.SetVar("dbsftight_downFailFullSF",'dbSFdowntight*(1-dbSFdowntight)*triggerTight[0]*puWeight')
        a.SetVar("dbsfloose_upFailFullSF",'dbSFuploose*(1-dbSFuploose)*triggerLoose[0]*puWeight')
        a.SetVar("dbsfloose_downFailFullSF",'dbSFdownloose*(1-dbSFdownloose)*triggerLoose[0]*puWeight')

        a.SetVar("dbsftight_upFailHalfSF",'(dbSFuptight)*triggerTight[0]*puWeight')
        a.SetVar("dbsftight_downFailHalfSF",'(dbSFdowntight)*triggerTight[0]*puWeight')
        a.SetVar("dbsfloose_upFailHalfSF",'(dbSFuploose)*triggerLoose[0]*puWeight')
        a.SetVar("dbsfloose_downFailHalfSF",'(dbSFdownloose)*triggerLoose[0]*puWeight')

#### Now do 2+1 weights

        a.SetVar("pileupweight_up",'dbSFnomloose*puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("pileupweight_down",'dbSFnomloose*puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("pileupweight_upFailFullSF",'(1-dbSFnomloose)*puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("pileupweight_downFailFullSF",'(1-dbSFnomloose)*puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("pileupweight_upFailHalfSF",'puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("pileupweight_downFailHalfSF",'puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("Pdfweight_up",'dbSFnomloose*Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("Pdfweight_down",'dbSFnomloose*Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("Pdfweight_upFailFullSF",'(1-dbSFnomloose)*Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("Pdfweight_downFailFullSF",'(1-dbSFnomloose)*Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("Pdfweight_upFailHalfSF",'Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("Pdfweight_downFailHalfSF",'Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("btagsfweight_up",'dbSFnomloose*puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]')
        a.SetVar("btagsfweight_down",'dbSFnomloose*puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]')

        a.SetVar("btagsfweight_upFailFullSF",'(1-dbSFnomloose)*puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]')
        a.SetVar("btagsfweight_downFailFullSF",'(1-dbSFnomloose)*puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]')

        a.SetVar("btagsfweight_upFailHalfSF",'puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]')
        a.SetVar("btagsfweight_downFailHalfSF",'puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]')

        a.SetVar("trigger_up",'dbSFnomloose*trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("trigger_down",'dbSFnomloose*trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("trigger_upFailFullSF",'(1-dbSFnomloose)*trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("trigger_downFailFullSF",'(1-dbSFnomloose)*trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("trigger_upFailHalfSF",'trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("trigger_downFailHalfSF",'trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("dbsfup",'dbSFuploose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("dbsfdown",'dbSFdownloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("dbsfupFailFullSF",'(1-dbSFuploose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("dbsfdownFailFullSF",'(1-dbSFdownloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')

        a.SetVar("dbsfupFailHalfSF",'trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')
        a.SetVar("dbsfdownFailHalfSF",'trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]')



a.SetVar("eta0","FatJet_eta[0]")
a.SetVar("eta1","FatJet_eta[1]")
a.SetVar("deltaEta","abs(FatJet_eta[0] - FatJet_eta[1])")
a.SetVar("FJtau21","FatJet_tau2[0]/FatJet_tau1[0]")
a.SetVar("tagger","FatJet_"+doubleB_name+"[0]")


DoubleB_lead_tight = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tagTight'][0])+" && FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tagTight'][1])+""
DoubleB_lead_loose = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tagLoose'][0])+" && FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tagLoose'][1])+""
DoubleB_sublead_tight = "FatJet_"+doubleB_name+"[1] > "+str(cutsDict[doubleB_short+'tagTight'][0])+" && FatJet_"+doubleB_name+"[1] < "+str(cutsDict[doubleB_short+'tagTight'][1])+""
DoubleB_sublead_loose = "FatJet_"+doubleB_name+"[1] > "+str(cutsDict[doubleB_short+'tagLoose'][0])+" && FatJet_"+doubleB_name+"[1] < "+str(cutsDict[doubleB_short+'tagLoose'][1])+""
inverted_DoubleB_lead_loose = "FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tagLoose'][0])
inverted_DoubleB_sublead_loose = "FatJet_"+doubleB_name+"[1] < "+str(cutsDict[doubleB_short+'tagLoose'][0])


srttString = "("+DoubleB_lead_tight+" && "+DoubleB_sublead_tight+") == 1"
srllString = "(("+DoubleB_lead_loose+" && "+DoubleB_sublead_loose+") && !("+srttString+")) == 1"
atttString = "(!("+DoubleB_lead_loose+") && ("+DoubleB_sublead_tight+")) == 1"
atllString = "(!("+DoubleB_lead_loose+") && ("+DoubleB_sublead_loose+") && !("+DoubleB_lead_tight+")) == 1"


### Control region algorithm
invertedCR = "("+inverted_DoubleB_lead_loose+" && "+inverted_DoubleB_sublead_loose+")"
invertedCRFail = "!("+invertedCR+") "

#a.SetVar("Pass21","FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tag'][0])+" && "+"FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tag'][1]))
#a.SetVar("Fail21","FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tag'][0]))
pass21String = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tag'][0])+" && "+"FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tag'][1])+""
fail21String = "FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tag'][0])+""

run21String = "((!("+srttString+") && (!("+atttString+")) && (!("+srllString+")) && (!("+atllString+"))) == 1)"
# cand21String = "((!(nFatJet > 1) || !(pt0 > 300 && pt1 > 300) || !(abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4) || !(abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3) || !(mreduced > 750.) || !((105 < mh1) && (mh1 < 135))) == 1)"
cand21String = "((!(nFatJet > 1) || !(pt0 > 300 && pt1 > 300) || !(abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4) || !(abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3) || !(mreduced > 750.) || !((110 < mh1) && (mh1 < 140))) == 1)"
# cand21String = "((!(nFatJet > 1) || !(pt0 > 300 && pt1 > 300) || !(abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4) || !(abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3) || !(mreduced > 750.) || !((115 < mh1) && (mh1 < 145))) == 1)"

if not a.isData: norm = (xsec*lumi)/a.genEventCount
else: norm = 1.

#cutstring_11 = '("+pt0+">350)&&(abs(FatJet_eta[0])<2.4) && (FatJet_pt[1]>350) && (abs(FatJet_eta[1])<2.4)'
#cutstring_21 = '("+pt0+">350)&&(abs(FatJet_eta[0])<2.4) && (Jet_pt[0]>30) && (Jet_pt[1]>30) && (abs(Jet_eta[0])<2.4) && (abs(Jet_eta[1])<2.4)'

slim_skim_Dict = OrderedDict()
slim_skim_Dict["triggers"] = "triggers == 1"
slim_skim_Dict["nFatJets"] = "nFatJet > 0"
#slim_skim_Dict["nJets"] = "nJet > 0"
#slim_skim_Dict["firstCuts"] = "("+cutstring_11+") || ("+cutstring_21+")"

filters_Dict = OrderedDict()
filters_Dict["Flag_goodVertices"] = "Flag_goodVertices == 1"
filters_Dict["Flag_globalSuperTightHalo2016Filter"] = "Flag_globalSuperTightHalo2016Filter == 1"
filters_Dict["Flag_HBHENoiseFilter"] = "Flag_HBHENoiseFilter == 1"
filters_Dict["Flag_HBHENoiseIsoFilter"] = "Flag_HBHENoiseIsoFilter == 1"
filters_Dict["Flag_EcalDeadCellTriggerPrimitiveFilter"] = "Flag_EcalDeadCellTriggerPrimitiveFilter == 1"
filters_Dict["Flag_BadPFMuonFilter"] = "Flag_BadPFMuonFilter == 1"

cutDictionary11SDM = OrderedDict()
cutDictionary11SDM["nFatJets"] = "nFatJet > 1"
cutDictionary11SDM["pt"] = "(pt0 > 300 && pt1 > 300)"
cutDictionary11SDM["eta"] = "abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4"
cutDictionary11SDM["jetID"] = "((FatJet_jetId[0] & 2) == 2) && ((FatJet_jetId[1] & 2) == 2)"
# cutDictionary11["PV"] = "PV_npvsGood > 0"
cutDictionary11SDM["deltaEta"] = "abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3"
cutDictionary11SDM["mreducedCut"] = "mreduced > 750."
# if options.year =='16':
#    cutDictionary11["tau21"] = "(FatJet_tau2[0]/FatJet_tau1[0] < 0.55) && (FatJet_tau2[1]/FatJet_tau1[1] < 0.55)"
# if options.year == '17'  or options.year == '18':
#    cutDictionary11["tau21"] = "(FatJet_tau2[0]/FatJet_tau1[0] < 0.45) && (FatJet_tau2[1]/FatJet_tau1[1] < 0.45)"
cutDictionary11 = OrderedDict()
# cutDictionary11["msoftdrop_1"] = "(105 < mh1) && (mh1 < 135)"
cutDictionary11["msoftdrop_1"] = "(110 < mh1) && (mh1 < 140)"
# cutDictionary11["msoftdrop_1"] = "(115 < mh1) && (mh1 < 145)"

cutDictionary21top = OrderedDict()
cutDictionary21top["candidate21"] = "("+cand21String+") || ("+run21String+")"
cutDictionary21top["nFatJets21"] = "nFatJet > 0"
cutDictionary21top["nJets21"] = "nJet >= 2"
cutDictionary21top["bb_pairs_check"] = "(Hemispherized[0] != 0) && (Hemispherized[1] != 0)"
cutDictionary21top["eta"] = "abs(FatJet_eta[1]) < 2.4"
cutDictionary21top["b_eta"] = "abs(Jet_eta[Hemispherized[0]]) < 2.0 && abs(Jet_eta[Hemispherized[1]]) < 2.0"
cutDictionary21top["pt"] = "(pt1 > 300)"
cutDictionary21top["b_pt"] = "Jet_pt[Hemispherized[0]] > 30 && Jet_pt[Hemispherized[1]] > 30"
cutDictionary21top["jetID"] = "((FatJet_jetId[1] & 2) == 2)"
# cutDictionary21["PV"] = "PV_npvsGood > 0"
cutDictionary21top["mbbCut"] = "90.0 < mbb && mbb < 140.0"
cutDictionary21top["DeepCSV"] = "(0.4184 < Jet_btagDeepB[Hemispherized[0]] && Jet_btagDeepB[Hemispherized[0]] < 1) && (0.4184 < Jet_btagDeepB[Hemispherized[1]] && Jet_btagDeepB[Hemispherized[1]] < 1)"
cutDictionary21top["deltaEta21"]= "abs(FatJet_eta[1] - (Jet_eta[Hemispherized[0]]+Jet_eta[Hemispherized[1]])) < 1.3"


cutDictionary21 = OrderedDict()
cutDictionary21["topMassCut"] = "topMass > 200.0 || topMass < 140.0"
cutDictionary21["topDeltaRCut"] = "topDeltaR > 1.0"


print("Doing slim and skim.")
slim_skim = a.Cut(slim_skim_Dict)

print ("Applying filters.")
filtered = a.Cut(filters_Dict,slim_skim)

print("Doing 1+1 preselection.")
presel11SDM = a.Cut(cutDictionary11SDM,filtered)
presel11 = a.Cut(cutDictionary11,presel11SDM)

SRTT = a.Cut({"SRTT":srttString},presel11)
ATTT = a.Cut({"ATTT":atttString},presel11)
SRLL = a.Cut({"SRLL":srllString},presel11)
ATLL = a.Cut({"ATLL":atllString},presel11)

SRCR = a.Cut({"CR":invertedCR},presel11)
ATCR = a.Cut({"CR":invertedCRFail},presel11)

print("Doing 2+1 preselection.")
presel21top = a.Cut(cutDictionary21top,filtered)
presel21 = a.Cut(cutDictionary21,presel21top)


# check1 = presel21.Histo1D("hemisphere1Check")
# check2 = presel21.Histo1D("hemisphere2Check")

Pass = a.Cut({"Pass21":pass21String},presel21)
Fail = a.Cut({"Fail21":fail21String},presel21)

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()

##### Make histos for kinematic checks

if not a.isData:
    hpt0TT = presel11.Histo1D(("pt0TT","pt0TT",50 ,150 ,1500),'pt0',"finalweightTight")
    hpt1TT = presel11.Histo1D(("pt1TT","pt1TT",50 ,150 ,1500),"pt1","finalweightTight")
    heta0TT = presel11.Histo1D(("eta0TT","eta0TT",50 ,-3.5 ,3.5),'eta0',"finalweightTight")
    heta1TT = presel11.Histo1D(("eta1TT","eta1TT",50 ,-3.5 ,3.5),"eta1","finalweightTight")
    hdeltaEtaTT = presel11.Histo1D(("deltaEtaTT","deltaEtaTT",50 ,0 ,3.5),"deltaEta","finalweightTight")
    hmredTT = presel11.Histo1D(("mredTT","mredTT",28 ,700 ,3500),"mreduced","finalweightTight")
    hmsd0TT = presel11.Histo1D(("msd0TT","msd0TT",50 ,0 ,400),"mh","finalweightTight")
    hmsd1TT = presel11.Histo1D(("msd1TT","msd1TT",50 ,0 ,400),"mh1","finalweightTight")
    htau21TT = presel11.Histo1D(("tau21TT","tau21TT",50 ,0 ,1),"FJtau21","finalweightTight")

    hmsd1_pre = presel11SDM.Histo1D(("msdsub_precut","msdsub_precut",50 ,0 ,400),"mh1","finalweightLoose")

    hpt0LL = presel11.Histo1D(("pt0LL","pt0LL",50 ,150 ,1500),'pt0',"finalweightLoose")
    hpt1LL = presel11.Histo1D(("pt1LL","pt1LL",50 ,150 ,1500),"pt1","finalweightLoose")
    heta0LL = presel11.Histo1D(("eta0LL","eta0LL",50 ,-3.5 ,3.5),'eta0',"finalweightLoose")
    heta1LL = presel11.Histo1D(("eta1LL","eta1LL",50 ,-3.5 ,3.5),"eta1","finalweightLoose")
    hdeltaEtaLL = presel11.Histo1D(("deltaEtaLL","deltaEtaLL",50 ,0 ,3.5),"deltaEta","finalweightLoose")
    hmredLL = presel11.Histo1D(("mredLL","mredLL",28 ,700 ,3500),"mreduced","finalweightLoose")
    hmsd0LL = presel11.Histo1D(("msd0LL","msd0LL",50 ,0 ,400),"mh","finalweightLoose")
    hmsd1LL = presel11.Histo1D(("msd1LL","msd1LL",50 ,0 ,400),"mh1","finalweightLoose")
    htau21LL = presel11.Histo1D(("tau21LL","tau21LL",50 ,0 ,1),"FJtau21","finalweightLoose")


    htaggerTT = presel11.Histo1D(("FatJet_"+doubleB_name+"[0]","FatJet_"+doubleB_name+"[0]_TT",50 ,-1 ,1),"tagger","finalweightTight")
    htaggerLL = presel11.Histo1D(("FatJet_"+doubleB_name+"[0]","FatJet_"+doubleB_name+"[0]_LL",50 ,-1 ,1),"tagger","finalweightLoose")

    htopMassBefore = presel21top.Histo1D(("topMassBefore","topMassBefore",50 ,100 ,1000),'topMass',"finalweightLoose")
    htopMassPass = Pass.Histo1D(("topMassPass","topMassPass",50 ,100 ,1000),'topMass',"finalweightLoose")
    htopMassFail = Fail.Histo1D(("topMassFail","topMassFail",50 ,100 ,1000),'topMass',"finalweightLoose")

    htopDeltaRBefore = presel21top.Histo1D(("topDeltaRBefore","topMassBefore",50 ,0 ,5),'topDeltaR',"finalweightLoose")
    htopDeltaRPass = Pass.Histo1D(("topDeltaRPass","topMassPass",50 ,0 ,5),'topDeltaR',"finalweightLoose")
    htopDeltaRFail = Fail.Histo1D(("topDeltaRFail","topMassFail",50 ,0 ,5),'topDeltaR',"finalweightLoose")

else:
    hpt0TT = presel11.Histo1D(("pt0TT","pt0TT",50 ,150 ,1500),'pt0')
    hpt1TT = presel11.Histo1D(("pt1TT","pt1TT",50 ,150 ,1500),"pt1")
    heta0TT = presel11.Histo1D(("eta0TT","eta0TT",50 ,-3.5 ,3.5),'eta0')
    heta1TT = presel11.Histo1D(("eta1TT","eta1TT",50 ,-3.5 ,3.5),"eta1")
    hdeltaEtaTT = presel11.Histo1D(("deltaEtaTT","deltaEtaTT",50 ,0 ,3.5),"deltaEta")
    hmredTT = presel11.Histo1D(("mredTT","mredTT",28 ,700 ,3500),"mreduced")
    hmsd0TT = presel11.Histo1D(("msd0TT","msd0TT",50 ,0 ,400),"mh")
    hmsd1TT = presel11.Histo1D(("msd1TT","msd1TT",50 ,0 ,400),"mh1")
    htau21TT = presel11.Histo1D(("tau21TT","tau21TT",50 ,0 ,1),"FJtau21")

    hpt0LL = presel11.Histo1D(("pt0LL","pt0LL",50 ,150 ,1500),'pt0')
    hpt1LL = presel11.Histo1D(("pt1LL","pt1LL",50 ,150 ,1500),"pt1")
    heta0LL = presel11.Histo1D(("eta0LL","eta0LL",50 ,-3.5 ,3.5),'eta0')
    heta1LL = presel11.Histo1D(("eta1LL","eta1LL",50 ,-3.5 ,3.5),"eta1")
    hdeltaEtaLL = presel11.Histo1D(("deltaEtaLL","deltaEtaLL",50 ,0 ,3.5),"deltaEta")
    hmredLL = presel11.Histo1D(("mredLL","mredLL",28 ,700 ,3500),"mreduced")
    hmsd0LL = presel11.Histo1D(("msd0LL","msd0LL",50 ,0 ,400),"mh")
    hmsd1LL = presel11.Histo1D(("msd1LL","msd1LL",50 ,0 ,400),"mh1")
    htau21LL = presel11.Histo1D(("tau21LL","tau21LL",50 ,0 ,1),"FJtau21")

    htaggerTT = presel11.Histo1D(("FatJet_"+doubleB_name+"[0]","FatJet_"+doubleB_name+"[0]_TT",50 ,-1 ,1),"tagger")
    htaggerLL = presel11.Histo1D(("FatJet_"+doubleB_name+"[0]","FatJet_"+doubleB_name+"[0]_LL",50 ,-1 ,1),"tagger")

    hmsd1_pre = presel11SDM.Histo1D(("msdsub_precut","msdsub_precut",50 ,0 ,400),"mh1")

    htopMassBefore = presel21top.Histo1D(("topMassBefore","topMassBefore",50 ,100 ,1000),'topMass')
    htopMassPass = Pass.Histo1D(("topMassPass","topMassPass",50 ,100 ,1000),'topMass')
    htopMassFail = Fail.Histo1D(("topMassFail","topMassFail",50 ,100 ,1000),'topMass')

    htopDeltaRBefore = presel21top.Histo1D(("topDeltaRBefore","topMassBefore",50 ,0 ,5),'topDeltaR')
    htopDeltaRPass = Pass.Histo1D(("topDeltaRPass","topMassPass",50 ,0 ,5),'topDeltaR')
    htopDeltaRFail = Fail.Histo1D(("topDeltaRFail","topMassFail",50 ,0 ,5),'topDeltaR')

if not a.isData:
    hSRTT11 = SRTT.Histo2D(("SRTT_11","SRTT_11",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced',"finalweightTight")
    hSFTT11 = SRTT.Histo2D(("SFTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightTightFailFullSF")
    hATTT11 = ATTT.Histo2D(("ATTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightTightFailHalfSF")

    hSRLL11 = SRLL.Histo2D(("SRLL_11","SRLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLoose")
    hSFLL11 = SRLL.Histo2D(("SFLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailFullSF")
    hATLL11 = ATLL.Histo2D(("ATLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailHalfSF")


    hSRTT21 = Pass.Histo2D(("Pass_21","Pass_21",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21',"finalweight21")
    hSFTT21 = Pass.Histo2D(("SFFail_21","ATTT_21",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21","finalweight21FailFullSF")
    hATTT21 = Fail.Histo2D(("Fail_21","ATTT_21",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21","finalweight21FailHalfSF")

else:
    hSRTT11 = SRTT.Histo2D(("SRTT_11","SRTT_11",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced')
    hATTT11 = ATTT.Histo2D(("ATTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hSRLL11 = SRLL.Histo2D(("SRLL_11","SRLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hATLL11 = ATLL.Histo2D(("ATLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")

    hSRTT21 = Pass.Histo2D(("Pass_21","Pass_21",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21')
    hATTT21 = Fail.Histo2D(("Fail_21","Fail_21",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21")

### Implement control region
if not a.isData:
    hSRCR11 = SRCR.Histo2D(("SRCR_11","SRCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLoose")
    hSFCR11 = SRCR.Histo2D(("SFCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailFullSF")
    hATCR11 = ATCR.Histo2D(("ATCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailHalfSF")
    hATCR11.Add(hSFCR11.GetPtr())

else:
    hSRCR11 = SRCR.Histo2D(("SRCR_11","SRCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hATCR11 = ATCR.Histo2D(("ATCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")


### Shape based templates

if not a.isData:

##### 1+1 templates
    hSRTT11_pdfUp = SRTT.Histo2D(("SRTT_11_pdfUp","SRTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','Pdfweight_tight_up')
    hATTT11_pdfUp = ATTT.Histo2D(("ATTT_11_pdfUp","ATTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_upFailHalfSF')
    hSFTT11_pdfUp = SRTT.Histo2D(("SFTT_11_pdfUp","ATTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_upFailFullSF')

    hSRLL11_pdfUp = SRLL.Histo2D(("SRLL_11_pdfUp","SRLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_up')
    hATLL11_pdfUp = ATLL.Histo2D(("ATLL_11_pdfUp","ATLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailHalfSF')
    hSFLL11_pdfUp = SRLL.Histo2D(("SFLL_11_pdfUp","ATLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailFullSF')

    hSRTT11_pdfDown = SRTT.Histo2D(("SRTT_11_pdfDown","SRTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','Pdfweight_tight_down')
    hATTT11_pdfDown = ATTT.Histo2D(("ATTT_11_pdfDown","ATTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_downFailHalfSF')
    hSFTT11_pdfDown = SRTT.Histo2D(("SFTT_11_pdfDown","ATTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_downFailFullSF')

    hSRLL11_pdfDown = SRLL.Histo2D(("SRLL_11_pdfDown","SRLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_down')
    hATLL11_pdfDown = ATLL.Histo2D(("ATLL_11_pdfDown","ATLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailHalfSF')
    hSFLL11_pdfDown = SRLL.Histo2D(("SFLL_11_pdfDown","ATLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailFullSF')

    hSRTT11_pileupUp = SRTT.Histo2D(("SRTT_11_pileupUp","SRTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','pileupweight_tight_up')
    hATTT11_pileupUp = ATTT.Histo2D(("ATTT_11_pileupUp","ATTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_upFailHalfSF')
    hSFTT11_pileupUp = SRTT.Histo2D(("SFTT_11_pileupUp","ATTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_upFailFullSF')

    hSRLL11_pileupUp = SRLL.Histo2D(("SRLL_11_pileupUp","SRLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_up')
    hATLL11_pileupUp = ATLL.Histo2D(("ATLL_11_pileupUp","ATLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailHalfSF')
    hSFLL11_pileupUp = SRLL.Histo2D(("SFLL_11_pileupUp","ATLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailFullSF')

    hSRTT11_pileupDown = SRTT.Histo2D(("SRTT_11_pileupDown","SRTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','pileupweight_tight_down')
    hATTT11_pileupDown = ATTT.Histo2D(("ATTT_11_pileupDown","ATTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_downFailHalfSF')
    hSFTT11_pileupDown = SRTT.Histo2D(("SFTT_11_pileupDown","ATTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_downFailFullSF')

    hSRLL11_pileupDown = SRLL.Histo2D(("SRLL_11_pileupDown","SRLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_down')
    hATLL11_pileupDown = ATLL.Histo2D(("ATLL_11_pileupDown","ATLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailHalfSF')
    hSFLL11_pileupDown = SRLL.Histo2D(("SFLL_11_pileupDown","ATLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailFullSF')

    hSRTT11_triggertight_up = SRTT.Histo2D(("SRTT_11_trigger_up","SRTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','triggertight_up')
    hATTT11_triggertight_up = ATTT.Histo2D(("ATTT_11_trigger_up","ATTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_upFailHalfSF')
    hSFTT11_triggertight_up = SRTT.Histo2D(("SFTT_11_trigger_up","ATTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_upFailFullSF')

    hSRLL11_triggerloose_up = SRLL.Histo2D(("SRLL_11_trigger_up","SRLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_up')
    hATLL11_triggerloose_up = ATLL.Histo2D(("ATLL_11_trigger_up","ATLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailHalfSF')
    hSFLL11_triggerloose_up = SRLL.Histo2D(("SFLL_11_trigger_up","ATLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailFullSF')

    hSRTT11_triggertight_down = SRTT.Histo2D(("SRTT_11_trigger_down","SRTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','triggertight_down')
    hATTT11_triggertight_down = ATTT.Histo2D(("ATTT_11_trigger_down","ATTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_downFailHalfSF')
    hSFTT11_triggertight_down = SRTT.Histo2D(("SFTT_11_trigger_down","ATTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_downFailFullSF')

    hSRLL11_triggerloose_down = SRLL.Histo2D(("SRLL_11_trigger_down","SRLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_down')
    hATLL11_triggerloose_down = ATLL.Histo2D(("ATLL_11_trigger_down","ATLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailHalfSF')
    hSFLL11_triggerloose_down = SRLL.Histo2D(("SFLL_11_trigger_down","ATLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailFullSF')

    hSRTT11_dbsftight_up = SRTT.Histo2D(("SRTT_11_dbsf_up","SRTT_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','dbsftight_up')
    hATTT11_dbsftight_up = ATTT.Histo2D(("ATTT_11_dbsf_up","ATTT_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_upFailHalfSF')
    hSFTT11_dbsftight_up = SRTT.Histo2D(("SFTT_11_dbsf_up","ATTT_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_upFailFullSF')

    hSRLL11_dbsfloose_up = SRLL.Histo2D(("SRLL_11_dbsf_up","SRLL_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_up')
    hATLL11_dbsfloose_up = ATLL.Histo2D(("ATLL_11_dbsf_up","ATLL_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_upFailHalfSF')
    hSFLL11_dbsfloose_up = SRLL.Histo2D(("SFLL_11_dbsf_up","ATLL_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_upFailFullSF')

    hSRTT11_dbsftight_down = SRTT.Histo2D(("SRTT_11_dbsf_down","SRTT_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','dbsftight_down')
    hATTT11_dbsftight_down = ATTT.Histo2D(("ATTT_11_dbsf_down","ATTT_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_downFailHalfSF')
    hSFTT11_dbsftight_down = SRTT.Histo2D(("SFTT_11_dbsf_down","ATTT_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_downFailFullSF')

    hSRLL11_dbsfloose_down = SRLL.Histo2D(("SRLL_11_dbsf_down","SRLL_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_down')
    hATLL11_dbsfloose_down = ATLL.Histo2D(("ATLL_11_dbsf_down","ATLL_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_downFailHalfSF')
    hSFLL11_dbsfloose_down = SRLL.Histo2D(("SFLL_11_dbsf_down","ATLL_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_downFailFullSF')

##### Control Region templates

    hSRCR11_pdfUp = SRCR.Histo2D(("SRCR_11_pdfUp","SRCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_up')
    hATCR11_pdfUp = ATCR.Histo2D(("ATCR_11_pdfUp","ATCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailHalfSF')
    hSFCR11_pdfUp = SRCR.Histo2D(("SFCR_11_pdfUp","ATCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailFullSF')

    hSRCR11_pdfDown = SRCR.Histo2D(("SRCR_11_pdfDown","SRCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_down')
    hATCR11_pdfDown = ATCR.Histo2D(("ATCR_11_pdfDown","ATCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailHalfSF')
    hSFCR11_pdfDown = SRCR.Histo2D(("SFCR_11_pdfDown","ATCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailFullSF')

    hSRCR11_pileupUp = SRCR.Histo2D(("SRCR_11_pileupUp","SRCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_up')
    hATCR11_pileupUp = ATCR.Histo2D(("ATCR_11_pileupUp","ATCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailHalfSF')
    hSFCR11_pileupUp = SRCR.Histo2D(("SFCR_11_pileupUp","ATCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailFullSF')

    hSRCR11_pileupDown = SRCR.Histo2D(("SRCR_11_pileupDown","SRCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_down')
    hATCR11_pileupDown = ATCR.Histo2D(("ATCR_11_pileupDown","ATCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailHalfSF')
    hSFCR11_pileupDown = SRCR.Histo2D(("SFCR_11_pileupDown","ATCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailFullSF')

    hSRCR11_triggerloose_up = SRCR.Histo2D(("SRCR_11_trigger_up","SRCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_up')
    hATCR11_triggerloose_up = ATCR.Histo2D(("ATCR_11_trigger_up","ATCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailHalfSF')
    hSFCR11_triggerloose_up = SRCR.Histo2D(("SFCR_11_trigger_up","ATCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailFullSF')

    hSRCR11_triggerloose_down = SRCR.Histo2D(("SRCR_11_trigger_down","SRCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_down')
    hATCR11_triggerloose_down = ATCR.Histo2D(("ATCR_11_trigger_down","ATCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailHalfSF')
    hSFCR11_triggerloose_down = SRCR.Histo2D(("SFCR_11_trigger_down","ATCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailFullSF')

    hSRCR11_dbsfloose_up = SRCR.Histo2D(("SRCR_11_dbsf_up","SRCR_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_up')
    hATCR11_dbsfloose_up = ATCR.Histo2D(("ATCR_11_dbsf_up","ATCR_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_upFailHalfSF')
    hSFCR11_dbsfloose_up = SRCR.Histo2D(("SFCR_11_dbsf_up","ATCR_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_upFailFullSF')

    hSRCR11_dbsfloose_down = SRCR.Histo2D(("SRCR_11_dbsf_down","SRCR_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_down')
    hATCR11_dbsfloose_down = ATCR.Histo2D(("ATCR_11_dbsf_down","ATCR_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_downFailHalfSF')
    hSFCR11_dbsfloose_down = SRCR.Histo2D(("SFCR_11_dbsf_down","ATCR_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_downFailFullSF')

##### Now for 2+1 template histo calls.

    hSRTT21_pdfUp = Pass.Histo2D(("SRTT_21_pdfUp","SRTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','Pdfweight_up')
    hATTT21_pdfUp = Fail.Histo2D(("ATTT_21_pdfUp","ATTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'Pdfweight_upFailHalfSF')
    hSFTT21_pdfUp = Pass.Histo2D(("SFTT_21_pdfUp","SFTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'Pdfweight_upFailFullSF')

    hSRTT21_pdfDown = Pass.Histo2D(("SRTT_21_pdfDown","SRTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','Pdfweight_down')
    hATTT21_pdfDown = Fail.Histo2D(("ATTT_21_pdfDown","ATTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'Pdfweight_downFailHalfSF')
    hSFTT21_pdfDown = Pass.Histo2D(("SFTT_21_pdfDown","ATTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'Pdfweight_downFailFullSF')

    hSRTT21_pileupUp = Pass.Histo2D(("SRTT_21_pileupUp","SRTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','pileupweight_up')
    hATTT21_pileupUp = Fail.Histo2D(("ATTT_21_pileupUp","ATTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'pileupweight_upFailHalfSF')
    hSFTT21_pileupUp = Pass.Histo2D(("SFTT_21_pileupUp","SFTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'pileupweight_upFailFullSF')

    hSRTT21_pileupDown = Pass.Histo2D(("SRTT_21_pileupDown","SRTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','pileupweight_down')
    hATTT21_pileupDown = Fail.Histo2D(("ATTT_21_pileupDown","ATTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'pileupweight_downFailHalfSF')
    hSFTT21_pileupDown = Pass.Histo2D(("SFTT_21_pileupDown","ATTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'pileupweight_downFailFullSF')

    hSRTT21_trigger_up = Pass.Histo2D(("SRTT_21_trigger_up","SRTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','trigger_up')
    hATTT21_trigger_up = Fail.Histo2D(("ATTT_21_trigger_up","ATTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'trigger_upFailHalfSF')
    hSFTT21_trigger_up = Pass.Histo2D(("SFTT_21_trigger_up","SFTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'trigger_upFailFullSF')

    hSRTT21_trigger_down = Pass.Histo2D(("SRTT_21_trigger_down","SRTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','trigger_down')
    hATTT21_trigger_down = Fail.Histo2D(("ATTT_21_trigger_down","ATTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'trigger_downFailHalfSF')
    hSFTT21_trigger_down = Pass.Histo2D(("SFTT_21_trigger_down","ATTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'trigger_downFailFullSF')

    hSRTT21_btagsfUp = Pass.Histo2D(("hSRTT_21_btagsfUp","SRTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','btagsfweight_up')
    hATTT21_btagsfUp = Fail.Histo2D(("hATTT_21_btagsfUp","ATTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'btagsfweight_upFailHalfSF')
    hSFTT21_btagsfUp = Pass.Histo2D(("hSFTT_21_btagsfUp","SFTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'btagsfweight_upFailFullSF')

    hSRTT21_btagsfDown = Pass.Histo2D(("hSRTT_21_btagsfDown","SRTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','btagsfweight_down')
    hATTT21_btagsfDown = Fail.Histo2D(("hATTT_21_btagsfDown","ATTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'btagsfweight_downFailHalfSF')
    hSFTT21_btagsfDown = Pass.Histo2D(("hSFTT_21_btagsfDown","ATTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'btagsfweight_downFailFullSF')

    hSRTT21_dbsf_up = Pass.Histo2D(("SRTT_21_dbsf_up","SRTT_21_dbsfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','dbsfup')
    hATTT21_dbsf_up = Fail.Histo2D(("ATTT_21_dbsf_up","ATTT_21_dbsfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'dbsfupFailHalfSF')
    hSFTT21_dbsf_up = Pass.Histo2D(("SFTT_21_dbsf_up","SFTT_21_dbsfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'dbsfupFailFullSF')

    hSRTT21_dbsf_down = Pass.Histo2D(("SRTT_21_dbsf_down","SRTT_21_dbsfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','dbsfdown')
    hATTT21_dbsf_down = Fail.Histo2D(("ATTT_21_dbsf_down","ATTT_21_dbsfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'dbsfdownFailHalfSF')
    hSFTT21_dbsf_down = Pass.Histo2D(("SFTT_21_dbsf_down","ATTT_21_dbsfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'dbsfdownFailFullSF')

    if 'ttbar' in options.input:
#### 1+1 Templates
        hSRTT11_topptUp = SRTT.Histo2D(("SRTT_11_topptUp","SRTT_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','topptweight_tight_up')
        hATTT11_topptUp = ATTT.Histo2D(("ATTT_11_topptUp","ATTT_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_upFailHalfSF')
        hSFTT11_topptUp = SRTT.Histo2D(("SFTT_11_topptUp","ATTT_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_upFailFullSF')

        hSRLL11_topptUp = SRLL.Histo2D(("SRLL_11_topptUp","SRLL_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_up')
        hATLL11_topptUp = ATLL.Histo2D(("ATLL_11_topptUp","ATLL_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_upFailHalfSF')
        hSFLL11_topptUp = SRLL.Histo2D(("SFLL_11_topptUp","ATLL_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_upFailFullSF')

        hSRTT11_topptDown = SRTT.Histo2D(("SRTT_11_topptDown","SRTT_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','topptweight_tight_down')
        hATTT11_topptDown = ATTT.Histo2D(("ATTT_11_topptDown","ATTT_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_downFailHalfSF')
        hSFTT11_topptDown = SRTT.Histo2D(("SFTT_11_topptDown","ATTT_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_downFailFullSF')

        hSRLL11_topptDown = SRLL.Histo2D(("SRLL_11_topptDown","SRLL_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_down')
        hATLL11_topptDown = ATLL.Histo2D(("ATLL_11_topptDown","ATLL_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_downFailHalfSF')
        hSFLL11_topptDown = SRLL.Histo2D(("SFLL_11_topptDown","ATLL_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_downFailFullSF')

### Now Control Region templates
        hSRCR11_topptUp = SRCR.Histo2D(("SRCR_11_topptUp","SRCR_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_up')
        hATCR11_topptUp = ATCR.Histo2D(("ATCR_11_topptUp","ATCR_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_upFailHalfSF')
        hSFCR11_topptUp = SRCR.Histo2D(("SFCR_11_topptUp","ATCR_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_upFailFullSF')

        hSRCR11_topptDown = SRCR.Histo2D(("SRCR_11_topptDown","SRCR_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_down')
        hATCR11_topptDown = ATCR.Histo2D(("ATCR_11_topptDown","ATCR_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_downFailHalfSF')
        hSFCR11_topptDown = SRCR.Histo2D(("SFCR_11_topptDown","ATCR_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_downFailFullSF')

### Now 2+1 top templates
        hSRTT21_topptUp = Pass.Histo2D(("SRTT_21_topptUp","SRTT_21_topptUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','topptweight_up')
        hATTT21_topptUp = Fail.Histo2D(("ATTT_21_topptUp","ATTT_21_topptUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'topptweight_upFailHalfSF')
        hSFTT21_topptUp = Pass.Histo2D(("SFTT_21_topptUp","SFTT_21_topptUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'topptweight_upFailFullSF')


        hSRTT21_topptDown = Pass.Histo2D(("SRTT_21_topptDown","SRTT_21_topptDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','topptweight_down')
        hATTT21_topptDown = Fail.Histo2D(("ATTT_21_topptDown","ATTT_21_topptDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'topptweight_downFailHalfSF')
        hSFTT21_topptDown = Pass.Histo2D(("SFTT_21_topptDown","ATTT_21_topptDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'topptweight_downFailFullSF')


        top_check = presel11.Histo1D("topptvectorcheck")


if not a.isData:

    hATTT11.Add(hSFTT11.GetPtr())
    hATLL11.Add(hSFLL11.GetPtr())
    hATTT21.Add(hSFTT21.GetPtr())

##### 1+1 templates

    hATTT11_pdfUp.Add(hSFTT11_pdfUp.GetPtr())
    hATLL11_pdfUp.Add(hSFLL11_pdfUp.GetPtr())
    hATTT11_pdfDown.Add(hSFTT11_pdfDown.GetPtr())
    hATLL11_pdfDown.Add(hSFLL11_pdfDown.GetPtr())
    hATTT11_pileupUp.Add(hSFTT11_pileupUp.GetPtr())
    hATLL11_pileupUp.Add(hSFLL11_pileupUp.GetPtr())
    hATTT11_pileupDown.Add(hSFTT11_pileupDown.GetPtr())
    hATLL11_pileupDown.Add(hSFLL11_pileupDown.GetPtr())
    hATTT11_triggertight_up.Add(hSFTT11_triggertight_up.GetPtr())
    hATLL11_triggerloose_up.Add(hSFLL11_triggerloose_up.GetPtr())
    hATTT11_triggertight_down.Add(hSFTT11_triggertight_down.GetPtr())
    hATLL11_triggerloose_down.Add(hSFLL11_triggerloose_down.GetPtr())
    hATTT11_dbsftight_up.Add(hSFTT11_dbsftight_up.GetPtr())
    hATLL11_dbsfloose_up.Add(hSFLL11_dbsfloose_up.GetPtr())
    hATTT11_dbsftight_down.Add(hSFTT11_dbsftight_down.GetPtr())
    hATLL11_dbsfloose_down.Add(hSFLL11_dbsfloose_down.GetPtr())

##### Control Region templates

    hATCR11_pdfUp.Add(hSFCR11_pdfUp.GetPtr())
    hATCR11_pdfDown.Add(hSFCR11_pdfDown.GetPtr())
    hATCR11_pileupUp.Add(hSFCR11_pileupUp.GetPtr())
    hATCR11_pileupDown.Add(hSFCR11_pileupDown.GetPtr())
    hATCR11_triggerloose_up.Add(hSFCR11_triggerloose_up.GetPtr())
    hATCR11_triggerloose_down.Add(hSFCR11_triggerloose_down.GetPtr())
    hATCR11_dbsfloose_up.Add(hSFCR11_dbsfloose_up.GetPtr())
    hATCR11_dbsfloose_down.Add(hSFCR11_dbsfloose_down.GetPtr())

##### Now for 2+1 template histo calls.
    hATTT21_pdfUp.Add(hSFTT21_pdfUp.GetPtr())
    hATTT21_pdfDown.Add(hSFTT21_pdfDown.GetPtr())
    hATTT21_pileupUp.Add(hSFTT21_pileupUp.GetPtr())
    hATTT21_pileupDown.Add(hSFTT21_pileupDown.GetPtr())
    hATTT21_trigger_up.Add(hSFTT21_trigger_up.GetPtr())
    hATTT21_trigger_down.Add(hSFTT21_trigger_down.GetPtr())
    hATTT21_btagsfUp.Add(hSFTT21_btagsfUp.GetPtr())
    hATTT21_btagsfDown.Add(hSFTT21_btagsfDown.GetPtr())
    hATTT21_dbsf_up.Add(hSFTT21_dbsf_up.GetPtr())
    hATTT21_dbsf_down.Add(hSFTT21_dbsf_down.GetPtr())

    if 'ttbar' in options.input:
#### 1+1 Templates

        hATTT11_topptUp.Add(hSFTT11_topptUp.GetPtr())
        hATLL11_topptUp.Add(hSFLL11_topptUp.GetPtr())
        hATTT11_topptDown.Add(hSFTT11_topptDown.GetPtr())
        hATLL11_topptDown.Add(hSFLL11_topptDown.GetPtr())

### Now Control Region templates

        hATCR11_topptUp.Add(hSFCR11_topptUp.GetPtr())
        hATCR11_topptDown.Add(hSFCR11_topptDown.GetPtr())       

### Now 2+1 top templates

        hATTT21_topptUp.Add(hSFTT21_topptUp.GetPtr())
        hATTT21_topptDown.Add(hSFTT21_topptDown.GetPtr())
if not a.isData:
    if 'ttbar' in options.input:
        for h in [hSRTT11,hATTT11,hSRLL11,hATLL11,hSRTT21,hATTT21,hSRTT11_pdfUp,hATTT11_pdfUp,hSRLL11_pdfUp,hATLL11_pdfUp,hSRTT11_pdfDown,hATTT11_pdfDown,hSRLL11_pdfDown,hATLL11_pdfDown,
        hSRTT11_pileupUp,hATTT11_pileupUp,hSRLL11_pileupUp,hATLL11_pileupUp,hSRTT11_pileupDown,hATTT11_pileupDown,hSRLL11_pileupDown,hATLL11_pileupDown,
        hSRTT11_topptUp,hATTT11_topptUp,hSRLL11_topptUp,hATLL11_topptUp,hSRTT11_topptDown,hATTT11_topptDown,hSRLL11_topptDown,hATLL11_topptDown,
        hSRTT11_triggertight_up,hATTT11_triggertight_up,hSRLL11_triggerloose_up,hATLL11_triggerloose_up,hSRTT11_triggertight_down,hATTT11_triggertight_down,hSRLL11_triggerloose_down,hATLL11_triggerloose_down,
        hSRTT11_dbsftight_up,hATTT11_dbsftight_up,hSRLL11_dbsfloose_up,hATLL11_dbsfloose_up,hSRTT11_dbsftight_down,hATTT11_dbsftight_down,hSRLL11_dbsfloose_down,hATLL11_dbsfloose_down,
        hSRTT21_pdfUp,hATTT21_pdfUp,hSRTT21_pdfDown,hATTT21_pdfDown,hSRTT21_pileupUp,hATTT21_pileupUp,hSRTT21_pileupDown,hATTT21_pileupDown,hSRTT21_dbsf_up,hATTT21_dbsf_up,hSRTT21_dbsf_down,hATTT21_dbsf_down,
        hSRTT21_trigger_up,hATTT21_trigger_up,hSRTT21_trigger_down,hATTT21_trigger_down,hSRTT21_btagsfUp,hATTT21_btagsfUp,hSRTT21_btagsfDown,hATTT21_btagsfDown,
        hSRTT21_topptUp,hATTT21_topptUp,hSRTT21_topptDown,hATTT21_topptDown,
        hpt0TT,hpt1TT,heta0TT,heta1TT,hdeltaEtaTT,hmredTT,hmsd1TT,htau21TT,hmsd0TT,hpt0LL,hpt1LL,heta0LL,heta1LL,hdeltaEtaLL,hmredLL,hmsd1LL,htau21LL,hmsd0LL,htaggerTT,htaggerLL,
        hSRCR11,hATCR11,hSRTT21,hATTT21,hSRCR11_pdfUp,hATCR11_pdfUp,hSRCR11_pdfDown,hATCR11_pdfDown,
        hSRCR11_pileupUp,hATCR11_pileupUp,hSRCR11_pileupDown,hATCR11_pileupDown,
        hSRCR11_topptUp,hATCR11_topptUp,hSRCR11_topptDown,hATCR11_topptDown,
        hSRCR11_triggerloose_up,hATCR11_triggerloose_up,hSRCR11_triggerloose_down,hATCR11_triggerloose_down,
        hSRCR11_dbsfloose_up,hATCR11_dbsfloose_up,hSRCR11_dbsfloose_down,hATCR11_dbsfloose_down,
        htopMassPass,htopMassFail,htopMassBefore,hmsd1_pre,htopDeltaRPass,htopDeltaRFail,htopDeltaRBefore]: h.Scale(norm)
    else:
        for h in [hSRTT11,hATTT11,hSRLL11,hATLL11,hSRTT21,hATTT21,hSRTT11_pdfUp,hATTT11_pdfUp,hSRLL11_pdfUp,hATLL11_pdfUp,hSRTT11_pdfDown,hATTT11_pdfDown,hSRLL11_pdfDown,hATLL11_pdfDown,
        hSRTT11_pileupUp,hATTT11_pileupUp,hSRLL11_pileupUp,hATLL11_pileupUp,hSRTT11_pileupDown,hATTT11_pileupDown,hSRLL11_pileupDown,hATLL11_pileupDown,
        hSRTT11_triggertight_up,hATTT11_triggertight_up,hSRLL11_triggerloose_up,hATLL11_triggerloose_up,hSRTT11_triggertight_down,hATTT11_triggertight_down,hSRLL11_triggerloose_down,hATLL11_triggerloose_down,
        hSRTT11_dbsftight_up,hATTT11_dbsftight_up,hSRLL11_dbsfloose_up,hATLL11_dbsfloose_up,hSRTT11_dbsftight_down,hATTT11_dbsftight_down,hSRLL11_dbsfloose_down,hATLL11_dbsfloose_down,
        hSRTT21_pdfUp,hATTT21_pdfUp,hSRTT21_pdfDown,hATTT21_pdfDown,hSRTT21_pileupUp,hATTT21_pileupUp,hSRTT21_pileupDown,hATTT21_pileupDown,hSRTT21_dbsf_up,hATTT21_dbsf_up,hSRTT21_dbsf_down,hATTT21_dbsf_down,
        hSRTT21_trigger_up,hATTT21_trigger_up,hSRTT21_trigger_down,hATTT21_trigger_down,hSRTT21_btagsfUp,hATTT21_btagsfUp,hSRTT21_btagsfDown,hATTT21_btagsfDown,
        hpt0TT,hpt1TT,heta0TT,heta1TT,hdeltaEtaTT,hmredTT,hmsd1TT,htau21TT,hmsd0TT,hpt0LL,hpt1LL,heta0LL,heta1LL,hdeltaEtaLL,hmredLL,hmsd1LL,htau21LL,hmsd0LL,htaggerTT,htaggerLL,
        hSRCR11,hATCR11,hSRTT21,hATTT21,hSRCR11_pdfUp,hATCR11_pdfUp,hSRCR11_pdfDown,hATCR11_pdfDown,
        hSRCR11_pileupUp,hATCR11_pileupUp,hSRCR11_pileupDown,hATCR11_pileupDown,
        hSRCR11_triggerloose_up,hATCR11_triggerloose_up,hSRCR11_triggerloose_down,hATCR11_triggerloose_down,
        hSRCR11_dbsfloose_up,hATCR11_dbsfloose_up,hSRCR11_dbsfloose_down,hATCR11_dbsfloose_down,
        htopMassPass,htopMassFail,htopMassBefore,hmsd1_pre,htopDeltaRPass,htopDeltaRFail,htopDeltaRBefore]: h.Scale(norm)
# else:
#     for h in [hSRTT11,hATTT11,hSRLL11,hATLL11,hSRTT21,hATTT21]: h.Scale(norm)
print("Norms finished")

norm_hist = ROOT.TH1F('norm','norm',1,0,1)
norm_hist.SetBinContent(1,norm)
norm_hist.Write()

# check1.Write()
# check2.Write()

hmsd1_pre.Write()

htopMassBefore.Write()
htopMassPass.Write()
htopMassFail.Write()

htopDeltaRBefore.Write()
htopDeltaRPass.Write()
htopDeltaRFail.Write()

hpt0TT.Write()
hpt1TT.Write()
heta0TT.Write()
heta1TT.Write()
hdeltaEtaTT.Write()
hmredTT.Write()
hmsd0TT.Write()
hmsd1TT.Write()
htau21TT.Write()

hpt0LL.Write()
hpt1LL.Write()
heta0LL.Write()
heta1LL.Write()
hdeltaEtaLL.Write()
hmredLL.Write()
hmsd0LL.Write()
hmsd1LL.Write()
htau21LL.Write()

htaggerTT.Write()
htaggerLL.Write()

hSRTT11.Write()
hATTT11.Write()
hSRLL11.Write()
hATLL11.Write()

hSRCR11.Write()
hATCR11.Write()

hSRTT21.Write()
hATTT21.Write()
if not a.isData:
    hSRTT11_pdfUp.Write()
    hATTT11_pdfUp.Write()
    hSRLL11_pdfUp.Write()
    hATLL11_pdfUp.Write()

    hSRTT11_pdfDown.Write()
    hATTT11_pdfDown.Write()
    hSRLL11_pdfDown.Write()
    hATLL11_pdfDown.Write()

    hSRTT11_pileupUp.Write()
    hATTT11_pileupUp.Write()
    hSRLL11_pileupUp.Write()
    hATLL11_pileupUp.Write()

    hSRTT11_pileupDown.Write()
    hATTT11_pileupDown.Write()
    hSRLL11_pileupDown.Write()
    hATLL11_pileupDown.Write()

    if 'ttbar' in options.input:
        hSRTT11_topptUp.Write()
        hATTT11_topptUp.Write()
        hSRLL11_topptUp.Write()
        hATLL11_topptUp.Write()

        hSRTT11_topptDown.Write()
        hATTT11_topptDown.Write()
        hSRLL11_topptDown.Write()
        hATLL11_topptDown.Write()

        hSRTT21_topptUp.Write()
        hATTT21_topptUp.Write()

        hSRTT21_topptDown.Write()
        hATTT21_topptDown.Write()

        top_check.Write()

    hSRTT11_triggertight_up.Write()
    hATTT11_triggertight_up.Write()
    hSRLL11_triggerloose_up.Write()
    hATLL11_triggerloose_up.Write()

    hSRTT11_triggertight_down.Write()
    hATTT11_triggertight_down.Write()
    hSRLL11_triggerloose_down.Write()
    hATLL11_triggerloose_down.Write()

    hSRTT11_dbsftight_up.Write()
    hATTT11_dbsftight_up.Write()
    hSRLL11_dbsfloose_up.Write()
    hATLL11_dbsfloose_up.Write()

    hSRTT11_dbsftight_down.Write()
    hATTT11_dbsftight_down.Write()
    hSRLL11_dbsfloose_down.Write()
    hATLL11_dbsfloose_down.Write()

    hSRCR11_pdfUp.Write()
    hATCR11_pdfUp.Write()

    hSRCR11_pdfDown.Write()
    hATCR11_pdfDown.Write()

    hSRCR11_pileupUp.Write()
    hATCR11_pileupUp.Write()

    hSRCR11_pileupDown.Write()
    hATCR11_pileupDown.Write()

    if 'ttbar' in options.input:
        hSRCR11_topptUp.Write()
        hATCR11_topptUp.Write()

        hSRCR11_topptDown.Write()
        hATCR11_topptDown.Write()

        hSRTT21_topptUp.Write()
        hATTT21_topptUp.Write()

        hSRTT21_topptDown.Write()
        hATTT21_topptDown.Write()

        top_check.Write()

    hSRCR11_triggerloose_up.Write()
    hATCR11_triggerloose_up.Write()

    hSRCR11_triggerloose_down.Write()
    hATCR11_triggerloose_down.Write()

    hSRCR11_dbsfloose_up.Write()
    hATCR11_dbsfloose_up.Write()

    hSRCR11_dbsfloose_down.Write()
    hATCR11_dbsfloose_down.Write()


    hSRTT21_pdfUp.Write()
    hATTT21_pdfUp.Write()

    hSRTT21_pdfDown.Write()
    hATTT21_pdfDown.Write()

    hSRTT21_pileupUp.Write()
    hATTT21_pileupUp.Write()

    hSRTT21_pileupDown.Write()
    hATTT21_pileupDown.Write()

    hSRTT21_trigger_up.Write()
    hATTT21_trigger_up.Write()

    hSRTT21_trigger_down.Write()
    hATTT21_trigger_down.Write()

    hSRTT21_btagsfUp.Write()
    hATTT21_btagsfUp.Write()

    hSRTT21_btagsfDown.Write()
    hATTT21_btagsfDown.Write()

    hSRTT21_dbsf_up.Write()
    hATTT21_dbsf_up.Write()

    hSRTT21_dbsf_down.Write()
    hATTT21_dbsf_down.Write()

out_f.Close()

print "Total time: "+str((time.time()-start_time)/60.) + ' min'
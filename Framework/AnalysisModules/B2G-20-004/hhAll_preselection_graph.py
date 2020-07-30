import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from  array import array

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

# Initialize
print("Start analyzer....")
a = analyzer(options.input)

# Example of how to calculate MC normalization for luminosity
if '_loc.txt' in options.input: setname = options.input.split('/')[-1].split('_loc.txt')[0]
elif '.root' in options.input: setname = options.input.split('/')[-1].split('_hh'+options.year+'.root')[0]
else: setname = ''
print("Setname="+setname)
if os.path.exists(options.config):
    print('JSON config imported')
    c = openJSON(options.config)
    if setname != '' and not a.isData:
        if 'QCD' in setname and options.year == '16':
            xsec = c['XSECS'][setname]
        else:  
            xsec = c['XSECS'][setname]

        lumi = c['lumi']
    else: 
        xsec = 1.
        lumi = 1.
if not a.isData: 
    if 'QCD' in setname: norm = 1.
    else: norm = (xsec*lumi)/a.genEventCount
else: norm = 1.

##JECs for actual values.
lead = {}
sublead = {}
if not a.isData:
    lead['JEScorr'] = "1.0"
    sublead['JEScorr'] = "1.0"
    lead['JMScorr'] = "1.0"
    sublead['JMScorr'] = "1.0"
    lead['JERcorr'] = 'FatJet_corr_JER[0]'
    sublead["JERcorr"] = 'FatJet_corr_JER[1]'
    lead['JMRcorr'] = "1.0"
    sublead['JMRcorr'] = "1.0"

    if options.JES != 'nom': 
        if options.JES == 'up':
            lead['JEScorr'] = "(1+(std::abs(FatJet_corr_JES_"+options.JES+"[0] - FatJet_corr_JES[0])/FatJet_corr_JES[0]))"
            sublead['JEScorr'] = "(1+(std::abs(FatJet_corr_JES_"+options.JES+"[1] - FatJet_corr_JES[1])/FatJet_corr_JES[1]))"
        if options.JES == 'down':
            lead['JEScorr'] = "(1-(std::abs(FatJet_corr_JES_"+options.JES+"[0] - FatJet_corr_JES[0])/FatJet_corr_JES[0]))"
            sublead['JEScorr'] = "(1-(std::abs(FatJet_corr_JES_"+options.JES+"[1] - FatJet_corr_JES[1])/FatJet_corr_JES[1]))"

    if options.JER != 'nom':
        if options.JER == 'up':
            lead['JERcorr'] = "(1+(std::abs(FatJet_corr_JER_"+options.JER+"[0] - FatJet_corr_JER[0])/FatJet_corr_JER[0]))"
            sublead['JERcorr'] = "(1+(std::abs(FatJet_corr_JER_"+options.JMS+"[1] - FatJet_corr_JER[1])/FatJet_corr_JER[1]))"
        if options.JER == 'down':
            lead['JERcorr'] = "(1-(std::abs(FatJet_corr_JER_"+options.JER+"[0] - FatJet_corr_JER[0])/FatJet_corr_JER[0]))"
            sublead['JERcorr'] = "(1-(std::abs(FatJet_corr_JER_"+options.JMS+"[1] - FatJet_corr_JER[1])/FatJet_corr_JER[1]))"

    if options.JMS != 'nom':
        if options.JMS == 'up':
            lead['JMScorr'] = "(1+(std::abs(FatJet_corr_JMS_"+options.JMS+"[0] - FatJet_corr_JMS[0])/FatJet_corr_JMS[0]))"
            sublead['JMScorr'] = "(1+(std::abs(FatJet_corr_JMS_"+options.JMS+"[1] - FatJet_corr_JMS[1])/FatJet_corr_JMS[1]))"
        if options.JMS == 'down':
            lead['JMScorr'] = "(1-(std::abs(FatJet_corr_JMS_"+options.JMS+"[0] - FatJet_corr_JMS[0])/FatJet_corr_JMS[0]))"
            sublead['JMScorr'] = "(1-(std::abs(FatJet_corr_JMS_"+options.JMS+"[1] - FatJet_corr_JMS[1])/FatJet_corr_JMS[1]))"

    if options.JMR != 'nom':
        if options.JMR == 'up':
            lead['JMRcorr'] = "(1+(std::abs(FatJet_msoftdrop_corr_JMR_"+options.JMR+"[0] - FatJet_msoftdrop_corr_JMR[0])/FatJet_msoftdrop_corr_JMR[0]))"
            sublead['JMRcorr'] = "(1+(std::abs(FatJet_msoftdrop_corr_JMR_"+options.JMR+"[1] - FatJet_msoftdrop_corr_JMR[1])/FatJet_msoftdrop_corr_JMR[1]))"
        if options.JMR == 'down':
            lead['JMRcorr'] = "(1-(std::abs(FatJet_msoftdrop_corr_JMR_"+options.JMR+"[0] - FatJet_msoftdrop_corr_JMR[0])/FatJet_msoftdrop_corr_JMR[0]))"
            sublead['JMRcorr'] = "(1-(std::abs(FatJet_msoftdrop_corr_JMR_"+options.JMR+"[1] - FatJet_msoftdrop_corr_JMR[1])/FatJet_msoftdrop_corr_JMR[1]))"


if not a.isData:
    lead['pt'] = "*"+lead['JEScorr']+"*"+lead['JERcorr']
    sublead['pt'] = "*"+sublead['JEScorr']+"*"+sublead['JERcorr']
    lead['SDmass'] = "*"+lead['JEScorr']+"*"+lead['JERcorr']+"*"+lead['JMRcorr']+"*"+sublead['JMScorr']
    sublead['SDmass'] = "*"+sublead['JEScorr']+"*"+sublead['JERcorr']+"*"+sublead['JMRcorr']+"*"+sublead['JMScorr']
###Apply corrections
if not a.isData:
    mass0 = "FatJet_msoftdrop_raw[0]"+lead['SDmass']
    mass1 = "FatJet_msoftdrop_raw[1]"+sublead['SDmass']
    pt0 = "FatJet_pt_nom[0]"+lead['pt']
    pt1 = "FatJet_pt_nom[1]"+sublead['pt']
else:
    mass0 = "FatJet_msoftdrop_raw[0]"
    mass1 = "FatJet_msoftdrop_raw[1]"
    pt0 = "FatJet_pt_nom[0]"
    pt1 = "FatJet_pt_nom[1]"
eta0 = "FatJet_eta[0]"
eta1 = "FatJet_eta[1]"
phi0 = "FatJet_phi[0]"
phi1 = "FatJet_phi[1]"

# if not a.isData:
#     mass1 = "FatJet_msoftdrop_nom[0]"+lead['SDmass']
#     mass0 = "FatJet_msoftdrop_nom[1]"+sublead['SDmass']
#     pt1 = "FatJet_pt_nom[0]"+lead['pt']
#     pt0 = "FatJet_pt_nom[1]"+sublead['pt']

# else:
#     mass1 = "FatJet_msoftdrop_nom[0]"
#     mass0 = "FatJet_msoftdrop_nom[1]"
#     pt1 = "FatJet_pt_nom[0]"
#     pt0 = "FatJet_pt_nom[1]"

# eta0 = "FatJet_eta[1]"
# eta1 = "FatJet_eta[0]"
# phi0 = "FatJet_phi[1]"
# phi1 = "FatJet_phi[0]"

print("mass 0 = "+ mass0)
print("mass 1 = "+ mass1)
print("pt 0 = "+ pt0)
print("pt 1 = "+ pt1)

cutsDict = {
    'doubleBtag':[0.8,1.0],
    'doubleBtagTight':[0.8,1.0],
    'doubleBtagLoose':[0.3,1.0],
    'DeepDBtag':[0.86,1.0],
    'DeepDBtagTight':[0.86,1.0],
    #'DeepDBtagTight':[0.6,1.0],
    'DeepDBtagLoose':[0.7,1.0],
    #'DeepDBtagLoose':[0.3,1.0],
    'dak8MDZHbbtag':[0.9,1.0],
    'dak8MDZHbbtagTight':[0.9,1.0],
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

if not a.isData:
### The following loads the btag calibration code in c++ so that it is available to RDF
    ROOT.gInterpreter.Declare('string year = string(TPython::Eval("options.year"));')
    btagLoadCode = '''
        string btagfilename;
        if (year == "16"){
              btagfilename = "JHUanalyzer/data/OfficialSFs/DeepJet_2016LegacySF_V1.csv";
          }else if (year == "17"){
              btagfilename = "JHUanalyzer/data/OfficialSFs/DeepFlavour_94XSF_V4_B_F.csv";
          }else if (year ==  "18"){
              btagfilename = "JHUanalyzer/data/OfficialSFs/DeepJet_102XSF_V2.csv";
          }
        BTagCalibration calib("DeepJet", btagfilename);

        BTagCalibrationReader reader(BTagEntry::OP_MEDIUM,  // operating point
                                 "central",             // central sys type
                                 {"up", "down"});      // other sys types

        reader.load(calib,                // calibration instance
                BTagEntry::FLAV_B,    // btag flavour
                "incl");
    '''

    ROOT.gInterpreter.ProcessLine(btagLoadCode)
    print ("Btag files load time: "+str((time.time()-start_time)/60.) + ' min')

## Sets custom functions for use by RDF

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


# Calculate some new comlumns that we'd like to cut on
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
mbbColumn.Add("bpt0","b_lead_vect.Pt()")
mbbColumn.Add("bpt1","b_sublead_vect.Pt()")
mbbColumn.Add("beta0","b_lead_vect.Eta()")
mbbColumn.Add("beta1","b_sublead_vect.Eta()")

mred21Column = VarGroup("mred21Column")
mred21Column.Add("mreduced21","analyzer::invariantMassThree(lead_vect,b_lead_vect,b_sublead_vect) - (mh-125.0) - (mbb-125)")

# Perform final column calculations (done last after selection to save on CPU time)
correctionColumns = VarGroup("correctionColumns")
correctionColumns11 = VarGroup("correctionColumns11")
correctionColumns21 = VarGroup("correctionColumns21")

    ### Btagging correction code

if not a.isData:
    correctionColumns21.Add("btagscalefactor","analyzer::BtagSF(reader,b_lead_vect,b_sublead_vect)")

    #### Trigger correction code

    triggerFile = ROOT.TFile("TriggerWeights.root","READ")
    triggerHistTightEff = triggerFile.Get("deepTagMD_HbbvsQCD"+'ratio11'+options.year)
    # triggerHistTight = triggerFile.Get(doubleB_name+'tight'+options.year)
    # triggerHistLoose = triggerFile.Get(doubleB_name+'11'+options.year)
    triggerHist21Eff = triggerFile.Get("deepTagMD_HbbvsQCD"+'ratio21'+options.year)
    # triggerHist21 = triggerFile.Get(doubleB_name+'21'+options.year)
    ROOT.gInterpreter.ProcessLine("auto tSF = "+"deepTagMD_HbbvsQCD"+"ratio11"+options.year+";")
    # ROOT.gInterpreter.ProcessLine("auto tHistT = "+doubleB_name+"tight"+options.year+";")
    correctionColumns.Add("triggerTight","analyzer::TriggerLookup(mreduced,tSF)")
    # ROOT.gInterpreter.ProcessLine("auto tHistL = "+doubleB_name+"loose"+options.year+";")
    correctionColumns.Add("triggerLoose","analyzer::TriggerLookup(mreduced,tSF)")
    ROOT.gInterpreter.ProcessLine("auto tSD21 = "+"deepTagMD_HbbvsQCD"+"21"+options.year+";")
    # ROOT.gInterpreter.ProcessLine("auto tHist21 = "+doubleB_name+"21"+options.year+";")
    correctionColumns21.Add("trigger21","analyzer::TriggerLookup(mreduced21,tSF)")

#### B tag SF
if "btagHbb" in options.doublebtagger:
    if "ttbar" in setname:
        correctionColumns.Add("ttbarNorm","0.72*(300<"+pt0+" && "+pt0+"<600)+0.65*(600<"+pt0+" && "+pt0+"<800)+0.52*(800<"+pt0+")")
        correctionColumns.Add("ttbarNormUp","0.77*(300<"+pt0+" && "+pt0+"<600)+0.71*(600<"+pt0+" && "+pt0+"<800)+0.59*(800<"+pt0+")")
        correctionColumns.Add("ttbarNormDown","0.67*(300<"+pt0+" && "+pt0+"<600)+0.59*(600<"+pt0+" && "+pt0+"<800)+0.45*(800<"+pt0+")")
    if options.year == '16':
        correctionColumns.Add("dbSFnomloose","1.03*("+pt0+"<350)+1.03*("+pt0+">350)")
        correctionColumns.Add("dbSFuploose","1.09*("+pt0+"<350)+1.09*("+pt0+">350)")
        correctionColumns.Add("dbSFdownloose","0.90*("+pt0+"<350)+0.90*("+pt0+">350)") 
        correctionColumns.Add("dbSFnomtight","0.95*("+pt0+"<350)+0.95*("+pt0+">350)")
        correctionColumns.Add("dbSFuptight","1.02*("+pt0+"<350)+1.02*("+pt0+">350)")
        correctionColumns.Add("dbSFdowntight","0.82*("+pt0+"<350)+0.82*("+pt0+">350)") 
    if options.year == '17':
        correctionColumns.Add("dbSFnomloose","0.96*("+pt0+"<350)+0.95*("+pt0+">350)")
        correctionColumns.Add("dbSFuploose","0.99*("+pt0+"<350)+1.01*("+pt0+">350)")
        correctionColumns.Add("dbSFdownloose","0.93*("+pt0+"<350)+0.91*("+pt0+">350)") 
        correctionColumns.Add("dbSFnomtight","0.85*("+pt0+"<350)+0.8*("+pt0+">350)")
        correctionColumns.Add("dbSFuptight","0.89*("+pt0+"<350)+0.87*("+pt0+">350)")
        correctionColumns.Add("dbSFdowntight","0.81*("+pt0+"<350)+0.76*("+pt0+">350)") 
    if options.year == '18':
        correctionColumns.Add("dbSFnomloose","0.93*("+pt0+"<350)+0.98*("+pt0+">350)")
        correctionColumns.Add("dbSFuploose","0.97*("+pt0+"<350)+1.03*("+pt0+">350)")
        correctionColumns.Add("dbSFdownloose","0.89*("+pt0+"<350)+0.94*("+pt0+">350)") 
        correctionColumns.Add("dbSFnomtight","0.89*("+pt0+"<350)+0.84*("+pt0+">350)")
        correctionColumns.Add("dbSFuptight","0.97*("+pt0+"<350)+0.89*("+pt0+">350)")
        correctionColumns.Add("dbSFdowntight","0.85*("+pt0+"<350)+0.79*("+pt0+">350)")
elif "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
    if "ttbar" in setname:
        correctionColumns.Add("dbSFnomloose","1.039*(300<"+pt0+" && "+pt0+"<600)+1.035*(600<"+pt0+" && "+pt0+"<800)+1.301*(800<"+pt0+")")
        correctionColumns.Add("dbSFuploose","1.1*(300<"+pt0+" && "+pt0+"<600)+1.14*(600<"+pt0+" && "+pt0+"<800)+1.626*(800<"+pt0+")")
        correctionColumns.Add("dbSFdownloose","0.981*(300<"+pt0+" && "+pt0+"<600)+0.937*(600<"+pt0+" && "+pt0+"<800)+1.035*(800<"+pt0+")")

        correctionColumns.Add("dbSFnomtight","1.039*(300<"+pt0+" && "+pt0+"<600)+1.035*(600<"+pt0+" && "+pt0+"<800)+1.301*(800<"+pt0+")")
        correctionColumns.Add("dbSFuptight","1.1*(300<"+pt0+" && "+pt0+"<600)+1.14*(600<"+pt0+" && "+pt0+"<800)+1.626*(800<"+pt0+")")
        correctionColumns.Add("dbSFdowntight","0.981*(300<"+pt0+" && "+pt0+"<600)+0.937*(600<"+pt0+" && "+pt0+"<800)+1.035*(800<"+pt0+")")

        correctionColumns.Add("ttbarNorm","0.72*(300<"+pt0+" && "+pt0+"<600)+0.65*(600<"+pt0+" && "+pt0+"<800)+0.52*(800<"+pt0+")")
        correctionColumns.Add("ttbarNormUp","0.77*(300<"+pt0+" && "+pt0+"<600)+0.71*(600<"+pt0+" && "+pt0+"<800)+0.59*(800<"+pt0+")")
        correctionColumns.Add("ttbarNormDown","0.67*(300<"+pt0+" && "+pt0+"<600)+0.59*(600<"+pt0+" && "+pt0+"<800)+0.45*(800<"+pt0+")")
    else:
        if options.year == '16':
            correctionColumns.Add("dbSFnomloose","1*(300<"+pt0+" && "+pt0+"<400)+0.97*(400<"+pt0+" && "+pt0+"<500)+0.91*(500<"+pt0+" && "+pt0+"<600)+0.95*("+pt0+">600)")
            correctionColumns.Add("dbSFuploose","1.06*(300<"+pt0+" && "+pt0+"<400)+1*(400<"+pt0+" && "+pt0+"<500)+0.96*(500<"+pt0+" && "+pt0+"<600)+0.99*("+pt0+">600)")
            correctionColumns.Add("dbSFdownloose","0.94*(300<"+pt0+" && "+pt0+"<400)+0.94*(400<"+pt0+" && "+pt0+"<500)+0.86*(500<"+pt0+" && "+pt0+"<600)+0.91*("+pt0+">600)")
            correctionColumns.Add("dbSFnomtight","1*(300<"+pt0+" && "+pt0+"<400)+0.97*(400<"+pt0+" && "+pt0+"<500)+0.91*(500<"+pt0+" && "+pt0+"<600)+0.95*("+pt0+">600)")
            correctionColumns.Add("dbSFuptight","1.06*(300<"+pt0+" && "+pt0+"<400)+1*(400<"+pt0+" && "+pt0+"<500)+0.96*(500<"+pt0+" && "+pt0+"<600)+0.99*("+pt0+">600)")
            correctionColumns.Add("dbSFdowntight","0.94*(300<"+pt0+" && "+pt0+"<400)+0.94*(400<"+pt0+" && "+pt0+"<500)+0.86*(500<"+pt0+" && "+pt0+"<600)+0.91*("+pt0+">600)")
        if options.year == '17':
            correctionColumns.Add("dbSFnomloose","1.05*(300<"+pt0+" && "+pt0+"<400)+1.01*(400<"+pt0+" && "+pt0+"<500)+1.06*(500<"+pt0+" && "+pt0+"<600)+1.13*("+pt0+">600)")
            correctionColumns.Add("dbSFuploose","1.07*(300<"+pt0+" && "+pt0+"<400)+1.04*(400<"+pt0+" && "+pt0+"<500)+1.09*(500<"+pt0+" && "+pt0+"<600)+1.18*("+pt0+">600)")
            correctionColumns.Add("dbSFdownloose","1.03*(300<"+pt0+" && "+pt0+"<400)+0.98*(400<"+pt0+" && "+pt0+"<500)+1.03*(500<"+pt0+" && "+pt0+"<600)+1.08*("+pt0+">600)")
            correctionColumns.Add("dbSFnomtight","1.05*(300<"+pt0+" && "+pt0+"<400)+1.01*(400<"+pt0+" && "+pt0+"<500)+1.06*(500<"+pt0+" && "+pt0+"<600)+1.13*("+pt0+">600)")
            correctionColumns.Add("dbSFuptight","1.07*(300<"+pt0+" && "+pt0+"<400)+1.04*(400<"+pt0+" && "+pt0+"<500)+1.09*(500<"+pt0+" && "+pt0+"<600)+1.18*("+pt0+">600)")
            correctionColumns.Add("dbSFdowntight","1.03*(300<"+pt0+" && "+pt0+"<400)+0.98*(400<"+pt0+" && "+pt0+"<500)+1.03*(500<"+pt0+" && "+pt0+"<600)+1.08*("+pt0+">600)")
        if options.year == '18':
            correctionColumns.Add("dbSFnomloose","1.35*(300<"+pt0+" && "+pt0+"<400)+1.22*(400<"+pt0+" && "+pt0+"<500)+1.31*(500<"+pt0+" && "+pt0+"<600)+1.30*("+pt0+">600)")
            correctionColumns.Add("dbSFuploose","1.38*(300<"+pt0+" && "+pt0+"<400)+1.25*(400<"+pt0+" && "+pt0+"<500)+1.35*(500<"+pt0+" && "+pt0+"<600)+1.34*("+pt0+">600)")
            correctionColumns.Add("dbSFdownloose","1.32*(300<"+pt0+" && "+pt0+"<400)+1.19*(400<"+pt0+" && "+pt0+"<500)+1.27*(500<"+pt0+" && "+pt0+"<600)+1.26*("+pt0+">600)")
            correctionColumns.Add("dbSFnomtight","1.35*(300<"+pt0+" && "+pt0+"<400)+1.22*(400<"+pt0+" && "+pt0+"<500)+1.31*(500<"+pt0+" && "+pt0+"<600)+1.30*("+pt0+">600)")
            correctionColumns.Add("dbSFuptight","1.38*(300<"+pt0+" && "+pt0+"<400)+1.25*(400<"+pt0+" && "+pt0+"<500)+1.35*(500<"+pt0+" && "+pt0+"<600)+1.34*("+pt0+">600)")
            correctionColumns.Add("dbSFdowntight","1.32*(300<"+pt0+" && "+pt0+"<400)+1.19*(400<"+pt0+" && "+pt0+"<500)+1.27*(500<"+pt0+" && "+pt0+"<600)+1.26*("+pt0+">600)")
else:
    correctionColumns.Add("dbSFnomloose","1*("+pt0+"<350)+1*("+pt0+">350)")
    correctionColumns.Add("dbSFuploose","1*("+pt0+"<350)+1*("+pt0+">350)")
    correctionColumns.Add("dbSFdownloose","1*("+pt0+"<350)+1*("+pt0+">350)") 
    correctionColumns.Add("dbSFnomtight","1*("+pt0+"<350)+1*("+pt0+">350)")
    correctionColumns.Add("dbSFuptight","1*("+pt0+"<350)+1*("+pt0+">350)")
    correctionColumns.Add("dbSFdowntight","1*("+pt0+"<350)+1*("+pt0+">350)")

if not a.isData:
    if 'ttbar' in setname:
        correctionColumns.Add("topptvector","analyzer::PTWLookup(nGenPart, GenPart_pdgId, GenPart_statusFlags, GenPart_pt, GenPart_eta, GenPart_phi, GenPart_mass, lead_vect, sublead_vect)")
        correctionColumns.Add("topptvectorcheck","topptvector[0]")

        if "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
            topstringnom = "*ttbarNorm*topptvector[0]"
            topstringalphaup = "*ttbarNorm*topptvector[1]"
            topstringalphadown = "*ttbarNorm*topptvector[2]"
            topstringbetaup = "*ttbarNorm*topptvector[3]"
            topstringbetadown = "*ttbarNorm*topptvector[4]"
        else:
            topstringnom = "*topptvector[0]"
            topstringalphaup = "*topptvector[1]"
            topstringalphadown = "*topptvector[2]"
            topstringbetaup = "*topptvector[3]"
            topstringbetadown = "*topptvector[4]"


        correctionColumns11.Add("topptweight_tight_Alphaup","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight"+topstringalphaup+"")
        correctionColumns11.Add("topptweight_tight_Alphadown","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight"+topstringalphadown+"")
        correctionColumns11.Add("topptweight_loose_Alphaup","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringalphaup+"")
        correctionColumns11.Add("topptweight_loose_Alphadown","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringalphadown+"")

        correctionColumns11.Add("topptweight_tight_AlphaupFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight"+topstringalphaup+"")
        correctionColumns11.Add("topptweight_tight_AlphadownFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight"+topstringalphadown+"")
        correctionColumns11.Add("topptweight_loose_AlphaupFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight"+topstringalphaup+"")
        correctionColumns11.Add("topptweight_loose_AlphadownFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight"+topstringalphadown+"")

        correctionColumns11.Add("topptweight_tight_AlphaupFailHalfSF","(dbSFnomtight)*triggerTight[0]*puWeight"+topstringalphaup+"")
        correctionColumns11.Add("topptweight_tight_AlphadownFailHalfSF","(dbSFnomtight)*triggerTight[0]*puWeight"+topstringalphadown+"")
        correctionColumns11.Add("topptweight_loose_AlphaupFailHalfSF","(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringalphaup+"")
        correctionColumns11.Add("topptweight_loose_AlphadownFailHalfSF","(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringalphadown+"")

        correctionColumns11.Add("topptweight_tight_Betaup","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight"+topstringbetaup+"")
        correctionColumns11.Add("topptweight_tight_Betadown","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight"+topstringbetadown+"")
        correctionColumns11.Add("topptweight_loose_Betaup","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringbetaup+"")
        correctionColumns11.Add("topptweight_loose_Betadown","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringbetadown+"")

        correctionColumns11.Add("topptweight_tight_BetaupFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight"+topstringbetaup+"")
        correctionColumns11.Add("topptweight_tight_BetadownFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight"+topstringbetadown+"")
        correctionColumns11.Add("topptweight_loose_BetaupFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight"+topstringbetaup+"")
        correctionColumns11.Add("topptweight_loose_BetadownFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight"+topstringbetadown+"")

        correctionColumns11.Add("topptweight_tight_BetaupFailHalfSF","(dbSFnomtight)*triggerTight[0]*puWeight"+topstringbetaup+"")
        correctionColumns11.Add("topptweight_tight_BetadownFailHalfSF","(dbSFnomtight)*triggerTight[0]*puWeight"+topstringbetadown+"")
        correctionColumns11.Add("topptweight_loose_BetaupFailHalfSF","(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringbetaup+"")
        correctionColumns11.Add("topptweight_loose_BetadownFailHalfSF","(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringbetadown+"")

        correctionColumns21.Add("topptweight_Alphaup","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringalphaup+"")
        correctionColumns21.Add("topptweight_Alphadown","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringalphadown+"")

        correctionColumns21.Add("topptweight_AlphaupFailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringalphaup+"")
        correctionColumns21.Add("topptweight_AlphadownFailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringalphadown+"")

        correctionColumns21.Add("topptweight_AlphaupFailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringalphaup+"")
        correctionColumns21.Add("topptweight_AlphadownFailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringalphadown+"")

        correctionColumns21.Add("topptweight_Betaup","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringbetaup+"")
        correctionColumns21.Add("topptweight_Betadown","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringbetadown+"")

        correctionColumns21.Add("topptweight_BetaupFailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringbetaup+"")
        correctionColumns21.Add("topptweight_BetadownFailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringbetadown+"")

        correctionColumns21.Add("topptweight_BetaupFailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringbetaup+"")
        correctionColumns21.Add("topptweight_BetadownFailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringbetadown+"")


        ### ttbar normaliation weights
        if "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
            correctionColumns11.Add("weight_tight_NormUp","ttbarNormUp*dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_tight_NormDown","ttbarNormDown*dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_loose_NormUp","ttbarNormUp*dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_loose_NormDown","ttbarNormDown*dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight*topptvector[0]")

            correctionColumns11.Add("weight_tight_NormUpFailFullSF","ttbarNormUp*dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_tight_NormDownFailFullSF","ttbarNormDown*dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_loose_NormUpFailFullSF","ttbarNormUp*dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_loose_NormDownFailFullSF","ttbarNormDown*dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight*topptvector[0]")

            correctionColumns11.Add("weight_tight_NormUpFailHalfSF","ttbarNormUp*(dbSFnomtight)*triggerTight[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_tight_NormDownFailHalfSF","ttbarNormDown*(dbSFnomtight)*triggerTight[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_loose_NormUpFailHalfSF","ttbarNormUp*(dbSFnomloose)*triggerLoose[0]*puWeight*topptvector[0]")
            correctionColumns11.Add("weight_loose_NormDownFailHalfSF","ttbarNormDown*(dbSFnomloose)*triggerLoose[0]*puWeight*topptvector[0]")

            correctionColumns21.Add("weight_NormUp","ttbarNormUp*dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]*topptvector[0]")
            correctionColumns21.Add("weight_NormDown","ttbarNormDown*dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]*topptvector[0]")

            correctionColumns21.Add("weight_NormUpFailFullSF","ttbarNormUp*(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]*topptvector[0]")
            correctionColumns21.Add("weight_NormDownFailFullSF","ttbarNormDown*(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]*topptvector[0]")

            correctionColumns21.Add("weight_NormUpFailHalfSF","ttbarNormUp*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]*topptvector[0]")
            correctionColumns21.Add("weight_NormDownFailHalfSF","ttbarNormDown*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]*topptvector[0]")

    else:
        topstringnom = ""

    if 'QCD' in setname:
        correctionColumns.Add("finalweightTight","dbSFnomtight*(dbSFnomtight)*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightLoose","dbSFnomloose*(dbSFnomloose)*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightTightFailFullSF","dbSFnomtight*(1-dbSFnomtight)*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightLooseFailFullSF","dbSFnomloose*(1-dbSFnomloose)*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightTightFailHalfSF","dbSFnomtight*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightLooseFailHalfSF","dbSFnomloose*puWeight"+topstringnom+"")

        correctionColumns21.Add("finalweight21","dbSFnomloose*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
        correctionColumns21.Add("finalweight21FailFullSF","(1-dbSFnomloose)*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
        correctionColumns21.Add("finalweight21FailHalfSF","puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
    else:
        # correctionColumns.Add("finalweightTight","dbSFnomtight*(dbSFnomtight)*puWeight"+topstringnom+"")
        # correctionColumns.Add("finalweightLoose","dbSFnomloose*(dbSFnomloose)*puWeight"+topstringnom+"")
        # correctionColumns.Add("finalweightTightFailFullSF","dbSFnomtight*(1-dbSFnomtight)*puWeight"+topstringnom+"")
        # correctionColumns.Add("finalweightLooseFailFullSF","dbSFnomloose*(1-dbSFnomloose)*puWeight"+topstringnom+"")
        # correctionColumns.Add("finalweightTightFailHalfSF","dbSFnomtight*puWeight"+topstringnom+"")
        # correctionColumns.Add("finalweightLooseFailHalfSF","dbSFnomloose*puWeight"+topstringnom+"")

        # correctionColumns21.Add("finalweight21","dbSFnomloose*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
        # correctionColumns21.Add("finalweight21FailFullSF","(1-dbSFnomloose)*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
        # correctionColumns21.Add("finalweight21FailHalfSF","puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")

        correctionColumns.Add("finalweightTight","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightLoose","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightTightFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightLooseFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightTightFailHalfSF","dbSFnomtight*triggerTight[0]*puWeight"+topstringnom+"")
        correctionColumns.Add("finalweightLooseFailHalfSF","dbSFnomloose*triggerLoose[0]*puWeight"+topstringnom+"")

        correctionColumns21.Add("finalweight21","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
        correctionColumns21.Add("finalweight21FailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
        correctionColumns21.Add("finalweight21FailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")


### Here I make the weights for the shape based uncertainties. This cannot be done inline with the Histo1D calls so it is done here.

if not a.isData:

    correctionColumns.Add("Pdfweight",'analyzer::PDFweight(LHEPdfWeight)')
    correctionColumns11.Add("Pdfweight_tight_up",'dbSFnomtight*(dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_tight_down",'dbSFnomtight*(dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_up",'dbSFnomloose*(dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_down",'dbSFnomloose*(dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("Pdfweight_tight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_tight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("Pdfweight_tight_upFailHalfSF",'(dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_tight_downFailHalfSF",'(dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_upFailHalfSF",'(dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_downFailHalfSF",'(dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("pileupweight_tight_up",'dbSFnomtight*(dbSFnomtight)*puWeightUp*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_tight_down",'dbSFnomtight*(dbSFnomtight)*puWeightDown*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_up",'dbSFnomloose*(dbSFnomloose)*puWeightUp*triggerLoose[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_down",'dbSFnomloose*(dbSFnomloose)*puWeightDown*triggerLoose[0]'+topstringnom+'')

    correctionColumns11.Add("pileupweight_tight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*puWeightUp*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_tight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*puWeightDown*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*puWeightUp*triggerLoose[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*puWeightDown*triggerLoose[0]'+topstringnom+'')

    correctionColumns11.Add("pileupweight_tight_upFailHalfSF",'(dbSFnomtight)*puWeightUp*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_tight_downFailHalfSF",'(dbSFnomtight)*puWeightDown*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_upFailHalfSF",'(dbSFnomloose)*puWeightUp*triggerLoose[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_downFailHalfSF",'(dbSFnomloose)*puWeightDown*triggerLoose[0]'+topstringnom+'')

    correctionColumns11.Add("triggertight_up",'dbSFnomtight*(dbSFnomtight)*triggerTight[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggertight_down",'dbSFnomtight*(dbSFnomtight)*triggerTight[2]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_up",'dbSFnomloose*(dbSFnomloose)*triggerLoose[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_down",'dbSFnomloose*(dbSFnomloose)*triggerLoose[2]*puWeight'+topstringnom+'')

    correctionColumns11.Add("triggertight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*triggerTight[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggertight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*triggerTight[2]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*triggerLoose[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*triggerLoose[2]*puWeight'+topstringnom+'')

    correctionColumns11.Add("triggertight_upFailHalfSF",'(dbSFnomtight)*triggerTight[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggertight_downFailHalfSF",'(dbSFnomtight)*triggerTight[2]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_upFailHalfSF",'(dbSFnomloose)*triggerLoose[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_downFailHalfSF",'(dbSFnomloose)*triggerLoose[2]*puWeight'+topstringnom+'')

    correctionColumns11.Add("dbsftight_up",'dbSFuptight*(dbSFuptight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsftight_down",'dbSFdowntight*(dbSFdowntight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_up",'dbSFuploose*(dbSFuploose)*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_down",'dbSFdownloose*(dbSFdownloose)*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("dbsftight_upFailFullSF",'dbSFuptight*(1-dbSFuptight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsftight_downFailFullSF",'dbSFdowntight*(1-dbSFdowntight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_upFailFullSF",'dbSFuploose*(1-dbSFuploose)*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_downFailFullSF",'dbSFdownloose*(1-dbSFdownloose)*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("dbsftight_upFailHalfSF",'(dbSFuptight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsftight_downFailHalfSF",'(dbSFdowntight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_upFailHalfSF",'(dbSFuploose)*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_downFailHalfSF",'(dbSFdownloose)*triggerLoose[0]*puWeight'+topstringnom+'')

#### Now do 2+1 weights

    correctionColumns21.Add("pileupweight_up",'dbSFnomloose*puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("pileupweight_down",'dbSFnomloose*puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("pileupweight_upFailFullSF",'(1-dbSFnomloose)*puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("pileupweight_downFailFullSF",'(1-dbSFnomloose)*puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("pileupweight_upFailHalfSF",'puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("pileupweight_downFailHalfSF",'puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("Pdfweight_up",'dbSFnomloose*Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("Pdfweight_down",'dbSFnomloose*Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("Pdfweight_upFailFullSF",'(1-dbSFnomloose)*Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("Pdfweight_downFailFullSF",'(1-dbSFnomloose)*Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("Pdfweight_upFailHalfSF",'Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("Pdfweight_downFailHalfSF",'Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("btagsfweight_up",'dbSFnomloose*puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]'+topstringnom+'')
    correctionColumns21.Add("btagsfweight_down",'dbSFnomloose*puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]'+topstringnom+'')

    correctionColumns21.Add("btagsfweight_upFailFullSF",'(1-dbSFnomloose)*puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]'+topstringnom+'')
    correctionColumns21.Add("btagsfweight_downFailFullSF",'(1-dbSFnomloose)*puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]'+topstringnom+'')

    correctionColumns21.Add("btagsfweight_upFailHalfSF",'puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]'+topstringnom+'')
    correctionColumns21.Add("btagsfweight_downFailHalfSF",'puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]'+topstringnom+'')

    correctionColumns21.Add("trigger_up",'dbSFnomloose*trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("trigger_down",'dbSFnomloose*trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("trigger_upFailFullSF",'(1-dbSFnomloose)*trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("trigger_downFailFullSF",'(1-dbSFnomloose)*trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("trigger_upFailHalfSF",'trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("trigger_downFailHalfSF",'trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("dbsfup",'dbSFuploose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("dbsfdown",'dbSFdownloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("dbsfupFailFullSF",'(1-dbSFuploose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("dbsfdownFailFullSF",'(1-dbSFdownloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("dbsfupFailHalfSF",'trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("dbsfdownFailHalfSF",'trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')


#### 1+1 algorithm
DoubleB_lead_tight = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tagTight'][0])+" && FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tagTight'][1])+""
DoubleB_lead_loose = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tagLoose'][0])+" && FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tagLoose'][1])+""
DoubleB_sublead_tight = "FatJet_"+doubleB_name+"[1] > "+str(cutsDict[doubleB_short+'tagTight'][0])+" && FatJet_"+doubleB_name+"[1] < "+str(cutsDict[doubleB_short+'tagTight'][1])+""
DoubleB_sublead_loose = "FatJet_"+doubleB_name+"[1] > "+str(cutsDict[doubleB_short+'tagLoose'][0])+" && FatJet_"+doubleB_name+"[1] < "+str(cutsDict[doubleB_short+'tagLoose'][1])+""

srttString = "("+DoubleB_lead_tight+" && "+DoubleB_sublead_tight+") == 1"
srllString = "(("+DoubleB_lead_loose+" && "+DoubleB_sublead_loose+") && !("+srttString+")) == 1"
atttString = "(!("+DoubleB_lead_loose+") && ("+DoubleB_sublead_tight+")) == 1"
atllString = "(!("+DoubleB_lead_loose+") && ("+DoubleB_sublead_loose+") && !("+DoubleB_sublead_tight+")) == 1"


### Control region algorithm
invertedCR = "("+DoubleB_lead_loose+" && !("+DoubleB_sublead_loose+") && !("+DoubleB_sublead_tight+")) == 1"
invertedCRFail ="(!("+DoubleB_lead_loose+") && !("+DoubleB_sublead_loose+") && !("+DoubleB_sublead_tight+")) == 1"


#### 2+1 Algorithm
pass21String = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tag'][0])+" && "+"FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tag'][1])+""
fail21String = "FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tag'][0])+""

run21String = "((!("+srttString+") && (!("+atttString+")) && (!("+srllString+")) && (!("+atllString+"))) == 1)"
# run21String = "((!("+srttString+") && (!("+atttString+")) && (!("+srllString+"))) == 1)"

cand21String = "((!(nFatJet > 1) || !(pt0 > 300 && pt1 > 300) || !(abs("+eta0+") < 2.4 && abs("+eta1+") < 2.4) || !(abs("+eta0+" - "+eta1+") < 1.3) || !(mreduced > 750.) || !((110 < mh1) && (mh1 < 140))) == 1)"
# cand21String = "((!(nFatJet > 1) || !(pt0 > 300 && pt1 > 300) || !(abs("+eta0+") < 2.4 && abs("+eta1+") < 2.4) || !(abs("+eta0+" - "+eta1+") < 1.3) || !(mreduced > 750.)) == 1)"

### Make selection columns
selectionColumns = VarGroup("selectionColumns")
selectionColumns.Add("SRTT",srttString)
selectionColumns.Add("SRLL",srllString)
selectionColumns.Add("ATTT",atttString)
selectionColumns.Add("ATLL",atllString)
selectionColumns.Add("CR",invertedCR)
selectionColumns.Add("CRFail",invertedCRFail)

selectionColumns21 = VarGroup("selectionColumns21")
selectionColumns21.Add("Pass21",pass21String)
selectionColumns21.Add("Fail21",fail21String)

#### Make cutgroups

slim_skim = CutGroup('slim_skim')
slim_skim.Add("triggers","triggers == 1")
# if a.isData: slim_skim.Add("triggers","triggers == 1")
slim_skim.Add("nFatJets1","nFatJet > 0")

filters = CutGroup('filters')
filters.Add("Flag_goodVertices","Flag_goodVertices == 1")
filters.Add("Flag_globalSuperTightHalo2016Filter","Flag_globalSuperTightHalo2016Filter == 1")
filters.Add("Flag_HBHENoiseFilter","Flag_HBHENoiseFilter == 1")
filters.Add("Flag_HBHENoiseIsoFilter","Flag_HBHENoiseIsoFilter == 1")
filters.Add("Flag_EcalDeadCellTriggerPrimitiveFilter","Flag_EcalDeadCellTriggerPrimitiveFilter == 1")
filters.Add("Flag_BadPFMuonFilter","Flag_BadPFMuonFilter == 1")

#### 1+1 cut groups

preselection11 = CutGroup('preselection11')
preselection11.Add("nFatJets2","nFatJet > 1")
preselection11.Add("pt0",""+pt0+" > 300")
preselection11.Add("pt1",""+pt1+" > 300")
preselection11.Add("eta0","abs("+eta0+") < 2.4")
preselection11.Add("eta1","abs("+eta1+") < 2.4")
preselection11.Add("jetID","((FatJet_jetId[0] & 2) == 2) && ((FatJet_jetId[1] & 2) == 2)")
# preselection11.Add("PV","PV_npvsGood > 0")
preselection11.Add("deltaEta","abs("+eta0+" - "+eta1+") < 1.3")
# preselection11.Add("tau21","(FatJet_tau2[0]/FatJet_tau1[0] < 0.55) && (FatJet_tau2[1]/FatJet_tau1[1] < 0.55)")
# Cut on new column
preselection12 = CutGroup('preselection12')
preselection12.Add("msoftdrop_1","(110 < mh1) && (mh1 < 140)")
preselection12.Add("cut_mreduced","mreduced > 750.")

#### 2+1 cut groups

preselection21 = CutGroup('preselection21')
preselection21.Add("candidate21","("+cand21String+") || ("+run21String+")")
preselection21.Add("nFatJets21","nFatJet > 0")
preselection21.Add("nJets21","nJet >= 2")

preselection22 = CutGroup('preselection22')
preselection22.Add("bb_pairs_check","(Hemispherized[0] != 0) && (Hemispherized[1] != 0)")
preselection22.Add("eta","abs(lead_vect.Eta()) < 2.4")
preselection22.Add("b_eta","abs(b_lead_vect.Eta()) < 2.0 && abs(b_sublead_vect.Eta()) < 2.0")
preselection22.Add("pt","(pt0 > 300)")
preselection22.Add("b_pt","b_lead_vect.Pt() > 30 && b_sublead_vect.Pt() > 30")
preselection22.Add("jetID","((FatJet_jetId[0] & 2) == 2)")
if options.year == '16': 
    preselection22.Add("DeepJet","(0.3093 < Jet_btagDeepFlavB[Hemispherized[0]] && Jet_btagDeepFlavB[Hemispherized[0]] < 1) && (0.3093 < Jet_btagDeepFlavB[Hemispherized[1]] && Jet_btagDeepFlavB[Hemispherized[1]] < 1)")
if options.year == '17': 
    preselection22.Add("DeepJet","(0.3033  < Jet_btagDeepFlavB[Hemispherized[0]] && Jet_btagDeepFlavB[Hemispherized[0]] < 1) && (0.3033  < Jet_btagDeepFlavB[Hemispherized[1]] && Jet_btagDeepFlavB[Hemispherized[1]] < 1)")
if options.year == '18': 
    preselection22.Add("DeepJet","(0.2770 < Jet_btagDeepFlavB[Hemispherized[0]] && Jet_btagDeepFlavB[Hemispherized[0]] < 1) && (0.2770 < Jet_btagDeepFlavB[Hemispherized[1]] && Jet_btagDeepFlavB[Hemispherized[1]] < 1)")
# preselection22.Add("DeepCSV","(0.6324 < Jet_btagDeepB[Hemispherized[0]] && Jet_btagDeepB[Hemispherized[0]] < 1) && (0.6324 < Jet_btagDeepB[Hemispherized[1]] && Jet_btagDeepB[Hemispherized[1]] < 1)")
preselection22.Add("deltaEta21","abs(lead_vect.Eta() - (b_lead_vect+b_sublead_vect).Eta()) < 1.3")
preselection22.Add("mbbCut","90.0 < mbb && mbb < 140.0")
preselection22.Add("cut_mreduced21","mreduced21 > 750.")
# preselection22.Add("mbbCut","105.0 < mbb && mbb < 135.0")
# preselection22.Add("msoftdrop_1","(110 < mh1) && (mh1 < 140)")

preselection23 = CutGroup('preselection23')
# preselection23.Add("topMass","topMass > 200.0")
# preselection23.Add("topMass","topMass > 220.0")
# preselection23.Add("topDeltaR","topDeltaR > 1.0")

plotsColumn = VarGroup("plotsColumn")
plotsColumn.Add("eta0","lead_vect.Eta()")
plotsColumn.Add("eta1","sublead_vect.Eta()")
plotsColumn.Add("deltaEta","abs(eta0 - eta1)")
plotsColumn.Add("FJtau21","FatJet_tau2[0]/FatJet_tau1[0]")
plotsColumn.Add("tagger","FatJet_"+doubleB_name+"[0]")


kinematicCuts = CutGroup("kinematicCuts")
kinematicCuts.Add("pt0",""+pt0+" > 300")
kinematicCuts.Add("eta0","abs("+eta0+") < 2.4")
kinematicCuts.Add("bb_pairs_check","(Hemispherized[0] != 0) && (Hemispherized[1] != 0)")
kinematicCuts.Add("b_eta","abs(Jet_eta[Hemispherized[0]]) < 2.4 && abs(Jet_eta[Hemispherized[1]]) < 2.4")
kinematicCuts.Add("DeepCSV","(0.2219 < Jet_btagDeepB[Hemispherized[0]] && Jet_btagDeepB[Hemispherized[0]] < 1) && (0.2219 < Jet_btagDeepB[Hemispherized[1]] && Jet_btagDeepB[Hemispherized[1]] < 1)")
kinematicCuts.Add("candidate21","("+cand21String+") || ("+run21String+")")
kinematicCuts.Add("cut_mreduced21","mreduced21 > 750.")

# Apply all groups in list order to the base RDF loaded in during analyzer() initialization
slimandskim = a.Apply([triggerGroup,slim_skim,filters])
setup = slimandskim.Apply([newcolumns,bbColumn,mbbColumn,mred21Column,selectionColumns,correctionColumns,correctionColumns11,selectionColumns21,correctionColumns21,plotsColumn])
# if not a.isData:
#     nminus1_11 = a.Apply([triggerGroup,newcolumns,selectionColumns,correctionColumns,correctionColumns11,plotsColumn])
#     nminus1_21 = a.Apply([triggerGroup,newcolumns,bbColumn,mbbColumn,mred21Column,selectionColumns21,correctionColumns,correctionColumns21,plotsColumn])
kinematicDistributions = setup.Apply([kinematicCuts])
preselected = setup.Apply([preselection11,preselection12])
cutTest21 = setup.Apply([preselection21,preselection22]).Cut("Pass21","Pass21==1")
preselected21 = setup.Apply([preselection21,preselection22,preselection23])

# Since four analysis regions are covered with relatively complicated cuts to define them, a manual forking is simplest though a Discriminate function does exist for when you need to keep pass and fail of a selection
SRTT = preselected.Cut("SRTT","SRTT==1")
ATTT = preselected.Cut("ATTT","ATTT==1")
SRLL = preselected.Cut("SRLL","SRLL==1")
ATLL = preselected.Cut("ATLL","ATLL==1")
SRCR = preselected.Cut("CR","CR==1")
ATCR = preselected.Cut("CRFail","CRFail==1")

Pass = preselected21.Cut("Pass21","Pass21==1")
Fail = preselected21.Cut("Fail21","Fail21==1")

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()

print("Outfile booked")

# Need to call DataFrame attribute since Histo2D/Histo1D is a method of RDataFrame - this means at any point, you have access to the plain RDataFrame object corresponding to each node!
##### Make histos for kinematic checks
# nom_check_plot = slimandskim.DataFrame.Histo2D(("nom_check_plot","nom_check_plot",50 ,150 ,1500 ,50 ,0 ,400),"FatJet_pt_nom[0]","FatJet_msoftdrop_nom[0]")
# raw_check_plot = slimandskim.DataFrame.Histo2D(("raw_check_plot","raw_check_plot",50 ,150 ,1500 ,50 ,0 ,400),"FatJet_pt_nom[0]","FatJet_msoftdrop_raw[0]")

deltaRCheck = cutTest21.DataFrame.Histo1D(("deltaRCheck","deltaRCheck",50,0,5),"topDeltaR")
trijetMassCheck = cutTest21.DataFrame.Histo1D(("trijetMassCheck","trijetMassCheck",50,100,1000),"topMass")
trijetMassDeltaR = cutTest21.Cut("DeltaR","topDeltaR > 1.0").DataFrame.Histo1D(("trijetMassCheckDeltaR","trijetMassCheckDeltaR",50,100,1000),"topMass")
hmred21 = preselected21.DataFrame.Histo1D(("mred21","mred21",50 ,500 ,2000),"mreduced21")

hpt0TT = kinematicDistributions.DataFrame.Histo1D(("pt0TT","pt0TT",50 ,150 ,1500),"pt0")
hpt1TT = kinematicDistributions.DataFrame.Histo1D(("pt1TT","pt1TT",50 ,150 ,1500),"pt1")
heta0TT = kinematicDistributions.DataFrame.Histo1D(("eta0TT","eta0TT",50 ,-3.5 ,3.5),"eta0")
heta1TT = kinematicDistributions.DataFrame.Histo1D(("eta1TT","eta1TT",50 ,-3.5 ,3.5),"eta1")
hdeltaEtaTT = kinematicDistributions.DataFrame.Histo1D(("deltaEtaTT","deltaEtaTT",50 ,0 ,3.5),"deltaEta")
hmredTT = kinematicDistributions.DataFrame.Histo1D(("mredTT","mredTT",28 ,700 ,3500),"mreduced")
hmsd0TT = kinematicDistributions.DataFrame.Histo1D(("msd0TT","msd0TT",50 ,0 ,400),"mh")
hmsd1TT = kinematicDistributions.DataFrame.Histo1D(("msd1TT","msd1TT",50 ,0 ,400),"mh1")
htau21TT = kinematicDistributions.DataFrame.Histo1D(("tau21TT","tau21TT",50 ,0 ,1),"FJtau21")

hpt0LL = kinematicDistributions.DataFrame.Histo1D(("pt0LL","pt0LL",50 ,150 ,1500),"pt0")
hpt1LL = kinematicDistributions.DataFrame.Histo1D(("pt1LL","pt1LL",50 ,150 ,1500),"pt1")
heta0LL = kinematicDistributions.DataFrame.Histo1D(("eta0LL","eta0LL",50 ,-3.5 ,3.5),"eta0")
heta1LL = kinematicDistributions.DataFrame.Histo1D(("eta1LL","eta1LL",50 ,-3.5 ,3.5),"eta1")
hdeltaEtaLL = kinematicDistributions.DataFrame.Histo1D(("deltaEtaLL","deltaEtaLL",50 ,0 ,3.5),"deltaEta")
hmredLL = kinematicDistributions.DataFrame.Histo1D(("mredLL","mredLL",28 ,700 ,3500),"mreduced")
hmsd0LL = kinematicDistributions.DataFrame.Histo1D(("msd0LL","msd0LL",50 ,0 ,400),"mh")
hmsd1LL = kinematicDistributions.DataFrame.Histo1D(("msd1LL","msd1LL",50 ,0 ,400),"mh1")
htau21LL = kinematicDistributions.DataFrame.Histo1D(("tau21LL","tau21LL",50 ,0 ,1),"FJtau21")

hpt021 = kinematicDistributions.DataFrame.Histo1D(("pt121","pt121",50 ,150 ,1500),"pt1")
bpt021 = kinematicDistributions.DataFrame.Histo1D(("bpt021","bpt021",50 ,150 ,1500),"bpt0")
bpt121 = kinematicDistributions.DataFrame.Histo1D(("bpt121","bpt121",50 ,150 ,1500),"bpt1")
heta021 = kinematicDistributions.DataFrame.Histo1D(("eta021","eta021",50 ,-3.5 ,3.5),"eta1")
beta021 = kinematicDistributions.DataFrame.Histo1D(("beta021","beta021",50 ,-3.5 ,3.5),"beta0")
heta021 = kinematicDistributions.DataFrame.Histo1D(("beta121","beta121",50 ,-3.5 ,3.5),"beta1")
hdeltaEta21 = kinematicDistributions.DataFrame.Histo1D(("deltaEta21","deltaEta21",50 ,0 ,3.5),"deltaEta")
hmred21 = kinematicDistributions.DataFrame.Histo1D(("mred21","mred21",28 ,700 ,3500),"mreduced21")
hmsd021 = kinematicDistributions.DataFrame.Histo1D(("msd021","msd021",50 ,0 ,400),"mh1")
hmbb21 = kinematicDistributions.DataFrame.Histo1D(("mbb21","mbb21",50 ,0 ,400),"mbb")


if not a.isData:
    hSRTT11 = SRTT.DataFrame.Histo2D(("SRTT_11","SRTT_11",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced',"finalweightTight")
    hSFTT11 = SRTT.DataFrame.Histo2D(("SFTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightTightFailFullSF")
    hATTT11 = ATTT.DataFrame.Histo2D(("ATTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightTightFailHalfSF")

    hSRLL11 = SRLL.DataFrame.Histo2D(("SRLL_11","SRLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLoose")
    hSFLL11 = SRLL.DataFrame.Histo2D(("SFLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailFullSF")
    hATLL11 = ATLL.DataFrame.Histo2D(("ATLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailHalfSF")


    hSRTT21 = Pass.DataFrame.Histo2D(("Pass_21","Pass_21",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21',"finalweight21")
    hSFTT21 = Pass.DataFrame.Histo2D(("SFFail_21","ATTT_21",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21","finalweight21FailFullSF")
    hATTT21 = Fail.DataFrame.Histo2D(("Fail_21","ATTT_21",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21","finalweight21FailHalfSF")

else:
    hSRTT11 = SRTT.DataFrame.Histo2D(("SRTT_11","SRTT_11",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced')
    hATTT11 = ATTT.DataFrame.Histo2D(("ATTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hSRLL11 = SRLL.DataFrame.Histo2D(("SRLL_11","SRLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hATLL11 = ATLL.DataFrame.Histo2D(("ATLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")

    hSRTT21 = Pass.DataFrame.Histo2D(("Pass_21","Pass_21",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21')
    hATTT21 = Fail.DataFrame.Histo2D(("Fail_21","Fail_21",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21")

### Implement control region
if not a.isData:
    hSRCR11 = SRCR.DataFrame.Histo2D(("SRCR_11","SRCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLoose")
    hSFCR11 = SRCR.DataFrame.Histo2D(("SFCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailFullSF")
    hATCR11 = ATCR.DataFrame.Histo2D(("ATCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailHalfSF")

else:
    hSRCR11 = SRCR.DataFrame.Histo2D(("SRCR_11","SRCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hATCR11 = ATCR.DataFrame.Histo2D(("ATCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")


# mhbins = list(range(45,235,10))
# print(mhbins)
# mredbins11 = list(range(700,3600,100))
# print(mredbins11)
# mredbins21 = list(range(700,2100,100))
# print(mredbins21)
### Shape based templates

if not a.isData:

##### 1+1 templates
    hSRTT11_pdfUp = SRTT.DataFrame.Histo2D(("SRTT_11_pdfUp","SRTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','Pdfweight_tight_up')
    hATTT11_pdfUp = ATTT.DataFrame.Histo2D(("ATTT_11_pdfUp","ATTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_upFailHalfSF')
    hSFTT11_pdfUp = SRTT.DataFrame.Histo2D(("SFTT_11_pdfUp","ATTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_upFailFullSF')

    hSRLL11_pdfUp = SRLL.DataFrame.Histo2D(("SRLL_11_pdfUp","SRLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_up')
    hATLL11_pdfUp = ATLL.DataFrame.Histo2D(("ATLL_11_pdfUp","ATLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailHalfSF')
    hSFLL11_pdfUp = SRLL.DataFrame.Histo2D(("SFLL_11_pdfUp","ATLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailFullSF')

    hSRTT11_pdfDown = SRTT.DataFrame.Histo2D(("SRTT_11_pdfDown","SRTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','Pdfweight_tight_down')
    hATTT11_pdfDown = ATTT.DataFrame.Histo2D(("ATTT_11_pdfDown","ATTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_downFailHalfSF')
    hSFTT11_pdfDown = SRTT.DataFrame.Histo2D(("SFTT_11_pdfDown","ATTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_downFailFullSF')

    hSRLL11_pdfDown = SRLL.DataFrame.Histo2D(("SRLL_11_pdfDown","SRLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_down')
    hATLL11_pdfDown = ATLL.DataFrame.Histo2D(("ATLL_11_pdfDown","ATLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailHalfSF')
    hSFLL11_pdfDown = SRLL.DataFrame.Histo2D(("SFLL_11_pdfDown","ATLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailFullSF')

    hSRTT11_pileupUp = SRTT.DataFrame.Histo2D(("SRTT_11_pileupUp","SRTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','pileupweight_tight_up')
    hATTT11_pileupUp = ATTT.DataFrame.Histo2D(("ATTT_11_pileupUp","ATTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_upFailHalfSF')
    hSFTT11_pileupUp = SRTT.DataFrame.Histo2D(("SFTT_11_pileupUp","ATTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_upFailFullSF')

    hSRLL11_pileupUp = SRLL.DataFrame.Histo2D(("SRLL_11_pileupUp","SRLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_up')
    hATLL11_pileupUp = ATLL.DataFrame.Histo2D(("ATLL_11_pileupUp","ATLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailHalfSF')
    hSFLL11_pileupUp = SRLL.DataFrame.Histo2D(("SFLL_11_pileupUp","ATLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailFullSF')

    hSRTT11_pileupDown = SRTT.DataFrame.Histo2D(("SRTT_11_pileupDown","SRTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','pileupweight_tight_down')
    hATTT11_pileupDown = ATTT.DataFrame.Histo2D(("ATTT_11_pileupDown","ATTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_downFailHalfSF')
    hSFTT11_pileupDown = SRTT.DataFrame.Histo2D(("SFTT_11_pileupDown","ATTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_downFailFullSF')

    hSRLL11_pileupDown = SRLL.DataFrame.Histo2D(("SRLL_11_pileupDown","SRLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_down')
    hATLL11_pileupDown = ATLL.DataFrame.Histo2D(("ATLL_11_pileupDown","ATLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailHalfSF')
    hSFLL11_pileupDown = SRLL.DataFrame.Histo2D(("SFLL_11_pileupDown","ATLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailFullSF')

    hSRTT11_triggertight_up = SRTT.DataFrame.Histo2D(("SRTT_11_trigger_up","SRTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','triggertight_up')
    hATTT11_triggertight_up = ATTT.DataFrame.Histo2D(("ATTT_11_trigger_up","ATTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_upFailHalfSF')
    hSFTT11_triggertight_up = SRTT.DataFrame.Histo2D(("SFTT_11_trigger_up","ATTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_upFailFullSF')

    hSRLL11_triggerloose_up = SRLL.DataFrame.Histo2D(("SRLL_11_trigger_up","SRLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_up')
    hATLL11_triggerloose_up = ATLL.DataFrame.Histo2D(("ATLL_11_trigger_up","ATLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailHalfSF')
    hSFLL11_triggerloose_up = SRLL.DataFrame.Histo2D(("SFLL_11_trigger_up","ATLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailFullSF')

    hSRTT11_triggertight_down = SRTT.DataFrame.Histo2D(("SRTT_11_trigger_down","SRTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','triggertight_down')
    hATTT11_triggertight_down = ATTT.DataFrame.Histo2D(("ATTT_11_trigger_down","ATTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_downFailHalfSF')
    hSFTT11_triggertight_down = SRTT.DataFrame.Histo2D(("SFTT_11_trigger_down","ATTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_downFailFullSF')

    hSRLL11_triggerloose_down = SRLL.DataFrame.Histo2D(("SRLL_11_trigger_down","SRLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_down')
    hATLL11_triggerloose_down = ATLL.DataFrame.Histo2D(("ATLL_11_trigger_down","ATLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailHalfSF')
    hSFLL11_triggerloose_down = SRLL.DataFrame.Histo2D(("SFLL_11_trigger_down","ATLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailFullSF')

    hSRTT11_dbsftight_up = SRTT.DataFrame.Histo2D(("SRTT_11_dbsf_up","SRTT_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_up')
    hATTT11_dbsftight_up = ATTT.DataFrame.Histo2D(("ATTT_11_dbsf_up","ATTT_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_upFailHalfSF')
    hSFTT11_dbsftight_up = SRTT.DataFrame.Histo2D(("SFTT_11_dbsf_up","ATTT_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_upFailFullSF')

    hSRLL11_dbsfloose_up = SRLL.DataFrame.Histo2D(("SRLL_11_dbsf_up","SRLL_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_up')
    hATLL11_dbsfloose_up = ATLL.DataFrame.Histo2D(("ATLL_11_dbsf_up","ATLL_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_upFailHalfSF')
    hSFLL11_dbsfloose_up = SRLL.DataFrame.Histo2D(("SFLL_11_dbsf_up","ATLL_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_upFailFullSF')

    hSRTT11_dbsftight_down = SRTT.DataFrame.Histo2D(("SRTT_11_dbsf_down","SRTT_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','dbsftight_down')
    hATTT11_dbsftight_down = ATTT.DataFrame.Histo2D(("ATTT_11_dbsf_down","ATTT_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_downFailHalfSF')
    hSFTT11_dbsftight_down = SRTT.DataFrame.Histo2D(("SFTT_11_dbsf_down","ATTT_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsftight_downFailFullSF')

    hSRLL11_dbsfloose_down = SRLL.DataFrame.Histo2D(("SRLL_11_dbsf_down","SRLL_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_down')
    hATLL11_dbsfloose_down = ATLL.DataFrame.Histo2D(("ATLL_11_dbsf_down","ATLL_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_downFailHalfSF')
    hSFLL11_dbsfloose_down = SRLL.DataFrame.Histo2D(("SFLL_11_dbsf_down","ATLL_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_downFailFullSF')

##### Control Region templates

    hSRCR11_pdfUp = SRCR.DataFrame.Histo2D(("SRCR_11_pdfUp","SRCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_up')
    hATCR11_pdfUp = ATCR.DataFrame.Histo2D(("ATCR_11_pdfUp","ATCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailHalfSF')
    hSFCR11_pdfUp = SRCR.DataFrame.Histo2D(("SFCR_11_pdfUp","ATCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailFullSF')

    hSRCR11_pdfDown = SRCR.DataFrame.Histo2D(("SRCR_11_pdfDown","SRCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_down')
    hATCR11_pdfDown = ATCR.DataFrame.Histo2D(("ATCR_11_pdfDown","ATCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailHalfSF')
    hSFCR11_pdfDown = SRCR.DataFrame.Histo2D(("SFCR_11_pdfDown","ATCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailFullSF')

    hSRCR11_pileupUp = SRCR.DataFrame.Histo2D(("SRCR_11_pileupUp","SRCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_up')
    hATCR11_pileupUp = ATCR.DataFrame.Histo2D(("ATCR_11_pileupUp","ATCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailHalfSF')
    hSFCR11_pileupUp = SRCR.DataFrame.Histo2D(("SFCR_11_pileupUp","ATCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailFullSF')

    hSRCR11_pileupDown = SRCR.DataFrame.Histo2D(("SRCR_11_pileupDown","SRCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_down')
    hATCR11_pileupDown = ATCR.DataFrame.Histo2D(("ATCR_11_pileupDown","ATCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailHalfSF')
    hSFCR11_pileupDown = SRCR.DataFrame.Histo2D(("SFCR_11_pileupDown","ATCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailFullSF')

    hSRCR11_triggerloose_up = SRCR.DataFrame.Histo2D(("SRCR_11_trigger_up","SRCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_up')
    hATCR11_triggerloose_up = ATCR.DataFrame.Histo2D(("ATCR_11_trigger_up","ATCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailHalfSF')
    hSFCR11_triggerloose_up = SRCR.DataFrame.Histo2D(("SFCR_11_trigger_up","ATCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailFullSF')

    hSRCR11_triggerloose_down = SRCR.DataFrame.Histo2D(("SRCR_11_trigger_down","SRCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_down')
    hATCR11_triggerloose_down = ATCR.DataFrame.Histo2D(("ATCR_11_trigger_down","ATCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailHalfSF')
    hSFCR11_triggerloose_down = SRCR.DataFrame.Histo2D(("SFCR_11_trigger_down","ATCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailFullSF')

    hSRCR11_dbsfloose_up = SRCR.DataFrame.Histo2D(("SRCR_11_dbsf_up","SRCR_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_up')
    hATCR11_dbsfloose_up = ATCR.DataFrame.Histo2D(("ATCR_11_dbsf_up","ATCR_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_upFailHalfSF')
    hSFCR11_dbsfloose_up = SRCR.DataFrame.Histo2D(("SFCR_11_dbsf_up","ATCR_11_dbsfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_upFailFullSF')

    hSRCR11_dbsfloose_down = SRCR.DataFrame.Histo2D(("SRCR_11_dbsf_down","SRCR_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_down')
    hATCR11_dbsfloose_down = ATCR.DataFrame.Histo2D(("ATCR_11_dbsf_down","ATCR_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_downFailHalfSF')
    hSFCR11_dbsfloose_down = SRCR.DataFrame.Histo2D(("SFCR_11_dbsf_down","ATCR_11_dbsfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'dbsfloose_downFailFullSF')

##### Now for 2+1 template histo calls.

    hSRTT21_pdfUp = Pass.DataFrame.Histo2D(("SRTT_21_pdfUp","SRTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','Pdfweight_up')
    hATTT21_pdfUp = Fail.DataFrame.Histo2D(("ATTT_21_pdfUp","ATTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'Pdfweight_upFailHalfSF')
    hSFTT21_pdfUp = Pass.DataFrame.Histo2D(("SFTT_21_pdfUp","SFTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'Pdfweight_upFailFullSF')

    hSRTT21_pdfDown = Pass.DataFrame.Histo2D(("SRTT_21_pdfDown","SRTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','Pdfweight_down')
    hATTT21_pdfDown = Fail.DataFrame.Histo2D(("ATTT_21_pdfDown","ATTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'Pdfweight_downFailHalfSF')
    hSFTT21_pdfDown = Pass.DataFrame.Histo2D(("SFTT_21_pdfDown","ATTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'Pdfweight_downFailFullSF')

    hSRTT21_pileupUp = Pass.DataFrame.Histo2D(("SRTT_21_pileupUp","SRTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','pileupweight_up')
    hATTT21_pileupUp = Fail.DataFrame.Histo2D(("ATTT_21_pileupUp","ATTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'pileupweight_upFailHalfSF')
    hSFTT21_pileupUp = Pass.DataFrame.Histo2D(("SFTT_21_pileupUp","SFTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'pileupweight_upFailFullSF')

    hSRTT21_pileupDown = Pass.DataFrame.Histo2D(("SRTT_21_pileupDown","SRTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','pileupweight_down')
    hATTT21_pileupDown = Fail.DataFrame.Histo2D(("ATTT_21_pileupDown","ATTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'pileupweight_downFailHalfSF')
    hSFTT21_pileupDown = Pass.DataFrame.Histo2D(("SFTT_21_pileupDown","ATTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'pileupweight_downFailFullSF')

    hSRTT21_trigger_up = Pass.DataFrame.Histo2D(("SRTT_21_trigger_up","SRTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','trigger_up')
    hATTT21_trigger_up = Fail.DataFrame.Histo2D(("ATTT_21_trigger_up","ATTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'trigger_upFailHalfSF')
    hSFTT21_trigger_up = Pass.DataFrame.Histo2D(("SFTT_21_trigger_up","SFTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'trigger_upFailFullSF')

    hSRTT21_trigger_down = Pass.DataFrame.Histo2D(("SRTT_21_trigger_down","SRTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','trigger_down')
    hATTT21_trigger_down = Fail.DataFrame.Histo2D(("ATTT_21_trigger_down","ATTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'trigger_downFailHalfSF')
    hSFTT21_trigger_down = Pass.DataFrame.Histo2D(("SFTT_21_trigger_down","ATTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'trigger_downFailFullSF')

    hSRTT21_btagsfUp = Pass.DataFrame.Histo2D(("hSRTT_21_btagsfUp","SRTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','btagsfweight_up')
    hATTT21_btagsfUp = Fail.DataFrame.Histo2D(("hATTT_21_btagsfUp","ATTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'btagsfweight_upFailHalfSF')
    hSFTT21_btagsfUp = Pass.DataFrame.Histo2D(("hSFTT_21_btagsfUp","SFTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'btagsfweight_upFailFullSF')

    hSRTT21_btagsfDown = Pass.DataFrame.Histo2D(("hSRTT_21_btagsfDown","SRTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','btagsfweight_down')
    hATTT21_btagsfDown = Fail.DataFrame.Histo2D(("hATTT_21_btagsfDown","ATTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'btagsfweight_downFailHalfSF')
    hSFTT21_btagsfDown = Pass.DataFrame.Histo2D(("hSFTT_21_btagsfDown","ATTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'btagsfweight_downFailFullSF')

    hSRTT21_dbsf_up = Pass.DataFrame.Histo2D(("SRTT_21_dbsf_up","SRTT_21_dbsfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','dbsfup')
    hATTT21_dbsf_up = Fail.DataFrame.Histo2D(("ATTT_21_dbsf_up","ATTT_21_dbsfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','dbsfupFailHalfSF')
    hSFTT21_dbsf_up = Pass.DataFrame.Histo2D(("SFTT_21_dbsf_up","SFTT_21_dbsfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','dbsfupFailFullSF')

    hSRTT21_dbsf_down = Pass.DataFrame.Histo2D(("SRTT_21_dbsf_down","SRTT_21_dbsfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','dbsfdown')
    hATTT21_dbsf_down = Fail.DataFrame.Histo2D(("ATTT_21_dbsf_down","ATTT_21_dbsfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','dbsfdownFailHalfSF')
    hSFTT21_dbsf_down = Pass.DataFrame.Histo2D(("SFTT_21_dbsf_down","ATTT_21_dbsfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','dbsfdownFailFullSF')

    if 'ttbar' in setname:
#### 1+1 Templates
        hSRTT11_topptAlphaUp = SRTT.DataFrame.Histo2D(("SRTT_11_topptAlphaUp","SRTT_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','topptweight_tight_Alphaup')
        hATTT11_topptAlphaUp = ATTT.DataFrame.Histo2D(("ATTT_11_topptAlphaUp","ATTT_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_AlphaupFailHalfSF')
        hSFTT11_topptAlphaUp = SRTT.DataFrame.Histo2D(("SFTT_11_topptAlphaUp","ATTT_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_AlphaupFailFullSF')

        hSRLL11_topptAlphaUp = SRLL.DataFrame.Histo2D(("SRLL_11_topptAlphaUp","SRLL_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_Alphaup')
        hATLL11_topptAlphaUp = ATLL.DataFrame.Histo2D(("ATLL_11_topptAlphaUp","ATLL_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_AlphaupFailHalfSF')
        hSFLL11_topptAlphaUp = SRLL.DataFrame.Histo2D(("SFLL_11_topptAlphaUp","ATLL_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_AlphaupFailFullSF')

        hSRTT11_topptAlphaDown = SRTT.DataFrame.Histo2D(("SRTT_11_topptAlphaDown","SRTT_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','topptweight_tight_Alphadown')
        hATTT11_topptAlphaDown = ATTT.DataFrame.Histo2D(("ATTT_11_topptAlphaDown","ATTT_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_AlphadownFailHalfSF')
        hSFTT11_topptAlphaDown = SRTT.DataFrame.Histo2D(("SFTT_11_topptAlphaDown","ATTT_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_AlphadownFailFullSF')

        hSRLL11_topptAlphaDown = SRLL.DataFrame.Histo2D(("SRLL_11_topptAlphaDown","SRLL_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_Alphadown')
        hATLL11_topptAlphaDown = ATLL.DataFrame.Histo2D(("ATLL_11_topptAlphaDown","ATLL_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_AlphadownFailHalfSF')
        hSFLL11_topptAlphaDown = SRLL.DataFrame.Histo2D(("SFLL_11_topptAlphaDown","ATLL_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_AlphadownFailFullSF')

        hSRTT11_topptBetaUp = SRTT.DataFrame.Histo2D(("SRTT_11_topptBetaUp","SRTT_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','topptweight_tight_Betaup')
        hATTT11_topptBetaUp = ATTT.DataFrame.Histo2D(("ATTT_11_topptBetaUp","ATTT_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_BetaupFailHalfSF')
        hSFTT11_topptBetaUp = SRTT.DataFrame.Histo2D(("SFTT_11_topptBetaUp","ATTT_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_BetaupFailFullSF')

        hSRLL11_topptBetaUp = SRLL.DataFrame.Histo2D(("SRLL_11_topptBetaUp","SRLL_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_Betaup')
        hATLL11_topptBetaUp = ATLL.DataFrame.Histo2D(("ATLL_11_topptBetaUp","ATLL_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_BetaupFailHalfSF')
        hSFLL11_topptBetaUp = SRLL.DataFrame.Histo2D(("SFLL_11_topptBetaUp","ATLL_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_BetaupFailFullSF')

        hSRTT11_topptBetaDown = SRTT.DataFrame.Histo2D(("SRTT_11_topptBetaDown","SRTT_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','topptweight_tight_Betadown')
        hATTT11_topptBetaDown = ATTT.DataFrame.Histo2D(("ATTT_11_topptBetaDown","ATTT_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_BetadownFailHalfSF')
        hSFTT11_topptBetaDown = SRTT.DataFrame.Histo2D(("SFTT_11_topptBetaDown","ATTT_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_BetadownFailFullSF')

        hSRLL11_topptBetaDown = SRLL.DataFrame.Histo2D(("SRLL_11_topptBetaDown","SRLL_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_Betadown')
        hATLL11_topptBetaDown = ATLL.DataFrame.Histo2D(("ATLL_11_topptBetaDown","ATLL_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_BetadownFailHalfSF')
        hSFLL11_topptBetaDown = SRLL.DataFrame.Histo2D(("SFLL_11_topptBetaDown","ATLL_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_BetadownFailFullSF')

        if "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
            hSRTT11_ttbarNormUp = SRTT.DataFrame.Histo2D(("SRTT_11_ttbarNormUp","SRTT_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','weight_tight_NormUp')
            hATTT11_ttbarNormUp = ATTT.DataFrame.Histo2D(("ATTT_11_ttbarNormUp","ATTT_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_tight_NormUpFailHalfSF')
            hSFTT11_ttbarNormUp = SRTT.DataFrame.Histo2D(("SFTT_11_ttbarNormUp","ATTT_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_tight_NormUpFailFullSF')

            hSRLL11_ttbarNormUp = SRLL.DataFrame.Histo2D(("SRLL_11_ttbarNormUp","SRLL_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormUp')
            hATLL11_ttbarNormUp = ATLL.DataFrame.Histo2D(("ATLL_11_ttbarNormUp","ATLL_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormUpFailHalfSF')
            hSFLL11_ttbarNormUp = SRLL.DataFrame.Histo2D(("SFLL_11_ttbarNormUp","ATLL_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormUpFailFullSF')

            hSRTT11_ttbarNormDown = SRTT.DataFrame.Histo2D(("SRTT_11_ttbarNormDown","SRTT_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','weight_tight_NormDown')
            hATTT11_ttbarNormDown = ATTT.DataFrame.Histo2D(("ATTT_11_ttbarNormDown","ATTT_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_tight_NormDownFailHalfSF')
            hSFTT11_ttbarNormDown = SRTT.DataFrame.Histo2D(("SFTT_11_ttbarNormDown","ATTT_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_tight_NormDownFailFullSF')

            hSRLL11_ttbarNormDown = SRLL.DataFrame.Histo2D(("SRLL_11_ttbarNormDown","SRLL_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormDown')
            hATLL11_ttbarNormDown = ATLL.DataFrame.Histo2D(("ATLL_11_ttbarNormDown","ATLL_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormDownFailHalfSF')
            hSFLL11_ttbarNormDown = SRLL.DataFrame.Histo2D(("SFLL_11_ttbarNormDown","ATLL_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormDownFailFullSF')



### Now Control Region templates
        hSRCR11_topptAlphaUp = SRCR.DataFrame.Histo2D(("SRCR_11_topptAlphaUp","SRCR_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_Alphaup')
        hATCR11_topptAlphaUp = ATCR.DataFrame.Histo2D(("ATCR_11_topptAlphaUp","ATCR_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_AlphaupFailHalfSF')
        hSFCR11_topptAlphaUp = SRCR.DataFrame.Histo2D(("SFCR_11_topptAlphaUp","ATCR_11_topptAlphaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_AlphaupFailFullSF')

        hSRCR11_topptAlphaDown = SRCR.DataFrame.Histo2D(("SRCR_11_topptAlphaDown","SRCR_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_Alphadown')
        hATCR11_topptAlphaDown = ATCR.DataFrame.Histo2D(("ATCR_11_topptAlphaDown","ATCR_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_AlphadownFailHalfSF')
        hSFCR11_topptAlphaDown = SRCR.DataFrame.Histo2D(("SFCR_11_topptAlphaDown","ATCR_11_topptAlphaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_AlphadownFailFullSF')

        hSRCR11_topptBetaUp = SRCR.DataFrame.Histo2D(("SRCR_11_topptBetaUp","SRCR_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_Betaup')
        hATCR11_topptBetaUp = ATCR.DataFrame.Histo2D(("ATCR_11_topptBetaUp","ATCR_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_BetaupFailHalfSF')
        hSFCR11_topptBetaUp = SRCR.DataFrame.Histo2D(("SFCR_11_topptBetaUp","ATCR_11_topptBetaUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_BetaupFailFullSF')

        hSRCR11_topptBetaDown = SRCR.DataFrame.Histo2D(("SRCR_11_topptBetaDown","SRCR_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_Betadown')
        hATCR11_topptBetaDown = ATCR.DataFrame.Histo2D(("ATCR_11_topptBetaDown","ATCR_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_BetadownFailHalfSF')
        hSFCR11_topptBetaDown = SRCR.DataFrame.Histo2D(("SFCR_11_topptBetaDown","ATCR_11_topptBetaDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_BetadownFailFullSF')

        hSRCR11_ttbarNormUp = SRCR.DataFrame.Histo2D(("SRCR_11_ttbarNormUp","SRCR_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormUp')
        hATCR11_ttbarNormUp = ATCR.DataFrame.Histo2D(("ATCR_11_ttbarNormUp","ATCR_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormUpFailHalfSF')
        hSFCR11_ttbarNormUp = SRCR.DataFrame.Histo2D(("SFCR_11_ttbarNormUp","ATCR_11_ttbarNormUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormUpFailFullSF')

        hSRCR11_ttbarNormDown = SRCR.DataFrame.Histo2D(("SRCR_11_ttbarNormDown","SRCR_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormDown')
        hATCR11_ttbarNormDown = ATCR.DataFrame.Histo2D(("ATCR_11_ttbarNormDown","ATCR_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormDownFailHalfSF')
        hSFCR11_ttbarNormDown = SRCR.DataFrame.Histo2D(("SFCR_11_ttbarNormDown","ATCR_11_ttbarNormDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'weight_loose_NormDownFailFullSF')


### Now 2+1 top templates
        hSRTT21_topptAlphaUp = Pass.DataFrame.Histo2D(("SRTT_21_topptAlphaUp","SRTT_21_topptAlphaUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','topptweight_Alphaup')
        hATTT21_topptAlphaUp = Fail.DataFrame.Histo2D(("ATTT_21_topptAlphaUp","ATTT_21_topptAlphaUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'topptweight_AlphaupFailHalfSF')
        hSFTT21_topptAlphaUp = Pass.DataFrame.Histo2D(("SFTT_21_topptAlphaUp","SFTT_21_topptAlphaUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'topptweight_AlphaupFailFullSF')

        hSRTT21_topptAlphaDown = Pass.DataFrame.Histo2D(("SRTT_21_topptAlphaDown","SRTT_21_topptAlphaDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','topptweight_Alphadown')
        hATTT21_topptAlphaDown = Fail.DataFrame.Histo2D(("ATTT_21_topptAlphaDown","ATTT_21_topptAlphaDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'topptweight_AlphadownFailHalfSF')
        hSFTT21_topptAlphaDown = Pass.DataFrame.Histo2D(("SFTT_21_topptAlphaDown","ATTT_21_topptAlphaDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'topptweight_AlphadownFailFullSF')

        hSRTT21_topptBetaUp = Pass.DataFrame.Histo2D(("SRTT_21_topptBetaUp","SRTT_21_topptBetaUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','topptweight_Betaup')
        hATTT21_topptBetaUp = Fail.DataFrame.Histo2D(("ATTT_21_topptBetaUp","ATTT_21_topptBetaUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'topptweight_BetaupFailHalfSF')
        hSFTT21_topptBetaUp = Pass.DataFrame.Histo2D(("SFTT_21_topptBetaUp","SFTT_21_topptBetaUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'topptweight_BetaupFailFullSF')

        hSRTT21_topptBetaDown = Pass.DataFrame.Histo2D(("SRTT_21_topptBetaDown","SRTT_21_topptBetaDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','topptweight_Betadown')
        hATTT21_topptBetaDown = Fail.DataFrame.Histo2D(("ATTT_21_topptBetaDown","ATTT_21_topptBetaDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'topptweight_BetadownFailHalfSF')
        hSFTT21_topptBetaDown = Pass.DataFrame.Histo2D(("SFTT_21_topptBetaDown","ATTT_21_topptBetaDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'topptweight_BetadownFailFullSF')
        
        if "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
            hSRTT21_ttbarNormUp = Pass.DataFrame.Histo2D(("SRTT_21_ttbarNormUp","SRTT_21_ttbarNormUp",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','weight_NormUp')
            hATTT21_ttbarNormUp = Fail.DataFrame.Histo2D(("ATTT_21_ttbarNormUp","ATTT_21_ttbarNormUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'weight_NormUpFailHalfSF')
            hSFTT21_ttbarNormUp = Pass.DataFrame.Histo2D(("SFTT_21_ttbarNormUp","SFTT_21_ttbarNormUp",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'weight_NormUpFailFullSF')

            hSRTT21_ttbarNormDown = Pass.DataFrame.Histo2D(("SRTT_21_ttbarNormDown","SRTT_21_ttbarNormDown",18 ,45 ,225 ,13 ,700 ,2000),'mh','mreduced21','weight_NormDown')
            hATTT21_ttbarNormDown = Fail.DataFrame.Histo2D(("ATTT_21_ttbarNormDown","ATTT_21_ttbarNormDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'weight_NormDownFailHalfSF')
            hSFTT21_ttbarNormDown = Pass.DataFrame.Histo2D(("SFTT_21_ttbarNormDown","ATTT_21_ttbarNormDown",18 ,45 ,225 ,13 ,700 ,2000),"mh","mreduced21",'weight_NormDownFailFullSF')


        top_check = preselected.DataFrame.Histo1D("topptvectorcheck")


#### The below is done to account for needing to derive a SF for the Fail distribution on the alphabet jet

if not a.isData:

    hATTT11.Add(hSFTT11.GetPtr())
    hATLL11.Add(hSFLL11.GetPtr())
    hATTT21.Add(hSFTT21.GetPtr())
    hATCR11.Add(hSFCR11.GetPtr())

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

    if 'ttbar' in setname:
#### 1+1 Templates

        hATTT11_topptAlphaUp.Add(hSFTT11_topptAlphaUp.GetPtr())
        hATLL11_topptAlphaUp.Add(hSFLL11_topptAlphaUp.GetPtr())
        hATTT11_topptAlphaDown.Add(hSFTT11_topptAlphaDown.GetPtr())
        hATLL11_topptAlphaDown.Add(hSFLL11_topptAlphaDown.GetPtr())

        hATTT11_topptBetaUp.Add(hSFTT11_topptBetaUp.GetPtr())
        hATLL11_topptBetaUp.Add(hSFLL11_topptBetaUp.GetPtr())
        hATTT11_topptBetaDown.Add(hSFTT11_topptBetaDown.GetPtr())
        hATLL11_topptBetaDown.Add(hSFLL11_topptBetaDown.GetPtr())

        if "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
            hATTT11_ttbarNormUp.Add(hSFTT11_ttbarNormUp.GetPtr())
            hATLL11_ttbarNormUp.Add(hSFLL11_ttbarNormUp.GetPtr())
            hATTT11_ttbarNormDown.Add(hSFTT11_ttbarNormDown.GetPtr())
            hATLL11_ttbarNormDown.Add(hSFLL11_ttbarNormDown.GetPtr())

### Now Control Region templates

        hATCR11_topptAlphaUp.Add(hSFCR11_topptAlphaUp.GetPtr())
        hATCR11_topptAlphaDown.Add(hSFCR11_topptAlphaDown.GetPtr())

        hATCR11_topptBetaUp.Add(hSFCR11_topptBetaUp.GetPtr())
        hATCR11_topptBetaDown.Add(hSFCR11_topptBetaDown.GetPtr())    

        if "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
            hATCR11_ttbarNormUp.Add(hSFCR11_ttbarNormUp.GetPtr())
            hATCR11_ttbarNormDown.Add(hSFCR11_ttbarNormDown.GetPtr())    

### Now 2+1 top templates

        hATTT21_topptAlphaUp.Add(hSFTT21_topptAlphaUp.GetPtr())
        hATTT21_topptAlphaDown.Add(hSFTT21_topptAlphaDown.GetPtr())

        hATTT21_topptBetaUp.Add(hSFTT21_topptBetaUp.GetPtr())
        hATTT21_topptBetaDown.Add(hSFTT21_topptBetaDown.GetPtr())

        if "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
            hATTT21_ttbarNormUp.Add(hSFTT21_ttbarNormUp.GetPtr())
            hATTT21_ttbarNormDown.Add(hSFTT21_ttbarNormDown.GetPtr())

#### Now we can process the histograms
hists = [hSRTT11,hATTT11,hSRLL11,hATLL11,hSRTT21,hATTT21,hSRCR11,hATCR11,        
        hpt0TT,hpt1TT,heta0TT,heta1TT,hdeltaEtaTT,hmredTT,hmsd1TT,htau21TT,hmsd0TT,hpt0LL,hpt1LL,heta0LL,heta1LL,hdeltaEtaLL,hmredLL,hmsd1LL,htau21LL,hmsd0LL,
        hpt021,bpt021,bpt121,heta021,beta021,heta021,hdeltaEta21,hmred21,hmsd021,hmbb21,
        deltaRCheck,trijetMassCheck,trijetMassDeltaR]
        # nom_check_plot,raw_check_plot]

if not a.isData:
    hists.extend([hSRTT11_pdfUp,hATTT11_pdfUp,hSRLL11_pdfUp,hATLL11_pdfUp,hSRTT11_pdfDown,hATTT11_pdfDown,hSRLL11_pdfDown,hATLL11_pdfDown,
        hSRTT11_pileupUp,hATTT11_pileupUp,hSRLL11_pileupUp,hATLL11_pileupUp,hSRTT11_pileupDown,hATTT11_pileupDown,hSRLL11_pileupDown,hATLL11_pileupDown,
        hSRTT11_triggertight_up,hATTT11_triggertight_up,hSRLL11_triggerloose_up,hATLL11_triggerloose_up,hSRTT11_triggertight_down,hATTT11_triggertight_down,hSRLL11_triggerloose_down,hATLL11_triggerloose_down,
        hSRTT11_dbsftight_up,hATTT11_dbsftight_up,hSRLL11_dbsfloose_up,hATLL11_dbsfloose_up,hSRTT11_dbsftight_down,hATTT11_dbsftight_down,hSRLL11_dbsfloose_down,hATLL11_dbsfloose_down,
        hSRTT21_pdfUp,hATTT21_pdfUp,hSRTT21_pdfDown,hATTT21_pdfDown,hSRTT21_pileupUp,hATTT21_pileupUp,hSRTT21_pileupDown,hATTT21_pileupDown,hSRTT21_dbsf_up,hATTT21_dbsf_up,hSRTT21_dbsf_down,hATTT21_dbsf_down,
        hSRTT21_trigger_up,hATTT21_trigger_up,hSRTT21_trigger_down,hATTT21_trigger_down,hSRTT21_btagsfUp,hATTT21_btagsfUp,hSRTT21_btagsfDown,hATTT21_btagsfDown,
        hSRCR11_pdfUp,hATCR11_pdfUp,hSRCR11_pdfDown,hATCR11_pdfDown,
        hSRCR11_pileupUp,hATCR11_pileupUp,hSRCR11_pileupDown,hATCR11_pileupDown,
        hSRCR11_triggerloose_up,hATCR11_triggerloose_up,hSRCR11_triggerloose_down,hATCR11_triggerloose_down,
        hSRCR11_dbsfloose_up,hATCR11_dbsfloose_up,hSRCR11_dbsfloose_down,hATCR11_dbsfloose_down])
    if 'ttbar' in setname:
        hists.extend([hSRTT11_topptAlphaUp,hATTT11_topptAlphaUp,hSRLL11_topptAlphaUp,hATLL11_topptAlphaUp,hSRTT11_topptAlphaDown,hATTT11_topptAlphaDown,hSRLL11_topptAlphaDown,hATLL11_topptAlphaDown,
            hSRCR11_topptAlphaUp,hATCR11_topptAlphaUp,hSRCR11_topptAlphaDown,hATCR11_topptAlphaDown,        
            hSRTT21_topptAlphaUp,hATTT21_topptAlphaUp,hSRTT21_topptAlphaDown,hATTT21_topptAlphaDown,
            hSRTT11_topptBetaUp,hATTT11_topptBetaUp,hSRLL11_topptBetaUp,hATLL11_topptBetaUp,hSRTT11_topptBetaDown,hATTT11_topptBetaDown,hSRLL11_topptBetaDown,hATLL11_topptBetaDown,
            hSRCR11_topptBetaUp,hATCR11_topptBetaUp,hSRCR11_topptBetaDown,hATCR11_topptBetaDown,        
            hSRTT21_topptBetaUp,hATTT21_topptBetaUp,hSRTT21_topptBetaDown,hATTT21_topptBetaDown])
        if "deepTagMD_HbbvsQCD" or "deepTagMD_ZHbbvsQCD" in options.doublebtagger:
            hists.extend([hSRTT11_ttbarNormUp,hATTT11_ttbarNormUp,hSRLL11_ttbarNormUp,hATLL11_ttbarNormUp,hSRTT11_ttbarNormDown,hATTT11_ttbarNormDown,hSRLL11_ttbarNormDown,hATLL11_ttbarNormDown,
            hSRCR11_ttbarNormUp,hATCR11_ttbarNormUp,hSRCR11_ttbarNormDown,hATCR11_ttbarNormDown,hSRTT21_ttbarNormUp,hATTT21_ttbarNormUp,hSRTT21_ttbarNormDown,hATTT21_ttbarNormDown])

norm_hist = ROOT.TH1F('norm','norm',1,0,1)
norm_hist.SetBinContent(1,norm)
norm_hist.Write()

# Draw a simple cutflow plot
SRTT_cuts = slim_skim+filters+preselection11+preselection12
SRTT_cuts.Add("SRTT","SRTT==1")
SRTT_cutflow = CutflowHist('cutflow11',SRTT) # SRTT.DataFrame already has the cuts and numbers, SRTT_cuts is just to name the histogram bins (but that means they must match up!)
# SRTT_cutflow.Scale(lumi/a.genEventCount)
SRTT_cutflow.Write()

Pass21_cuts = slim_skim+filters+preselection21+preselection22+preselection23
Pass21_cuts.Add("Pass21","Pass21==1")
Pass21_cutflow = CutflowHist('cutflow21',Pass) 
# Pass21_cutflow.Scale(lumi/a.genEventCount)
Pass21_cutflow.Write()

# if not a.isData:
#     nminus1_21_node = Nminus1(nminus1_21,Pass21_cuts)

#     trijetDeltaRhist = nminus1_21_node["topDeltaR"].DataFrame.Histo1D(("trijetDeltaR","trijetDeltaR",50 ,0 ,5),"topDeltaR","finalweightTight")
#     trijetMasshist = nminus1_21_node["topMass"].DataFrame.Histo1D(("trijetMass","trijetMass",50 ,100 ,1000),"topMass","finalweightTight")

#     hists.extend([trijetDeltaRhist,trijetMasshist])

for h in hists: 
    h.Scale(norm)
    h.Write()

# Cleanup
out_f.Close()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
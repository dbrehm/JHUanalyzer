import ROOT
import subprocess

outfile = ROOT.TFile.Open('TriggerWeights.root','RECREATE')
qcds = ['QCDHT700','QCDHT1000','QCDHT1500','QCDHT2000']
for y in ['16','17','18']:
    if y == '16': datas = ['dataB2','dataC','dataD','dataE','dataF','dataG','dataH']
    elif y == '17': datas = ['dataB','dataC','dataD','dataE','dataF']
    elif y == '18': datas = ['dataA','dataB','dataC','dataD']

    for doubleb in ['deepTagMD_HbbvsQCD']:#,'deepTagMD_ZHbbvsQCD','btagDDBvL']:
        new_file = 'HHtrigger'+y+'_data_'+doubleb+'.root'
        hadd_string = 'hadd '+new_file

        new_file_qcd = 'HHtrigger'+y+'_QCD_'+doubleb+'.root'
        hadd_string_qcd = 'hadd '+new_file_qcd
        print 'Executing: rm ' + new_file
        subprocess.call(['rm '+new_file],shell=True) 
        print 'Executing: rm ' + new_file_qcd
        subprocess.call(['rm '+new_file_qcd],shell=True) 
        for d in datas:
            hadd_string += ' HHtrigger'+y+'_'+d+'_'+doubleb+'.root'
        for q in qcds:
            hadd_string_qcd += ' HHtrigger'+y+'_'+q+'_'+doubleb+'.root'
            
        print 'Executing: ' + hadd_string
        subprocess.call([hadd_string],shell=True)

        print 'Executing: ' + hadd_string_qcd
        subprocess.call([hadd_string_qcd],shell=True)

        infile = ROOT.TFile.Open('HHtrigger'+y+'_data_'+doubleb+'.root')
        infileQ = ROOT.TFile.Open('HHtrigger'+y+'_QCD_'+doubleb+'.root')
        infileTT = ROOT.TFile.Open('HHtrigger'+y+'_ttbar_'+doubleb+'.root')

        hnum = infile.Get('hnum') 
        hden = infile.Get('hden')

        hnum21 = infile.Get('hnum21') 
        hden21 = infile.Get('hden21')

        hnumQ = infileQ.Get('hnum') 
        hdenQ = infileQ.Get('hden')

        hnum21Q = infileQ.Get('hnum21') 
        hden21Q = infileQ.Get('hden21')   

        hnumtt = infileTT.Get('hnum') 
        hdentt = infileTT.Get('hden')

        hnum21tt = infileTT.Get('hnum21') 
        hden21tt = infileTT.Get('hden21')


        hnum2D = infile.Get('hnum2D') 
        hden2D = infile.Get('hden2D')

        hnum212D = infile.Get('hnum212D') 
        hden212D = infile.Get('hden212D')

        hnumQ2D = infileQ.Get('hnum2D') 
        hdenQ2D = infileQ.Get('hden2D')

        hnum21Q2D = infileQ.Get('hnum212D') 
        hden21Q2D = infileQ.Get('hden212D')   

        hnumtt2D = infileTT.Get('hnum2D') 
        hdentt2D = infileTT.Get('hden2D')

        hnum21tt2D = infileTT.Get('hnum212D') 
        hden21tt2D = infileTT.Get('hden212D')


        hh11 = hnum.Clone(doubleb+'tight'+y)
        hh11.Divide(hden)

        hh11Q = hnumQ.Clone(doubleb+'tight'+y+'QCD')
        hh11Q.Divide(hdenQ)

        hh11tt = hnumtt.Clone(doubleb+'tight'+y+'ttbar')
        hh11tt.Divide(hdentt)


        hh21 = hnum21.Clone(doubleb+'21'+y)
        hh21.Divide(hden21)

        hh21Q = hnum21Q.Clone(doubleb+'21'+y+'QCD')
        hh21Q.Divide(hden21Q)

        hh21tt = hnum21tt.Clone(doubleb+'21'+y+'ttbar')
        hh21tt.Divide(hden21tt)



        hh112D = hnum2D.Clone(doubleb+'tight2D'+y)
        hh112D.Divide(hden2D)

        hh11Q2D = hnumQ2D.Clone(doubleb+'tight2D'+y+'QCD')
        hh11Q2D.Divide(hdenQ2D)

        hh11tt2D = hnumtt2D.Clone(doubleb+'tight2D'+y+'ttbar')
        hh11tt2D.Divide(hdentt2D)


        hh212D = hnum212D.Clone(doubleb+'212D'+y)
        hh212D.Divide(hden212D)

        hh21Q2D = hnum21Q2D.Clone(doubleb+'212D'+y+'QCD')
        hh21Q2D.Divide(hden21Q2D)

        hh21tt2D = hnum21tt2D.Clone(doubleb+'212D'+y+'ttbar')
        hh21tt2D.Divide(hden21tt2D)


        h11D = ROOT.TEfficiency(hnum, hden)

        h21D = ROOT.TEfficiency(hnum21, hden21)

        h11Q = ROOT.TEfficiency(hnumQ, hdenQ)

        h21Q = ROOT.TEfficiency(hnum21Q, hden21Q)

        h11tt = ROOT.TEfficiency(hnumtt, hdentt)

        h21tt = ROOT.TEfficiency(hnum21tt, hden21tt)



        h11D2D = ROOT.TEfficiency(hnum2D, hden2D)

        h21D2D = ROOT.TEfficiency(hnum212D, hden212D)

        h11Q2D = ROOT.TEfficiency(hnumQ2D, hdenQ2D)

        h21Q2D = ROOT.TEfficiency(hnum21Q2D, hden21Q2D)


        # h11 = ROOT.TEfficiency(hh11, hh11Q)

        # h21 = ROOT.TEfficiency(hh21, hh21Q)

        # h11.SetStatisticOption(ROOT.TEfficiency.kFCP)
        # h11.SetName(doubleb+"11"+y+"Effplot")
        # h11.SetTitle(doubleb+"11"+y+"Effplot"";m_reduced;Efficiency")

        # h21.SetStatisticOption(ROOT.TEfficiency.kFCP)
        # h21.SetName(doubleb+'21'+y+"Effplot")
        # h21.SetTitle(doubleb+'21'+y+"Effplot"";m_reduced;Efficiency")

        h11D.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h11D.SetName(doubleb+"11"+y+"Effplot-Data")
        h11D.SetTitle(doubleb+"11"+y+"Effplot-Data"";m_reduced;Efficiency")

        h21D.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h21D.SetName(doubleb+'21'+y+"Effplot-Data")
        h21D.SetTitle(doubleb+'21'+y+"Effplot-Data"";m_reduced;Efficiency")

        h11Q.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h11Q.SetName(doubleb+"11"+y+"Effplot-QCD")
        h11Q.SetTitle(doubleb+"11"+y+"Effplot-QCD"";m_reduced;Efficiency")

        h21Q.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h21Q.SetName(doubleb+'21'+y+"Effplot-QCD")
        h21Q.SetTitle(doubleb+'21'+y+"Effplot-QCD"";m_reduced;Efficiency")

        h11tt.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h11tt.SetName(doubleb+"11"+y+"Effplot-ttbar")
        h11tt.SetTitle(doubleb+"11"+y+"Effplot-ttbar"";m_reduced;Efficiency")

        h21tt.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h21tt.SetName(doubleb+'21'+y+"Effplot-ttbar")
        h21tt.SetTitle(doubleb+'21'+y+"Effplot-ttbar"";m_reduced;Efficiency")




        ratio11 = hh11.Clone(doubleb+'ratio11'+y)
        ratio11.SetTitle(doubleb+'ratio11'+y)
        for b in range(1,hh11.GetNbinsX()+1):
            ratio11.SetBinContent(b,h11D.GetEfficiency(b)/h11Q.GetEfficiency(b))
            ratio11.SetBinError(b,max([h11D.GetEfficiencyErrorUp(b),h11Q.GetEfficiencyErrorUp(b),h11D.GetEfficiencyErrorLow(b),h11Q.GetEfficiencyErrorLow(b)]))

        ratio11TT = hh11.Clone(doubleb+'ratio11ttbar'+y)
        ratio11TT.SetTitle(doubleb+'ratio11ttbar'+y)
        for b in range(1,hh11.GetNbinsX()+1):
            ratio11TT.SetBinContent(b,h11D.GetEfficiency(b)/h11tt.GetEfficiency(b))
            ratio11TT.SetBinError(b,max([h11D.GetEfficiencyErrorUp(b),h11tt.GetEfficiencyErrorUp(b),h11D.GetEfficiencyErrorLow(b),h11tt.GetEfficiencyErrorLow(b)]))

        ratioQCDttbar11 = ratio11TT.Clone(doubleb+'ratio11QCDtoTTbar'+y)
        ratioQCDttbar11.SetTitle(doubleb+'ratio11QCDtoTTbar'+y)
        ratioQCDttbar11.Add(ratio11,-1)
        ratioQCDttbar11.Divide(ratio11,)

        ratio21 = hh21.Clone(doubleb+'ratio21'+y)
        ratio21.SetTitle(doubleb+'ratio21'+y)
        for b in range(1,hh21.GetNbinsX()+1):
            ratio21.SetBinContent(b,h21D.GetEfficiency(b)/h21Q.GetEfficiency(b))
            ratio21.SetBinError(b,max([h21D.GetEfficiencyErrorUp(b),h21Q.GetEfficiencyErrorUp(b),h21D.GetEfficiencyErrorLow(b),h21Q.GetEfficiencyErrorLow(b)]))

        ratio21TT = hh21.Clone(doubleb+'ratio21ttbar'+y)
        ratio21TT.SetTitle(doubleb+'ratio21ttbar'+y)
        for b in range(1,hh21.GetNbinsX()+1):
            ratio21TT.SetBinContent(b,h21D.GetEfficiency(b)/h21tt.GetEfficiency(b))
            ratio21TT.SetBinError(b,max([h21D.GetEfficiencyErrorUp(b),h21tt.GetEfficiencyErrorUp(b),h21D.GetEfficiencyErrorLow(b),h21tt.GetEfficiencyErrorLow(b)]))

        ratioQCDttbar21 = ratio21TT.Clone(doubleb+'ratio21QCDtoTTbar'+y)
        ratioQCDttbar21.SetTitle(doubleb+'ratio21QCDtoTTbar'+y)
        ratioQCDttbar21.Add(ratio21,-1)
        ratioQCDttbar21.Divide(ratio21)


        #### Now make for 2D trigger corrections.

        ratio112D = hh112D.Clone(doubleb+'ratio112D'+y)
        ratio112D.SetTitle(doubleb+'ratio112D'+y)
        for xb in range(1,hh112D.GetNbinsX()+1):
            for yb in range(1,hh112D.GetNbinsY()+1):
                b = hh112D.GetBin(xb,yb)
                ratio112D.SetBinContent(b,h11D2D.GetEfficiency(b)/h11Q2D.GetEfficiency(b))
                ratio112D.SetBinError(b,max([h11D2D.GetEfficiencyErrorUp(b),h11Q2D.GetEfficiencyErrorUp(b),h11D2D.GetEfficiencyErrorLow(b),h11Q2D.GetEfficiencyErrorLow(b)]))
        
        ratio212D = hh212D.Clone(doubleb+'ratio212D'+y)
        ratio212D.SetTitle(doubleb+'ratio212D'+y)
        for xb in range(1,hh212D.GetNbinsX()+1):
            for yb in range(1,hh212D.GetNbinsX()+1):
                b = hh212D.GetBin(xb,yb)
                ratio212D.SetBinContent(b,h21D2D.GetEfficiency(b)/h21Q2D.GetEfficiency(b))
                ratio212D.SetBinError(b,max([h21D2D.GetEfficiencyErrorUp(b),h21Q2D.GetEfficiencyErrorUp(b),h21D2D.GetEfficiencyErrorLow(b),h21Q2D.GetEfficiencyErrorLow(b)]))


        outfile.cd()
        # h11.Write()
        # h21.Write()
        ratio11.Write()
        ratio21.Write()

        ratio11TT.Write()
        ratio21TT.Write()

        ratioQCDttbar11.Write()
        ratioQCDttbar21.Write()

        h11D.Write()
        hh11.Write()
        h21D.Write()
        hh21.Write()

        h11Q.Write()
        hh11Q.Write()
        h21Q.Write()
        hh21Q.Write()

        h11tt.Write()
        hh11tt.Write()
        h21tt.Write()
        hh21tt.Write()

        hh112D.Write()
        hh212D.Write()
        hh11Q2D.Write()
        hh21Q2D.Write()
        hh11tt2D.Write()
        hh21tt2D.Write()

        ratio112D.Write()
        ratio212D.Write()

outfile.Close()
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


        ratio11 = hh11.Clone(doubleb+'ratio11'+y)
        ratio11.SetTitle(doubleb+'ratio11'+y)
        ratio11.Divide(hh11,hh11Q,1,1,"B")

        ratio11TT = hh11.Clone(doubleb+'ratio11ttbar'+y)
        ratio11TT.SetTitle(doubleb+'ratio11ttbar'+y)
        ratio11TT.Divide(hh11,hh11tt,1,1,"B")

        ratioQCDttbar11 = ratio11.Clone(doubleb+'ratio11QCDtoTTbar'+y)
        ratioQCDttbar11.SetTitle(doubleb+'ratio11QCDtoTTbar'+y)
        ratioQCDttbar11.Add(ratio11TT,-1)

        ratio21 = hh21.Clone(doubleb+'ratio21'+y)
        ratio21.SetTitle(doubleb+'ratio21'+y)
        ratio21.Divide(hh21,hh21Q,1,1,"B")

        ratio21TT = hh21.Clone(doubleb+'ratio21ttbar'+y)
        ratio21TT.SetTitle(doubleb+'ratio21ttbar'+y)
        ratio21TT.Divide(hh21,hh21tt,1,1,"B")

        ratioQCDttbar21 = ratio21.Clone(doubleb+'ratio21QCDtoTTbar'+y)
        ratioQCDttbar21.SetTitle(doubleb+'ratio21QCDtoTTbar'+y)
        ratioQCDttbar21.Add(ratio21TT,-1)

       
        h11D = ROOT.TEfficiency(hnum, hden)

        h21D = ROOT.TEfficiency(hnum21, hden21)

        h11Q = ROOT.TEfficiency(hnumQ, hdenQ)

        h21Q = ROOT.TEfficiency(hnum21Q, hden21Q)

        h11tt = ROOT.TEfficiency(hnumtt, hdentt)

        h21tt = ROOT.TEfficiency(hnum21tt, hden21tt)

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

outfile.Close()
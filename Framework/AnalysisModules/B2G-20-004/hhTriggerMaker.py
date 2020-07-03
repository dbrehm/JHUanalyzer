import ROOT
import subprocess

outfile = ROOT.TFile.Open('TriggerWeights.root','RECREATE')
qcds = ['QCDHT700','QCDHT1000','QCDHT1500','QCDHT2000']
for y in ['16','17','18']:
    if y == '16': datas = ['dataB2','dataC','dataD','dataE','dataF','dataG','dataH']
    elif y == '17': datas = ['dataB','dataC','dataD','dataE','dataF']
    elif y == '18': datas = ['dataA','dataB','dataC','dataD']

    for doubleb in ['btagHbb','deepTagMD_HbbvsQCD']:#,'deepTagMD_ZHbbvsQCD','btagDDBvL']:
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

        hnum = infile.Get('hnum') 
        hden = infile.Get('hden')

        hnum21 = infile.Get('hnum21') 
        hden21 = infile.Get('hden21')

        hnumQ = infileQ.Get('hnum') 
        hdenQ = infileQ.Get('hden')

        hnum21Q = infileQ.Get('hnum21') 
        hden21Q = infileQ.Get('hden21')   

        hh11 = hnum.Clone(doubleb+'tight'+y)
        hh11.Divide(hden)

        hh11Q = hnumQ.Clone(doubleb+'tight'+y)
        hh11Q.Divide(hdenQ)


        hh21 = hnum21.Clone(doubleb+'21'+y)
        hh21.Divide(hden21)

        hh21Q = hnum21Q.Clone(doubleb+'21'+y)
        hh21Q.Divide(hden21Q)

        hh11.Divide(hh11Q)
        hh21.Divide(hh21Q)
       
        h11D = ROOT.TEfficiency(hnum, hden)

        h21D = ROOT.TEfficiency(hnum21, hden21)

        h11Q = ROOT.TEfficiency(hnumQ, hdenQ)

        h21Q = ROOT.TEfficiency(hnum21Q, hden21Q)

        h11 = ROOT.TEfficiency(hh11, hh11Q)

        h21 = ROOT.TEfficiency(hh21, hh21Q)

        h11.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h11.SetName(doubleb+"11"+y+"Effplot")
        h11.SetTitle(doubleb+"11"+y+"Effplot"";m_reduced;Efficiency")

        h21.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h21.SetName(doubleb+'21'+y+"Effplot")
        h21.SetTitle(doubleb+'21'+y+"Effplot"";m_reduced;Efficiency")

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


        outfile.cd()
        h11.Write()
        h21.Write()

        h11D.Write()
        hh11.Write()
        h21D.Write()
        hh21.Write()

        h11Q.Write()
        hh11Q.Write()
        h21Q.Write()
        hh21Q.Write()

outfile.Close()
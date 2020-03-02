import ROOT
import subprocess

outfile = ROOT.TFile.Open('TriggerWeights.root','RECREATE')

for y in ['16','17','18']:
    if y == '16': datas = ['dataB2','dataC','dataD','dataE','dataF','dataG','dataH']
    elif y == '17': datas = ['dataB','dataC','dataD','dataE','dataF']
    elif y == '18': datas = ['dataA','dataB','dataC1','dataC2','dataD']

    for doubleb in ['btagHbb','deepTagMD_HbbvsQCD']:#,'deepTagMD_ZHbbvsQCD','btagDDBvL']:
        new_file = 'HHtrigger'+y+'_data_'+doubleb+'.root'
        hadd_string = 'hadd '+new_file
        print 'Executing: rm ' + new_file
        subprocess.call(['rm '+new_file],shell=True) 
        for d in datas:
            hadd_string += ' HHtrigger'+y+'_'+d+'_'+doubleb+'.root'
            
        print 'Executing: ' + hadd_string
        subprocess.call([hadd_string],shell=True)

        infile = ROOT.TFile.Open('HHtrigger'+y+'_data_'+doubleb+'.root')

        hnum = infile.Get('hnum') 
        hden = infile.Get('hden')
        # hnumLoose = infile.Get('hnumLoose') 
        # hdenLoose = infile.Get('hdenLoose')
        # hnumCR = infile.Get('hnumCR') 
        # hdenCR = infile.Get('hdenCR')
        hnum21 = infile.Get('hnum21') 
        hden21 = infile.Get('hden21')  
       
        h11 = ROOT.TEfficiency(hnum, hden)
        # hloose = ROOT.TEfficiency(hnumLoose, hdenLoose)
        # hCR = ROOT.TEfficiency(hnumCR, hdenCR)
        h21 = ROOT.TEfficiency(hnum21, hden21)

        h11.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h11.SetName(doubleb+"11"+y+"Effplot")
        h11.SetTitle(doubleb+"11"+y+"Effplot"";m_reduced;Efficiency")
        # hloose.SetStatisticOption(ROOT.TEfficiency.kFCP)
        # hloose.SetName(doubleb+'loose'+y)
        # hloose.SetTitle(doubleb+'loose'+y+";m_jj;Efficiency")
        # hCR.SetStatisticOption(ROOT.TEfficiency.kFCP)
        # hCR.SetName(doubleb+'CR'+y)
        # hCR.SetTitle(doubleb+'CR'+y+";m_jj;Efficiency")
        h21.SetStatisticOption(ROOT.TEfficiency.kFCP)
        h21.SetName(doubleb+'21'+y+"Effplot")
        h21.SetTitle(doubleb+'21'+y+"Effplot"";m_reduced;Efficiency")

        hh11 = hnum.Clone(doubleb+'tight'+y)
        hh11.Divide(hden)

        # hloose = hnumLoose.Clone(doubleb+'loose'+y)
        # hloose.Divide(hdenLoose)

        hh21 = hnum21.Clone(doubleb+'21'+y)
        hh21.Divide(hden21)

        # htight.SetMaximum(1.1)
        # hloose.SetMaximum(1.1)
        # h21.SetMaximum(1.1)
        # htight.SetMinimum(0)
        # hloose.SetMinimum(0)
        # h21.SetMinimum(0)

        outfile.cd()
        h11.Write()
        hh11.Write()
        # hloose.Write()
        # hCR.Write()
        h21.Write()
        hh21.Write()

outfile.Close()
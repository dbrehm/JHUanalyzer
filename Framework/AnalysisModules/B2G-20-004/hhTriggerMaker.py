import ROOT
import subprocess, math

def DivEff(eff1,eff2,year,reg):
    h_for_binning = eff1.GetTotalHistogram()
    x_nbins = h_for_binning.GetNbinsX()
    x_low   = h_for_binning.GetXaxis().GetXmin()
    x_high  = h_for_binning.GetXaxis().GetXmax()
    y_nbins = h_for_binning.GetNbinsY()
    y_low   = h_for_binning.GetYaxis().GetXmin()
    y_high  = h_for_binning.GetYaxis().GetXmax()

    h = ROOT.TH2F('DivEff'+reg+year,'',x_nbins,x_low,x_high,y_nbins,y_low,y_high)
    h.SetTitle(reg+" 20"+year+" 2D Efficiency Nominal Ratio Data/QCD;m_h;m_reduced;SF")
    hup = h.Clone('DivEffUp'+reg+year)
    hup.SetTitle(reg+" 20"+year+" 2D Efficiency Up Ratio Data/QCD;m_h;m_reduced;SF")
    hdown = h.Clone('DivEffDown'+reg+year)
    hdown.SetTitle(reg+" 20"+year+" 2D Efficiency Down Ratio Data/QCD;m_h;m_reduced;SF")

    for ix in range(1,x_nbins+1):
        for iy in range(1,y_nbins+1):
            ibin = eff1.GetGlobalBin(ix,iy)
            # print ('%s %.2f %.2f'%(ibin,eff1.GetEfficiency(ibin),eff2.GetEfficiency(ibin)))
            if eff2.GetEfficiency(ibin) == 0 or eff1.GetEfficiency(ibin) == 0:
                div = 0
                div_err_up = 0
                div_err_down = 0
            else:
                div = eff1.GetEfficiency(ibin)/eff2.GetEfficiency(ibin)
                div_err_up = div*math.sqrt(eff1.GetEfficiencyErrorUp(ibin)/eff1.GetEfficiency(ibin)+eff2.GetEfficiencyErrorUp(ibin)/eff2.GetEfficiency(ibin))
                div_err_down = div*math.sqrt(eff1.GetEfficiencyErrorLow(ibin)/eff1.GetEfficiency(ibin)+eff2.GetEfficiencyErrorLow(ibin)/eff2.GetEfficiency(ibin))

            h.SetBinContent(ibin,div)
            hup.SetBinContent(ibin,div+div_err_up)
            hdown.SetBinContent(ibin,div-div_err_down)

    h.SetMaximum(1.05)
    hup.SetMaximum(1.05)
    hdown.SetMaximum(1.05)

    return h,hup,hdown

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

        fdata = ROOT.TFile.Open('HHtrigger'+y+'_data_'+doubleb+'.root')
        fqcd = ROOT.TFile.Open('HHtrigger'+y+'_QCD_'+doubleb+'.root')
        infileTT = ROOT.TFile.Open('HHtrigger'+y+'_ttbar_'+doubleb+'.root')

        hdata_num = fdata.Get('hnum2D')
        hdata_den = fdata.Get('hden2D')
        hqcd_num = fqcd.Get('hnum2D')
        hqcd_den = fqcd.Get('hden2D')
        httbar_num = fqcd.Get('hnum2D')
        httbar_den = fqcd.Get('hden2D')

        hdata_num21 = fdata.Get('hnum212D')
        hdata_den21 = fdata.Get('hden212D')
        hqcd_num21 = fqcd.Get('hnum212D')
        hqcd_den21 = fqcd.Get('hden212D')

        eff_data = ROOT.TEfficiency(hdata_num,hdata_den)
        eff_qcd = ROOT.TEfficiency(hqcd_num,hqcd_den)
        eff_ttbar = ROOT.TEfficiency(httbar_num,httbar_den)
                
        eff_data.SetStatisticOption(ROOT.TEfficiency.kFCP)
        eff_qcd.SetStatisticOption(ROOT.TEfficiency.kFCP)
        eff_ttbar.SetStatisticOption(ROOT.TEfficiency.kFCP)


        eff_data21 = ROOT.TEfficiency(hdata_num21,hdata_den21)
        eff_qcd21 = ROOT.TEfficiency(hqcd_num21,hqcd_den21)

        eff_data21.SetStatisticOption(ROOT.TEfficiency.kFCP)
        eff_qcd21.SetStatisticOption(ROOT.TEfficiency.kFCP)

        h,hup,hdown = DivEff(eff_data,eff_qcd,y,'FullyMerged')
        h21,hup21,hdown21 = DivEff(eff_data21,eff_qcd21,y,'SemiResolved')

        eff_data.SetName(doubleb+"11"+y+"Effplot_Data_2D")
        eff_data.SetTitle(doubleb+"11"+y+"Efficiency-Data-2D;m_h;m_reduced;Efficiency")

        eff_data21.SetName(doubleb+'21'+y+"Effplot_Data_2D")
        eff_data21.SetTitle(doubleb+'21'+y+"Effplot-Data-2D;m_h;m_reduced;Efficiency")

        eff_qcd.SetName(doubleb+"11"+y+"Effplot_QCD_2D")
        eff_qcd.SetTitle(doubleb+"11"+y+"Efficiency-QCD-2D;m_h;m_reduced;Efficiency")

        eff_qcd21.SetName(doubleb+'21'+y+"Effplot_QCD_2D")
        eff_qcd21.SetTitle(doubleb+'21'+y+"Efficiency-QCD-2D;m_h;m_reduced;Efficiency")

        eff_ttbar.SetName(doubleb+"11"+y+"Effplot_ttbar_2D")
        eff_ttbar.SetTitle(doubleb+"11"+y+"Efficiency-ttbar-2D;m_h;m_reduced;Efficiency")

        outfile.cd()

        h.Write()
        hup.Write()
        hdown.Write()

        h21.Write()
        hup21.Write()
        hdown21.Write()

        eff_data.Write()
        eff_qcd.Write()
        eff_ttbar.Write()

        eff_data21.Write()
        eff_qcd21.Write()

        c = ROOT.TCanvas('c','c',1200,700)
        c.Divide(3,2)
        c.cd(1)
        eff_data.Draw('lego')
        c.cd(2)
        eff_qcd.Draw('lego')
        # c.cd(3)
        # eff_ttbar.Draw('lego')
        c.cd(4)
        h.Draw('colz')
        c.cd(5)
        hup.Draw('colz')
        c.cd(6)
        hdown.Draw('colz')

        c.SaveAs('20'+y+'triggerMaps.png')

outfile.Close()
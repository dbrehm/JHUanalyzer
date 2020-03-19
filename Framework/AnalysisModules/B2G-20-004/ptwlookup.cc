#include <cmath>
#include <stdbool.h>
using namespace ROOT::VecOps;
using rvec_i = const RVec<int> &;
using rvec_d = const RVec<double> &;

namespace analyzer {
    std::vector<float> PTWLookup(int nGenJet, rvec_i GPpdgId, rvec_i GPstatusFlags, rvec_d GPpt, rvec_d GPeta, rvec_d GPphi, rvec_d GPmass, ROOT::Math::PtEtaPhiMVector jet0, ROOT::Math::PtEtaPhiMVector jet1 ){

        std::vector<float> out;

        float genTpt = 0;
        float genTBpt = 0;
        float wTPt, wTbarPt, wTPtAlphaup, wTbarPtAlphaup, wTPtAlphadown, wTbarPtAlphadown ,wTPtBetaup, wTbarPtBetaup, wTPtBetadown, wTbarPtBetadown; 
        bool pair_exists = 0.0;

        float alpha = 0.0615;
        float beta = 0.0005;

        // For all gen particles
        for (int i =0; i < nGenJet; i++){
            if ((GPpdgId[i] == -6) && (GPstatusFlags[i] & (1 << 13))){ 
                ROOT::Math::PtEtaPhiMVector antitop_lv(GPpt[i],GPeta[i],GPphi[i],GPmass[i]);
                if ((ROOT::Math::VectorUtil::DeltaR(antitop_lv,jet0) <0.8) || (ROOT::Math::VectorUtil::DeltaR(antitop_lv,jet1)) <0.8){
                    genTBpt = GPpt[i];
                }
            }else if ((GPpdgId[i] == 6) && (GPstatusFlags[i] & (1 << 13))){ 
                ROOT::Math::PtEtaPhiMVector top_lv(GPpt[i],GPeta[i],GPphi[i],GPmass[i]);
                if ((ROOT::Math::VectorUtil::DeltaR(top_lv,jet0) <0.8) || (ROOT::Math::VectorUtil::DeltaR(top_lv,jet1)) <0.8){
                    genTpt = GPpt[i];
                }
            }
        }

        if ((genTpt == 0) || (genTBpt == 0)){
            pair_exists = 0.0;
        }else{ 
            pair_exists = 1.0;
        }
        
        if (genTpt == 0){ 
            wTPt = 1.0;
        }else{
            wTPt = exp(alpha-beta*genTpt);
            wTPtAlphaup = exp(2*alpha-beta*genTpt);
            wTPtAlphadown = exp(0.5*alpha-beta*genTpt);
            wTPtBetaup = exp(alpha-2*beta*genTpt);
            wTPtBetadown = exp(alpha-0.5*beta*genTpt);
        }

        if (genTBpt == 0){ 
            wTbarPt = 1.0;
        }else{
            wTbarPt = exp(alpha-beta*genTBpt);
            wTbarPtAlphaup = exp(2*alpha-beta*genTpt);
            wTbarPtAlphadown = exp(0.5*alpha-beta*genTpt);
            wTbarPtBetaup = exp(alpha-2*beta*genTpt);
            wTbarPtBetadown = exp(alpha-0.5*beta*genTpt);
        }

        out.push_back(sqrt(wTPt*wTbarPt));
        /// Here we are making varying shapes for up and down on Alpha and Beta
        out.push_back(sqrt(wTPt*wTbarPt));
        // out.push_back(2.0*sqrt(wTPt*wTbarPt));
        // out.push_back(0.5*sqrt(wTPt*wTbarPt));
        out.push_back(sqrt(wTPtAlphaup*wTbarPt));
        out.push_back(sqrt(wTPtAlphadown*wTbarPt));
        out.push_back(sqrt(wTPtBetaup*wTbarPt));
        out.push_back(sqrt(wTPtBetadown*wTbarPt));

        out.push_back(sqrt(wTPt*wTbarPtAlphaup));
        out.push_back(sqrt(wTPt*wTbarPtAlphadown));
        out.push_back(sqrt(wTPt*wTbarPtBetaup));
        out.push_back(sqrt(wTPt*wTbarPtBetadown));
	    
        out.push_back(pair_exists);
        return out;
    }
}

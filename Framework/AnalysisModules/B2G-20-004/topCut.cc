#define _USE_MATH_DEFINES

#include <cmath>
#include "ROOT/RVec.hxx"
using namespace ROOT::VecOps;
using rvec_f = const RVec<float> &;
//return boolean which checks to see if a third ak4 jet, when combined with the 
//two ak4 jets from Hemispherizem, could have come from a top quark
namespace analyzer {
     RVec<float> topCut(int first, int second, rvec_f Jpt, rvec_f Jeta, rvec_f Jphi, rvec_f Jmass, unsigned int Jnjets){
        RVec<float> out;
        float deltaR = -1.0;
        ROOT::Math::PtEtaPhiMVector v1(Jpt[first],Jeta[first],Jphi[first],Jmass[first]);
        ROOT::Math::PtEtaPhiMVector v2(Jpt[second],Jeta[second],Jphi[second],Jmass[second]);
        float Mass = 0.0;
        for(int i = 0; i < Jnjets; i++){
            if (i == first || i == second){
                continue;
            }
            ROOT::Math::PtEtaPhiMVector test(Jpt[i],Jeta[i],Jphi[i],Jmass[i]);
            float deltaR1 = ROOT::Math::VectorUtil::DeltaR(v1,test);
            float deltaR2 = ROOT::Math::VectorUtil::DeltaR(v2,test);
            // float deltaR1 = sqrt(pow(v1.Eta()-test.Eta(),2)+pow(v1.Phi()-test.Phi(),2));
            // float deltaR2 = sqrt(pow(v2.Eta()-test.Eta(),2)+pow(v2.Phi()-test.Phi(),2));
            // cout << "First index = " << first << " Second index = " << second << "third index = " << i << " mass of 3 jets = " << testMass << endl;
            float deltaPhi1 = ROOT::Math::VectorUtil::DeltaPhi(v1,test);
            float deltaPhi2 = ROOT::Math::VectorUtil::DeltaPhi(v2,test);
            if ((deltaPhi1 < M_PI_2 ) && (deltaPhi2 < M_PI_2 )){
                // cout << "Jets in same hemisphere" << endl;
                if (deltaR == -1.0){
                    deltaR = std::min(deltaR1,deltaR2);
                    Mass = (v1+v2+test).M();
                }
                else if (deltaR  > std::min(deltaR1,deltaR2)){
                    deltaR = std::min(deltaR1,deltaR2);
                    Mass = (v1+v2+test).M();
                }
            }
        }
        
        out.emplace_back(Mass);
        out.emplace_back(deltaR);
        return out;
     }
}

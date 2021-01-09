//   MUST MAKE TRIGGER WEIGHTS BEFORE USE!!!

#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<float> TriggerLookup(float varx, float vary, TH2F* TRPnom, TH2F* TRPup, TH2F* TRPdown){
        
        
        float Weight = 1.0;
        float Weightup = 1.0;
        float Weightdown = 1.0;

        std::vector<float> out;

        if (vary < 2000){
            int bin0 = TRPnom->FindBin(varx,vary);
            Weight = TRPnom->GetBinContent(bin0);
            Weightup = TRPup->GetBinContent(bin0);
            Weightdown = TRPdown->GetBinContent(bin0);
        }
        
        // cout << "Nominal is : " << Weight << " error up is: " << Weightup << " error down is: "<< Weightdown << " m_h is: " << varx << " m_red is: " << vary << " " << endl;
        out.push_back(Weight);
        out.push_back(Weightup);
        out.push_back(Weightdown);
        return out;
    }
}
//   MUST MAKE TRIGGER WEIGHTS BEFORE USE!!!

#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<double> TriggerLookup(float varx, float vary, TH2D* TRP){
        double Weight = 1.0;
        double Weightup = 1.0;
        double Weightdown = 1.0;

        std::vector<double> out;

        int bin0 = TRP->GetBin(varx,vary);
        double error = TRP->GetBinError(bin0);
        // double errorDown = TRP->GetBinError(bin0);
        double jetTriggerWeight = TRP->GetBinContent(bin0);

        // cout << "NOT fully efficient" << endl;
        // Check that we're not in an empty bin in the fully efficient region
        if (jetTriggerWeight == 0.0){
            if ((TRP->GetBinContent(bin0-1) == 1.0) && (TRP->GetBinContent(bin0+1) == 1.0)){
                jetTriggerWeight = 1.0;
                Weight = 1.0;
            }else if (((TRP->GetBinContent(bin0-1) > 0) || (TRP->GetBinContent(bin0+1) > 0))){
                cout << "NOT fully efficient and jetTriggerWeight = 0. " << endl;
                jetTriggerWeight = (TRP->GetBinContent(bin0-1)+TRP->GetBinContent(bin0+1))/2.0;
                Weight = (TRP->GetBinContent(bin0-1)+TRP->GetBinContent(bin0+1))/2.0;
            }else if (vary > 1200){
                cout << "Trigger weight forced to 1. " << endl;
                jetTriggerWeight = 1.0;
                Weight = 1.0;
            }else{
                cout << "Weight still 0. " << endl;
                Weight = jetTriggerWeight;
            }
        }else if (jetTriggerWeight < 0.0){
            Weight = 0.0;
        }else if (0.0 <= jetTriggerWeight){
            Weight = jetTriggerWeight;
        }

        double deltaTriggerEff = 0.05*(1.0-jetTriggerWeight);

        double one = 1.0;
        double zero = 0.0;

        double correction = std::max(deltaTriggerEff,error);
        
        Weightup = (jetTriggerWeight + correction);
        Weightdown = abs(jetTriggerWeight - correction);
        
        cout << "Nominal is : " << Weight << " error up is: " << Weightup << " error down is: "<< Weightdown << " m_h is: " << varx << " m_red is: " << vary << " " << endl;
        out.push_back(Weight);
        out.push_back(Weightup);
        out.push_back(Weightdown);
        return out;
    }
}
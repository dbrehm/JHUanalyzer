//   MUST MAKE TRIGGER WEIGHTS BEFORE USE!!!

#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<float> TriggerLookup(float var, TEfficiency* TRP ){
        float Weight = 1;
        float Weightup = 1;
        float Weightdown = 1;

        std::vector<float> out;

        if (var < 4000.0){
            int bin0 = TRP->GetBin(var);
            cout << "Got bin." << endl;
            float jetTriggerWeight = TRP->GetEfficiency(bin0);
            cout << "Got weight." << endl;
            // Check that we're not in an empty bin in the fully efficient region
            if (jetTriggerWeight == 0){
                if ((TRP->GetEfficiency(bin0-1) == 1.0) && (TRP->GetEfficiency(bin0+1) == 1.0)){
                    jetTriggerWeight = 1.0;
                }else if (((TRP->GetEfficiency(bin0-1) > 0) || (TRP->GetEfficiency(bin0+1) > 0))){
                    jetTriggerWeight = (TRP->GetEfficiency(bin0-1)+TRP->GetEfficiency(bin0+1))/2.0;
                }
            }
            cout << "Checked for fully efficient region." << endl;

            Weight = jetTriggerWeight;
            float deltaTriggerEff  = 0.5*(1.0-jetTriggerWeight);
            float one = 1.0;
            float zero = 0.0;
            Weightup = std::min(one,(jetTriggerWeight + sqrt(pow((deltaTriggerEff),2) + pow(TRP->GetEfficiencyErrorUp(bin0),2) ))) ;
            Weightdown = std::max(zero,(jetTriggerWeight - sqrt(pow((deltaTriggerEff),2) + pow(TRP->GetEfficiencyErrorLow(bin0),2) )));
            cout << "Weights made." << endl;

        }    
        out.push_back(Weight);
        out.push_back(Weightup);
        out.push_back(Weightdown);
        return out;
    }
}
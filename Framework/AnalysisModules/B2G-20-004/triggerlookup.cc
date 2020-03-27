//   MUST MAKE TRIGGER WEIGHTS BEFORE USE!!!

#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<float> TriggerLookup(float var, TH1D* TRP, TEfficiency* TEff ){
        float Weight = 1;
        float Weightup = 1;
        float Weightdown = 1;

        std::vector<float> out;

        if (var < 4000.0){
            int bin0 = TRP->FindBin(var); 
            float jetTriggerWeight = TEff->GetEfficiency(bin0);
            // Check that we're not in an empty bin in the fully efficient region
            if (jetTriggerWeight == 0){
                if ((TEff->GetEfficiency(bin0-1) == 1.0) && (TEff->GetEfficiency(bin0+1) == 1.0)){
                    jetTriggerWeight = 1.0;
                }else if (((TEff->GetEfficiency(bin0-1) > 0) || (TEff->GetEfficiency(bin0+1) > 0))){
                    jetTriggerWeight = (TEff->GetEfficiency(bin0-1)+TEff->GetEfficiency(bin0+1))/2.0;
                }
            }

            Weight = jetTriggerWeight;
            float deltaTriggerEff  = 0.5*(1.0-jetTriggerWeight);
            float errorUp = TEff->GetEfficiencyErrorUp(bin0);
            float errorDown = TEff->GetEfficiencyErrorLow(bin0);
            float one = 1.0;
            float zero = 0.0;
            Weightup = std::min(one,(jetTriggerWeight + sqrt(pow((deltaTriggerEff),2) + pow(errorUp,2) ))) ;
            Weightdown = std::max(zero,(jetTriggerWeight - sqrt(pow((deltaTriggerEff),2) + pow(errorDown,2) )));

        }    
        out.push_back(Weight);
        out.push_back(Weightup);
        out.push_back(Weightdown);
        return out;
    }
}
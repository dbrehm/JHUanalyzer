//   MUST MAKE TRIGGER WEIGHTS BEFORE USE!!!

#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<double> TriggerLookup(float var, TEfficiency* TEff){
        double Weight = 1.0;
        double Weightup = 1.0;
        double Weightdown = 1.0;

        std::vector<double> out;

        if (var < 2000.0){
            int bin0 = TEff->GetBin(var); 
            double jetTriggerWeight = TEff->GetEfficiency(bin0);
            // Check that we're not in an empty bin in the fully efficient region
            if (jetTriggerWeight == 0){
                if ((TEff->GetEfficiency(bin0-1) == 1.0) && (TEff->GetEfficiency(bin0+1) == 1.0)){
                    jetTriggerWeight = 1.0;
                }else if (((TEff->GetEfficiency(bin0-1) > 0) || (TEff->GetEfficiency(bin0+1) > 0))){
                    jetTriggerWeight = (TEff->GetEfficiency(bin0-1)+TEff->GetEfficiency(bin0+1))/2.0;
                }
            }

            if (jetTriggerWeight < 0){
                Weight = 0;
            }else if (0 < jetTriggerWeight){
                Weight = jetTriggerWeight;
            }

            double deltaTriggerEff = 0.05*(1.0-jetTriggerWeight);
            double errorUp = TEff->GetEfficiencyErrorUp(bin0);
            double errorDown = TEff->GetEfficiencyErrorLow(bin0);
            double one = 1.0;
            double zero = 0.0;

            Weightup = (jetTriggerWeight + std::max(deltaTriggerEff,errorUp));

            Weightdown = std::max(zero,(jetTriggerWeight - std::max(deltaTriggerEff,errorDown)));
        

        }    
        //cout << "Trigger eff is : " << Weight << " error up is: " << Weightup << " error down is: "<< Weightdown << endl;
        out.push_back(Weight);
        out.push_back(Weightup);
        out.push_back(Weightdown);
        return out;
    }
}
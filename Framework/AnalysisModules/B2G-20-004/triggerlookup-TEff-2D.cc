//   MUST MAKE TRIGGER WEIGHTS BEFORE USE!!!

#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<double> TriggerLookup(float varx, float vary, TEfficiency* TEffD,TEfficiency* TEffQ){
        double Weight = 1.0;
        double Weightup = 1.0;
        double Weightdown = 1.0;

        std::vector<double> out;

        int bin0 = TEffD->GetGlobalBin(varx,vary);

        double jetTriggerWeight_data = TEffD->GetEfficiency(bin0);
        double errorUp_data = TEffD->GetEfficiencyErrorUp(bin0);
        double errorDown_data = TEffD->GetEfficiencyErrorLow(bin0);

        double jetTriggerWeight_qcd = TEffQ->GetEfficiency(bin0);
        double errorUp_qcd = TEffQ->GetEfficiencyErrorUp(bin0);
        double errorDown_qcd = TEffQ->GetEfficiencyErrorLow(bin0);

        if (vary < 2000.0){
            // Check that we're not in an empty bin in the fully efficient region
            if (jetTriggerWeight_data == 0){
                if ((TEffD->GetEfficiency(bin0-1) == 1.0) && (TEffD->GetEfficiency(bin0+1) == 1.0)){
                    jetTriggerWeight_data = 1.0;
                }else if (((TEffD->GetEfficiency(bin0-1) > 0) || (TEffD->GetEfficiency(bin0+1) > 0))){
                    jetTriggerWeight_data = (TEffD->GetEfficiency(bin0-1)+TEffD->GetEfficiency(bin0+1))/2.0;
                }
            }

            double jetTriggerWeight = jetTriggerWeight_data/jetTriggerWeight_qcd;

            if (jetTriggerWeight < 0){
                Weight = 0;
            }else if (0 < jetTriggerWeight){
                Weight = jetTriggerWeight;
            }

            double deltaTriggerEff = 0.05*(1.0-jetTriggerWeight);

            double one = 1.0;
            double zero = 0.0;

            Weightup = (jetTriggerWeight + std::max(deltaTriggerEff,std::max(errorUp_data,errorUp_qcd)));

            Weightdown = std::max(zero,(jetTriggerWeight - std::max(deltaTriggerEff,std::max(errorDown_data,errorDown_qcd))));
        

        }    
        //cout << "Trigger eff is : " << Weight << " error up is: " << Weightup << " error down is: "<< Weightdown << endl;
        out.push_back(Weight);
        out.push_back(Weightup);
        out.push_back(Weightdown);
        return out;
    }
}
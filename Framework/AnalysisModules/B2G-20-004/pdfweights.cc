#include <cmath>
#include <string>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<float> PDFweight(RVec<Float_t> pdfbranch, const std::string& year) {
        // [up,down]
        
        std::vector<float> v;
        int size = pdfbranch.size();

        // Only check those weights with weight < 1000
        std::vector<float> pdfs;
        float currentpdf;
        for (size_t i=0; i< size; ++i) {
            currentpdf = pdfbranch[i];
            if (abs(currentpdf)<1000.0){
                pdfs.push_back(currentpdf);
            }
        }

        // If no weights < 1000, return 0
        if (pdfs.size() == 0) {
            v.push_back(0.0);
            v.push_back(0.0);
            return v;
        }

        int npdfs = pdfs.size();

        float weight = 0.0;

        if(year.compare("16") != 0){
            // Computes sqrt of sum of differences squared
            float sumsquares = 0;
            for(size_t i=0; i < npdfs; ++i){
                sumsquares += pow((pdfs[i]-pdfs[0]),2);
            }
            weight = sqrt(sumsquares);

        }else{
            // Get the average of the weights
            float sum = 0.0;
            for (size_t i=0; i<npdfs; ++i) {
                sum += pdfs[i];
            }
            float average = sum / npdfs;

            // Calculate the variance from the average

            for (size_t i=0; i<npdfs; ++i) {
                currentpdf = pdfs[i];
                float old_weight = weight;
                weight = old_weight + pow((currentpdf-average),2);
            }

        }

        v.push_back(std::min(13.0,1.0+sqrt(weight/npdfs)));
        v.push_back(std::max(-13.0,1.0-sqrt(weight/npdfs)));


        return v;
    }
}
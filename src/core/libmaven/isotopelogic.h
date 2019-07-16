#ifndef ISOTOPELOGIC_H
#define ISOTOPELOGIC_H

#include "mzMassCalculator.h"
#include "standardincludes.h"

class mzLink;
class Scan;
class PeakGroup;
class Compound;

class IsotopeLogic {
public:
	IsotopeLogic();
	void userChangedFormula();

	string _formula;
	float _charge;
	vector<mzLink> links;
	Scan* _scan;
	PeakGroup* _group;
	Compound* _compound;
	MassCalculator mcalc;
	Compound* tempCompound;

private:
};

#endif // ISOTOPELOGIC_H
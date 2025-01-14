#include "constants.h"
#include "datastructures/adduct.h"
#include "mzMassCalculator.h"
#include "mzUtils.h"

Adduct::Adduct()
{
    this->_name = "";
    this->_nmol = 0;
    this->_charge = 0;
    this->_mass = 0;
}

Adduct::Adduct(string name, int nmol, int charge, float mass)
{
    this->_name = name;
    this->_nmol = nmol;
    this->_charge = charge;
    this->_mass = mass;
}

Adduct::Adduct(const Adduct& a)
{
    this->_name = a._name;
    this->_nmol = a._nmol;
    this->_charge = a._charge;
    this->_mass =  a._mass;
}

bool Adduct::operator==(const Adduct& other)
{
    return (_name == other._name
            && _nmol == other._nmol
            && _charge == other._charge
            && mzUtils::almostEqual(_mass, other._mass)
            && isParent() == other.isParent());
}

bool Adduct::operator<(const Adduct& other)
{
    if (_charge != other._charge)
        return _charge < other._charge;
    if (_nmol != other._nmol)
        return _nmol < other._nmol;
    return _name < other._name;
}

string Adduct::getName()
{
    return this->_name;
}

int Adduct::getCharge()
{
    return this->_charge;
}

int Adduct::getNmol()
{
    return this->_nmol;
}

float Adduct::getMass()
{
    return this->_mass;
}

bool Adduct::isParent() const
{
    if (abs(_charge) > 1)
        return false;

    if (_nmol > 1)
        return false;

    // limit decimal precision to 7, in order to prevent hydrogen-level masses
    // from being compared at much higher precision
    stringstream ss;
    ss << setprecision(7) << _mass;
    auto adductMass = stof(ss.str());
    ss.str(std::string());
    ss << setprecision(7) << static_cast<float>(PROTON_MASS);
    auto protonMass = stof(ss.str());
    if (mzUtils::almostEqual(abs(adductMass), protonMass)
        || mzUtils::almostEqual(abs(adductMass), 0.0f)) {
        return true;
    }

    return false;
}

float Adduct::computeParentMass(float mz)
{
    return (mz * static_cast<float>(abs(_charge)) - _mass)
           / static_cast<float>(_nmol);
}

float Adduct::computeAdductMz(float parentMass)
{
    if (isParent() && MassCalculator::ionizationType == MassCalculator::EI) {
        MassCalculator massCalc;
        return massCalc.adjustMass(parentMass, _charge);
    }

    return (parentMass * static_cast<float>(_nmol) + _mass)
           / static_cast<float>(abs(_charge));
}

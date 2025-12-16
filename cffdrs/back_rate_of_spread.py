import math
from cffdrs.rate_of_spread import rate_of_spread


def back_rate_of_spread(FUELTYPE, FFMC, BUI, WSV, FMC, SFC, PC, PDF, CC, CBH):
    """
    Back Fire Rate of Spread Calculator

    Calculate the Back Fire Spread Rate. All variables names are laid out in the same manner as Forestry Canada Fire Danger Group (FCFDG) (1992).

    Args:
        FUELTYPE: The Fire Behaviour Prediction FuelType
        FFMC: Fine Fuel Moisture Code
        BUI: Buildup Index
        WSV: Wind Speed Vector
        FMC: Foliar Moisture Content
        SFC: Surface Fuel Consumption
        PC: Percent Conifer
        PDF: Percent Dead Balsam Fir
        CC: Degree of Curing
        CBH: Crown Base Height

    Returns:
        BROS: Back Fire Rate of Spread
    """
    if isinstance(FFMC, list):
        m = [250.0 * 59.5 / 101.0 * (101 - f) / (59.5 + f) for f in FFMC]
        fF = [91.9 * math.exp(-0.1386 * mm) * (1 + (mm**5.31) / 49300000) for mm in m]
        BfW = [math.exp(-0.05039 * w) for w in WSV]
        BISI = [0.208 * b * ff for b, ff in zip(BfW, fF)]
        BROS = rate_of_spread(FUELTYPE, BISI, BUI, FMC, SFC, PC, PDF, CC, CBH)
    else:
        m = 250.0 * 59.5 / 101.0 * (101 - FFMC) / (59.5 + FFMC)
        fF = 91.9 * math.exp(-0.1386 * m) * (1 + (m**5.31) / 49300000)
        BfW = math.exp(-0.05039 * WSV)
        BISI = 0.208 * BfW * fF
        BROS = rate_of_spread(FUELTYPE, BISI, BUI, FMC, SFC, PC, PDF, CC, CBH)
    return BROS
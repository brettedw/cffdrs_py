"""
Initial Spread Index Calculator

Computes the Initial Spread Index from the FWI System. Equations are from Van Wagner (1985)
as listed below, except for the modification for fbp taken from FCFDG (1992).

Equations and FORTRAN program for the Canadian Forest Fire Weather Index System. 1985.
Van Wagner, C.E.; Pickett, T.L. Canadian Forestry Service, Petawawa National Forestry
Institute, Chalk River, Ontario. Forestry Technical Report 33. 18 p.

Forestry Canada Fire Danger Group (FCFDG) (1992). Development and Structure of the
Canadian Forest Fire Behavior Prediction System. Technical Report ST-X-3, Forestry
Canada, Ottawa, Ontario.
"""

from typing import Union, List
import math

# Used in conversion between FFMC and moisture content
FFMC_COEFFICIENT = 250.0 * 59.5 / 101.0


def initial_spread_index(
    ffmc: Union[float, List[float]],
    ws: Union[float, List[float]],
    fbp_mod: bool = False
) -> Union[float, List[float]]:
    """
    Calculate the Initial Spread Index.

    Args:
        ffmc: Fine Fuel Moisture Code
        ws: Wind Speed (km/h)
        fbp_mod: TRUE/FALSE if using the fbp modification at the extreme end

    Returns:
        ISI: Initial Spread Index
    """
    # Eq. 10 - Moisture content
    if isinstance(ffmc, list):
        fm = [FFMC_COEFFICIENT * (101 - f) / (59.5 + f) for f in ffmc]
    else:
        fm = FFMC_COEFFICIENT * (101 - ffmc) / (59.5 + ffmc)

    # Eq. 24 - Wind Effect
    # The modification also takes care of the ISI modification for the fbp functions
    # This modification is Equation 53a in FCFDG (1992)
    if isinstance(ws, list):
        fw = [0.0] * len(ws)
        for i in range(len(ws)):
            if ws[i] >= 40 and fbp_mod:
                fw[i] = 12 * (1 - math.exp(-0.0818 * (ws[i] - 28)))
            else:
                fw[i] = math.exp(0.05039 * ws[i])
    else:
        if ws >= 40 and fbp_mod:
            fw = 12 * (1 - math.exp(-0.0818 * (ws - 28)))
        else:
            fw = math.exp(0.05039 * ws)

    # Eq. 25 - Fine Fuel Moisture
    if isinstance(fm, list):
        ff = [91.9 * math.exp(-0.1386 * m) * (1 + (m ** 5.31) / 49300000) for m in fm]
    else:
        ff = 91.9 * math.exp(-0.1386 * fm) * (1 + (fm ** 5.31) / 49300000)

    # Eq. 26 - Spread Index Equation
    isi = [0.208 * f * w for f, w in zip(ff, fw)] if isinstance(ff, list) else 0.208 * ff * fw
    return isi
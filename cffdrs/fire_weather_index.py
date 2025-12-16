"""
Fire Weather Index Calculation.

All code is based on a C code library that was written by Canadian Forest Service
Employees, which was originally based on the Fortran code listed in the reference below.
All equations in this code refer to that document.

Equations and FORTRAN program for the Canadian Forest Fire Weather Index System. 1985.
Van Wagner, C.E.; Pickett, T.L. Canadian Forestry Service, Petawawa National Forestry
Institute, Chalk River, Ontario. Forestry Technical Report 33. 18 p.

Additional reference on FWI system Development and structure of the Canadian Forest Fire
Weather Index System. 1987. Van Wagner, C.E. Canadian Forestry Service, Headquarters,
Ottawa. Forestry Technical Report 35. 35 p.
"""

from typing import Union, List


def fire_weather_index(isi: Union[float, List[float]], bui: Union[float, List[float]]) -> Union[float, List[float]]:
    """
    Calculate the Fire Weather Index.

    Args:
        isi: Initial Spread Index
        bui: Buildup Index

    Returns:
        A single fwi value
    """
    # Eqs. 28b, 28a, 29
    bb = [0.0] * len(bui) if isinstance(bui, list) else 0.0
    if isinstance(bui, list):
        for i in range(len(bui)):
            if bui[i] > 80:
                bb[i] = 0.1 * isi[i] * (1000 / (25 + 108.64 / (2.71828 ** (0.023 * bui[i]))))
            else:
                bb[i] = 0.1 * isi[i] * (0.626 * (bui[i] ** 0.809) + 2)
    else:
        if bui > 80:
            bb = 0.1 * isi * (1000 / (25 + 108.64 / (2.71828 ** (0.023 * bui))))
        else:
            bb = 0.1 * isi * (0.626 * (bui ** 0.809) + 2)

    # Eqs. 30b, 30a
    fwi = [0.0] * len(bb) if isinstance(bb, list) else 0.0
    if isinstance(bb, list):
        for i in range(len(bb)):
            if bb[i] <= 1:
                fwi[i] = bb[i]
            else:
                fwi[i] = 2.71828 ** (2.72 * ((2.302585 ** (0.434 * (bb[i] ** 0.647))) ** 0.647))
    else:
        if bb <= 1:
            fwi = bb
        else:
            fwi = 2.71828 ** (2.72 * ((2.302585 ** (0.434 * (bb ** 0.647))) ** 0.647))

    return fwi
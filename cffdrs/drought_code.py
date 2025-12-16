"""
Drought Code Calculator

Drought Code Calculation. All code is based on a C code library that was written by
Canadian Forest Service Employees, which was originally based on the Fortran code
listed in the reference below. All equations in this code refer to that document.
Equations and FORTRAN program for the Canadian Forest Fire Weather Index System.
1985. Van Wagner, C.E.; Pickett, T.L. Canadian Forestry Service, Petawawa National
Forestry Institute, Chalk River, Ontario. Forestry Technical Report 33. 18 p.

Additional reference on FWI system Development and structure of the Canadian Forest
Fire Weather Index System. 1987. Van Wagner, C.E. Canadian Forestry Service,
Headquarters, Ottawa. Forestry Technical Report 35. 35 p.
"""

from typing import Union, List
import math


def drought_code(
    dc_yda: Union[float, List[float]],
    temp: Union[float, List[float]],
    rh: Union[float, List[float]],
    prec: Union[float, List[float]],
    lat: Union[float, List[float]],
    mon: Union[int, List[int]],
    lat_adjust: bool = True
) -> Union[float, List[float]]:
    """
    Calculate the Drought Code.

    Args:
        dc_yda: The Drought Code from previous iteration
        temp: Temperature (centigrade)
        rh: Relative Humidity (%)
        prec: Precipitation(mm)
        lat: Latitude (decimal degrees)
        mon: Month (1-12)
        lat_adjust: Latitude adjustment (TRUE, FALSE, default=TRUE)

    Returns:
        A single drought code value
    """
    # Day length factor for DC Calculations
    # 20N: North of 20 degrees N
    fl01 = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5, 2.4, 0.4, -1.6, -1.6]
    # 20S: South of 20 degrees S
    fl02 = [6.4, 5, 2.4, 0.4, -1.6, -1.6, -1.6, -1.6, -1.6, 0.9, 3.8, 5.8]

    # Constrain temperature
    if isinstance(temp, list):
        temp_adj = [min(t, -2.8) if t < -2.8 else t for t in temp]
    else:
        temp_adj = min(temp, -2.8) if temp < -2.8 else temp

    # Eq. 22 - Potential Evapotranspiration
    if isinstance(temp_adj, list):
        pe = [0.36 * (t + 2.8) + fl01[m-1] for t, m in zip(temp_adj, mon)]
        pe = [p / 2 for p in pe]
    else:
        pe = (0.36 * (temp_adj + 2.8) + fl01[mon-1]) / 2

    # Daylength factor adjustment by latitude for Potential Evapotranspiration
    if lat_adjust:
        if isinstance(lat, list):
            for i in range(len(lat)):
                if lat[i] <= -20:
                    pe[i] = (0.36 * (temp_adj[i] + 2.8) + fl02[mon[i]-1]) / 2
                elif lat[i] > -20 and lat[i] <= 20:
                    pe[i] = (0.36 * (temp_adj[i] + 2.8) + 1.4) / 2
        else:
            if lat <= -20:
                pe = (0.36 * (temp_adj + 2.8) + fl02[mon-1]) / 2
            elif lat > -20 and lat <= 20:
                pe = (0.36 * (temp_adj + 2.8) + 1.4) / 2

    # Cap potential evapotranspiration at 0 for negative winter DC values
    if isinstance(pe, list):
        pe = [max(p, 0) for p in pe]
    else:
        pe = max(pe, 0)

    if isinstance(prec, list):
        ra = prec
    else:
        ra = prec

    # Eq. 18 - Effective Rainfall
    if isinstance(ra, list):
        rw = [0.83 * r - 1.27 for r in ra]
    else:
        rw = 0.83 * ra - 1.27

    # Eq. 19
    if isinstance(dc_yda, list):
        smi = [800 * math.exp(-d / 400) for d in dc_yda]
    else:
        smi = 800 * math.exp(-dc_yda / 400)

    # Alteration to Eq. 21
    if isinstance(dc_yda, list):
        dr0 = [d - 400 * math.log(1 + 3.937 * r / s) for d, r, s in zip(dc_yda, rw, smi)]
        dr0 = [max(d, 0) for d in dr0]
    else:
        dr0 = dc_yda - 400 * math.log(1 + 3.937 * rw / smi)
        dr0 = max(dr0, 0)

    # if precip is less than 2.8 then use yesterday's DC
    if isinstance(prec, list):
        dr = [d if p <= 2.8 else d0 for p, d, d0 in zip(prec, dc_yda, dr0)]
    else:
        dr = dc_yda if prec <= 2.8 else dr0

    # Alteration to Eq. 23
    if isinstance(dr, list):
        dc1 = [d + p for d, p in zip(dr, pe)]
        dc1 = [max(d, 0) for d in dc1]
    else:
        dc1 = dr + pe
        dc1 = max(dc1, 0)

    return dc1
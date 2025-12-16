"""
Foliar Moisture Content Calculator

Calculate Foliar Moisture Content on a specified day.
All variables names are laid out in the same manner as Forestry Canada Fire
Danger Group (FCFDG) (1992). Development and Structure of the Canadian Forest
Fire Behavior Prediction System." Technical Report ST-X-3, Forestry Canada,
Ottawa, Ontario.
"""

from typing import Union, List
import math


def foliar_moisture_content(
    lat: Union[float, List[float]],
    long: Union[float, List[float]],
    elv: Union[float, List[float]],
    dj: Union[int, List[int]],
    d0: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate Foliar Moisture Content on a specified day.

    Args:
        lat: Latitude (decimal degrees)
        long: Longitude (decimal degrees)
        elv: Elevation (metres)
        dj: Day of year (julian date)
        d0: Date of minimum foliar moisture content. If D0, date of min FMC, is not
            known then D0 = NULL.

    Returns:
        FMC: Foliar Moisture Content value
    """
    # Initialize vectors
    if isinstance(lat, list):
        fmc = [0.0] * len(lat)
        lat_n = [0.0] * len(lat)
    else:
        fmc = 0.0
        lat_n = 0.0

    # Calculate Normalized Latitude
    # Eqs. 1 & 3 (FCFDG 1992)
    if isinstance(lat, list):
        for i in range(len(lat)):
            if d0[i] <= 0:
                if elv[i] <= 0:
                    lat_n[i] = 46 + 23.4 * math.exp(-0.0360 * (150 - long[i]))
                else:
                    lat_n[i] = 43 + 33.7 * math.exp(-0.0351 * (150 - long[i]))
            else:
                lat_n[i] = lat_n[i]  # Keep as is
    else:
        if d0 <= 0:
            if elv <= 0:
                lat_n = 46 + 23.4 * math.exp(-0.0360 * (150 - long))
            else:
                lat_n = 43 + 33.7 * math.exp(-0.0351 * (150 - long))

    # Calculate Date of minimum foliar moisture content
    # Eqs. 2 & 4 (FCFDG 1992)
    if isinstance(lat, list):
        for i in range(len(lat)):
            if d0[i] <= 0:
                if elv[i] <= 0:
                    d0[i] = 151 * (lat[i] / lat_n[i])
                else:
                    d0[i] = 142.1 * (lat[i] / lat_n[i]) + 0.0172 * elv[i]
    else:
        if d0 <= 0:
            if elv <= 0:
                d0 = 151 * (lat / lat_n)
            else:
                d0 = 142.1 * (lat / lat_n) + 0.0172 * elv

    # Round D0 to the nearest integer because it is a date
    if isinstance(d0, list):
        d0 = [round(d) for d in d0]
    else:
        d0 = round(d0)

    # Number of days between day of year and date of min FMC
    # Eq. 5 (FCFDG 1992)
    if isinstance(dj, list):
        nd = [abs(d - d0_val) for d, d0_val in zip(dj, d0)]
    else:
        nd = abs(dj - d0)

    # Calculate final FMC
    # Eqs. 6, 7, & 8 (FCFDG 1992)
    if isinstance(nd, list):
        fmc = [0.0] * len(nd)
        for i in range(len(nd)):
            if nd[i] < 30:
                fmc[i] = 85 + 0.0189 * (nd[i] ** 2)
            elif nd[i] >= 30 and nd[i] < 50:
                fmc[i] = 32.9 + 3.17 * nd[i] - 0.0288 * (nd[i] ** 2)
            else:
                fmc[i] = 120
    else:
        if nd < 30:
            fmc = 85 + 0.0189 * (nd ** 2)
        elif nd >= 30 and nd < 50:
            fmc = 32.9 + 3.17 * nd - 0.0288 * (nd ** 2)
        else:
            fmc = 120

    return fmc
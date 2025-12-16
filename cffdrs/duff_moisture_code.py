"""
Duff Moisture Code Calculator

Duff Moisture Code Calculation. All code is based on a C code library that was
written by Canadian Forest Service Employees, which was originally based on the
Fortran code listed in the reference below. All equations in this code refer to
that document.

Equations and FORTRAN program for the Canadian Forest Fire Weather Index System.
1985. Van Wagner, C.E.; Pickett, T.L. Canadian Forestry Service, Petawawa National
Forestry Institute, Chalk River, Ontario. Forestry Technical Report 33. 18 p.

Additional reference on FWI system Development and structure of the Canadian Forest
Fire Weather Index System. 1987. Van Wagner, C.E. Canadian Forestry Service,
Headquarters, Ottawa. Forestry Technical Report 35. 35 p.
"""

from typing import Union, List
import math


def duff_moisture_code(
    dmc_yda: Union[float, List[float]],
    temp: Union[float, List[float]],
    rh: Union[float, List[float]],
    prec: Union[float, List[float]],
    lat: Union[float, List[float]],
    mon: Union[int, List[int]],
    lat_adjust: bool = True
) -> Union[float, List[float]]:
    """
    Calculate the Duff Moisture Code.

    Args:
        dmc_yda: The Duff Moisture Code from previous iteration
        temp: Temperature (centigrade)
        rh: Relative Humidity (%)
        prec: Precipitation(mm)
        lat: Latitude (decimal degrees)
        mon: Month (1-12)
        lat_adjust: Latitude adjustment (TRUE, FALSE, default=TRUE)

    Returns:
        A single duff moisture code value
    """
    # Reference latitude for DMC day length adjustment
    # 46N: Canadian standard, latitude >= 30N   (Van Wagner 1987)
    ell01 = [6.5, 7.5, 9, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8, 7, 6]
    # 20N: For 30 > latitude >= 10
    ell02 = [7.9, 8.4, 8.9, 9.5, 9.9, 10.2, 10.1, 9.7, 9.1, 8.6, 8.1, 7.8]
    # 20S: For -10 > latitude >= -30
    ell03 = [10.1, 9.6, 9.1, 8.5, 8.1, 7.8, 7.9, 8.3, 8.9, 9.4, 9.9, 10.2]
    # 40S: For -30 > latitude
    ell04 = [11.5, 10.5, 9.2, 7.9, 6.8, 6.2, 6.5, 7.4, 8.7, 10, 11.2, 11.8]
    # For latitude near the equator, we just use a factor of 9 for all months

    # constrain low end of temperature
    if isinstance(temp, list):
        temp_adj = [max(t, -1.1) for t in temp]
    else:
        temp_adj = max(temp, -1.1)

    # Eq. 16 - The log drying rate
    if isinstance(temp_adj, list):
        rk = [1.894 * (t + 1.1) * (100 - r) * ell01[m-1] * 1e-04
              for t, r, m in zip(temp_adj, rh, mon)]
    else:
        rk = 1.894 * (temp_adj + 1.1) * (100 - rh) * ell01[mon-1] * 1e-04

    # Adjust the day length and thus the drying r, based on latitude and month
    if lat_adjust:
        if isinstance(lat, list):
            for i in range(len(lat)):
                if lat[i] <= 30 and lat[i] > 10:
                    rk[i] = 1.894 * (temp_adj[i] + 1.1) * (100 - rh[i]) * ell02[mon[i]-1] * 1e-04
                elif lat[i] <= -10 and lat[i] > -30:
                    rk[i] = 1.894 * (temp_adj[i] + 1.1) * (100 - rh[i]) * ell03[mon[i]-1] * 1e-04
                elif lat[i] <= -30 and lat[i] >= -90:
                    rk[i] = 1.894 * (temp_adj[i] + 1.1) * (100 - rh[i]) * ell04[mon[i]-1] * 1e-04
                elif lat[i] <= 10 and lat[i] > -10:
                    rk[i] = 1.894 * (temp_adj[i] + 1.1) * (100 - rh[i]) * 9 * 1e-04
        else:
            if lat <= 30 and lat > 10:
                rk = 1.894 * (temp_adj + 1.1) * (100 - rh) * ell02[mon-1] * 1e-04
            elif lat <= -10 and lat > -30:
                rk = 1.894 * (temp_adj + 1.1) * (100 - rh) * ell03[mon-1] * 1e-04
            elif lat <= -30 and lat >= -90:
                rk = 1.894 * (temp_adj + 1.1) * (100 - rh) * ell04[mon-1] * 1e-04
            elif lat <= 10 and lat > -10:
                rk = 1.894 * (temp_adj + 1.1) * (100 - rh) * 9 * 1e-04

    # Constrain P
    if isinstance(prec, list):
        pr = [dmc_yda[i] if prec[i] <= 1.5 else 0 for i in range(len(prec))]
        for i in range(len(prec)):
            if prec[i] > 1.5:
                ra = prec[i]
                # Eq. 11 - Net rain amount
                rw = 0.92 * ra - 1.27
                # Alteration to Eq. 12 to calculate more accurately
                wmi = 20 + 280 / math.exp(0.023 * dmc_yda[i])
                # Eqs. 13a, 13b, 13c
                if dmc_yda[i] <= 33:
                    b = 100 / (0.5 + 0.3 * dmc_yda[i])
                elif dmc_yda[i] <= 65:
                    b = 14 - 1.3 * math.log(dmc_yda[i])
                else:
                    b = 6.2 * math.log(dmc_yda[i]) - 17.2
                # Eq. 14 - Moisture content after rain
                wmr = wmi + 1000 * rw / (48.77 + b * rw)
                # Alteration to Eq. 15 to calculate more accurately
                pr[i] = 43.43 * (5.6348 - math.log(wmr - 20))
    else:
        if prec <= 1.5:
            pr = dmc_yda
        else:
            ra = prec
            # Eq. 11 - Net rain amount
            rw = 0.92 * ra - 1.27
            # Alteration to Eq. 12 to calculate more accurately
            wmi = 20 + 280 / math.exp(0.023 * dmc_yda)
            # Eqs. 13a, 13b, 13c
            if dmc_yda <= 33:
                b = 100 / (0.5 + 0.3 * dmc_yda)
            elif dmc_yda <= 65:
                b = 14 - 1.3 * math.log(dmc_yda)
            else:
                b = 6.2 * math.log(dmc_yda) - 17.2
            # Eq. 14 - Moisture content after rain
            wmr = wmi + 1000 * rw / (48.77 + b * rw)
            # Alteration to Eq. 15 to calculate more accurately
            pr = 43.43 * (5.6348 - math.log(wmr - 20))

    if isinstance(pr, list):
        pr = [max(p, 0) for p in pr]
    else:
        pr = max(pr, 0)

    # Calculate final P (DMC)
    if isinstance(pr, list):
        dmc1 = [p + r for p, r in zip(pr, rk)]
        dmc1 = [max(d, 0) for d in dmc1]
    else:
        dmc1 = pr + rk
        dmc1 = max(dmc1, 0)

    return dmc1
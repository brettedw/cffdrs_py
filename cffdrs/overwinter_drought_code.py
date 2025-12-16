"""
Overwintering Drought Code

This module calculates an initial or season starting Drought Code (DC) value based on
a standard method of overwintering the Drought Code (Lawson and Armitage 2008).
This method uses the final DC value from previous year, over winter precipitation
and estimates of how much over-winter precipitation 'refills' the moisture in this
fuel layer. This function could be used for either one weather station or for
multiple weather stations.

Of the three fuel moisture codes (i.e. FFMC, DMC and DC) making up the FWI System,
only the DC needs to be considered in terms of its values carrying over from one
fire season to the next. In Canada both the FFMC and the DMC are assumed to reach
moisture saturation from overwinter precipitation at or before spring melt; this
is a reasonable assumption and any error in these assumed starting conditions
quickly disappears. If snowfall (or other overwinter precipitation) is not large
enough however, the fuel layer tracked by the Drought Code may not fully reach
saturation after spring snow melt; because of the long response time in this fuel
layer (53 days in standard conditions) a large error in this spring starting
condition can affect the DC for a significant portion of the fire season. In areas
where overwinter precipitation is 200 mm or more, full moisture recharge occurs
and DC overwintering is usually unnecessary. More discussion of overwintering and
fuel drying time lag can be found in Lawson and Armitage (2008) and Van Wagner (1985).
"""

import math
from typing import Union, List


def overwinter_drought_code(
    DCf: Union[float, List[float]] = 100.0,
    rw: Union[float, List[float]] = 200.0,
    a: Union[float, List[float]] = 0.75,
    b: Union[float, List[float]] = 0.75
) -> Union[float, List[float]]:
    """
    Calculate overwintering Drought Code.

    Args:
        DCf: Final fall DC value from previous year
        rw: Winter precipitation (mm)
        a: User selected values accounting for carry-over fraction
        b: User selected values accounting for wetting efficiency fraction

    Returns:
        Overwintered DC value(s)
    """
    # Convert single values to lists for uniform processing
    if isinstance(DCf, (int, float)):
        DCf = [float(DCf)]
    if isinstance(rw, (int, float)):
        rw = [float(rw)]
    if isinstance(a, (int, float)):
        a = [float(a)]
    if isinstance(b, (int, float)):
        b = [float(b)]

    # Ensure all lists have the same length
    max_len = max(len(DCf), len(rw), len(a), len(b))
    if len(DCf) == 1 and max_len > 1:
        DCf = DCf * max_len
    if len(rw) == 1 and max_len > 1:
        rw = rw * max_len
    if len(a) == 1 and max_len > 1:
        a = a * max_len
    if len(b) == 1 and max_len > 1:
        b = b * max_len

    if not (len(DCf) == len(rw) == len(a) == len(b)):
        raise ValueError("All input parameters must have the same length")

    DCs = []
    for i in range(len(DCf)):
        # Eq. 3 - Final fall moisture equivalent of the DC
        Qf = 800.0 * math.exp(-DCf[i] / 400.0)
        # Eq. 2 - Starting spring moisture equivalent of the DC
        Qs = a[i] * Qf + b[i] * (3.94 * rw[i])
        # Eq. 4 - Spring start-up value for the DC
        dc_val = 400.0 * math.log(800.0 / Qs)
        # Constrain DC
        dc_val = max(dc_val, 15.0)
        DCs.append(dc_val)

    # Return single value if single input, otherwise list
    return DCs[0] if len(DCs) == 1 else DCs


# Alias for backward compatibility
wDC = overwinter_drought_code
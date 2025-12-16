"""
Rate of spread at time t calculation

Computes the Rate of Spread prediction based on fuel type and FWI conditions at
elapsed time since ignition. Equations are from listed FCFDG (1992).

All variables names are laid out in the same manner as Forestry Canada Fire Danger
Group (FCFDG) (1992). Development and Structure of the Canadian Forest Fire Behavior
Prediction System." Technical Report ST-X-3, Forestry Canada, Ottawa, Ontario.
"""

from typing import Union, List
import math


def rate_of_spread_at_time(
    fueltype: Union[str, List[str]],
    ro_seq: Union[float, List[float]],
    hr: Union[float, List[float]],
    cfb: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate the Rate of Spread at time since ignition.

    Args:
        fueltype: The Fire Behaviour Prediction FuelType
        ro_seq: Equilibrium Rate of Spread (m/min)
        hr: Time since ignition (hours)
        cfb: Crown Fraction Burned

    Returns:
        ROSt: Rate of Spread at time since ignition value
    """
    # Eq. 72 - alpha constant value, dependent on fuel type
    if isinstance(fueltype, list):
        alpha = [0.0] * len(fueltype)
        for i in range(len(fueltype)):
            if fueltype[i] in ["C1", "O1A", "O1B", "S1", "S2", "S3", "D1"]:
                alpha[i] = 0.115
            else:
                alpha[i] = 0.115 - 18.8 * (cfb[i] ** 2.5) * math.exp(-8 * cfb[i])
    else:
        if fueltype in ["C1", "O1A", "O1B", "S1", "S2", "S3", "D1"]:
            alpha = 0.115
        else:
            alpha = 0.115 - 18.8 * (cfb ** 2.5) * math.exp(-8 * cfb)

    # Eq. 70 - Rate of Spread at time since ignition
    rost = ro_seq * (1 - math.exp(-alpha * hr))
    return rost
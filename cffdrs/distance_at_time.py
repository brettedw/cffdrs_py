"""
Distance at time t calculator

Calculate the Head fire spread distance at time t. In the documentation this
variable is just "D".

All variables names are laid out in the same manner as Forestry Canada Fire
Danger Group (FCFDG) (1992). Development and Structure of the Canadian Forest
Fire Behavior Prediction System." Technical Report ST-X-3, Forestry Canada,
Ottawa, Ontario.
"""

from typing import Union, List


def distance_at_time(
    fueltype: Union[str, List[str]],
    ro_seq: Union[float, List[float]],
    hr: Union[float, List[float]],
    cfb: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate the Head fire spread distance at time t.

    Args:
        fueltype: The Fire Behaviour Prediction FuelType
        ro_seq: The predicted equilibrium rate of spread (m/min)
        hr: The elapsed time (min)
        cfb: Crown Fraction Burned

    Returns:
        DISTt: Head fire spread distance at time t
    """
    # Eq. 72 (FCFDG 1992) - Calculate the alpha constant for the DISTt calculation
    if isinstance(fueltype, list):
        alpha = [0.0] * len(fueltype)
        for i in range(len(fueltype)):
            if fueltype[i] in ["C1", "O1A", "O1B", "S1", "S2", "S3", "D1"]:
                alpha[i] = 0.115
            else:
                alpha[i] = 0.115 - 18.8 * (cfb[i] ** 2.5) * (2.71828 ** (-8 * cfb[i]))
    else:
        if fueltype in ["C1", "O1A", "O1B", "S1", "S2", "S3", "D1"]:
            alpha = 0.115
        else:
            alpha = 0.115 - 18.8 * (cfb ** 2.5) * (2.71828 ** (-8 * cfb))

    # Eq. 71 (FCFDG 1992) Calculate Head fire spread distance
    dist_t = ro_seq * (hr + (2.71828 ** (-alpha * hr)) / alpha - 1 / alpha)
    return dist_t
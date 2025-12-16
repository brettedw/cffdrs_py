"""
Length-to-Breadth ratio at time t

Computes the Length to Breadth ratio of an elliptically shaped fire at elapsed
time since ignition. Equations are from listed FCFDG (1992) and Wotton et. al.
(2009), and are marked as such.

All variables names are laid out in the same manner as Forestry Canada Fire Danger
Group (FCFDG) (1992). Development and Structure of the Canadian Forest Fire Behavior
Prediction System." Technical Report ST-X-3, Forestry Canada, Ottawa, Ontario.

Wotton, B.M., Alexander, M.E., Taylor, S.W. 2009. Updates and revisions to the 1992
Canadian forest fire behavior prediction system. Nat. Resour. Can., Can. For.
Serv., Great Lakes For. Cent., Sault Ste. Marie, Ontario, Canada. Information
Report GLC-X-10, 45p.
"""

from typing import Union, List
import math


def length_to_breadth_at_time(
    fueltype: Union[str, List[str]],
    lb: Union[float, List[float]],
    hr: Union[float, List[float]],
    cfb: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate the Length to Breadth ratio at elapsed time since ignition.

    Args:
        fueltype: The Fire Behaviour Prediction FuelType
        lb: Length to Breadth ratio
        hr: Time since ignition (hours)
        cfb: Crown Fraction Burned

    Returns:
        LBt: Length to Breadth ratio at time since ignition
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

    # Eq. 81 (Wotton et.al. 2009) - LB at time since ignition
    lbt = (lb - 1) * (1 - math.exp(-alpha * hr)) + 1
    return lbt
"""
Length-to-Breadth ratio

Computes the Length to Breadth ratio of an elliptically shaped fire. Equations are from
listed FCFDG (1992) except for errata 80 from Wotton et. al. (2009).

All variables names are laid out in the same manner as Forestry Canada Fire Danger Group
(FCFDG) (1992). Development and Structure of the Canadian Forest Fire Behavior Prediction
System." Technical Report ST-X-3, Forestry Canada, Ottawa, Ontario.

Wotton, B.M., Alexander, M.E., Taylor, S.W. 2009. Updates and revisions to the 1992
Canadian forest fire behavior prediction system. Nat. Resour. Can., Can. For. Serv.,
Great Lakes For. Cent., Sault Ste. Marie, Ontario, Canada. Information Report GLC-X-10, 45p.
"""

from typing import Union, List
import math


def length_to_breadth(
    fueltype: Union[str, List[str]],
    wsv: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate the Length to Breadth ratio of an elliptically shaped fire.

    Args:
        fueltype: The Fire Behaviour Prediction FuelType
        wsv: The Wind Speed (km/h)

    Returns:
        Length to Breadth ratio value
    """
    # Calculation is depending on if fuel type is grass (O1) or other fueltype
    if isinstance(fueltype, list):
        lb = [0.0] * len(fueltype)
        for i in range(len(fueltype)):
            if fueltype[i] in ["O1A", "O1B"]:
                # Correction to original Equation 80 is made here
                # Eq. 80a / 80b from Wotton 2009
                lb[i] = 1.1 * (wsv[i] ** 0.464) if wsv[i] >= 1.0 else 1.0
            else:
                # Eq. 79
                lb[i] = 1.0 + 8.729 * (1 - math.exp(-0.030 * wsv[i])) ** 2.155
    else:
        if fueltype in ["O1A", "O1B"]:
            # Correction to original Equation 80 is made here
            # Eq. 80a / 80b from Wotton 2009
            lb = 1.1 * (wsv ** 0.464) if wsv >= 1.0 else 1.0
        else:
            # Eq. 79
            lb = 1.0 + 8.729 * (1 - math.exp(-0.030 * wsv)) ** 2.155

    return lb
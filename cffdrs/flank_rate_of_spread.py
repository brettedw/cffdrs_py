"""
Flank Fire Rate of Spread Calculator

Computes the Flank Fire Spread Rate.
All variables names are laid out in the same manner as Forestry Canada Fire Danger Group
(FCFDG) (1992). Development and Structure of the Canadian Forest Fire Behavior Prediction
System." Technical Report ST-X-3, Forestry Canada, Ottawa, Ontario.

References:
    Forestry Canada Fire Danger Group (FCFDG) (1992). Development and Structure of the
    Canadian Forest Fire Behavior Prediction System. Technical Report ST-X-3, Forestry
    Canada, Ottawa, Ontario.
"""

from typing import Union, List


def flank_rate_of_spread(
    ros: Union[float, List[float]],
    bros: Union[float, List[float]],
    lb: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate the Flank Fire Spread Rate.

    Args:
        ros: Fire Rate of Spread (m/min)
        bros: Back Fire Rate of Spread (m/min)
        lb: Length to breadth ratio

    Returns:
        FROS: Flank Fire Spread Rate (m/min)
    """
    # Eq. 89 (FCFDG 1992)
    if isinstance(ros, list):
        fros = [(r + b) / l / 2 for r, b, l in zip(ros, bros, lb)]
    else:
        fros = (ros + bros) / lb / 2
    return fros
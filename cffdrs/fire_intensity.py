"""
Fire Intensity Calculator

Computes the Predicted Fire Intensity from the FWI System.
All variables names are laid out in the same manner as Forestry Canada Fire
Danger Group (FCFDG) (1992). Development and Structure of the Canadian Forest
Fire Behavior Prediction System." Technical Report ST-X-3, Forestry Canada,
Ottawa, Ontario.

References:
    Forestry Canada Fire Danger Group (FCFDG) (1992). Development and Structure
    of the Canadian Forest Fire Behavior Prediction System. Technical Report
    ST-X-3, Forestry Canada, Ottawa, Ontario.
"""

from typing import Union, List


def fire_intensity(fc: Union[float, List[float]], ros: Union[float, List[float]]) -> Union[float, List[float]]:
    """
    Calculate the Predicted Fire Intensity.

    Args:
        fc: Fuel Consumption (kg/m^2)
        ros: Rate of Spread (m/min)

    Returns:
        FI: Fire Intensity (kW/m)
    """
    # Eq. 69 (FCFDG 1992) Fire Intensity (kW/m)
    if isinstance(fc, list):
        fi = [300 * f * r for f, r in zip(fc, ros)]
    else:
        fi = 300 * fc * ros
    return fi
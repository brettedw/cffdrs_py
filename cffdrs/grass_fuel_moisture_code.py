"""
Grass Fuel Moisture Calculation

This is the actual calculation for grass fuel moisture.
"""

from typing import Union, List


def grass_fuel_moisture_code(mc0: Union[float, List[float]]) -> Union[float, List[float]]:
    """
    Calculate the Grass Fuel Moisture Code.

    Args:
        mc0: An output from the mcCalc functions

    Returns:
        GFMC0: Grass Fuel Moisture Code
    """
    # Eq. 12 - Calculate GFMC
    if isinstance(mc0, list):
        gfmc0 = [59.5 * ((250 - m) / (250.0 + m)) for m in mc0]
    else:
        gfmc0 = 59.5 * ((250 - mc0) / (250.0 + mc0))
    return gfmc0
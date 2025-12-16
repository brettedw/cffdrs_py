"""
Crown Fuel Load function

Originally from FBP.
"""

from typing import Union, List


def crown_fuel_load(
    fueltype: Union[str, List[str]],
    cfl: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate crown fuel load.

    Args:
        fueltype: Character fueltype indicator
        cfl: Crown Fuel Load

    Returns:
        Crown Fuel Load (kg/m^2)
    """
    # Fuel type default CFL values
    cfls = {
        "C1": 0.75, "C2": 0.8, "C3": 1.15, "C4": 1.2, "C5": 1.2, "C6": 1.8, "C7": 0.5,
        "D1": 0, "M1": 0.8, "M2": 0.8, "M3": 0.8, "M4": 0.8,
        "S1": 0, "S2": 0, "S3": 0, "O1A": 0, "O1B": 0
    }

    if isinstance(fueltype, list):
        result = [0.0] * len(fueltype)
        for i in range(len(fueltype)):
            ft = fueltype[i]
            cfl_val = cfl[i] if isinstance(cfl, list) else cfl

            if (cfl_val <= 0 or cfl_val > 2 or cfl_val is None) and ft in cfls:
                result[i] = cfls[ft]
            else:
                result[i] = cfl_val
    else:
        if (cfl <= 0 or cfl > 2 or cfl is None) and fueltype in cfls:
            result = cfls[fueltype]
        else:
            result = cfl

    return result
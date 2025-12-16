"""
Crown Base Height function

Logic originally in fbp() pulled into its own function.
"""

from typing import Union, List


def crown_base_height(
    fueltype: Union[str, List[str]],
    cbh: Union[float, List[float]],
    sd: Union[float, List[float]],
    sh: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate crown base height.

    Args:
        fueltype: Fuel type
        cbh: Crown Base Height
        sd: Stand Density (stems/ha)
        sh: Stand Height (m)

    Returns:
        Crown Base Height (m)
    """
    # Fuel type default CBH values
    cbhs = {
        "C1": 2, "C2": 3, "C3": 8, "C4": 4, "C5": 18, "C6": 7, "C7": 10,
        "D1": 0, "M1": 6, "M2": 6, "M3": 6, "M4": 6,
        "S1": 0, "S2": 0, "S3": 0, "O1A": 0, "O1B": 0
    }

    if isinstance(fueltype, list):
        result = [0.0] * len(fueltype)
        for i in range(len(fueltype)):
            ft = fueltype[i]
            cbh_val = cbh[i] if isinstance(cbh, list) else cbh
            sd_val = sd[i] if isinstance(sd, list) else sd
            sh_val = sh[i] if isinstance(sh, list) else sh

            if (cbh_val <= 0 or cbh_val > 50 or cbh_val is None) and ft in cbhs:
                if ft == "C6" and sd_val > 0 and sh_val > 0:
                    result[i] = -11.2 + 1.06 * sh_val + 0.0017 * sd_val
                else:
                    result[i] = cbhs[ft]
            else:
                result[i] = cbh_val
            result[i] = 1e-07 if result[i] < 0 else result[i]
    else:
        if (cbh <= 0 or cbh > 50 or cbh is None) and fueltype in cbhs:
            if fueltype == "C6" and sd > 0 and sh > 0:
                result = -11.2 + 1.06 * sh + 0.0017 * sd
            else:
                result = cbhs[fueltype]
        else:
            result = cbh
        result = 1e-07 if result < 0 else result

    return result
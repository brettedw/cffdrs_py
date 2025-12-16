"""
Surface Fuel Consumption Calculator

Computes the Surface Fuel Consumption by Fuel Type. All variables names are laid
out in the same manner as FCFDG (1992) or Wotton et. al (2009)

Forestry Canada Fire Danger Group (FCFDG) (1992). "Development and Structure of the
Canadian Forest Fire Behavior Prediction System." Technical Report ST-X-3,
Forestry Canada, Ottawa, Ontario.

Wotton, B.M., Alexander, M.E., Taylor, S.W. 2009. Updates and revisions to the 1992
Canadian forest fire behavior prediction system. Nat. Resour. Can., Can. For.
Serv., Great Lakes For. Cent., Sault Ste. Marie, Ontario, Canada. Information
Report GLC-X-10, 45p.
"""

from typing import Union, List


def surface_fuel_consumption(
    fueltype: Union[str, List[str]],
    ffmc: Union[float, List[float]],
    bui: Union[float, List[float]],
    pc: Union[float, List[float]],
    gfl: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate the Surface Fuel Consumption by Fuel Type.

    Args:
        fueltype: The Fire Behaviour Prediction FuelType
        bui: Buildup Index
        ffmc: Fine Fuel Moisture Code
        pc: Percent Conifer (%)
        gfl: Grass Fuel Load (kg/m^2)

    Returns:
        SFC: Surface Fuel Consumption (kg/m^2)
    """
    if isinstance(fueltype, list):
        sfc = [-999.0] * len(fueltype)
        for i in range(len(fueltype)):
            ft = fueltype[i]
            ffmc_val = ffmc[i] if isinstance(ffmc, list) else ffmc
            bui_val = bui[i] if isinstance(bui, list) else bui
            pc_val = pc[i] if isinstance(pc, list) else pc
            gfl_val = gfl[i] if isinstance(gfl, list) else gfl

            # Eqs. 9a, 9b (Wotton et. al. 2009) - Solving the lower bound of FFMC value
            # for the C1 fuel type SFC calculation
            if ft == "C1":
                if ffmc_val > 84:
                    sfc[i] = 0.75 + 0.75 * (1 - (2.71828 ** (-0.23 * (ffmc_val - 84)))) ** 0.5
                else:
                    sfc[i] = 0.75 - 0.75 * (1 - (2.71828 ** (-0.23 * (84 - ffmc_val)))) ** 0.5
            # Eq. 10 (FCFDG 1992) - C2, M3, and M4 Fuel Types
            elif ft in ["C2", "M3", "M4"]:
                sfc[i] = 5.0 * (1 - 2.71828 ** (-0.0115 * bui_val))
            # Eq. 11 (FCFDG 1992) - C3, C4 Fuel Types
            elif ft in ["C3", "C4"]:
                sfc[i] = 5.0 * (1 - 2.71828 ** (-0.0164 * bui_val)) ** 2.24
            # Eq. 12 (FCFDG 1992) - C5, C6 Fuel Types
            elif ft in ["C5", "C6"]:
                sfc[i] = 5.0 * (1 - 2.71828 ** (-0.0149 * bui_val)) ** 2.48
            # Eqs. 13, 14, 15 (FCFDG 1992) - C7 Fuel Types
            elif ft == "C7":
                sfc[i] = (2 * (1 - 2.71828 ** (-0.104 * (ffmc_val - 70))) if ffmc_val > 70 else 0) + \
                        1.5 * (1 - 2.71828 ** (-0.0201 * bui_val))
            # Eq. 16 (FCFDG 1992) - D1 Fuel Type
            elif ft == "D1":
                sfc[i] = 1.5 * (1 - 2.71828 ** (-0.0183 * bui_val))
            # Eq. 17 (FCFDG 1992) - M1 and M2 Fuel Types
            elif ft in ["M1", "M2"]:
                sfc[i] = (pc_val / 100 * (5.0 * (1 - 2.71828 ** (-0.0115 * bui_val)))) + \
                        ((100 - pc_val) / 100 * (1.5 * (1 - 2.71828 ** (-0.0183 * bui_val))))
            # Eq. 18 (FCFDG 1992) - Grass Fuel Types
            elif ft in ["O1A", "O1B"]:
                sfc[i] = gfl_val
            # Eq. 19, 20, 25 (FCFDG 1992) - S1 Fuel Type
            elif ft == "S1":
                sfc[i] = 4.0 * (1 - 2.71828 ** (-0.025 * bui_val)) + \
                        4.0 * (1 - 2.71828 ** (-0.034 * bui_val))
            # Eq. 21, 22, 25 (FCFDG 1992) - S2 Fuel Type
            elif ft == "S2":
                sfc[i] = 10.0 * (1 - 2.71828 ** (-0.013 * bui_val)) + \
                        6.0 * (1 - 2.71828 ** (-0.060 * bui_val))
            # Eq. 23, 24, 25 (FCFDG 1992) - S3 Fuel Type
            elif ft == "S3":
                sfc[i] = 12.0 * (1 - 2.71828 ** (-0.0166 * bui_val)) + \
                        20.0 * (1 - 2.71828 ** (-0.0210 * bui_val))
    else:
        ffmc_val = ffmc
        bui_val = bui
        pc_val = pc
        gfl_val = gfl

        # Eqs. 9a, 9b (Wotton et. al. 2009) - Solving the lower bound of FFMC value
        # for the C1 fuel type SFC calculation
        if fueltype == "C1":
            if ffmc_val > 84:
                sfc = 0.75 + 0.75 * (1 - (2.71828 ** (-0.23 * (ffmc_val - 84)))) ** 0.5
            else:
                sfc = 0.75 - 0.75 * (1 - (2.71828 ** (-0.23 * (84 - ffmc_val)))) ** 0.5
        # Eq. 10 (FCFDG 1992) - C2, M3, and M4 Fuel Types
        elif fueltype in ["C2", "M3", "M4"]:
            sfc = 5.0 * (1 - 2.71828 ** (-0.0115 * bui_val))
        # Eq. 11 (FCFDG 1992) - C3, C4 Fuel Types
        elif fueltype in ["C3", "C4"]:
            sfc = 5.0 * (1 - 2.71828 ** (-0.0164 * bui_val)) ** 2.24
        # Eq. 12 (FCFDG 1992) - C5, C6 Fuel Types
        elif fueltype in ["C5", "C6"]:
            sfc = 5.0 * (1 - 2.71828 ** (-0.0149 * bui_val)) ** 2.48
        # Eqs. 13, 14, 15 (FCFDG 1992) - C7 Fuel Types
        elif fueltype == "C7":
            sfc = (2 * (1 - 2.71828 ** (-0.104 * (ffmc_val - 70))) if ffmc_val > 70 else 0) + \
                  1.5 * (1 - 2.71828 ** (-0.0201 * bui_val))
        # Eq. 16 (FCFDG 1992) - D1 Fuel Type
        elif fueltype == "D1":
            sfc = 1.5 * (1 - 2.71828 ** (-0.0183 * bui_val))
        # Eq. 17 (FCFDG 1992) - M1 and M2 Fuel Types
        elif fueltype in ["M1", "M2"]:
            sfc = (pc_val / 100 * (5.0 * (1 - 2.71828 ** (-0.0115 * bui_val)))) + \
                  ((100 - pc_val) / 100 * (1.5 * (1 - 2.71828 ** (-0.0183 * bui_val))))
        # Eq. 18 (FCFDG 1992) - Grass Fuel Types
        elif fueltype in ["O1A", "O1B"]:
            sfc = gfl_val
        # Eq. 19, 20, 25 (FCFDG 1992) - S1 Fuel Type
        elif fueltype == "S1":
            sfc = 4.0 * (1 - 2.71828 ** (-0.025 * bui_val)) + \
                  4.0 * (1 - 2.71828 ** (-0.034 * bui_val))
        # Eq. 21, 22, 25 (FCFDG 1992) - S2 Fuel Type
        elif fueltype == "S2":
            sfc = 10.0 * (1 - 2.71828 ** (-0.013 * bui_val)) + \
                  6.0 * (1 - 2.71828 ** (-0.060 * bui_val))
        # Eq. 23, 24, 25 (FCFDG 1992) - S3 Fuel Type
        elif fueltype == "S3":
            sfc = 12.0 * (1 - 2.71828 ** (-0.0166 * bui_val)) + \
                  20.0 * (1 - 2.71828 ** (-0.0210 * bui_val))

    # Constrain SFC value
    if isinstance(sfc, list):
        sfc = [max(s, 0.000001) for s in sfc]
    else:
        sfc = max(sfc, 0.000001)

    return sfc
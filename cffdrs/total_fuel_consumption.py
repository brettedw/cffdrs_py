"""
Total Fuel Consumption calculation

Computes the Total (Surface + Crown) Fuel Consumption by Fuel Type.
All variables names are laid out in the same manner as FCFDG (1992) or
Wotton et. al (2009)

Forestry Canada Fire Danger Group (FCFDG) (1992). "Development and Structure of the
Canadian Forest Fire Behavior Prediction System." Technical Report ST-X-3,
Forestry Canada, Ottawa, Ontario.

Wotton, B.M., Alexander, M.E., Taylor, S.W. 2009. Updates and revisions to the 1992
Canadian forest fire behavior prediction system. Nat. Resour. Can., Can. For.
Serv., Great Lakes For. Cent., Sault Ste. Marie, Ontario, Canada. Information
Report GLC-X-10, 45p.
"""

from typing import Union, List


def crown_fuel_consumption(
    fueltype: Union[str, List[str]],
    cfl: Union[float, List[float]],
    cfb: Union[float, List[float]],
    pc: Union[float, List[float]],
    pdf: Union[float, List[float]]
) -> Union[float, List[float]]:
    """
    Calculate Crown Fuel Consumption.

    Args:
        fueltype: The Fire Behaviour Prediction FuelType
        cfl: Crown Fuel Load (kg/m^2)
        cfb: Crown Fraction Burned (0-1)
        pc: Percent Conifer (%)
        pdf: Percent Dead Balsam Fir (%)

    Returns:
        CFC: Crown Fuel Consumption (kg/m^2)
    """
    # Eq. 66a (Wotton 2009) - Crown Fuel Consumption (CFC)
    cfc = [c * f for c, f in zip(cfl, cfb)] if isinstance(cfl, list) else cfl * cfb

    if isinstance(fueltype, list):
        result = [0.0] * len(fueltype)
        for i in range(len(fueltype)):
            ft = fueltype[i]
            cfc_val = cfc[i] if isinstance(cfc, list) else cfc
            pc_val = pc[i] if isinstance(pc, list) else pc
            pdf_val = pdf[i] if isinstance(pdf, list) else pdf

            if ft in ["M1", "M2"]:
                # Eq. 66b (Wotton 2009) - CFC for M1/M2 types
                result[i] = pc_val / 100 * cfc_val
            elif ft in ["M3", "M4"]:
                # Eq. 66c (Wotton 2009) - CFC for M3/M4 types
                result[i] = pdf_val / 100 * cfc_val
            else:
                result[i] = cfc_val
    else:
        if fueltype in ["M1", "M2"]:
            # Eq. 66b (Wotton 2009) - CFC for M1/M2 types
            cfc = pc / 100 * cfc
        elif fueltype in ["M3", "M4"]:
            # Eq. 66c (Wotton 2009) - CFC for M3/M4 types
            cfc = pdf / 100 * cfc
        # For other fuel types, cfc remains as calculated

    return cfc


def total_fuel_consumption(
    fueltype: Union[str, List[str]],
    cfl: Union[float, List[float]],
    cfb: Union[float, List[float]],
    sfc: Union[float, List[float]],
    pc: Union[float, List[float]],
    pdf: Union[float, List[float]],
    option: str = "TFC"
) -> Union[float, List[float]]:
    """
    Calculate Total Fuel Consumption.

    Args:
        fueltype: The Fire Behaviour Prediction FuelType
        cfl: Crown Fuel Load (kg/m^2)
        cfb: Crown Fraction Burned (0-1)
        sfc: Surface Fuel Consumption (kg/m^2)
        pc: Percent Conifer (%)
        pdf: Percent Dead Balsam Fir (%)
        option: Type of output ("TFC" or "CFC")

    Returns:
        TFC: Total (Surface + Crown) Fuel Consumption (kg/m^2) or CFC
    """
    cfc = crown_fuel_consumption(fueltype, cfl, cfb, pc, pdf)

    # Return CFC if requested
    if option == "CFC":
        return cfc

    # Eq. 67 (FCFDG 1992) - Total Fuel Consumption
    tfc = [s + c for s, c in zip(sfc, cfc)] if isinstance(sfc, list) else sfc + cfc
    return tfc
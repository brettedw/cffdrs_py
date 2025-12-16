import math

def buildup_effect(FUELTYPE, BUI):
    """
    Build Up Effect Calculator

    Computes the Buildup Effect on Fire Spread Rate. All variables names are laid out in the same manner as Forestry Canada Fire Danger Group (FCFDG)(1992).

    Args:
        FUELTYPE: The Fire Behaviour Prediction FuelType
        BUI: The Buildup Index value

    Returns:
        BE: Build up effect
    """
    d = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "D1", "M1", "M2", "M3", "M4", "S1", "S2", "S3", "O1A", "O1B"]
    BUIo = [72, 64, 62, 66, 56, 62, 106, 32, 50, 50, 50, 50, 38, 63, 31, 1, 1]
    Q = [0.9, 0.7, 0.75, 0.8, 0.8, 0.8, 0.85, 0.9, 0.8, 0.8, 0.8, 0.8, 0.75, 0.75, 0.75, 1.0, 1.0]
    fuel_dict = dict(zip(d, zip(BUIo, Q)))
    BE = []
    for ft, bui in zip(FUELTYPE, BUI):
        if ft in fuel_dict and bui > 0 and fuel_dict[ft][0] > 0:
            BE.append(math.exp(50 * math.log(fuel_dict[ft][1]) * (1 / bui - 1 / fuel_dict[ft][0])))
        else:
            BE.append(1)
    return BE
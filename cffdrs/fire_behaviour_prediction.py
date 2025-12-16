"""
Fire Behaviour Prediction System Calculation

This module contains the primary function for calculating FBP for a single timestep.
Not all equations are calculated within this function, but have been broken down further.
"""

import math
import warnings
from typing import Dict, List, Literal, Optional, Any, Union

from cffdrs.CFBcalc import crown_fraction_burned
from cffdrs.Slopecalc import slope_adjustment
from cffdrs.back_rate_of_spread import back_rate_of_spread
from cffdrs.buildup_effect import buildup_effect
from cffdrs.crown_base_height import crown_base_height
from cffdrs.crown_fuel_load import crown_fuel_load
from cffdrs.distance_at_time import distance_at_time
from cffdrs.fire_intensity import fire_intensity
from cffdrs.flank_rate_of_spread import flank_rate_of_spread
from cffdrs.foliar_moisture_content import foliar_moisture_content
from cffdrs.initial_spread_index import initial_spread_index
from cffdrs.length_to_breadth import length_to_breadth
from cffdrs.length_to_breadth_at_time import length_to_breadth_at_time
from cffdrs.rate_of_spread import rate_of_spread_extended
from cffdrs.rate_of_spread_at_time import rate_of_spread_at_time
from cffdrs.surface_fuel_consumption import surface_fuel_consumption
from cffdrs.total_fuel_consumption import total_fuel_consumption

OutputType = Literal["Primary", "Secondary", "All", "P", "S", "A", "RAZ0", "WSV0"]


def fire_behaviour_prediction(input: Optional[Dict[str, Any]] = None, output: OutputType = "Primary") -> Dict[str, Any]:
    """
    Fire Behavior Prediction System calculations.

    Args:
        input: Dictionary of required and optional information needed to calculate FBP function.
                Keys are column names, values are lists of values or single values (for single calculations).
        output: What fbp outputs to return. Options are "Primary", "Secondary", "All", "P", "S", "A", "RAZ0", "WSV0". Default: "Primary"

    Returns:
        Dictionary with FBP outputs, keys as column names, values as lists or single values matching input format.
    """
    # Quite often users will have a data frame called "input" already attached
    # to the workspace. To mitigate this, we remove that if it exists, and warn
    # the user of this case.
    # In Python, we don't have attached datasets like R, so skip this.

    output = output.upper()

    # if input does not exist, then set defaults
    if input is None:
        input = {
            "FUELTYPE": ["C2"], "ACCEL": [0], "DJ": [180], "D0": [0], "ELV": [0], "BUIEFF": [1],
            "HR": [1], "FFMC": [90], "ISI": [0], "BUI": [60], "WS": [10], "WD": [0], "GS": [0],
            "ASPECT": [0], "PC": [50], "PDF": [35], "CC": [80], "GFL": [0.35], "CBH": [3], "CFL": [1],
            "LAT": [55], "LONG": [-120], "FMC": [0], "THETA": [0]
        }
        input["FUELTYPE"] = [str(x) for x in input["FUELTYPE"]]

    # set local scope variables from the parameters for simpler referencing
    # Convert keys to upper
    input_upper = {k.upper(): v for k, v in input.items()}

    # Check if input is scalar (single values instead of lists)
    is_scalar = all(not isinstance(v, list) for v in input_upper.values()) if input_upper else False
    if is_scalar:
        input_upper = {k: [v] for k, v in input_upper.items()}

    ID = input_upper.get("ID", [None] * len(next(iter(input_upper.values()))))
    FUELTYPE = input_upper.get("FUELTYPE", [])
    FFMC = input_upper.get("FFMC", [])
    BUI = input_upper.get("BUI", [])
    WS = input_upper.get("WS", [])
    WD = input_upper.get("WD", [])
    FMC = input_upper.get("FMC", [])
    GS = input_upper.get("GS", [])
    LAT = input_upper.get("LAT", [])
    LONG = input_upper.get("LONG", [])
    ELV = input_upper.get("ELV", [])
    DJ = input_upper.get("DJ", [])
    D0 = input_upper.get("D0", [])
    SD = input_upper.get("SD", [])
    SH = input_upper.get("SH", [])
    HR = input_upper.get("HR", [])
    PC = input_upper.get("PC", [])
    PDF = input_upper.get("PDF", [])
    GFL = input_upper.get("GFL", [])
    CC = input_upper.get("CC", [])
    THETA = input_upper.get("THETA", [])
    ACCEL = input_upper.get("ACCEL", [])
    ASPECT = input_upper.get("ASPECT", [])
    BUIEFF = input_upper.get("BUIEFF", [])
    CBH = input_upper.get("CBH", [])
    CFL = input_upper.get("CFL", [])
    ISI = input_upper.get("ISI", [])

    n0 = len(FUELTYPE) if FUELTYPE else 0

    ############################################################################
    #                         BEGIN
    # Set warnings for missing and required input variables.
    # Set defaults for inputs that are not already set.
    ############################################################################
    if not FUELTYPE or all(x is None for x in FUELTYPE):
        warnings.warn("FuelType is a required input, default FuelType = C2 is used in the calculation")
        FUELTYPE = ["C2"] * n0

    FUELTYPE = [str(x).upper() for x in FUELTYPE]

    if not FFMC or all(x is None for x in FFMC):
        warnings.warn("FFMC is a required input, default FFMC = 90 is used in the calculation")
        FFMC = [90] * n0

    if not BUI or all(x is None for x in BUI):
        warnings.warn("BUI is a required input, default BUI = 60 is used in the calculation")
        BUI = [60] * n0

    if not WS or all(x is None for x in WS):
        warnings.warn("WS is a required input, WS = 10 km/hr is used in the calculation")
        WS = [10] * n0

    if not GS or all(x is None for x in GS):
        warnings.warn("GS is a required input, GS = 0 is used in the calculation")
        GS = [0] * n0

    if not LAT or all(x is None for x in LAT):
        warnings.warn("LAT is a required input, default LAT=55 is used in the calculation")
        LAT = [55] * n0

    if not LONG or all(x is None for x in LONG):
        warnings.warn("LONG is a required input, LONG = -120 is used in the calculation")
        LONG = [-120] * n0

    if not DJ or all(x is None for x in DJ):
        warnings.warn("Dj is a required input, Dj = 180 is used in the calculation")
        DJ = [180] * n0

    if not ASPECT or all(x is None for x in ASPECT):
        warnings.warn("Aspect is a required input, Aspect = 0 is used in the calculation")
        ASPECT = [0] * n0

    WD = WD if WD else [0] * n0
    FMC = FMC if FMC else [0] * n0
    ELV = ELV if ELV else [0] * n0
    SD = SD if SD else [0] * n0
    SH = SH if SH else [0] * n0
    D0 = D0 if D0 else [0] * n0
    HR = HR if HR else [1] * n0
    PC = PC if PC else [50] * n0
    PDF = PDF if PDF else [35] * n0
    GFL = GFL if GFL else [0.35] * n0
    CC = CC if CC else [80] * n0
    THETA = THETA if THETA else [0] * n0
    ACCEL = ACCEL if ACCEL else [0] * n0
    BUIEFF = BUIEFF if BUIEFF else [1] * n0
    CBH = CBH if CBH else [0] * n0
    CFL = CFL if CFL else [0] * n0
    ISI = ISI if ISI else [0] * n0

    # Convert Wind Direction from degrees to radians
    WD = [x * math.pi / 180 if x is not None else 0 for x in WD]
    # Convert Theta from degrees to radians
    THETA = [x * math.pi / 180 if x is not None else 0 for x in THETA]
    ASPECT = [0 if x is None else x for x in ASPECT]
    ASPECT = [x + 360 if x < 0 else x for x in ASPECT]
    # Convert Aspect from degrees to radians
    ASPECT = [x * math.pi / 180 for x in ASPECT]
    ACCEL = [0 if x is None or x < 0 else x for x in ACCEL]
    if any(x not in [0, 1] for x in ACCEL if x is not None):
        warnings.warn("Input variable Accel is out of range, will be assigned to 1")
    ACCEL = [1 if x not in [0, 1] else x for x in ACCEL]
    DJ = [0 if x < 0 or x > 366 else x for x in DJ]
    DJ = [180 if x is None else x for x in DJ]
    D0 = [0 if x is None or x < 0 or x > 366 else x for x in D0]
    ELV = [0 if x < 0 or x > 10000 else x for x in ELV]
    ELV = [0 if x is None else x for x in ELV]
    BUIEFF = [0 if x <= 0 else 1 for x in BUIEFF]
    BUIEFF = [1 if x is None else x for x in BUIEFF]
    HR = [-x if x < 0 else x for x in HR]
    HR = [24 if x > 366 * 24 else x for x in HR]
    HR = [0 if x is None else x for x in HR]
    FFMC = [0 if x < 0 or x > 101 else x for x in FFMC]
    FFMC = [90 if x is None else x for x in FFMC]
    ISI = [0 if x is None or x < 0 or x > 300 else x for x in ISI]
    BUI = [0 if x < 0 or x > 1000 else x for x in BUI]
    BUI = [60 if x is None else x for x in BUI]
    WS = [0 if x < 0 or x > 300 else x for x in WS]
    WS = [10 if x is None else x for x in WS]
    WD = [0 if x is None or x < -2 * math.pi or x > 2 * math.pi else x for x in WD]
    GS = [0 if x is None or x < 0 or x > 200 else x for x in GS]
    GS = [0 if ASPECT[i] < -2 * math.pi or ASPECT[i] > 2 * math.pi else GS[i] for i in range(len(GS))]
    PC = [50 if x is None or x < 0 or x > 100 else x for x in PC]
    PDF = [35 if x is None or x < 0 or x > 100 else x for x in PDF]
    CC = [95 if x <= 0 or x > 100 else x for x in CC]
    CC = [80 if x is None else x for x in CC]
    GFL = [0.35 if x is None or x <= 0 or x > 100 else x for x in GFL]
    LAT = [0 if x < -90 or x > 90 else x for x in LAT]
    LAT = [55 if x is None else x for x in LAT]
    LONG = [0 if x < -180 or x > 360 else x for x in LONG]
    LONG = [-120 if x is None else x for x in LONG]
    THETA = [0 if x is None or x < -2 * math.pi or x > 2 * math.pi else x for x in THETA]
    SD = [-999 if x < 0 or x > 1e5 else x for x in SD]
    SD = [0 if x is None else x for x in SD]
    SH = [-999 if x < 0 or x > 100 else x for x in SH]
    SH = [0 if x is None else x for x in SH]

    FUELTYPE = [x.replace("-", "").replace(" ", "") for x in FUELTYPE]
    if any(x is None for x in FUELTYPE):
        warnings.warn("FuelType contains NA, using C2 (default) in the calculation")
        FUELTYPE = ["C2" if x is None else x for x in FUELTYPE]

    ############################################################################
    #                         END
    ############################################################################
    ############################################################################
    #                         START
    # Corrections
    ############################################################################
    # Convert hours to minutes
    HR = [x * 60 for x in HR]
    # Corrections to reorient Wind Azimuth(WAZ) and Uphill slope azimuth(SAZ)
    WAZ = [x + math.pi for x in WD]
    WAZ = [x - 2 * math.pi if x > 2 * math.pi else x for x in WAZ]
    SAZ = [x + math.pi for x in ASPECT]
    SAZ = [x - 2 * math.pi if x > 2 * math.pi else x for x in SAZ]
    # Any negative longitudes (western hemisphere) are translated to positive longitudes
    LONG = [-x if x < 0 else x for x in LONG]

    ############################################################################
    #                         END
    ############################################################################
    ############################################################################
    #                         START
    # Initializing variables
    ############################################################################
    SFC = [0] * len(LONG)
    TFC = [0] * len(LONG)
    HFI = [0] * len(LONG)
    CFB = [0] * len(LONG)
    ROS = [0] * len(LONG)
    RAZ = [-999] * len(LONG)
    validOutTypes = ["SECONDARY", "ALL", "S", "A", "RAZ0", "WSV0"]
    if output in validOutTypes:
        FROS = [0] * len(LONG)
        BROS = [0] * len(LONG)
        TROS = [0] * len(LONG)
        HROSt = [0] * len(LONG)
        FROSt = [0] * len(LONG)
        BROSt = [0] * len(LONG)
        TROSt = [0] * len(LONG)
        FCFB = [0] * len(LONG)
        BCFB = [0] * len(LONG)
        TCFB = [0] * len(LONG)
        FFI = [0] * len(LONG)
        BFI = [0] * len(LONG)
        TFI = [0] * len(LONG)
        FTFC = [0] * len(LONG)
        BTFC = [0] * len(LONG)
        TTFC = [0] * len(LONG)
        TI = [-999] * len(LONG)
        FTI = [-999] * len(LONG)
        BTI = [-999] * len(LONG)
        TTI = [-999] * len(LONG)
        LB = [-999] * len(LONG)
        WSV = [-999] * len(LONG)

    # Note: The following functions need to be imported or defined
    CBH = crown_base_height(FUELTYPE, CBH, SD, SH)
    CFL = crown_fuel_load(FUELTYPE, CFL)
    FMC_temp = foliar_moisture_content(LAT, LONG, ELV, DJ, D0)
    FMC = [FMC_temp[i] if FMC[i] <= 0 or FMC[i] > 120 or FMC[i] is None else FMC[i] for i in range(len(FMC))]
    FMC = [0 if FUELTYPE[i] in ["D1", "S1", "S2", "S3", "O1A", "O1B"] else FMC[i] for i in range(len(FMC))]

    ############################################################################
    #                         END
    ############################################################################

    # Calculate Surface fuel consumption (SFC)
    SFC = surface_fuel_consumption(FUELTYPE, FFMC, BUI, PC, GFL)
    # Disable BUI Effect if necessary
    BUI = [0 if BUIEFF[i] != 1 else BUI[i] for i in range(len(BUI))]
    slope_values = slope_adjustment(FUELTYPE, FFMC, BUI, WS, WAZ, GS, SAZ, FMC, SFC, PC, PDF, CC, CBH, ISI)
    # Calculate the net effective windspeed (WSV)
    WSV0 = slope_values["WSV"]
    if output == "WSV0":
        return {"WSV0": WSV0[0] if is_scalar else WSV0}
    WSV = [WSV0[i] if GS[i] > 0 and FFMC[i] > 0 else WS[i] for i in range(len(WS))]
    # Calculate the net effective wind direction (RAZ)
    RAZ0 = slope_values["RAZ"]
    if output == "RAZ0":
        return {"RAZ0": RAZ0[0] if is_scalar else RAZ0}
    RAZ = [RAZ0[i] if GS[i] > 0 and FFMC[i] > 0 else WAZ[i] for i in range(len(WAZ))]
    # Calculate or keep Initial Spread Index (ISI)
    isi_updates = []
    for i in range(len(ISI)):
        if ISI[i] > 0:
            isi_updates.append(ISI[i])
        else:
            isi_val = initial_spread_index(FFMC[i], WSV[i], True)
            isi_updates.append(isi_val[0] if isinstance(isi_val, list) else isi_val)
    ISI = isi_updates
    # HACK: C6 ROS depends on CFB so do this to not repeat calculations
    ros_vars = rate_of_spread_extended(FUELTYPE, ISI, BUI, FMC, SFC, PC, PDF, CC, CBH)
    ROS = ros_vars["ROS"]
    CFB = [ros_vars["CFB"][i] if CFL[i] > 0 else 0 for i in range(len(CFL))]
    CSI = ros_vars["CSI"]
    RSO = ros_vars["RSO"]
    # Calculate Total Fuel Consumption (TFC)
    TFC = total_fuel_consumption(FUELTYPE, CFL, CFB, SFC, PC, PDF)
    # Calculate Head Fire Intensity(HFI)
    HFI = fire_intensity(TFC, ROS)
    # Adjust Crown Fraction Burned
    CFB = [-CFB[i] if HR[i] < 0 else CFB[i] for i in range(len(CFB))]
    # Adjust RAZ
    RAZ = [x * 180 / math.pi for x in RAZ]
    RAZ = [0 if x == 360 else x for x in RAZ]
    # Calculate Fire Type (S = Surface, C = Crowning, I = Intermittent Crowning)
    FD = ["I"] * len(CFB)
    FD = ["S" if CFB[i] < 0.1 else FD[i] for i in range(len(FD))]
    FD = ["C" if CFB[i] >= 0.9 else FD[i] for i in range(len(FD))]
    # Calculate Crown Fuel Consumption(CFC)
    CFC = total_fuel_consumption(FUELTYPE, CFL, CFB, SFC, PC, PDF, option="CFC")
    # Calculate the Secondary Outputs
    if output in ["SECONDARY", "ALL", "S", "A"]:
        # Eq. 39 (FCFDG 1992) Calculate Spread Factor (GS is group slope)
        SF = [10 if GS[i] >= 70 else math.exp(3.533 * (GS[i] / 100)**1.2) for i in range(len(GS))]
        # Calculate The Buildup Effect
        BE = buildup_effect(FUELTYPE, BUI)
        # Calculate length to breadth ratio
        LB = length_to_breadth(FUELTYPE, WSV)
        LBt = [LB[i] if ACCEL[i] == 0 else length_to_breadth_at_time(FUELTYPE[i], LB[i], HR[i], CFB[i]) for i in range(len(LB))]
        # Calculate Back fire rate of spread (BROS)
        BROS = back_rate_of_spread(FUELTYPE, FFMC, BUI, WSV, FMC, SFC, PC, PDF, CC, CBH)
        # Calculate Flank fire rate of spread (FROS)
        FROS = flank_rate_of_spread(ROS, BROS, LB)
        # Calculate the eccentricity
        E = [math.sqrt(1 - 1 / LB[i] / LB[i]) for i in range(len(LB))]
        # Calculate the rate of spread towards angle theta (TROS)
        TROS = [ROS[i] * (1 - E[i]) / (1 - E[i] * math.cos(THETA[i] - RAZ[i])) for i in range(len(ROS))]
        # Calculate rate of spread at time t for Flank, Back of fire and at angle theta.
        ROSt = [ROS[i] if ACCEL[i] == 0 else rate_of_spread_at_time(FUELTYPE[i], ROS[i], HR[i], CFB[i]) for i in range(len(ROS))]
        BROSt = [BROS[i] if ACCEL[i] == 0 else rate_of_spread_at_time(FUELTYPE[i], BROS[i], HR[i], CFB[i]) for i in range(len(BROS))]
        FROSt = [FROS[i] if ACCEL[i] == 0 else flank_rate_of_spread([ROSt[i]], [BROSt[i]], [LBt[i]])[0] for i in range(len(FROS))]
        # Calculate rate of spread towards angle theta at time t (TROSt)
        TROSt = [TROS[i] if ACCEL[i] == 0 else (ROSt[i] * (1 - math.sqrt(1 - 1 / LBt[i] / LBt[i])) / (1 - math.sqrt(1 - 1 / LBt[i] / LBt[i]) * math.cos(THETA[i] - RAZ[i]))) for i in range(len(TROS))]
        # Calculate Crown Fraction Burned for Flank, Back of fire and angle theta.
        FCFB = [0 if CFL[i] == 0 else (0 if FUELTYPE[i] == "C6" else crown_fraction_burned(FROS[i], RSO[i])) for i in range(len(FROS))]
        BCFB = [0 if CFL[i] == 0 else (0 if FUELTYPE[i] == "C6" else crown_fraction_burned(BROS[i], RSO[i])) for i in range(len(BROS))]
        TCFB = [0 if CFL[i] == 0 else (0 if FUELTYPE[i] == "C6" else crown_fraction_burned(TROS[i], RSO[i])) for i in range(len(TROS))]
        # Calculate Total fuel consumption for the Flank fire, Back fire and at angle theta
        FTFC = total_fuel_consumption(FUELTYPE, CFL, FCFB, SFC, PC, PDF)
        BTFC = total_fuel_consumption(FUELTYPE, CFL, BCFB, SFC, PC, PDF)
        TTFC = total_fuel_consumption(FUELTYPE, CFL, TCFB, SFC, PC, PDF)
        # Calculate the Fire Intensity at the Flank, Back and at angle theta fire
        FFI = fire_intensity(FTFC, FROS)
        BFI = fire_intensity(BTFC, BROS)
        TFI = fire_intensity(TTFC, TROS)
        # Calculate Rate of spread at time t for the Head, Flank, Back of fire and at angle theta.
        HROSt = [-ROSt[i] if HR[i] < 0 else ROSt[i] for i in range(len(ROSt))]
        FROSt = [-FROSt[i] if HR[i] < 0 else FROSt[i] for i in range(len(FROSt))]
        BROSt = [-BROSt[i] if HR[i] < 0 else BROSt[i] for i in range(len(BROSt))]
        TROSt = [-TROSt[i] if HR[i] < 0 else TROSt[i] for i in range(len(TROSt))]

        # Calculate the elapsed time to crown fire initiation for Head, Flank, Back fire and at angle theta.
        a1 = [0.115 - (18.8 * CFB[i]**2.5 * math.exp(-8 * CFB[i])) for i in range(len(CFB))]
        TI = [math.log(max(1 - RSO[i] / ROS[i], 1)) / (-a1[i]) for i in range(len(a1))]
        a2 = [0.115 - (18.8 * FCFB[i]**2.5 * math.exp(-8 * FCFB[i])) for i in range(len(FCFB))]
        FTI = [math.log(max(1 - RSO[i] / FROS[i], 1)) / (-a2[i]) for i in range(len(a2))]
        a3 = [0.115 - (18.8 * BCFB[i]**2.5 * math.exp(-8 * BCFB[i])) for i in range(len(BCFB))]
        BTI = [math.log(max(1 - RSO[i] / BROS[i], 1)) / (-a3[i]) for i in range(len(a3))]
        a4 = [0.115 - (18.8 * TCFB[i]**2.5 * math.exp(-8 * TCFB[i])) for i in range(len(TCFB))]
        TTI = [math.log(max(1 - RSO[i] / TROS[i], 1)) / (-a4[i]) for i in range(len(a4))]

        # Fire spread distance for Head, Back, and Flank of fire
        DH = [distance_at_time(FUELTYPE[i], ROS[i], HR[i], CFB[i]) if ACCEL[i] == 1 else ROS[i] * HR[i] for i in range(len(ROS))]
        DB = [distance_at_time(FUELTYPE[i], BROS[i], HR[i], CFB[i]) if ACCEL[i] == 1 else BROS[i] * HR[i] for i in range(len(BROS))]
        DF = [(DH[i] + DB[i]) / (LBt[i] * 2) if ACCEL[i] == 1 else (DH[i] + DB[i]) / (LB[i] * 2) for i in range(len(DH))]

    # Create an id field if it does not exist
    if not ID or all(x is None for x in ID):
        ID = [str(i) for i in range(len(FUELTYPE))]

    # if Primary is selected, wrap the primary outputs into a data frame and return them
    if output in ["PRIMARY", "P"]:
        FBP = {
            "ID": ID,
            "CFB": CFB,
            "CFC": CFC,
            "FD": FD,
            "HFI": HFI,
            "RAZ": RAZ,
            "ROS": ROS,
            "SFC": SFC,
            "TFC": TFC
        }
        # Apply condition for WA, NF
        for key in ["CFB", "CFC", "HFI", "RAZ", "ROS", "SFC", "TFC"]:
            FBP[key] = [0 if FUELTYPE[i] in ["WA", "NF"] else FBP[key][i] for i in range(len(FBP[key]))]
        FBP["FD"] = ["NA" if FUELTYPE[i] in ["WA", "NF"] else FBP["FD"][i] for i in range(len(FBP["FD"]))]
    elif output in ["SECONDARY", "S"]:
        # If Secondary is selected, wrap the secondary outputs into a data frame and return them.
        FBP = {
            "ID": ID,
            "BE": BE,
            "SF": SF,
            "ISI": ISI,
            "FFMC": FFMC,
            "FMC": FMC,
            "D0": D0,
            "RSO": RSO,
            "CSI": CSI,
            "FROS": FROS,
            "BROS": BROS,
            "HROSt": HROSt,
            "FROSt": FROSt,
            "BROSt": BROSt,
            "FCFB": FCFB,
            "BCFB": BCFB,
            "FFI": FFI,
            "BFI": BFI,
            "FTFC": FTFC,
            "BTFC": BTFC,
            "TI": TI,
            "FTI": FTI,
            "BTI": BTI,
            "LB": LB,
            "LBt": LBt,
            "WSV": WSV,
            "DH": DH,
            "DB": DB,
            "DF": DF,
            "TROS": TROS,
            "TROSt": TROSt,
            "TCFB": TCFB,
            "TFI": TFI,
            "TTFC": TTFC,
            "TTI": TTI
        }
        for key in FBP:
            if key != "ID":
                FBP[key] = [0 if FUELTYPE[i] in ["WA", "NF"] else FBP[key][i] for i in range(len(FBP[key]))]
    elif output in ["ALL", "A"]:
        # If all outputs are selected, then wrap all outputs into a data frame and return it.
        FBP = {
            "ID": ID,
            "CFB": CFB,
            "CFC": CFC,
            "FD": FD,
            "HFI": HFI,
            "RAZ": RAZ,
            "ROS": ROS,
            "SFC": SFC,
            "TFC": TFC,
            "BE": BE,
            "SF": SF,
            "ISI": ISI,
            "FFMC": FFMC,
            "FMC": FMC,
            "D0": D0,
            "RSO": RSO,
            "CSI": CSI,
            "FROS": FROS,
            "BROS": BROS,
            "HROSt": HROSt,
            "FROSt": FROSt,
            "BROSt": BROSt,
            "FCFB": FCFB,
            "BCFB": BCFB,
            "FFI": FFI,
            "BFI": BFI,
            "FTFC": FTFC,
            "BTFC": BTFC,
            "TI": TI,
            "FTI": FTI,
            "BTI": BTI,
            "LB": LB,
            "LBt": LBt,
            "WSV": WSV,
            "DH": DH,
            "DB": DB,
            "DF": DF,
            "TROS": TROS,
            "TROSt": TROSt,
            "TCFB": TCFB,
            "TFI": TFI,
            "TTFC": TTFC,
            "TTI": TTI
        }
        for key in ["CFB", "CFC", "HFI", "RAZ", "ROS", "SFC", "TFC", "BE", "SF", "ISI", "FFMC", "FMC", "D0", "RSO", "CSI", "FROS", "BROS", "HROSt", "FROSt", "BROSt", "FCFB", "BCFB", "FFI", "BFI", "FTFC", "BTFC", "TI", "FTI", "BTI", "LB", "LBt", "WSV", "DH", "DB", "DF", "TROS", "TROSt", "TCFB", "TFI", "TTFC", "TTI"]:
            FBP[key] = [0 if FUELTYPE[i] in ["WA", "NF"] else FBP[key][i] for i in range(len(FBP[key]))]
        FBP["FD"] = ["NA" if FUELTYPE[i] in ["WA", "NF"] else FBP["FD"][i] for i in range(len(FBP["FD"]))]

    if is_scalar:
        FBP = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in FBP.items()}

    return FBP


def _FBPcalc(*args, **kwargs):
    """
    Deprecated function.
    """
    warnings.warn("_FBPcalc is deprecated, use fire_behaviour_prediction instead", DeprecationWarning)
    return fire_behaviour_prediction(*args, **kwargs)


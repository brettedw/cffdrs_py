


from cffdrs.fire_behaviour_prediction import fire_behaviour_prediction


def fbp(input=None, output="Primary", m=None, cores=1):
    """
    Fire Behavior Prediction System function

    Calculates the outputs from the Canadian Forest Fire Behavior Prediction (FBP) System (Forestry Canada Fire Danger Group 1992) based on given fire weather and fuel moisture conditions (from the Canadian Forest Fire Weather Index (FWI) System (Van Wagner 1987)), fuel type, date, and slope. Fire weather, for the purpose of FBP System calculation, comprises observations of 10 m wind speed and direction at the time of the fire, and two associated outputs from the Fire Weather Index System, the Fine Fuel Moisture Content (FFMC) and Buildup Index (BUI).

    Args:
        input: The input data, a data.frame containing fuel types, fire weather component, and slope (see below). Each vector of inputs defines a single FBP System prediction for a single fuel type and set of weather conditions. The data.frame can be used to evaluate the FBP System for a single fuel type and instant in time, or multiple records for a single point (e.g., one weather station, either hourly or daily for instance) or multiple points (multiple weather stations or a gridded surface). All input variables have to be named as listed below, but they are case insensitive, and do not have to be in any particular order. Fuel type is of type character; other arguments are numeric. Missing values in numeric variables could either be assigned as NA or leave as blank.
        output: FBP output offers 3 options (see details in Values section):
        m: Optimal number of pixels at each iteration of computation when nrow(input) >= 1000. Default m = NULL, where the function will assign m = 1000 when nrow(input) is between 1000 and 500,000, and m = 3000 otherwise. By including this option, the function is able to process large dataset more efficiently. The optimal value may vary with different computers.
        cores: Number of CPU cores (integer) used in the computation, default is 1. By signing cores > 1, the function will apply parallel computation technique provided by the foreach package, which significantly reduces the computation time for large input data (over a million records). For small dataset, cores=1 is actually faster.

    Returns:
        fbp returns a dataframe with primary, secondary, or all output variables, a combination of the primary and secondary outputs.
    """
    if input is None:
        input = {
            "FUELTYPE": ["C2"],
            "ACCEL": [0],
            "DJ": [180],
            "D0": [0],
            "ELV": [0],
            "BUIEFF": [1],
            "HR": [1],
            "FFMC": [90],
            "ISI": [0],
            "BUI": [60],
            "WS": [10],
            "WD": [0],
            "GS": [0],
            "ASPECT": [0],
            "PC": [50],
            "PDF": [35],
            "CC": [80],
            "GFL": [0.35],
            "CBH": [3],
            "CFL": [1],
            "LAT": [55],
            "LONG": [-120],
            "FMC": [0],
            "THETA": [0]
        }
    fullList = fire_behaviour_prediction(input, output)
    return fullList
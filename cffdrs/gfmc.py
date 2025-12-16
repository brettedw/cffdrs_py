"""
Grass Fuel Moisture Code

Calculates both the moisture content of the surface of a fully cured matted grass
layer and also an equivalent Grass Fuel Moisture Code (gfmc) (Wotton, 2009) to
create a parallel with the hourly ffmc. The calculation is based on hourly (or
sub-hourly) weather observations of temperature, relative humidity, wind speed,
rainfall, and solar radiation. The user must also estimate an initial value of
the gfmc for the layer. This function could be used for either one weather station
or multiple weather stations.

References:
    Wotton, B.M. 2009. A grass moisture model for the Canadian Forest Fire Danger
    Rating System. In: Proceedings 8th Fire and Forest Meteorology Symposium,
    Kalispell, MT Oct 13-15, 2009. Paper 3-2.

    Van Wagner, C.E. 1977. A method of computing fine fuel moisture content
    throughout the diurnal cycle. Environment Canada, Canadian Forestry Service,
    Petawawa Forest Experiment Station, Chalk River, Ontario. Information Report
    PS-X-69.
"""

from typing import Union, List, Dict, Any
import copy

from cffdrs.grass_fuel_moisture import grass_fuel_moisture
from cffdrs.grass_fuel_moisture_code import grass_fuel_moisture_code


def gfmc(
    input: Dict[str, List[Any]],
    gfmc_old: Union[float, List[float]] = 85.0,
    batch: bool = True,
    time_step: float = 1.0,
    ro_fl: float = 0.3,
    out: str = "GFMCandMC"
) -> Union[Dict[str, List[Any]], List[Dict[str, Any]]]:
    """
    Calculate the Grass Fuel Moisture Code.

    Args:
        input: A dictionary containing input variables of weather observations.
               Keys are case-insensitive. Required keys: temp, rh, ws, prec, isol
        gfmc_old: Previous value of GFMC (default 85)
        batch: Whether the computation is iterative or single step (default True)
        time_step: Time step in hours (default 1.0)
        ro_fl: Nominal fuel load of the fine fuel layer (default 0.3 kg/m^2)
        out: Output format - "GFMCandMC", "MC", "GFMC", or "ALL"

    Returns:
        GFMC and moisture content values in requested format
    """
    # Convert input keys to lowercase for consistency
    input_lower = {k.lower(): v for k, v in input.items()}

    # Required columns
    required_cols = ['temp', 'rh', 'ws', 'prec', 'isol']
    missing_cols = [col for col in required_cols if col not in input_lower]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    # Extract data
    temp = input_lower['temp']
    rh = input_lower['rh']
    ws = input_lower['ws']
    prec = input_lower['prec']
    isol = input_lower['isol']

    # Check for batch processing
    if batch:
        if 'id' in input_lower:
            n = len(set(input_lower['id']))
            # Check if stations have consistent data lengths
            station_counts = {}
            for station_id in input_lower['id']:
                station_counts[station_id] = station_counts.get(station_id, 0) + 1
            if len(set(station_counts.values())) > 1:
                raise ValueError("Multiple stations must have the same number of observations")
        else:
            n = 1
    else:
        n = len(temp)

    # Validate data length consistency
    data_lengths = [len(input_lower[col]) for col in required_cols]
    if len(set(data_lengths)) > 1:
        raise ValueError("All input columns must have the same length")

    if len(temp) % n != 0:
        print("Warning: Input data length does not match number of weather stations")

    # Handle GFMCold parameter
    if isinstance(gfmc_old, (int, float)):
        gfmc_old = [float(gfmc_old)] * n
    elif len(gfmc_old) == 1 and n > 1:
        print("Warning: One GFMCold value for multiple weather stations")
        gfmc_old = gfmc_old * n
    elif len(gfmc_old) != n:
        raise ValueError("Number of GFMCold values doesn't match number of weather stations")

    # Validate output type
    valid_out_types = ["GFMCandMC", "MC", "GFMC", "ALL"]
    if out not in valid_out_types:
        raise ValueError(f"'{out}' is an invalid output type. Valid types: {valid_out_types}")

    # Get the length of the data stream
    n0 = len(temp) // n
    gfmc_values = []
    mc_values = []

    current_gfmc_old = gfmc_old.copy()

    # Iterate through time steps
    for i in range(n0):
        # Get data for all stations at this time step
        start_idx = n * i
        end_idx = n * (i + 1)

        temp_step = temp[start_idx:end_idx]
        rh_step = rh[start_idx:end_idx]
        ws_step = ws[start_idx:end_idx]
        prec_step = prec[start_idx:end_idx]
        isol_step = isol[start_idx:end_idx]

        # Calculate moisture content
        mc = grass_fuel_moisture(
            temp=temp_step,
            rh=rh_step,
            ws=ws_step,
            prec=prec_step,
            isol=isol_step,
            gfmc_old=current_gfmc_old,
            time_step=time_step,
            ro_fl=ro_fl
        )

        # Calculate GFMC
        gfmc_step = grass_fuel_moisture_code(mc)

        # Update for next iteration
        if isinstance(gfmc_step, list):
            current_gfmc_old = gfmc_step
        else:
            current_gfmc_old = [gfmc_step]

        gfmc_values.extend(gfmc_step if isinstance(gfmc_step, list) else [gfmc_step])
        mc_values.extend(mc if isinstance(mc, list) else [mc])

    # Return requested output format
    if out == "ALL":
        result = copy.deepcopy(input)
        result['GFMC'] = gfmc_values
        result['MC'] = mc_values
        return result
    elif out == "GFMC":
        return {'GFMC': gfmc_values}
    elif out == "MC":
        return {'MC': mc_values}
    else:  # GFMCandMC
        return {'GFMC': gfmc_values, 'MC': mc_values}
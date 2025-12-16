

def buildup_index(dmc, dc):
    """
    Build Up Index Calculator

    Buildup Index Calculation. All code is based on a C code library that was written by Canadian Forest Service Employees, which was originally based on the Fortran code listed in the reference below. All equations in this code refer to that document.

    Args:
        dc: Drought Code (single value or list)
        dmc: Duff Moisture Code (single value or list)

    Returns:
        Build Up Index value(s)
    """
    # Handle single values by converting to lists
    single_input = False
    if not isinstance(dmc, list):
        dmc = [dmc]
        single_input = True
    if not isinstance(dc, list):
        dc = [dc]

    bui1 = []
    for dmc_val, dc_val in zip(dmc, dc):
        if dmc_val == 0 and dc_val == 0:
            bui1.append(0)
        elif dmc_val == 0 or dc_val == 0:
            bui1.append(0)
        else:
            bui1.append(0.8 * dc_val * dmc_val / (dmc_val + 0.4 * dc_val))

    p = [(dmc_val - bui1[i]) / dmc_val if dmc_val != 0 else 0 for i, dmc_val in enumerate(dmc)]
    cc = []
    for dmc_val in dmc:
        if dmc_val < 0:
            cc_val = 0.92  # Avoid complex numbers for negative dmc
        else:
            cc_val = 0.92 + ((0.0114 * dmc_val)**1.7)
        cc.append(cc_val)
    bui0 = [dmc_val - cc[i] * p[i] for i, dmc_val in enumerate(dmc)]
    bui0 = [max(0, bui0_val) for bui0_val in bui0]  # Ensure non-negative
    bui1 = [bui0[i] if bui1[i] < dmc[i] else bui1[i] for i in range(len(bui1))]

    # Return single value if single inputs, otherwise return list
    return bui1[0] if single_input else bui1
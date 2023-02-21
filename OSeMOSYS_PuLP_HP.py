# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Dennis Dreier, Copyright 2020
# OSeMOSYS version: OSeMOSYS_2017_11_08

__doc__ = """

========================================================================================================================

    OSeMOSYS-PuLP: A Stochastic Modeling Framework for Long-Term Energy Systems Modeling

========================================================================================================================

    OSeMOSYS-PuLP-HP

    This is the high performance (HP) version of OSeMOSYS-PuLP
    This is a BETA version.

========================================================================================================================

    OSeMOSYS-PuLP: A Stochastic Modeling Framework for Long-Term Energy Systems Modeling

    Please cite this software by using the following reference of the original scientific article:

    Dennis Dreier, Mark Howells, OSeMOSYS-PuLP: A Stochastic Modeling Framework for Long-Term Energy Systems Modeling.
    Energies 2019, 12, 1382, https://doi.org/10.3390/en12071382

    Additional references to be cited for the OSeMOSYS modelling framework (see DOI links for complete references):
    Howells et al. (2011), https://doi.org/10.1016/j.enpol.2011.06.033
    Gardumi et al. (2018), https://doi.org/10.1016/j.esr.2018.03.005

    Other sources:
    OSeMOSYS GitHub: https://github.com/OSeMOSYS/
    OSeMOSYS website: http://www.osemosys.org/
    OpTIMUS community: http://www.optimus.community/

========================================================================================================================

"""

import os
import datetime as dt
import logging
import numpy as np
import pandas as pd
import pulp
import itertools

logging.basicConfig(level=logging.DEBUG)
logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\tOSeMOSYS-PuLP-HP started.")

# ----------------------------------------------------------------------------------------------------------------------
#	 SETUP - DATA SOURCES and MONTE CARLO SIMULATION
# ----------------------------------------------------------------------------------------------------------------------

# Input data

inputFile = "Test_case_Input.xlsx"  # Update with actual filename
inputDir = "Input_Data"
modelName = inputFile.split('.')[0]
sheetSets = "SETS"
sheetParams = "PARAMETERS"
sheetParamsDefault = "PARAMETERS_DEFAULT"
sheetMcs = "MCS"
sheetMcsNum = "MCS_num"
outputDir = "Output_Data"

# Output data
save_as_csv = True  # True: Output data will be saved as CSV file; False: No saving. Note: Rapid process.
save_as_excel = False  # True: Output data will be saved as Excel file; False: No saving. Note: Takes a lot of time.

# ----------------------------------------------------------------------------------------------------------------------
#    FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def createParameter(_df, _name):
    return _df[_df['PARAM'] == _name].set_index('INDEX').to_dict()['VALUE']


def createVariable(_name, _v):
    return newVarDict(_name, _v[_name]['lb'], _v[_name]['ub'], _v[_name]['cat'], _v[_name]['sets'])


def createTuple(_df, _set_name):
    if _set_name in ['DAYTYPE', 'DAILYTIMEBRACKET', 'SEASON', 'MODE_OF_OPERATION', 'YEAR', 'TIMESLICE']:
        return tuple([str(int(float(x))) for x in _df[_set_name] if x != 'nan'])
    else:
        return tuple([x for x in _df[_set_name] if x != 'nan'])


def permutateSets(_sets_list):
    """ Permutation of sets """
    return tuple(itertools.product(*_sets_list))


def ci(_tuple):
    """ Combine indices """
    return "-".join([str(i) for i in _tuple])


def newVarDict(_name, _lb, _ub, _cat, _sets):
    """
    This function create a dictionary for a variable having a lower bound (lb),
    upper bound (ub), category (cat), using combined indices from the SETS
    """
    return {ci(v): pulp.LpVariable(f"{_name}_" + ci(v), lowBound=_lb, upBound=_ub, cat=_cat)
            for v in permutateSets(_sets)}


def loadData(filePath, sheetSets, sheetParams, sheetParamsDefault, sheetMcs, sheetMcsNum):
    """
    This function loads all data from the input data set to dataframes.
    """

    # Data: SETS
    sets_df = pd.read_excel(io=filePath, sheet_name=sheetSets)
    sets_df['REGION'] = sets_df['REGION'].astype(str)
    sets_df['REGION2'] = sets_df['REGION2'].astype(str)
    sets_df['DAYTYPE'] = sets_df['DAYTYPE'].astype(str)
    sets_df['EMISSION'] = sets_df['EMISSION'].astype(str)
    sets_df['FUEL'] = sets_df['FUEL'].astype(str)
    sets_df['DAILYTIMEBRACKET'] = sets_df['DAILYTIMEBRACKET'].astype(str)
    sets_df['SEASON'] = sets_df['SEASON'].astype(str)
    sets_df['TIMESLICE'] = sets_df['TIMESLICE'].astype(str)
    sets_df['MODE_OF_OPERATION'] = sets_df['MODE_OF_OPERATION'].astype(str)
    sets_df['STORAGE'] = sets_df['STORAGE'].astype(str)
    sets_df['TECHNOLOGY'] = sets_df['TECHNOLOGY'].astype(str)
    sets_df['YEAR'] = sets_df['YEAR'].astype(str)
    sets_df['FLEXIBLEDEMANDTYPE'] = sets_df['FLEXIBLEDEMANDTYPE'].astype(str)

    # Data: PARAMETERS
    df = pd.read_excel(io=filePath, sheet_name=sheetParams)
    df['PARAM'] = df['PARAM'].astype(str)
    df['VALUE'] = df['VALUE'].apply(pd.to_numeric, downcast='signed')
    df['REGION'] = df['REGION'].astype(str)
    df['REGION2'] = df['REGION2'].astype(str)
    df['DAYTYPE'] = df['DAYTYPE'].astype('Int64')
    df['DAYTYPE'] = df['DAYTYPE'].astype(str)
    df['EMISSION'] = df['EMISSION'].astype(str)
    df['FUEL'] = df['FUEL'].astype(str)
    df['DAILYTIMEBRACKET'] = df['DAILYTIMEBRACKET'].astype('Int64')
    df['DAILYTIMEBRACKET'] = df['DAILYTIMEBRACKET'].astype(str)
    df['SEASON'] = df['SEASON'].astype('Int64')
    df['SEASON'] = df['SEASON'].astype(str)
    df['TIMESLICE'] = df['TIMESLICE'].astype('Int64')
    df['TIMESLICE'] = df['TIMESLICE'].astype(str)
    df['MODE_OF_OPERATION'] = df['MODE_OF_OPERATION'].astype('Int64')
    df['MODE_OF_OPERATION'] = df['MODE_OF_OPERATION'].astype(str)
    df['STORAGE'] = df['STORAGE'].astype(str)
    df['TECHNOLOGY'] = df['TECHNOLOGY'].astype(str)
    df['YEAR'] = df['YEAR'].astype('Int64')

    # Data: Parameters default values
    defaults_df = pd.read_excel(io=filePath, sheet_name=sheetParamsDefault)
    defaults_df = defaults_df.fillna(0)
    defaults_df['PARAM'] = defaults_df['PARAM'].astype(str)
    defaults_df['VALUE'] = defaults_df['VALUE'].apply(pd.to_numeric, downcast='signed')

    # Data: Monte Carlo Simulation (MCS)
    mcs_df = pd.read_excel(io=filePath, sheet_name=sheetMcs)
    mcs_df['DEFAULT_SETTING'] = mcs_df['DEFAULT_SETTING'].apply(pd.to_numeric, downcast='signed')
    mcs_df['REL_SD'] = mcs_df['REL_SD'].astype('Int64')
    mcs_df['REL_MIN'] = mcs_df['REL_MIN'].astype('Int64')
    mcs_df['REL_MAX'] = mcs_df['REL_MAX'].astype('Int64')
    mcs_df['DISTRIBUTION'] = mcs_df['DISTRIBUTION'].astype(str)
    mcs_df['ARRAY'] = [[float(i) for i in str(x).split(",")] for x in mcs_df['ARRAY']]

    mcs_df['PARAM'] = mcs_df['PARAM'].astype(str)
    mcs_df['REGION'] = mcs_df['REGION'].astype(str)
    mcs_df['REGION2'] = mcs_df['REGION2'].astype(str)
    mcs_df['DAYTYPE'] = mcs_df['DAYTYPE'].astype('Int64')
    mcs_df['DAYTYPE'] = mcs_df['DAYTYPE'].astype(str)
    mcs_df['EMISSION'] = mcs_df['EMISSION'].astype(str)
    mcs_df['FUEL'] = mcs_df['FUEL'].astype(str)
    mcs_df['DAILYTIMEBRACKET'] = mcs_df['DAILYTIMEBRACKET'].astype('Int64')
    mcs_df['DAILYTIMEBRACKET'] = mcs_df['DAILYTIMEBRACKET'].astype(str)
    mcs_df['SEASON'] = mcs_df['SEASON'].astype('Int64')
    mcs_df['SEASON'] = mcs_df['SEASON'].astype(str)
    mcs_df['TIMESLICE'] = mcs_df['TIMESLICE'].astype(str)
    mcs_df['MODE_OF_OPERATION'] = mcs_df['MODE_OF_OPERATION'].astype('Int64')
    mcs_df['MODE_OF_OPERATION'] = mcs_df['MODE_OF_OPERATION'].astype(str)
    mcs_df['STORAGE'] = mcs_df['STORAGE'].astype(str)
    mcs_df['TECHNOLOGY'] = mcs_df['TECHNOLOGY'].astype(str)
    mcs_df['YEAR'] = mcs_df['YEAR'].astype('Int64')

    # Number of MCS simulations
    n_df = pd.read_excel(io=filePath, sheet_name=sheetMcsNum)
    n = n_df.at[0, 'MCS_num']
    return sets_df, df, defaults_df, mcs_df, n


def generateRandomData(_ref, _dist, _rel_sd, _rel_min, _rel_max, _array):
    """
    This function generates random data for the parameters included in the Monte Carlo Simulations.

    reference (format: float): mean for normal distribution, mode for both triangular and uniform distributions
    dist: type of distribution. Choose from: "normal", "triangular", "uniform" (format: string)
    rel_sd: relative standard deviation from mean or mode. Unit: percent as decimals (format: float)
    rel_min: relative minimum deviation from mean or mode. Unit: percent as decimals (format: float), must be a negative value
    rel_max: relative maximum deviation from mean or mode. Unit: percent as decimals (format: float), must be a positive value
    array: array with potential values. One value out of the array will be randomly chosen.
    ==================================================================================================================
    Note: To use the reference value without any distribution, then write as input in the excel file in the tab "MCS":
    Columns: PARAM: "parameter name", DEFAULT_SETTING:	"1", DIST: "normal", REL_SD: "0".
    This will make the code to choose the reference value as defined for the model without MCS.
    """

    if _dist == "normal":
        # mean, standard deviation, generate 1 value at the time
        value = np.random.normal(_ref, _rel_sd * _ref, 1)[0]
    elif _dist == "triangular":
        # minimum value, mode, maximum value, generate 1 value at the time
        value = np.random.triangular((1 + _rel_min) * _ref, _ref, (1 + _rel_max) * _ref, 1)[0]
    elif _dist == "uniform":
        # minimum value, maximum value, generate 1 value at the time
        value = np.random.uniform((1 + _rel_min) * _ref, (1 + _rel_max) * _ref, 1)[0]
    elif _dist == "choice":
        if len(_array) > 1:
            value = np.random.choice(_array)
        else:
            logging.error("ERROR: Review MCS_df array column. Expected length of array: larger than 1, but is: 0 or 1")
    else:
        logging.error("ERROR: Select an available distribution, review input data and/or add default input data for this parameter.")
        return

    # This if condition prevents input errors caused by negative values for the parameters
    if value >= 0:
        return value
    else:
        return 0


def saveResultsTemporary(_model, _scenario_i):
    """
    This function saves results from one simulation temporary.
    """

    df = pd.DataFrame()

    # Cost
    cost_df = pd.DataFrame(data={'NAME': ['Cost'],
                                 'VALUE': [_model.objective.value()],
                                 'INDICES': [[np.nan]],
                                 'ELEMENTS': [[np.nan]],
                                 'SCENARIO': [_scenario_i]
                                 })

    df = pd.concat([df, cost_df])

    # All other variables
    res = tuple([v for v in _model.variables() if v.name != "Cost"])

    names = []
    values = []
    indices = []
    elements = []
    scenarios = []

    for v in res:
        full_name = v.name.split('_')
        name = full_name[0]
        # logging.info(full_name)
        if not "dummy" in v.name:
            value = v.value()
            index = variables[str(name)]['indices']
            element = full_name[1:]
            scenario = _scenario_i

            names.append(name)
            values.append(value)
            indices.append(index)
            elements.append(element)
            scenarios.append(scenario)


    other_df = pd.DataFrame(data={'NAME': names,
                                 'VALUE': values,
                                 'INDICES': indices,
                                 'ELEMENTS': elements,
                                 'SCENARIO': scenarios
                                 })

    df = pd.concat([df, other_df])
    df['REGION'] = [e[i.index('r')] if 'r' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['REGION2'] = [e[i.index('rr')] if 'rr' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['DAYTYPE'] = [e[i.index('ld')] if 'ld' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['FUEL'] = [e[i.index('f')] if 'f' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['EMISSION'] = [e[i.index('e')] if 'e' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['DAILYTIMEBRACKET'] = [e[i.index('lh')] if 'lh' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['SEASON'] = [e[i.index('ls')] if 'ls' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['TIMESLICE'] = [e[i.index('l')] if 'l' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['MODE_OF_OPERATION'] = [e[i.index('m')] if 'm' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['STORAGE'] = [e[i.index('s')] if 's' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['TECHNOLOGY'] = [e[i.index('t')] if 't' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['YEAR'] = [e[i.index('y')] if 'y' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df.drop(columns={'INDICES', 'ELEMENTS'}, inplace=True)
    return df


def saveResultsToCSV(dataframe, fileDir, fileName):
    """
    This function saves all results to a CSV file.
    """
    _df = dataframe
    # Shorten abstract variable names
    _df['NAME'].replace(
        regex={'Total': 'Tot', 'Annual': 'Ann', 'Technology': 'Tech', 'Discounted': 'Disc', 'Production': 'Prod'},
        inplace=True)

    if not os.path.exists(fileDir):
        os.makedirs(fileDir)

        _df.to_csv(path_or_buf=os.path.join(fileDir, fileName), sep=',', index=False)
    return


def saveResultsToExcel(dataframe, fileDir, fileName):
    """
    This function saves all results to an Excel file.
    """
    _df = dataframe
    # Shorten abstract variable names to keep Excel worksheet name limit of 31 characters
    _df['NAME'].replace(
        regex={'Total': 'Tot', 'Annual': 'Ann', 'Technology': 'Tech', 'Discounted': 'Disc', 'Production': 'Prod', 'Penalty': 'Pen'},
        inplace=True)

    dataframe_list = [_df[_df['NAME'] == str(name)] for name in _df['NAME'].unique()]

    if not os.path.exists(fileDir):
        os.makedirs(fileDir)

    writer = pd.ExcelWriter(os.path.join(fileDir, fileName))

    for d, name in zip(dataframe_list, _df['NAME'].unique()):
        d.to_excel(writer, sheet_name=name, index=False)

    writer.save()
    return


# ----------------------------------------------------------------------------------------------------------------------
#    LOAD DATA
# ----------------------------------------------------------------------------------------------------------------------

inputPath = os.path.join(inputDir, inputFile)
sets_df, df, defaults_df, mcs_df, n = loadData(
    inputPath, sheetSets, sheetParams, sheetParamsDefault, sheetMcs, sheetMcsNum)
parameters_mcs = mcs_df['PARAM'].unique()  # list of parameters to be included in monte carlo simulation

logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
             f"Data is loaded.")

# ----------------------------------------------------------------------------------------------------------------------
#    SETS
# ----------------------------------------------------------------------------------------------------------------------

YEAR = createTuple(sets_df, 'YEAR')
TECHNOLOGY = createTuple(sets_df, 'TECHNOLOGY')
TIMESLICE = createTuple(sets_df, 'TIMESLICE')
FUEL = createTuple(sets_df, 'FUEL')
EMISSION = createTuple(sets_df, 'EMISSION')
MODE_OF_OPERATION = createTuple(sets_df, 'MODE_OF_OPERATION')
REGION = createTuple(sets_df, 'REGION')
REGION2 = createTuple(sets_df, 'REGION2')
SEASON = createTuple(sets_df, 'SEASON')
DAYTYPE = createTuple(sets_df, 'DAYTYPE')
DAILYTIMEBRACKET = createTuple(sets_df, 'DAILYTIMEBRACKET')
FLEXIBLEDEMANDTYPE = createTuple(sets_df, 'FLEXIBLEDEMANDTYPE')
STORAGE = createTuple(sets_df, 'STORAGE')

logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
             f"Sets are created.")

# ----------------------------------------------------------------------------------------------------------------------
#    PARAMETERS AND DATA
# ----------------------------------------------------------------------------------------------------------------------

df['INDEX'] = [ci([str(r), str(rr), str(ld), str(e), str(f), str(lh), str(ls), str(l), str(s), str(m), str(t), str(y)])\
                   .replace('nan-', '').replace('<NA>-', '').replace('-nan', '').replace('-<NA>', '')
               for r, rr, ld, e, f, lh, ls, l, s, m, t, y in
                 zip(df.REGION, df.REGION2, df.DAYTYPE, df.EMISSION, df.FUEL, df.DAILYTIMEBRACKET, df.SEASON,\
                     df.TIMESLICE, df.STORAGE, df.MODE_OF_OPERATION, df.TECHNOLOGY, df.YEAR)]

# Dictionaries for parameters
AccumulatedAnnualDemand = createParameter(df, 'AccumulatedAnnualDemand')
AnnualEmissionLimit = createParameter(df, 'AnnualEmissionLimit')
AnnualExogenousEmission = createParameter(df, 'AnnualExogenousEmission')
AvailabilityFactor = createParameter(df, 'AvailabilityFactor')
CapacityFactor = createParameter(df, 'CapacityFactor')
CapacityOfOneTechnologyUnit = createParameter(df, 'CapacityOfOneTechnologyUnit')
CapacityToActivityUnit = createParameter(df, 'CapacityToActivityUnit')
CapitalCost = createParameter(df, 'CapitalCost')
CapitalCostStorage = createParameter(df, 'CapitalCostStorage')
Conversionld = createParameter(df, 'Conversionld')
Conversionlh = createParameter(df, 'Conversionlh')
Conversionls = createParameter(df, 'Conversionls')
DaySplit = createParameter(df, 'DaySplit')
DaysInDayType = createParameter(df, 'DaysInDayType')
DepreciationMethod = createParameter(df, 'DepreciationMethod')
DiscountRateTech = createParameter(df, 'DiscountRateTech')
DiscountRateSto = createParameter(df, 'DiscountRateSto')
EmissionActivityRatio = createParameter(df, 'EmissionActivityRatio')
EmissionsPenalty = createParameter(df, 'EmissionsPenalty')
FixedCost = createParameter(df, 'FixedCost')
GIS_Losses = createParameter(df, 'GIS_Losses')
InputActivityRatio = createParameter(df, 'InputActivityRatio')
MinStorageCharge = createParameter(df, 'MinStorageCharge')
ModelPeriodEmissionLimit = createParameter(df, 'ModelPeriodEmissionLimit')
ModelPeriodExogenousEmission = createParameter(df, 'ModelPeriodExogenousEmission')
OperationalLife = createParameter(df, 'OperationalLife')
OperationalLifeStorage = createParameter(df, 'OperationalLifeStorage')
OutputActivityRatio = createParameter(df, 'OutputActivityRatio')
OutputModeofoperation = createParameter(df, 'OutputModeofoperation')
REMinProductionTarget = createParameter(df, 'REMinProductionTarget')
RETagFuel = createParameter(df, 'RETagFuel')
RETagTechnology = createParameter(df, 'RETagTechnology')
ReserveMargin = createParameter(df, 'ReserveMargin')
ReserveMarginTagFuel = createParameter(df, 'ReserveMarginTagFuel')
ReserveMarginTagTechnology = createParameter(df, 'ReserveMarginTagTechnology')
ResidualCapacity = createParameter(df, 'ResidualCapacity')
ResidualStorageCapacity = createParameter(df, 'ResidualStorageCapacity')
SpecifiedAnnualDemand = createParameter(df, 'SpecifiedAnnualDemand')
SpecifiedDemandProfile = createParameter(df, 'SpecifiedDemandProfile')
StorageLevelStart = createParameter(df, 'StorageLevelStart')
StorageMaxChargeRate = createParameter(df, 'StorageMaxChargeRate')
StorageMaxDischargeRate = createParameter(df, 'StorageMaxDischargeRate')
StorageMaxCapacity = createParameter(df, 'StorageMaxCapacity')
StorageLevelStart = createParameter(df, 'StorageLevelStart')
StorageL2D = createParameter(df, 'StorageL2D')
StorageUvalue = createParameter(df, 'StorageUvalue')
StorageFlowTemperature = createParameter(df, 'StorageFlowTemperature')
StorageReturnTemperature = createParameter(df, 'StorageReturnTemperature')
StorageAmbientTemperature = createParameter(df, 'StorageAmbientTemperature')
Storagetagheating = createParameter(df, 'Storagetagheating')
Storagetagcooling = createParameter(df, 'Storagetagcooling')
TechWithCapacityNeededToMeetPeakTS = createParameter(df, 'TechWithCapacityNeededToMeetPeakTS')
TechnologyFromStorage = createParameter(df, 'TechnologyFromStorage')
TechnologyToStorage = createParameter(df, 'TechnologyToStorage')
TotalAnnualMaxCapacity = createParameter(df, 'TotalAnnualMaxCapacity')
TotalAnnualMaxCapacityInvestment = createParameter(df, 'TotalAnnualMaxCapacityInvestment')
TotalAnnualMinCapacity = createParameter(df, 'TotalAnnualMinCapacity')
TotalAnnualMinCapacityInvestment = createParameter(df, 'TotalAnnualMinCapacityInvestment')
TotalTechnologyAnnualActivityLowerLimit = createParameter(df, 'TotalTechnologyAnnualActivityLowerLimit')
TotalTechnologyAnnualActivityUpperLimit = createParameter(df, 'TotalTechnologyAnnualActivityUpperLimit')
TotalTechnologyModelPeriodActivityLowerLimit = createParameter(df, 'TotalTechnologyModelPeriodActivityLowerLimit')
TotalTechnologyModelPeriodActivityUpperLimit = createParameter(df, 'TotalTechnologyModelPeriodActivityUpperLimit')
TradeRoute = createParameter(df, 'TradeRoute')
VariableCost = createParameter(df, 'VariableCost')
YearSplit = createParameter(df, 'YearSplit')

# Default values for parameters
dflt = defaults_df.set_index('PARAM').to_dict()['VALUE']

logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
             f"Parameters are created.")

# ----------------------------------------------------------------------------------------------------------------------
#    PERMUTATION OF SETS
# ----------------------------------------------------------------------------------------------------------------------

# Global sets
# REGION (no permutation needed for REGION)
REGION_FUEL_TIMESLICE_YEAR = permutateSets([REGION, FUEL, TIMESLICE, YEAR])
REGION_TECHNOLOGY_YEAR = permutateSets([REGION, TECHNOLOGY, YEAR])
REGION_TIMESLICE_TECHNOLOGY_YEAR = permutateSets([REGION, TIMESLICE, TECHNOLOGY, YEAR])
REGION_FUEL_TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR = permutateSets([REGION, FUEL, TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY, YEAR])
REGION_FUEL_TIMESLICE_TECHNOLOGY_YEAR = permutateSets([REGION, FUEL, TIMESLICE, TECHNOLOGY, YEAR])
REGION_REGION2_FUEL_TIMESLICE_YEAR = permutateSets([REGION, REGION2, FUEL, TIMESLICE, YEAR])
REGION_FUEL_YEAR = permutateSets([REGION, FUEL, YEAR])
REGION_REGION2_FUEL_YEAR = permutateSets([REGION, REGION2, FUEL, YEAR])
REGION_MODE_OF_OPERATION_TECHNOLOGY_YEAR = permutateSets([REGION, MODE_OF_OPERATION, TECHNOLOGY, YEAR])
REGION_DAYTYPE_DAILYTIMEBRACKET_SEASON_STORAGE_YEAR = permutateSets([REGION, DAYTYPE, DAILYTIMEBRACKET, SEASON, STORAGE, YEAR])
REGION_STORAGE = permutateSets([REGION, STORAGE])
REGION_STORAGE_YEAR = permutateSets([REGION, STORAGE, YEAR])
REGION_STORAGE_TIMESLICE_YEAR = permutateSets([REGION, STORAGE, TIMESLICE, YEAR])
REGION_SEASON_STORAGE_YEAR = permutateSets([REGION, SEASON, STORAGE, YEAR])
REGION_DAYTYPE_SEASON_STORAGE_YEAR = permutateSets([REGION, DAYTYPE, SEASON, STORAGE, YEAR])
REGION_YEAR = permutateSets([REGION, YEAR])
REGION_TECHNOLOGY = permutateSets([REGION, TECHNOLOGY])
REGION_TIMESLICE_YEAR = permutateSets([REGION, TIMESLICE, YEAR])
REGION_FUEL_TECHNOLOGY_YEAR = permutateSets([REGION, FUEL, TECHNOLOGY, YEAR])
REGION_EMISSION_MODE_OF_OPERATION_TECHNOLOGY_YEAR = permutateSets([REGION, EMISSION, MODE_OF_OPERATION, TECHNOLOGY, YEAR])
REGION_EMISSION_TECHNOLOGY_YEAR = permutateSets([REGION, EMISSION, TECHNOLOGY, YEAR])
REGION_EMISSION_YEAR = permutateSets([REGION, EMISSION, YEAR])
REGION_EMISSION = permutateSets([REGION, EMISSION])
# Local sets within equations
MODE_OF_OPERATION_YEAR = permutateSets([MODE_OF_OPERATION, YEAR])
TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY = permutateSets([TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY])
TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR = permutateSets([TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY, YEAR])
DAYTYPE_DAILYTIMEBRACKET_SEASON = permutateSets([DAYTYPE, DAILYTIMEBRACKET, SEASON])
DAYTYPE_DAILYTIMEBRACKET = permutateSets([DAYTYPE, DAILYTIMEBRACKET])
FUEL_TECHNOLOGY = permutateSets([FUEL, TECHNOLOGY])
FUEL_TIMESLICE = permutateSets([FUEL, TIMESLICE])
MODE_OF_OPERATION_TECHNOLOGY = permutateSets([ MODE_OF_OPERATION, TECHNOLOGY])
TIMESLICE_YEAR = permutateSets([ TIMESLICE, YEAR])

# ----------------------------------------------------------------------------------------------------------------------
#    MODEL CONSTRUCTION
# ----------------------------------------------------------------------------------------------------------------------

i = 0
while i <= n:

    # ====  Simulation loops  ====

    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                 f"Model run: {i}")

    # ------------------------------------------------------------------------------------------------------------------
    #    MODEL INITIALIZATION
    # ------------------------------------------------------------------------------------------------------------------

    model = pulp.LpProblem(modelName, pulp.LpMinimize)

    # ------------------------------------------------------------------------------------------------------------------
    #    MODEL VARIABLES
    # ------------------------------------------------------------------------------------------------------------------

    variables = {

        # ====  Net Present Cost  ====

        # 'Cost'

        # ====  Demands  ====

       'RateOfDemand': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},
       'Demand': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},

        # ====  Storage  ====

       'RateOfStorageCharge': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
       'RateOfStorageDischarge': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
       'NetChargeWithinYear': {'sets': [REGION, DAYTYPE, DAILYTIMEBRACKET, SEASON, STORAGE, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'ld', 'lh', 'ls', 's', 'y']},
       'NetChargeWithinDay': {'sets': [REGION, DAYTYPE, DAILYTIMEBRACKET, SEASON, STORAGE, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'ld', 'lh', 'ls', 's', 'y']},
       'StorageLevelYearStart': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'StorageLevelYearFinish': {'StorageLevelYearFinish': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'StorageLevelSeasonStart': {'sets': [REGION, SEASON, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'ls', 's', 'y']},
       'StorageLevelTimesliceStart': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
       'StorageLosses': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
       'StorageLevelDayTypeStart': {'sets': [REGION, DAYTYPE, SEASON, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'ld', 'ls', 's', 'y']},
       'StorageLevelDayTypeFinish': {'sets': [REGION, DAYTYPE, SEASON, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'ld', 'ls', 's', 'y']},
       'StorageLowerLimit': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'StorageUpperLimit': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'StorageLossesheating': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
       'StorageLossescooling': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
       'AccumulatedNewStorageCapacity': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'StorageSurfaceArea': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'NewStorageCapacity': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'CapitalInvestmentStorage': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'DiscountedCapitalInvestmentStorage': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'DiscountedCapitalInvestmentByStorage': {'sets': [REGION, STORAGE], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's']},
       'SalvageValueStorage': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'DiscountedSalvageValueStorage': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
       'DiscountedSalvageValueByStorage': {'sets': [REGION, STORAGE], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's']},
       'TotalDiscountedStorageCost': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},

        # ====  Capacity Variables  ====

       'NumberOfNewTechnologyUnits': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Integer', 'indices': ['r', 't', 'y']},
       'NewCapacity': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'AccumulatedNewCapacity': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'TotalCapacityAnnual': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},

        # ====  Activity Variables  ====

       'RateOfActivity': {'sets': [REGION, TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'l', 'm', 't', 'y']},
       'RateOfTotalActivity': {'sets': [REGION, TIMESLICE, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'l', 't', 'y']},
       'TotalTechnologyAnnualActivity': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'TotalAnnualTechnologyActivityByMode': {'sets': [REGION, MODE_OF_OPERATION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'm', 't', 'y']},
       'TotalTechnologyModelPeriodActivity': {'sets': [REGION, TECHNOLOGY], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't']},
       'RateOfProductionByTechnologyByMode': {'sets': [REGION, FUEL, TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'm', 't', 'y']},
       'RateOfProductionByTechnology': {'sets': [REGION, FUEL, TIMESLICE, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 't', 'y']},
       'ProductionByTechnology': {'sets': [REGION, FUEL, TIMESLICE, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 't', 'y']},
       'ProductionByTechnologyAnnual': {'sets': [REGION, FUEL, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 't', 'y']},
       'RateOfProduction': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},
       'Production': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},
       'RateOfUseByTechnologyByMode': {'sets': [REGION, FUEL, TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'm ', 't', 'y']},
       'RateOfUseByTechnology': {'sets': [REGION, FUEL, TIMESLICE, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 't', 'y']},
       # 'UseByTechnologyAnnual': {'sets': [REGION, FUEL, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 't', 'y']},
       # 'RateOfUse': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},
       # 'UseByTechnology': {'sets': [REGION, FUEL, TIMESLICE, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 't', 'y']},
       'Use': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},
       'Trade': {'sets': [REGION, REGION2, FUEL, TIMESLICE, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'rr', 'f', 'l', 'y']},
       # 'TradeAnnual': {'sets': [REGION, REGION2, FUEL, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'rr', 'f', 'y']},
       'ProductionAnnual': {'sets': [REGION, FUEL, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'y']},
       # 'UseAnnual': {'sets': [REGION, FUEL, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'y']},

        # ====  Costing Variables  ====

       'CapitalInvestment': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'DiscountedCapitalInvestment': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'SalvageValue': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'DiscountedSalvageValue': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'OperatingCost': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'DiscountedOperatingCost': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'AnnualVariableOperatingCost': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'AnnualFixedOperatingCost': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'TotalDiscountedCostByTechnology': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'TotalDiscountedCost': {'sets': [REGION, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'y']},
       'ModelPeriodCostByRegion': {'sets': [REGION], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r']},

        # ====  Reserve Margin  ====

       'TotalCapacityInReserveMargin': {'sets': [REGION, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'y']},
       'DemandNeedingReserveMargin': {'sets': [REGION, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'l', 'y']},

        # ====  RE Gen Target  ====

       # 'TotalREProductionAnnual': {'sets': [REGION, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'y']},
       'RETotalProductionOfTargetFuelAnnual': {'sets': [REGION, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'y']},

        # ====  Emissions  ====

       'AnnualTechnologyEmissionByMode': {'sets': [REGION, EMISSION, MODE_OF_OPERATION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'e', 'm', 't', 'y']},
       'AnnualTechnologyEmission': {'sets': [REGION, EMISSION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'e', 't', 'y']},
       'AnnualTechnologyEmissionPenaltyByEmission': {'sets': [REGION, EMISSION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'e', 't', 'y']},
       'AnnualTechnologyEmissionsPenalty': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'DiscountedTechnologyEmissionsPenalty': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
       'AnnualEmissions': {'sets': [REGION, EMISSION, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'e', 'y']},
       'ModelPeriodEmissions': {'sets': [REGION, EMISSION], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'e']}
    }

    # Dictionaries for variables

    # ====  Net Present Cost  ====

    # 'Cost'

    # ====  Demands  ====

    RateOfDemand = createVariable('RateOfDemand', variables)
    Demand = createVariable('Demand', variables)

    # ====  Storage  ====

    RateOfStorageCharge = createVariable('RateOfStorageCharge', variables)
    RateOfStorageDischarge = createVariable('RateOfStorageDischarge', variables)
    NetChargeWithinYear = createVariable('NetChargeWithinYear', variables)
    NetChargeWithinDay = createVariable('NetChargeWithinDay', variables)
    StorageLevelYearStart = createVariable('StorageLevelYearStart', variables)
    StorageLevelYearFinish = createVariable('StorageLevelYearFinish', variables)
    StorageLevelSeasonStart = createVariable('StorageLevelSeasonStart', variables)
    StorageLevelTimesliceStart = createVariable('StorageLevelTimesliceStart', variables)
    StorageLosses = createVariable('StorageLosses', variables)
    StorageLevelDayTypeStart = createVariable('StorageLevelDayTypeStart', variables)
    StorageLevelDayTypeFinish = createVariable('StorageLevelDayTypeFinish', variables)
    StorageLowerLimit = createVariable('StorageLowerLimit', variables)
    StorageUpperLimit = createVariable('StorageUpperLimit', variables)
    AccumulatedNewStorageCapacity = createVariable('AccumulatedNewStorageCapacity', variables)
    StorageSurfaceArea = createVariable('StorageSurfaceArea', variables)
    StorageLossescooling = createVariable('StorageLossescooling', variables)
    StorageLossesheating = createVariable('StorageLossesheating', variables)
    NewStorageCapacity = createVariable('NewStorageCapacity', variables)
    CapitalInvestmentStorage = createVariable('CapitalInvestmentStorage', variables)
    DiscountedCapitalInvestmentStorage = createVariable('DiscountedCapitalInvestmentStorage', variables)
    SalvageValueStorage = createVariable('SalvageValueStorage', variables)
    DiscountedSalvageValueStorage = createVariable('DiscountedSalvageValueStorage', variables)
    TotalDiscountedStorageCost = createVariable('TotalDiscountedStorageCost', variables)

    # ====  Capacity Variables  ====

    NumberOfNewTechnologyUnits = createVariable('NumberOfNewTechnologyUnits', variables)
    NewCapacity = createVariable('NewCapacity', variables)
    AccumulatedNewCapacity = createVariable('AccumulatedNewCapacity', variables)
    TotalCapacityAnnual = createVariable('TotalCapacityAnnual', variables)

    # ====  Activity Variables  ====

    RateOfActivity = createVariable('RateOfActivity', variables)
    RateOfTotalActivity = createVariable('RateOfTotalActivity', variables)
    TotalTechnologyAnnualActivity = createVariable('TotalTechnologyAnnualActivity', variables)
    TotalAnnualTechnologyActivityByMode = createVariable('TotalAnnualTechnologyActivityByMode', variables)
    TotalTechnologyModelPeriodActivity = createVariable('TotalTechnologyModelPeriodActivity', variables)
    RateOfProductionByTechnologyByMode = createVariable('RateOfProductionByTechnologyByMode', variables)
    RateOfProductionByTechnology = createVariable('RateOfProductionByTechnology', variables)
    ProductionByTechnology = createVariable('ProductionByTechnology', variables)
    ProductionByTechnologyAnnual = createVariable('ProductionByTechnologyAnnual', variables)
    RateOfProduction = createVariable('RateOfProduction', variables)
    Production = createVariable('Production', variables)
    RateOfUseByTechnologyByMode = createVariable('RateOfUseByTechnologyByMode', variables)
    RateOfUseByTechnology = createVariable('RateOfUseByTechnology', variables)
    # UseByTechnologyAnnual = createVariable('UseByTechnologyAnnual', variables)
    # RateOfUse = createVariable('RateOfUse', variables)
    # UseByTechnology = createVariable('UseByTechnology', variables)
    Use = createVariable('Use', variables)
    Trade = createVariable('Trade', variables)
    # TradeAnnual = createVariable('TradeAnnual', variables)
    ProductionAnnual = createVariable('ProductionAnnual', variables)
    # UseAnnual = createVariable('UseAnnual', variables)

    # ====  Costing Variables  ====

    CapitalInvestment = createVariable('CapitalInvestment', variables)
    DiscountedCapitalInvestment = createVariable('DiscountedCapitalInvestment', variables)
    SalvageValue = createVariable('SalvageValue', variables)
    DiscountedSalvageValue = createVariable('DiscountedSalvageValue', variables)
    OperatingCost = createVariable('OperatingCost', variables)
    DiscountedOperatingCost = createVariable('DiscountedOperatingCost', variables)
    AnnualVariableOperatingCost = createVariable('AnnualVariableOperatingCost', variables)
    AnnualFixedOperatingCost = createVariable('AnnualFixedOperatingCost', variables)
    TotalDiscountedCostByTechnology = createVariable('TotalDiscountedCostByTechnology', variables)
    TotalDiscountedCost = createVariable('TotalDiscountedCost', variables)
    ModelPeriodCostByRegion = createVariable('ModelPeriodCostByRegion', variables)

    # ====  Reserve Margin  ====

    TotalCapacityInReserveMargin = createVariable('TotalCapacityInReserveMargin', variables)
    DemandNeedingReserveMargin = createVariable('DemandNeedingReserveMargin', variables)

    # ====  RE Gen Target  ====

    # TotalREProductionAnnual = createVariable('TotalREProductionAnnual', variables)
    RETotalProductionOfTargetFuelAnnual = createVariable('RETotalProductionOfTargetFuelAnnual', variables)

    # ====  Emissions  ====

    AnnualTechnologyEmissionByMode = createVariable('AnnualTechnologyEmissionByMode', variables)
    AnnualTechnologyEmission = createVariable('AnnualTechnologyEmission', variables)
    AnnualTechnologyEmissionPenaltyByEmission = createVariable('AnnualTechnologyEmissionPenaltyByEmission', variables)
    AnnualTechnologyEmissionsPenalty = createVariable('AnnualTechnologyEmissionsPenalty', variables)
    DiscountedTechnologyEmissionsPenalty = createVariable('DiscountedTechnologyEmissionsPenalty', variables)
    AnnualEmissions = createVariable('AnnualEmissions', variables)
    ModelPeriodEmissions = createVariable('ModelPeriodEmissions', variables)

    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                 f"Variables are created.")

    # ------------------------------------------------------------------------------------------------------------------
    #    OBJECTIVE FUNCTION
    # ------------------------------------------------------------------------------------------------------------------

    Cost = pulp.LpVariable("Cost", cat='Continuous')
    model += Cost, "Objective"
    model += Cost == pulp.lpSum([TotalDiscountedCost.get(ci(ry)) for ry in REGION_YEAR]), "Cost_function"

    # ------------------------------------------------------------------------------------------------------------------
    #    CONSTRAINTS
    # ------------------------------------------------------------------------------------------------------------------

    for rfly in REGION_FUEL_TIMESLICE_YEAR:
        # EQ_SpecifiedDemand
        model += RateOfDemand.get(ci(rfly)) == SpecifiedAnnualDemand.get(ci([*rfly[0:2], rfly[3]]), dflt.get('SpecifiedAnnualDemand')) * SpecifiedDemandProfile.get(ci(rfly), dflt.get('SpecifiedDemandProfile')) / YearSplit.get(ci(rfly[2:4])), ""

    # ====  Capacity Adequacy A  ====

    for rlty in REGION_TIMESLICE_TECHNOLOGY_YEAR:
        # CAa3_TotalActivityOfEachTechnology
        model += RateOfTotalActivity.get(ci(rlty)) == pulp.lpSum([(RateOfActivity.get(ci([*rlty[0:2], m, *rlty[2:4]])) * OutputModeofoperation.get(ci([rlty[0], m, *rlty[2:4]]), dflt.get('OutputModeofoperation'))) for m in MODE_OF_OPERATION]), ""
        # CAa4_Constraint_Capacity
        model += RateOfTotalActivity.get(ci(rlty)) <= TotalCapacityAnnual.get(ci([rlty[0], *rlty[2:4]])) * CapacityFactor.get(ci(rlty), dflt.get('CapacityFactor')) * CapacityToActivityUnit.get(ci([rlty[0], rlty[2]]), dflt.get('CapacityToActivityUnit')), ""

    for rty in REGION_TECHNOLOGY_YEAR:
        # CAa1_TotalNewCapacity
        model += AccumulatedNewCapacity.get(ci(rty)) == pulp.lpSum([NewCapacity.get(ci([*rty[0:2], yy])) for yy in YEAR if (float(int(rty[2]) - int(yy)) < float(OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')))) and (int(rty[2]) - int(yy) >= 0)]), ""
        # CAa2_TotalAnnualCapacity
        model += TotalCapacityAnnual.get(ci(rty)) == AccumulatedNewCapacity.get(ci(rty)) + ResidualCapacity.get(ci(rty), dflt.get('ResidualCapacity')), ""

        if CapacityOfOneTechnologyUnit.get(ci(rty), dflt.get('CapacityOfOneTechnologyUnit')) != 0:
            # CAa5_TotalNewCapacity
            model += NewCapacity.get(ci(rty)) == CapacityOfOneTechnologyUnit.get(ci(rty), dflt.get('CapacityOfOneTechnologyUnit')) * NumberOfNewTechnologyUnits.get(ci(rty)), ""

    # ====  Capacity Adequacy B  ====
        # CAb1_PlannedMaintenance
        model += pulp.lpSum([RateOfTotalActivity.get(ci([rty[0], l, *rty[1:3]])) * YearSplit.get(ci([l, rty[2]])) for l in TIMESLICE]) <= pulp.lpSum(([TotalCapacityAnnual.get(ci(rty)) * CapacityFactor.get(ci([rty[0], l, *rty[1:3]]), dflt.get('CapacityFactor')) * YearSplit.get(ci([l, rty[2]])) for l in TIMESLICE])) * CapacityToActivityUnit.get(ci([rty[0], rty[1]]), dflt.get('CapacityToActivityUnit')) * AvailabilityFactor.get(ci([rty[0], *rty[1:3]]), dflt.get('AvailabilityFactor')), ""
    # ====  Energy Balance A  ====

    for rflmty in REGION_FUEL_TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR:
        # EBa1_RateOfFuelProduction1
        if OutputActivityRatio.get(ci([*rflmty[0:2], *rflmty[3:6]]), dflt.get('OutputActivityRatio')) != 0:
            model += RateOfProductionByTechnologyByMode.get(ci(rflmty)) == RateOfActivity.get(ci([rflmty[0], *rflmty[2:6]])) * OutputActivityRatio.get(ci([*rflmty[0:2], *rflmty[3:6]]), dflt.get('OutputActivityRatio')), ""
        else:
            model += RateOfProductionByTechnologyByMode.get(ci(rflmty)) == 0, ""
        # EBa4_RateOfFuelUse1
        if InputActivityRatio.get(ci([*rflmty[0:2], *rflmty[3:6]]), dflt.get('InputActivityRatio')) != 0:
            model += RateOfUseByTechnologyByMode.get(ci(rflmty)) == RateOfActivity.get(ci([rflmty[0], *rflmty[2:6]])) * InputActivityRatio.get(ci([*rflmty[0:2], *rflmty[3:6]]), dflt.get('InputActivityRatio')), ""

    for rflty in REGION_FUEL_TIMESLICE_TECHNOLOGY_YEAR:
        # EBa2_RateOfFuelProduction2
        model += RateOfProductionByTechnology.get(ci(rflty)) == pulp.lpSum([RateOfProductionByTechnologyByMode.get(ci([*rflty[0:3], m, *rflty[3:5]])) for m in MODE_OF_OPERATION if OutputActivityRatio.get(ci([*rflty[0:2], m, *rflty[3:5]]), dflt.get('OutputActivityRatio')) != 0]), ""
        # EBa5_RateOfFuelUse2
        model += RateOfUseByTechnology.get(ci(rflty)) == pulp.lpSum([RateOfUseByTechnologyByMode.get(ci([*rflty[0:3], m, *rflty[3:5]])) for m in MODE_OF_OPERATION if InputActivityRatio.get(ci([*rflty[0:2], m, *rflty[3:5]]), dflt.get('InputActivityRatio')) != 0]), ""

    for rfly in REGION_FUEL_TIMESLICE_YEAR:
        # EBa3_RateOfFuelProduction3
        model += RateOfProduction.get(ci(rfly)) == pulp.lpSum([RateOfProductionByTechnology.get(ci([*rfly[0:3], t, rfly[3]])) for t in TECHNOLOGY]), ""
        # EBa6_RateOfFuelUse3
        # model += RateOfUse.get(ci(rfly)) == pulp.lpSum([RateOfUseByTechnology.get(ci([*rfly[0:3], t, rfly[3]])) for t in TECHNOLOGY]), ""
        # EBa7_EnergyBalanceEachTS1
        model += Production.get(ci(rfly)) == RateOfProduction.get(ci(rfly)) * YearSplit.get(ci(rfly[2:4])), ""
        # EBa8_EnergyBalanceEachTS2
        # model += Use.get(ci(rfly)) == RateOfUse.get(ci(rfly)) * YearSplit.get(ci(rfly[2:4])), ""
        model += Use.get(ci(rfly)) == pulp.lpSum([RateOfUseByTechnology.get(ci([*rfly[0:3], t, rfly[3]])) for t in TECHNOLOGY]) * YearSplit.get(ci(rfly[2:4])), ""

        # EBa9_EnergyBalanceEachTS3
        model += Demand.get(ci(rfly)) == RateOfDemand.get(ci(rfly)) * YearSplit.get(ci(rfly[2:4])), ""

        # EBa11_EnergyBalanceEachTS5
        model += Production.get(ci(rfly)) >= Demand.get(ci(rfly)) + Use.get(ci(rfly)) + (GIS_Losses.get(ci([*rfly[0:2]]), dflt.get('GIS_Losses')) * (8760 / int(max(TIMESLICE)))) + pulp.lpSum([Trade.get(ci([rfly[0], rr, *rfly[1:4]])) * TradeRoute.get(ci([rfly[0], rr, rfly[1], rfly[3]]), dflt.get('TradeRoute')) for rr in REGION2]), ""

    for rr2fly in REGION_REGION2_FUEL_TIMESLICE_YEAR:
        # EBa10_EnergyBalanceEachTS4
        model += Trade.get(ci(rr2fly)) == -Trade.get(ci([rr2fly[1], rr2fly[0], *rr2fly[2:5]])), ""

    # ====  Energy Balance B  ====

    for rfy in REGION_FUEL_YEAR:
        # EBb1_EnergyBalanceEachYear1
        model += ProductionAnnual.get(ci(rfy)) == pulp.lpSum([Production.get(ci([*rfy[0:2], l, rfy[2]])) for l in TIMESLICE]), ""
        # EBb2_EnergyBalanceEachYear2
        # model += UseAnnual.get(ci(rfy)) == pulp.lpSum([Use.get(ci([rfy[0], l, *rfy[1:3]])) for l in TIMESLICE]), ""

    # for rr2fy in REGION_REGION2_FUEL_YEAR:
    #     # EBb3_EnergyBalanceEachYear3
    #     model += TradeAnnual.get(ci(rr2fy)) == pulp.lpSum([Trade.get(ci([*rr2fy[0:2], l, *rr2fy[2:4]])) for l in TIMESLICE]), ""
    #
    # for rfy in REGION_FUEL_YEAR:

        # EBb4_EnergyBalanceEachYear4
        # model += ProductionAnnual.get(ci(rfy)) >= UseAnnual.get(ci(rfy)) + pulp.lpSum([TradeAnnual.get(ci([rfy[0], rr, *rfy[1:3]])) * TradeRoute.get(ci([rfy[0], rr, *rfy[1:3]]), dflt.get('TradeRoute')) for rr in REGION2]) + AccumulatedAnnualDemand.get(ci(rfy), dflt.get('AccumulatedAnnualDemand')), ""
        model += ProductionAnnual.get(ci(rfy)) >= pulp.lpSum([Use.get(ci([rfy[0], l, *rfy[1:3]])) for l in TIMESLICE])+ pulp.lpSum([pulp.lpSum([Trade.get(ci([rfy[0], rr, l, *rfy[1:3]])) for l in TIMESLICE]) * TradeRoute.get(ci([rfy[0], rr, *rfy[1:3]]), dflt.get('TradeRoute')) for rr in REGION2]) + AccumulatedAnnualDemand.get(ci(rfy), dflt.get('AccumulatedAnnualDemand')), ""

    # ====  Accounting Technology Production/Use  ====

    for rflty in REGION_FUEL_TIMESLICE_TECHNOLOGY_YEAR:
        # Acc1_FuelProductionByTechnology
        model += ProductionByTechnology.get(ci(rflty)) == pulp.lpSum([RateOfProductionByTechnologyByMode.get(ci([*rflty[0:3], m, *rflty[3:5]])) for m in MODE_OF_OPERATION if OutputActivityRatio.get(ci([*rflty[0:2], m, *rflty[3:5]]), dflt.get('OutputActivityRatio')) != 0]) * YearSplit.get(ci([rflty[2], rflty[4]])), ""
        # Acc2_FuelUseByTechnology
        # model += UseByTechnology.get(ci(rflty)) == RateOfUseByTechnology.get(ci(rflty)) * YearSplit.get(ci([rflty[2], rflty[4]])), ""

    for rmty in REGION_MODE_OF_OPERATION_TECHNOLOGY_YEAR:
        # Acc3_AverageAnnualRateOfActivity
        model += TotalAnnualTechnologyActivityByMode.get(ci(rmty)) == pulp.lpSum([RateOfActivity.get(ci([rmty[0], l, *rmty[1:4]])) * YearSplit.get(ci([l, rmty[3]])) for l in TIMESLICE]), ""

    for r in REGION:
        # Acc4_ModelPeriodCostByRegion
        model += ModelPeriodCostByRegion.get(r) == pulp.lpSum([TotalDiscountedCost.get(ci([r, y])) for y in YEAR]), ""

      # ====  Updated Storage equations -  ===

    for rsy in REGION_STORAGE_YEAR:
     #S5_and_S6_StorageLevelYearStart
        if int(rsy[2]) == int(min(YEAR)):
            model += StorageLevelYearStart.get(ci(rsy)) == StorageLevelStart.get(ci(rsy[0:2]), dflt.get('StorageLevelStart')), ""
        else:
            model += StorageLevelYearStart.get(ci(rsy)) == StorageLevelYearStart.get(ci([*rsy[0:2], str(int(rsy[2])-1)])) + pulp.lpSum([((RateOfStorageCharge.get(ci([*rsy[0:2], l, str(int(rsy[2])-1)])) - RateOfStorageDischarge.get(ci([*rsy[0:2], l, str(int(rsy[2])-1)]))) * YearSplit.get(ci([l, str(int(rsy[2])-1)]))) for l in TIMESLICE]), ""
                
    for rsly in REGION_STORAGE_TIMESLICE_YEAR:
        # S1_RateOfStorageCharge
        model += RateOfStorageCharge.get(ci(rsly)) == pulp.lpSum([RateOfActivity.get(ci([rsly[0], rsly[2], *mt, rsly[3]])) * TechnologyToStorage.get(ci([*rsly[0:2], *mt]), dflt.get('TechnologyToStorage'))  for mt in MODE_OF_OPERATION_TECHNOLOGY if TechnologyToStorage.get(ci(([*rsly[0:2],*mt])), dflt.get('TechnologyToStorage')) > 0]), ""
        # S2_RateOfStorageDischarge
        model += RateOfStorageDischarge.get(ci(rsly)) == pulp.lpSum([RateOfActivity.get(ci([rsly[0], rsly[2], *mt, rsly[3]])) * TechnologyFromStorage.get(ci([*rsly[0:2], *mt]), dflt.get('TechnologyFromStorage')) for mt in MODE_OF_OPERATION_TECHNOLOGY if TechnologyFromStorage.get(ci([*rsly[0:2], *mt]), dflt.get('TechnologyFromStorage')) > 0]), ""
    for rsly in REGION_STORAGE_TIMESLICE_YEAR:
        #S1_and_S2_StorageLevelTimesliceStart  
        if int(rsly[2]) == int(min(TIMESLICE)):
            model += StorageLevelTimesliceStart.get(ci(rsly)) == StorageLevelYearStart.get(ci([*rsly[0:2], rsly[3]])), ""
        else:
            model += StorageLevelTimesliceStart.get(ci(rsly)) == StorageLevelTimesliceStart.get(ci([*rsly[0:2], str(int(rsly[2])-1), rsly[3]])) - StorageLosses.get(ci([*rsly[0:2], str(int(rsly[2])-1), rsly[3]]))  + ((RateOfStorageCharge.get(ci([*rsly[0:2], str(int(rsly[2])-1), rsly[3]])) - RateOfStorageDischarge.get(ci([*rsly[0:2], str(int(rsly[2])-1), rsly[3]]))) * YearSplit.get(ci([str(int(rsly[2])-1), rsly[3]]))), ""

    for rs in REGION_STORAGE:
        #SC8_StorageRefilling 
        model += 0 == pulp.lpSum([RateOfActivity.get(ci([rs[0], *lmty])) * TechnologyToStorage.get(ci([*rs[0:2], *lmty[1:3]]), dflt.get('TechnologyToStorage')) * YearSplit.get(ci([lmty[0], lmty[3]])) for lmty in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR if TechnologyToStorage.get(ci(([*rs[0:2], *lmty[1:3]])), dflt.get('TechnologyToStorage')) > 0]) - pulp.lpSum([RateOfActivity.get(ci([rs[0], *lmty])) * TechnologyFromStorage.get(ci([*rs[0:2], *lmty[1:3]]), dflt.get('TechnologyFromStorage')) * YearSplit.get(ci([lmty[0], lmty[3]])) for lmty in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR if TechnologyFromStorage.get(ci([*rs[0:2], *lmty[1:3]]), dflt.get('TechnologyFromStorage')) > 0]) , ""
            
    #===== Storage Constraints ====
    
    for rsy in REGION_STORAGE_YEAR:
    # SI3_TotalNewStorage
        model += AccumulatedNewStorageCapacity.get(ci(rsy)) ==  pulp.lpSum([NewStorageCapacity.get(ci([*rsy[0:2], yy])) for yy in YEAR if (float(int(rsy[2]) - int(yy)) < float(OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')))) and (int(rsy[2])-int(yy) >= 0)]), ""
        
    # SI1_StorageUpperLimit
        model += StorageUpperLimit.get(ci(rsy)) == (AccumulatedNewStorageCapacity.get(ci(rsy)) + ResidualStorageCapacity.get(ci(rsy), dflt.get('ResidualStorageCapacity'))), ""
     
    # SI1_StorageMaxCapacity
        model += StorageUpperLimit.get(ci(rsy)) <= StorageMaxCapacity.get(ci(rsy[0:2]), dflt.get('StorageMaxCapacity')), ""
   
    for rsly in REGION_STORAGE_TIMESLICE_YEAR:
        #SC1_LowerLimit
        model += StorageLevelTimesliceStart.get(ci(rsly)) >= MinStorageCharge.get(ci([*rsly[0:2], rsly[3]]), dflt.get('MinStorageCharge')) * StorageUpperLimit.get(ci([*rsly[0:2], rsly[3]])), ""
        
        #SC2_Upper_Limit
        model += StorageLevelTimesliceStart.get(ci(rsly)) <= StorageUpperLimit.get(ci([*rsly[0:2], rsly[3]])), "" 

    # ====  Storage Investments  ====

    for rsy in REGION_STORAGE_YEAR:
        # SI2_StorageLowerLimit
        #model += StorageLowerLimit.get(ci(rsy)) == MinStorageCharge.get(ci(rsy), dflt.get('MinStorageCharge')) * StorageUpperLimit.get(ci(rsy)), ""
        # SI4_UndiscountedCapitalInvestmentStorage
        model += CapitalInvestmentStorage.get(ci(rsy)) == CapitalCostStorage.get(ci(rsy), dflt.get('CapitalCostStorage')) * NewStorageCapacity.get(ci(rsy)), ""
        # SI5_DiscountingCapitalInvestmentStorage
        model += DiscountedCapitalInvestmentStorage.get(ci(rsy)) == CapitalInvestmentStorage.get(ci(rsy)) * (1/ ((1+DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')))**(int(rsy[2]) - int(min(YEAR))))), ""
        # SI6_SalvageValueStorageAtEndOfPeriod1
        if float(int(rsy[2]) + OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))) - 1 <= float(max(YEAR)):
            model += SalvageValueStorage.get(ci(rsy)) == 0, ""
        # SI7_SalvageValueStorageAtEndOfPeriod2
        if ((DepreciationMethod.get(rsy[0], dflt.get('DepreciationMethod')) == 1) and (float(int(rsy[2])+OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))-1) > float(max(YEAR))) and (DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')) == 0)) or ((DepreciationMethod.get(rsy[0], dflt.get('DepreciationMethod')) == 2) and (float(int(rsy[2])+OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))-1) > float(max(YEAR)))):
            model += SalvageValueStorage.get(ci(rsy)) == CapitalInvestmentStorage.get(ci(rsy)) * (1-(int(max(YEAR))-int(rsy[2])+1))/OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')), ""
        # SI8_SalvageValueStorageAtEndOfPeriod3
        if (DepreciationMethod.get(rsy[0], dflt.get('DepreciationMethod')) == 1) and (float(int(rsy[2])+OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))-1) > float(max(YEAR))) and (DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')) > 0):
            model += SalvageValueStorage.get(ci(rsy)) == CapitalInvestmentStorage.get(ci(rsy)) * (1-(((1+DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')))**(int(max(YEAR)) - int(rsy[2])+1)-1)/((1+DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')))**OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))-1))), ""
        # SI9_SalvageValueStorageDiscountedToStartYear
        model += DiscountedSalvageValueStorage.get(ci(rsy)) == SalvageValueStorage.get(ci(rsy)) * (1 /((1+DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')))**(int(max(YEAR))-int(min(YEAR))+1))), ""
        # SI10_TotalDiscountedCostByStorage
        model += TotalDiscountedStorageCost.get(ci(rsy)) == DiscountedCapitalInvestmentStorage.get(ci(rsy))-DiscountedSalvageValueStorage.get(ci(rsy)), ""
    

    # ====  Capital Costs  ====

    for rty in REGION_TECHNOLOGY_YEAR:
        # CC1_UndiscountedCapitalInvestment
        model += CapitalInvestment.get(ci(rty)) == CapitalCost.get(ci(rty), dflt.get('CapitalCost')) * NewCapacity.get(ci(rty)),  ""
        # CC2_DiscountingCapitalInvestment
        model += DiscountedCapitalInvestment.get(ci(rty)) == CapitalInvestment.get(ci(rty)) * (1/((1 + DiscountRateTech.get(ci(rty[0:2]), dflt.get('DiscountRateTech'))) ** (int(rty[2]) - int(min(YEAR))))), ""
        
        
    for rty in REGION_TECHNOLOGY_YEAR:
    # ====  Salvage Value  ====

        # SV1_SalvageValueAtEndOfPeriod1
        if (DepreciationMethod.get(rty[0], dflt.get('DepreciationMethod')) == 1) and (float(int(rty[2]) + OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife'))) - 1 > float(max(YEAR))) and (DiscountRateTech.get(ci(rty[0:2]), dflt.get('DiscountRateTech')) > 0):
            model += SalvageValue.get(ci(rty)) == CapitalCost.get(ci(rty), dflt.get('CapitalCost')) * NewCapacity.get(ci(rty)) * (1 - (((1 +  DiscountRateTech.get(ci(rty[0:2]), dflt.get('DiscountRateTech'))) ** (int(max(YEAR)) - int(rty[2]) + 1) - 1) / ((1 +  DiscountRateTech.get(ci(rty[0:2]), dflt.get('DiscountRateTech'))) ** OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')) - 1))), ""
        # SV2_SalvageValueAtEndOfPeriod2
        if ((DepreciationMethod.get(rty[0], dflt.get('DepreciationMethod')) == 1) and (float(int(rty[2]) + OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife'))) - 1 > float(max(YEAR))) and ( DiscountRateTech.get(ci(rty[0:2]), dflt.get('DiscountRateTech')) == 0)) or ((DepreciationMethod.get(rty[0], dflt.get('DepreciationMethod')) == 2) and (float(int(rty[2]) + OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife'))) - 1 > float(max(YEAR)))):
            model += SalvageValue.get(ci(rty)) == CapitalCost.get(ci(rty), dflt.get('CapitalCost')) * NewCapacity.get(ci(rty)) * (1 - (int(max(YEAR)) - int(rty[2]) + 1) / OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife'))), ""
        # SV3_SalvageValueAtEndOfPeriod3)
        if float(int(rty[2]) + OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')) - 1) <= float(max(YEAR)):
            model += SalvageValue.get(ci(rty)) == 0, ""
        # SV4_SalvageValueDiscountedToStartYear
        model += DiscountedSalvageValue.get(ci(rty)) == SalvageValue.get(ci(rty)) * (1 / ((1 +  DiscountRateTech.get(ci(rty[0:2]), dflt.get('DiscountRateTech'))) ** (1 + int(max(YEAR)) - int(min(YEAR))))), ""

    # ====  Operating Costs  ====

        # OC1_OperatingCostsVariable
        model += AnnualVariableOperatingCost.get(ci(rty)) == pulp.lpSum([TotalAnnualTechnologyActivityByMode.get(ci([rty[0], m, *rty[1:3]])) * VariableCost.get(ci([rty[0], m, *rty[1:3]]), dflt.get('VariableCost')) for m in MODE_OF_OPERATION]), ""
        # OC2_OperatingCostsFixedAnnual
        model += AnnualFixedOperatingCost.get(ci(rty)) == TotalCapacityAnnual.get(ci(rty)) * FixedCost.get(ci(rty), dflt.get('FixedCost')), ""
        # OC3_OperatingCostsTotalAnnual
        model += OperatingCost.get(ci(rty)) == AnnualFixedOperatingCost.get(ci(rty)) + AnnualVariableOperatingCost.get(ci(rty)), ""
        # OC4_DiscountedOperatingCostsTotalAnnual
        model += DiscountedOperatingCost.get(ci(rty)) == OperatingCost.get(ci(rty)) * (1 / ((1 +  DiscountRateTech.get(ci(rty[0:2]), dflt.get('DiscountRateTech'))) ** (int(rty[2]) - int(min(YEAR)) + 0.5))), ""

    # ====  Total Discounted Costs  ====

    for ry in REGION_YEAR:
        # TDC2_TotalDiscountedCost
        model += TotalDiscountedCost.get(ci(ry)) == pulp.lpSum([TotalDiscountedCostByTechnology.get(ci([ry[0], t, ry[1]])) for t in TECHNOLOGY]) + pulp.lpSum([TotalDiscountedStorageCost.get(ci([ry[0], s, ry[1]])) for s in STORAGE]), ""

    for rty in REGION_TECHNOLOGY_YEAR:
        # TDC1_TotalDiscountedCostByTechnology
        model += TotalDiscountedCostByTechnology.get(ci(rty)) == DiscountedOperatingCost.get(ci(rty)) + DiscountedCapitalInvestment.get(ci(rty)) + DiscountedTechnologyEmissionsPenalty.get(ci(rty)) - DiscountedSalvageValue.get(ci(rty)), ""

    # ====  Total Capacity Constraints  ====

        # TCC1_TotalAnnualMaxCapacityConstraint
        model += TotalCapacityAnnual.get(ci(rty)) <= TotalAnnualMaxCapacity.get(ci(rty), dflt.get('TotalAnnualMaxCapacity')), ""
        # TCC2_TotalAnnualMinCapacityConstraint
        if TotalAnnualMinCapacity.get(ci(rty), dflt.get('TotalAnnualMinCapacity')) > 0:
            model += TotalCapacityAnnual.get(ci(rty)) >= TotalAnnualMinCapacity.get(ci(rty), dflt.get('TotalAnnualMaxCapacity')), ""

    # ====  New Capacity Constraints  ====

        # NCC1_TotalAnnualMaxNewCapacityConstraint
        model += NewCapacity.get(ci(rty)) <= TotalAnnualMaxCapacityInvestment.get(ci(rty), dflt.get('TotalAnnualMaxCapacityInvestment')), ""
        # NCC2_TotalAnnualMinNewCapacityConstraint
        if TotalAnnualMinCapacityInvestment.get(ci(rty), dflt.get('TotalAnnualMinCapacityInvestment')) > 0:
            model += NewCapacity.get(ci(rty)) >= TotalAnnualMinCapacityInvestment.get(ci(rty), dflt.get('TotalAnnualMinCapacityInvestment')), ""

    # ====  Annual Activity Constraints  ====

        # AAC1_TotalAnnualTechnologyActivity
        model += TotalTechnologyAnnualActivity.get(ci(rty)) == pulp.lpSum([RateOfTotalActivity.get(ci([rty[0], l, *rty[1:3]])) * YearSplit.get(ci([l, rty[2]])) for l in TIMESLICE]), ""
        # AAC2_TotalAnnualTechnologyActivityUpperLimit
        model += TotalTechnologyAnnualActivity.get(ci(rty)) <= TotalTechnologyAnnualActivityUpperLimit.get(ci(rty), dflt.get('TotalTechnologyAnnualActivityUpperLimit')), ""
        # AAC3_TotalAnnualTechnologyActivityLowerLimit
        if TotalTechnologyAnnualActivityLowerLimit.get(ci(rty), dflt.get('TotalTechnologyAnnualActivityLowerLimit')) > 0:
            model += TotalTechnologyAnnualActivity.get(ci(rty)) >= TotalTechnologyAnnualActivityLowerLimit.get(ci(rty), dflt.get('TotalTechnologyAnnualActivityLowerLimit')), ""

    # ====  Total Activity Constraints  ====

    for rt in REGION_TECHNOLOGY:
        # TAC1_TotalModelHorizonTechnologyActivity
        model += TotalTechnologyModelPeriodActivity.get(ci(rt)) == pulp.lpSum([TotalTechnologyAnnualActivity.get(ci([*rt, y])) for y in YEAR]), ""
        # TAC2_TotalModelHorizonTechnologyActivityUpperLimit
        if TotalTechnologyModelPeriodActivityUpperLimit.get(ci(rt), dflt.get('TotalTechnologyModelPeriodActivityUpperLimit')) > 0:
            model += TotalTechnologyModelPeriodActivity.get(ci(rt)) <= TotalTechnologyModelPeriodActivityUpperLimit.get(ci(rt), dflt.get('TotalTechnologyModelPeriodActivityUpperLimit')), ""
        #TAC3_TotalModelHorizenTechnologyActivityLowerLimit
        if TotalTechnologyModelPeriodActivityLowerLimit.get(ci(rt), dflt.get('TotalTechnologyModelPeriodActivityLowerLimit')) > 0:
            model += TotalTechnologyModelPeriodActivity.get(ci(rt)) >= TotalTechnologyModelPeriodActivityLowerLimit.get(ci(rt), dflt.get('TotalTechnologyModelPeriodActivityLowerLimit')), ""

    # ====  Reserve Margin Constraint  ====

    for ry in REGION_YEAR:
        # RM1_ReserveMargin_TechnologiesIncluded_In_Activity_Units
        model += TotalCapacityInReserveMargin.get(ci(ry)) == pulp.lpSum([TotalCapacityAnnual.get(ci([ry[0], t, ry[1]])) * ReserveMarginTagTechnology.get(ci([ry[0], t, ry[1]]), dflt.get('ReserveMarginTagTechnology')) * CapacityToActivityUnit.get(ci([ry[0], t]), dflt.get('CapacityToActivityUnit')) for t in TECHNOLOGY]), ""

    for rly in REGION_TIMESLICE_YEAR:
        # RM2_ReserveMargin_FuelsIncluded
        model += DemandNeedingReserveMargin.get(ci(rly)) == pulp.lpSum([RateOfProduction.get(ci([rly[0], f, *rly[1:3]])) * ReserveMarginTagFuel.get(ci([rly[0], f, rly[2]]), dflt.get('ReserveMarginTagFuel')) for f in FUEL]), ""
        # RM3_ReserveMargin_Constraint
        model += DemandNeedingReserveMargin.get(ci(rly)) <= TotalCapacityInReserveMargin.get(ci([rly[0], rly[2]])) * (1/ReserveMargin.get(ci([rly[0], rly[2]]), dflt.get('ReserveMargin'))), ""

    # ====  RE Production Target  ====

    for rfty in REGION_FUEL_TECHNOLOGY_YEAR:
        # RE1_FuelProductionByTechnologyAnnual
        model += ProductionByTechnologyAnnual.get(ci(rfty)) == pulp.lpSum([ProductionByTechnology.get(ci([rfty[0], l, *rfty[1:4]])) for l in TIMESLICE]), ""

    for ry in REGION_YEAR:
        # RE2_TechIncluded
        # model += TotalREProductionAnnual.get(ci(ry)) == pulp.lpSum([ProductionByTechnologyAnnual.get(ci([ry[0], *ft, ry[1]])) * RETagTechnology.get(ci([ry[0], ft[1], ry[1]]), dflt.get('RETagTechnology')) for ft in FUEL_TECHNOLOGY]), ""

        # RE3_FuelIncluded
        model += RETotalProductionOfTargetFuelAnnual.get(ci(ry)) == pulp.lpSum([RateOfProduction.get(ci([ry[0], *fl, ry[1]])) * YearSplit.get(ci([fl[1], ry[1]])) * RETagFuel.get(ci([ry[0], fl[0], ry[1]]), dflt.get('RETagFuel')) for fl in FUEL_TIMESLICE]), ""
        # RE4_EnergyConstraint
        # model += TotalREProductionAnnual.get(ci(ry)) >= REMinProductionTarget.get(ci(ry), dflt.get('REMinProductionTarget')) * RETotalProductionOfTargetFuelAnnual.get(ci(ry)), ""

        # Combined: RE4_EnergyConstraint >= RE2_TechIncluded
        model += pulp.lpSum([ProductionByTechnologyAnnual.get(ci([ry[0], *ft, ry[1]])) * RETagTechnology.get(ci([ry[0], ft[1], ry[1]]), dflt.get('RETagTechnology')) for ft in FUEL_TECHNOLOGY]) >= REMinProductionTarget.get(ci(ry), dflt.get('REMinProductionTarget')) * RETotalProductionOfTargetFuelAnnual.get(ci(ry)), ""

    # for rfty in REGION_FUEL_TECHNOLOGY_YEAR:
    #     # RE5_FuelUseByTechnologyAnnual
    #     model += UseByTechnologyAnnual.get(ci(rfty)) == pulp.lpSum([RateOfUseByTechnology.get(ci([*rfty[0:2], l, *rfty[2:4]])) * YearSplit.get(ci([l, rfty[3]])) for l in TIMESLICE]), ""

    # ====  Emissions Accounting  ====

    for remty in REGION_EMISSION_MODE_OF_OPERATION_TECHNOLOGY_YEAR:
        # E1_AnnualEmissionProductionByMode
        model += AnnualTechnologyEmissionByMode.get(ci(remty)) == EmissionActivityRatio.get(ci(remty), dflt.get('EmissionActivityRatio')) * TotalAnnualTechnologyActivityByMode.get(ci([remty[0], *remty[2:5]])), ""

    for rety in REGION_EMISSION_TECHNOLOGY_YEAR:
        # E2_AnnualEmissionProduction
        model += AnnualTechnologyEmission.get(ci(rety)) == pulp.lpSum([AnnualTechnologyEmissionByMode.get(ci([*rety[0:2], m, *rety[2:4]])) for m in MODE_OF_OPERATION]), ""
        # E3_EmissionsPenaltyByTechAndEmission
        model += AnnualTechnologyEmissionPenaltyByEmission.get(ci(rety)) == AnnualTechnologyEmission.get(ci(rety)) * EmissionsPenalty.get(ci([*rety[0:2], rety[3]]), dflt.get('EmissionsPenalty')), ""

    for rty in REGION_TECHNOLOGY_YEAR:
        # E4_EmissionsPenaltyByTechnology
        model += AnnualTechnologyEmissionsPenalty.get(ci(rty)) == pulp.lpSum([AnnualTechnologyEmissionPenaltyByEmission.get(ci([rty[0], e, *rty[1:3]])) for e in EMISSION]), ""
        # E5_DiscountedEmissionsPenaltyByTechnology
        model += DiscountedTechnologyEmissionsPenalty.get(ci(rty)) == AnnualTechnologyEmissionsPenalty.get(ci(rty)) * (1 / ((1 + DiscountRateTech.get(ci(rty[0:2]), dflt.get('DiscountRateTech'))) ** (int(rty[2]) - int(min(YEAR)) + 0.5))), ""

    for rey in REGION_EMISSION_YEAR:
        # E6_EmissionsAccounting1
        model += AnnualEmissions.get(ci(rey)) == pulp.lpSum([AnnualTechnologyEmission.get(ci([*rey[0:2], t, rey[2]])) for t in TECHNOLOGY]), ""
        # E8_AnnualEmissionsLimit
        model += AnnualEmissions.get(ci(rey)) <= AnnualEmissionLimit.get(ci(rey), dflt.get('AnnualEmissionLimit')) - AnnualExogenousEmission.get(ci(rey), dflt.get('AnnualExogenousEmission')), ""

    for re in REGION_EMISSION:
        # E7_EmissionsAccounting2
        model += pulp.lpSum([AnnualEmissions.get(ci([*re, y])) for y in YEAR]) == ModelPeriodEmissions.get(ci(re)) - ModelPeriodExogenousEmission.get(ci(re), dflt.get('ModelPeriodExogenousEmission')), ""
        # E9_ModelPeriodEmissionsLimit
        model += ModelPeriodEmissions.get(ci(re)) <= ModelPeriodEmissionLimit.get(ci(re), dflt.get('ModelPeriodEmissionLimit')), ""

    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                 f"Model is built.")

    # ------------------------------------------------------------------------------------------------------------------
    #    SAVE MODEL
    # ------------------------------------------------------------------------------------------------------------------

    # Write model to LP-file
    # model.writeLP(f"{modelName}_{i}.lp")

    # ------------------------------------------------------------------------------------------------------------------
    #    SOLVE
    # ------------------------------------------------------------------------------------------------------------------

    model.solve()
    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                 f"Model is solved. Solution is: "
                 f"{pulp.LpStatus[model.status]}")

    # ------------------------------------------------------------------------------------------------------------------
    #    SAVE RESULTS
    # ------------------------------------------------------------------------------------------------------------------

    if str(pulp.LpStatus[model.status]) == "Optimal":
        logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                     f"The optimal solution found a cost value of "
                     f"{round(model.objective.value(), 2)}")

        # Create dataframe to save results after the model was run the first time
        if i == 0:
            res_df = pd.DataFrame()
        res_df = pd.concat([res_df, saveResultsTemporary(model, i)])

        logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                     f"Results are saved temporarily.")
    else:
        logging.error(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                      f"Error: Optimisation status for Scenario_{i} is: {pulp.LpStatus[model.status]}")

    del model  # Delete model

    i += 1

    # ------------------------------------------------------------------------------------------------------------------
    #    MONTE CARLO SIMULATION
    # ------------------------------------------------------------------------------------------------------------------

    if n > 0:

        # Note: Monte Carlo Simulation is applied to all selected parameters (parameters_mcs).
        # For each parameter, the parameters_mcs is only applied to parameter values that are not equal to default values,
        # i.e. values that were explicitly set.

        # ====  Reference parameters and data  ====

        mcs_df['INDEX'] = [ci([str(r), str(rr), str(ld), str(e), str(f), str(lh), str(ls), str(l), str(m), str(s), str(t), str(y)])\
                           .replace('nan-', '').replace('<NA>-', '').replace('-nan', '').replace('-<NA>', '')
                       for r, rr, ld, e, f, lh, ls, l, m, s, t, y in
                         zip(mcs_df.REGION, mcs_df.REGION2, mcs_df.DAYTYPE, mcs_df.EMISSION, mcs_df.FUEL, mcs_df.DAILYTIMEBRACKET, mcs_df.SEASON,\
                             mcs_df.TIMESLICE, mcs_df.MODE_OF_OPERATION, mcs_df.STORAGE, mcs_df.TECHNOLOGY, mcs_df.YEAR)]

        if i == 1:
            dflt_ref = dflt.copy()

            # All parameters
            parameters = list(df.PARAM.unique())
            parameters.extend(list(defaults_df.PARAM.unique()))
            parameters = sorted(tuple(set(parameters)))

            for p in parameters:
                # Copy of original data as reference
                globals()[f"{p}_ref"] = globals()[f"{p}"].copy()

        # ====  Random data generation  ====

        for p_mcs in parameters_mcs:
            # Dict with value where: Distribution specified, without default_setting:
            d1_df = mcs_df[(mcs_df['PARAM'] == p_mcs) & (mcs_df['DEFAULT_SETTING'] != 1)].copy()

            if len(d1_df) > 0:
                d1_df['VALUE'] = [generateRandomData(globals()[f"{p_mcs}_ref"].get(index, dflt.get(p_mcs)), dist, rel_sd, rel_min, rel_max, array)
                                         for dist, rel_sd, rel_min, rel_max, array, index in zip(
                        d1_df['DISTRIBUTION'], d1_df['REL_SD'], d1_df['REL_MIN'], d1_df['REL_MAX'], d1_df['ARRAY'], d1_df['INDEX'])]

                d1 = d1_df.set_index('INDEX').to_dict()['VALUE']

            # Default setting is not supported, yet.
            if len(mcs_df[(mcs_df['PARAM'] == p_mcs) & (mcs_df['DEFAULT_SETTING'] == 1)]) > 0:
                logging.error(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                              f"Error: DEFAULT_SETTING in Monte Carlo Simulation is not supported, yet.")

            # Update global dictionary with new values from random generation
            globals()[f"{p_mcs}"].update(d1)

# ----------------------------------------------------------------------------------------------------------------------
#	SAVE ALL RESULTS
# ----------------------------------------------------------------------------------------------------------------------

logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
             f"Analysis is finished. Please wait until the results are saved!")

# CSV
if save_as_csv is True:
    outputFileCSV = f"{modelName}_results.csv"
    saveResultsToCSV(res_df, outputDir, outputFileCSV)

# Excel
if save_as_excel is True:
    outputFileExcel = f"{modelName}_results.xlsx"
    saveResultsToExcel(res_df, outputDir, outputFileExcel)

logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
             f"All results are saved now.")

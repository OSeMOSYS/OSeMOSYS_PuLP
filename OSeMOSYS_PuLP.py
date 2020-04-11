# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Dennis Dreier, Copyright 2019, Version: OSeMOSYS_2017_11_08_PuLP_2019_09_11
# License: Apache License Version 2.0

__doc__ = """
# ============================================================================
#
#	OSeMOSYS-PuLP: A Stochastic Modeling Framework for Long-Term Energy Systems Modeling
#
#
#	How to cite OSeMOSYS-PuLP:
#
#	Dennis Dreier, Mark Howells, OSeMOSYS-PuLP: A Stochastic Modeling Framework for Long-Term Energy Systems Modeling. 
#	Energies 2019, 12, 1382, https://doi.org/10.3390/en12071382
#
#	Additional references to be cited (see DOI links for complete references):
#	Howells et al. (2011), https://doi.org/10.1016/j.enpol.2011.06.033
#	Gardumi et al. (2018), https://doi.org/10.1016/j.esr.2018.03.005
#
#	Other sources:
#   OSeMOSYS GitHub: https://github.com/OSeMOSYS/
#	OSeMOSYS website: http://www.osemosys.org/
#	OpTIMUS community: http://www.optimus.community/
#
# ============================================================================
#
#	OSeMOSYS-PuLP 
#	
#	Version: OSeMOSYS_2017_11_08_PuLP_2019_09_11
#	--> OSeMOSYS-PuLP code version: 2019_09_11
#	--> OSeMOSYS modelling framework version: 2017_11_08
#
# ============================================================================
#	
#	To use the script, do the following steps:
#
#	1) Provide input data to the input data file (see script section "SETUP - DATA SOURCES and MONTE CARLO SIMULATION")
#	2) Results (i.e. values of variables to be saved) must be selected through the 
#	activation of the respective variables names in the dictionary "var_dict"
#	in the function "saveResultsTemporary" in this script (i.e. add or delete "#" in front of
#	the respecitve variable name).
#	3) Run script.
#	4) Review results in the output data file(see script section "SETUP - DATA SOURCES and MONTE CARLO SIMULATION")
#
# ============================================================================
#
#	The OSeMOSYS modelling framework code was translated from the GNU MathProg code implementation,
#	version: 8 November 2017 (OSeMOSYS_2017_11_08).
#
#	Excerpt of the OSeMOSYS GNU MathProg copyright and license:
#
#   Copyright [2010-2015] [OSeMOSYS Forum steering committee see: www.osemosys.org]
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License."
#
# ============================================================================
"""

import os
import datetime as dt
import logging
import numpy as np
import pandas as pd
import pulp

logging.basicConfig(level=logging.DEBUG)
logging.info("{}\tScript started.".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# ----------------------------------------------------------------------------------------------------------------------
#	 SETUP - DATA SOURCES and MONTE CARLO SIMULATION
# ----------------------------------------------------------------------------------------------------------------------

# Input data
modelName = "Utopia"
inputDir = ".\Input_Data\\"
inputFile = "UTOPIA_BASE.xlsx"
sheetSets = "SETS"
sheetParams = "PARAMETERS"
sheetParamsDefault = "PARAMETERS_DEFAULT"
sheetMcs = "MCS"
sheetMcsNum = "MCS_num"

# Output data
outputDir = ".\Output_Data\\"
outputFile = "UTOPIA_BASE_results.xlsx"

# ----------------------------------------------------------------------------------------------------------------------
#    FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def newVar(name, lb, ub, cat, *indices):
    """
    This function create a new variable having a lower bound (lb),
    upper bound (ub), category (cat), using indices from SETS
    """
    _name = name
    for index in indices:
        _name = "{}_{}".format(_name, index)
    return pulp.LpVariable(_name, lowBound=lb, upBound=ub, cat=cat)


def loadData(filePath, sheetSets, sheetParams, sheetParamsDefault, sheetMcs, sheetMcsNum):
    """
    This function loads all data from the input data set to dataframes.
    """
    # Data: SETS
    sets_df = pd.read_excel(io=filePath, sheet_name=sheetSets)
    sets_df['SET'] = sets_df['SET'].astype(str)
    sets_df['ELEMENTS'] = sets_df['ELEMENTS'].astype(str)
    # Data: PARAMETERS
    p_df = pd.read_excel(io=filePath, sheet_name=sheetParams)
    p_df = p_df.fillna(0)
    p_df['PARAM'] = p_df['PARAM'].astype(str)
    p_df['VALUE'] = p_df['VALUE'].apply(pd.to_numeric, downcast='signed')
    p_df['REGION'] = p_df['REGION'].astype(str)
    p_df['REGION2'] = p_df['REGION2'].astype(str)
    p_df['DAYTYPE'] = p_df['DAYTYPE'].astype(int)
    p_df['DAYTYPE'] = p_df['DAYTYPE'].astype(str)
    p_df['EMISSION'] = p_df['EMISSION'].astype(str)
    p_df['FUEL'] = p_df['FUEL'].astype(str)
    p_df['DAILYTIMEBRACKET'] = p_df['DAILYTIMEBRACKET'].astype(int)
    p_df['DAILYTIMEBRACKET'] = p_df['DAILYTIMEBRACKET'].astype(str)
    p_df['SEASON'] = p_df['SEASON'].astype(int)
    p_df['SEASON'] = p_df['SEASON'].astype(str)
    p_df['TIMESLICE'] = p_df['TIMESLICE'].astype(str)
    p_df['MODE_OF_OPERATION'] = p_df['MODE_OF_OPERATION'].astype(int)
    p_df['MODE_OF_OPERATION'] = p_df['MODE_OF_OPERATION'].astype(str)
    p_df['STORAGE'] = p_df['STORAGE'].astype(str)
    p_df['TECHNOLOGY'] = p_df['TECHNOLOGY'].astype(str)
    p_df['YEAR'] = p_df['YEAR'].astype(int)
    p_df['YEAR'] = p_df['YEAR'].astype(str)
    # Data: Parameters default values
    p_default_df = pd.read_excel(io=filePath, sheet_name=sheetParamsDefault)
    p_default_df = p_default_df.fillna(0)
    p_default_df['PARAM'] = p_default_df['PARAM'].astype(str)
    p_default_df['VALUE'] = p_default_df['VALUE'].apply(pd.to_numeric, downcast='signed')
    # Data: Monte Carlo Simulation (MCS)
    mcs_df = pd.read_excel(io=filePath, sheet_name=sheetMcs)
    mcs_df = mcs_df.fillna(0)
    mcs_df['DEFAULT_SETTING'] = mcs_df['DEFAULT_SETTING'].apply(pd.to_numeric, downcast='signed')
    mcs_df['DEFAULT_SETTING'] = mcs_df['DEFAULT_SETTING'].astype(int)
    mcs_df['REL_SD'] = mcs_df['REL_SD'].apply(pd.to_numeric, downcast='signed')
    mcs_df['REL_MIN'] = mcs_df['REL_MIN'].apply(pd.to_numeric, downcast='signed')
    mcs_df['REL_MAX'] = mcs_df['REL_MAX'].apply(pd.to_numeric, downcast='signed')
    mcs_df['DISTRIBUTION'] = mcs_df['DISTRIBUTION'].astype(str)
    mcs_df['ARRAY'] = [[float(i) for i in str(x).split(",")] for x in mcs_df['ARRAY']]
    mcs_df['PARAM'] = mcs_df['PARAM'].astype(str)
    mcs_df['REGION'] = mcs_df['REGION'].astype(str)
    mcs_df['DAYTYPE'] = mcs_df['DAYTYPE'].astype(int)
    mcs_df['DAYTYPE'] = mcs_df['DAYTYPE'].astype(str)
    mcs_df['EMISSION'] = mcs_df['EMISSION'].astype(str)
    mcs_df['FUEL'] = mcs_df['FUEL'].astype(str)
    mcs_df['DAILYTIMEBRACKET'] = mcs_df['DAILYTIMEBRACKET'].astype(int)
    mcs_df['DAILYTIMEBRACKET'] = mcs_df['DAILYTIMEBRACKET'].astype(str)
    mcs_df['SEASON'] = mcs_df['SEASON'].astype(int)
    mcs_df['SEASON'] = mcs_df['SEASON'].astype(str)
    mcs_df['TIMESLICE'] = mcs_df['TIMESLICE'].astype(str)
    mcs_df['MODE_OF_OPERATION'] = mcs_df['MODE_OF_OPERATION'].astype(int)
    mcs_df['MODE_OF_OPERATION'] = mcs_df['MODE_OF_OPERATION'].astype(str)
    mcs_df['STORAGE'] = mcs_df['STORAGE'].astype(str)
    mcs_df['TECHNOLOGY'] = mcs_df['TECHNOLOGY'].astype(str)
    mcs_df['YEAR'] = mcs_df['YEAR'].astype(int)
    mcs_df['YEAR'] = mcs_df['YEAR'].astype(str)
    # Number of MCS simulations
    mcs_num_df = pd.read_excel(io=filePath, sheet_name=sheetMcsNum)
    mcs_num = mcs_num_df.at[0, 'MCS_num']
    return sets_df, p_df, p_default_df, mcs_df, mcs_num


def generateRandomData(reference, list):
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
    dist, rel_sd, rel_min, rel_max, array = list[0], list[1], list[2], list[3], list[4]

    if dist == "normal":
        value = np.random.normal(reference, rel_sd * reference, 1)[
            0]  # mean, standard deviation, generate 1 value at the time
    elif dist == "triangular":
        value = np.random.triangular((1 + rel_min) * reference, reference, (1 + rel_max) * reference, 1)[
            0]  # minimum value, mode, maximum value, generate 1 value at the time
    elif dist == "uniform":
        value = np.random.uniform((1 + rel_min) * reference, (1 + rel_max) * reference, 1)[
            0]  # minimum value, maximum value, generate 1 value at the time
    elif dist == "choice":
        if len(array) > 1:
            value = np.random.choice(array)
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

		
def saveResultsTemporary(dataframe, model_name, scenario):

    # Activate variable names in "var_dict" to be included in the results,
    # or comment out all redundant variables.

    df = dataframe

    var_dict = {

        ########			Demands 					#############
        #"RateOfDemand": ["r", "l", "f", "y"],
        "Demand": ["r", "l", "f", "y"],

        ########     		Storage                 		#############
        #"RateOfStorageCharge": ["r", "s", "ls", "ld", "lh", "y"],
        #"RateOfStorageDischarge": ["r", "s", "ls", "ld", "lh", "y"],
        #"NetChargeWithinYear": ["r", "s", "ls", "ld", "lh", "y"],
        #"NetChargeWithinDay": ["r", "s", "ls", "ld", "lh", "y"],
        #"StorageLevelYearStart": ["r", "s", "y"],
        #"StorageLevelYearFinish": ["r", "s", "y"],
        #"StorageLevelSeasonStart": ["r", "s", "ls", "y"],
        #"StorageLevelDayTypeStart": ["r", "s", "ls", "ld", "y"],
        #"StorageLevelDayTypeFinish": ["r", "s", "ls", "ld", "y"],
        #"StorageLowerLimit": ["r", "s", "y"],
        #"StorageUpperLimit": ["r", "s", "y"],
        #"AccumulatedNewStorageCapacity": ["r", "s", "y"],
        #"NewStorageCapacity": ["r", "s", "y"],
        #"CapitalInvestmentStorage": ["r", "s", "y"],
        #"DiscountedCapitalInvestmentStorage": ["r", "s", "y"],
        #"SalvageValueStorage": ["r", "s", "y"],
        #"DiscountedSalvageValueStorage": ["r", "s", "y"],
        #"TotalDiscountedStorageCost": ["r", "s", "y"],

        #########		    Capacity Variables 			#############
        #"NumberOfNewTechnologyUnits": ["r", "t", "y"],
        "NewCapacity": ["r", "t", "y"],
        #"AccumulatedNewCapacity": ["r", "t", "y"],
        "TotalCapacityAnnual": ["r", "t", "y"],

        #########		    Activity Variables 			#############
        #"RateOfActivity": ["r", "l", "t", "m", "y"],
        #"RateOfTotalActivity": ["r", "t", "l", "y"],
        #"TotalTechnologyAnnualActivity": ["r", "t", "y"],
        #"TotalAnnualTechnologyActivityByMode": ["r", "t", "m", "y"],
        #"TotalTechnologyModelPeriodActivity": ["r", "t"],
        #"RateOfProductionByTechnologyByMode": ["r", "l", "t", "m", "f", "y"],
        #"RateOfProductionByTechnology": ["r", "l", "t", "f", "y"],
        #"ProductionByTechnology": ["r", "l", "t", "f", "y"],
        #"ProductionByTechnologyAnnual": ["r", "t", "f", "y"],
        #"RateOfProduction": ["r", "l", "f", "y"],
        #"Production": ["r", "l", "f", "y"],
        #"RateOfUseByTechnologyByMode": ["r", "l", "t", "m", "f", "y"],
        #"RateOfUseByTechnology": ["r", "l", "t", "f", "y"],
        #"UseByTechnologyAnnual": ["r", "t", "f", "y"],
        #"RateOfUse": ["r", "l", "f", "y"],
        #"UseByTechnology": ["r", "l", "t", "f", "y"],
        #"Use": ["r", "l", "f", "y"],
        #"Trade": ["r", "rr", "l", "f", "y"],
        #"TradeAnnual": ["r", "rr", "f", "y"],
        #"ProductionAnnual": ["r", "f", "y"],
        "UseAnnual": ["r", "f", "y"],

        #########		    Costing Variables 			#############
        "CapitalInvestment": ["r", "t", "y"],
        #"DiscountedCapitalInvestment": ["r", "t", "y"],
        #"SalvageValue": ["r", "t", "y"],
        #"DiscountedSalvageValue": ["r", "t", "y"],
        #"OperatingCost": ["r", "t", "y"],
        #"DiscountedOperatingCost": ["r", "t", "y"],
        #"AnnualVariableOperatingCost": ["r", "t", "y"],
        #"AnnualFixedOperatingCost": ["r", "t", "y"],
        "TotalDiscountedCostByTechnology": ["r", "t", "y"],
        #"TotalDiscountedCost": ["r", "y"],
        #"ModelPeriodCostByRegion": ["r"],

        #########			Reserve Margin				#############
        #"TotalCapacityInReserveMargin": ["r", "y"],
        #"DemandNeedingReserveMargin": ["r", "l", "y"],

        #########			RE Gen Target				#############
        #"TotalREProductionAnnual": ["r", "y"],
        #"RETotalProductionOfTargetFuelAnnual": ["r", "y"],

        #########			Emissions					#############
        #"AnnualTechnologyEmissionByMode": ["r", "t", "e", "m", "y"],
        #"AnnualTechnologyEmission": ["r", "t", "e", "y"],
        #"AnnualTechnologyEmissionPenaltyByEmission": ["r", "t", "e", "y"],
        #"AnnualTechnologyEmissionsPenalty": ["r", "t", "y"],
        #"DiscountedTechnologyEmissionsPenalty": ["r", "t", "y"],
        "AnnualEmissions": ["r", "e", "y"],
        "ModelPeriodEmissions": ["r", "e"]
    }

    # Objective value ("cost")
    temp_df = pd.DataFrame(columns=[
        'SCENARIO',
        'VAR_NAME',
        'VAR_VALUE',
        'REGION',
        'REGION2',
        'DAYTYPE',
        'EMISSION',
        'FUEL',
        'DAILYTIMEBRACKET',
        'SEASON',
        'TIMESLICE',
        'MODE_OF_OPERATION',
        'STORAGE',
        'TECHNOLOGY',
        'YEAR',
        'FLEXIBLEDEMANDTYPE'])

    temp_df.at[0, 'SCENARIO'] = scenario
    temp_df.at[0, 'VAR_NAME'] = "cost"
    temp_df.at[0, 'VAR_VALUE'] = model_name.objective.value()
    temp_df.at[0, 'REGION'] = " "
    temp_df.at[0, 'REGION2'] = " "
    temp_df.at[0, 'DAYTYPE'] = " "
    temp_df.at[0, 'EMISSION'] = " "
    temp_df.at[0, 'FUEL'] = " "
    temp_df.at[0, 'DAILYTIMEBRACKET'] = " "
    temp_df.at[0, 'SEASON'] = " "
    temp_df.at[0, 'TIMESLICE'] = " "
    temp_df.at[0, 'MODE_OF_OPERATION'] = " "
    temp_df.at[0, 'STORAGE'] = " "
    temp_df.at[0, 'TECHNOLOGY'] = " "
    temp_df.at[0, 'YEAR'] = " "
    temp_df.at[0, 'FLEXIBLEDEMANDTYPE'] = " "

    df = pd.concat([df, temp_df])

    # Variables values (only variables that are included in var_dict)
    selected_variables = [variable for key in var_dict.keys() for variable in model_name.variables() if key == variable.name.split("_")[0]]

    for var in selected_variables:

        # Temporal dataframe in loop
        temp_df = pd.DataFrame(columns=[
            'SCENARIO',
            'VAR_NAME',
            'VAR_VALUE',
            'REGION',
            'REGION2',
            'DAYTYPE',
            'EMISSION',
            'FUEL',
            'DAILYTIMEBRACKET',
            'SEASON',
            'TIMESLICE',
            'MODE_OF_OPERATION',
            'STORAGE',
            'TECHNOLOGY',
            'YEAR',
            'FLEXIBLEDEMANDTYPE'])

        # Variable name
        var_name = var.name.split("_")[0]

        # Variable indices
        var_concrete_indices_list = var.name.split("_")[1:]

        # Variable abstract indices
        var_abstract_indices_list = var_dict[var_name]

        # Dictionary
        abstract_dict = {key: "" for key in ["r", "rr", "ld", "e", "f", "lh", "ls", "l", "m", "s", "t", "y", "fdt"]}  # default value: " "
        concrete_dict = {key: value for key, value in zip(var_abstract_indices_list, var_concrete_indices_list)}
        data_dict = {**abstract_dict, **concrete_dict}  # Merge dictionaries

        # Write data to temporary dataframe
        temp_df.at[0, 'SCENARIO'] = scenario
        temp_df.at[0, 'VAR_NAME'] = var.name.split("_")[0]
        temp_df.at[0, 'VAR_VALUE'] = var.varValue
        temp_df.at[0, 'REGION'] = data_dict["r"]
        temp_df.at[0, 'REGION2'] = data_dict["rr"]
        temp_df.at[0, 'DAYTYPE'] = data_dict["ld"]
        temp_df.at[0, 'EMISSION'] = data_dict["e"]
        temp_df.at[0, 'FUEL'] = data_dict["f"]
        temp_df.at[0, 'DAILYTIMEBRACKET'] = data_dict["lh"]
        temp_df.at[0, 'SEASON'] = data_dict["ls"]
        temp_df.at[0, 'TIMESLICE'] = data_dict["l"]
        temp_df.at[0, 'MODE_OF_OPERATION'] = data_dict["m"]
        temp_df.at[0, 'STORAGE'] = data_dict["s"]
        temp_df.at[0, 'TECHNOLOGY'] = data_dict["t"]
        temp_df.at[0, 'YEAR'] = data_dict["y"]
        temp_df.at[0, 'FLEXIBLEDEMANDTYPE'] = data_dict["fdt"]

        df = pd.concat([df, temp_df])

    return df


def saveResults(dataframe, fileDir, fileName):
    """
    This function saves all results to an Excel file.
    """
    df = dataframe
    name_list = df['VAR_NAME'].unique()
    dataframe_list = [df[df['VAR_NAME'] == str(name)] for name in name_list]

    if not os.path.exists(fileDir):
        os.makedirs(fileDir)

    writer = pd.ExcelWriter(os.path.join(fileDir, fileName))

    for df, name in zip(dataframe_list, name_list):
        df.to_excel(writer, sheet_name=name, index=False)

    writer.save()
    return


# ----------------------------------------------------------------------------------------------------------------------
#    LOAD DATA
# ----------------------------------------------------------------------------------------------------------------------

inputPath = os.path.join(inputDir, inputFile)
sets_df, p_df, p_default_df, mcs_df, mcs_num = loadData(inputPath, sheetSets, sheetParams, sheetParamsDefault, sheetMcs, sheetMcsNum)
mcs_parameters = mcs_df['PARAM'].unique()  # list of parameters to be included in monte carlo simulation

logging.info("{}\tData is loaded.".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# ----------------------------------------------------------------------------------------------------------------------
#    SETS
# ----------------------------------------------------------------------------------------------------------------------

YEAR = sets_df[sets_df['SET'] == "YEAR"].ELEMENTS.tolist()[0].split(" ")
TECHNOLOGY = sets_df[sets_df['SET'] == "TECHNOLOGY"].ELEMENTS.tolist()[0].split(" ")
TIMESLICE = sets_df[sets_df['SET'] == "TIMESLICE"].ELEMENTS.tolist()[0].split(" ")
FUEL = sets_df[sets_df['SET'] == "FUEL"].ELEMENTS.tolist()[0].split(" ")
EMISSION = sets_df[sets_df['SET'] == "EMISSION"].ELEMENTS.tolist()[0].split(" ")
MODE_OF_OPERATION = sets_df[sets_df['SET'] == "MODE_OF_OPERATION"].ELEMENTS.tolist()[0].split(" ")
REGION = sets_df[sets_df['SET'] == "REGION"].ELEMENTS.tolist()[0].split(" ")
REGION2 = sets_df[sets_df['SET'] == "REGION2"].ELEMENTS.tolist()[0].split(" ")
SEASON = sets_df[sets_df['SET'] == "SEASON"].ELEMENTS.tolist()[0].split(" ")
DAYTYPE = sets_df[sets_df['SET'] == "DAYTYPE"].ELEMENTS.tolist()[0].split(" ")
DAILYTIMEBRACKET = sets_df[sets_df['SET'] == "DAILYTIMEBRACKET"].ELEMENTS.tolist()[0].split(" ")
FLEXIBLEDEMANDTYPE = sets_df[sets_df['SET'] == "FLEXIBLEDEMANDTYPE"].ELEMENTS.tolist()[0].split(" ")
STORAGE = sets_df[sets_df['SET'] == "STORAGE"].ELEMENTS.tolist()[0].split(" ")

logging.info("{}\tSets are created.".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# ----------------------------------------------------------------------------------------------------------------------
#    PARAMETERS AND DATA
# ----------------------------------------------------------------------------------------------------------------------

########			Global 						#########

# YearSplit
YearSplit = p_df[p_df['PARAM'] == "YearSplit"][['TIMESLICE', 'YEAR', 'VALUE']].groupby('TIMESLICE')\
	.apply(lambda df: df.set_index('YEAR')['VALUE'].to_dict()).to_dict()

# DiscountRate
DiscountRate_default_value = p_default_df[p_default_df['PARAM'] == "DiscountRate"].VALUE.iat[0]
DiscountRate_specified = tuple([(str(r)) for r in p_df[p_df['PARAM'] == "DiscountRate"].REGION])
DiscountRate = {str(r): p_df[(p_df['PARAM'] == "DiscountRate") & (p_df['REGION'] == r)].VALUE.iat[0]\
	if (str(r)) in DiscountRate_specified else DiscountRate_default_value for r in REGION}

# DaySplit
DaySplit_default_value = p_default_df[p_default_df['PARAM'] == "DaySplit"].VALUE.iat[0]
DaySplit_specified = tuple([(str(lh), str(y)) for lh, y in zip(
	p_df[p_df['PARAM'] == "DaySplit"].DAILYTIMEBRACKET, p_df[p_df['PARAM'] == "DaySplit"].YEAR)])
DaySplit = {str(lh): {str(y): p_df[(p_df['PARAM'] == "DaySplit") & (p_df['DAILYTIMEBRACKET'] == lh) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(lh), str(y)) in DaySplit_specified else DaySplit_default_value for y in YEAR} for lh in DAILYTIMEBRACKET}

# Conversionls
Conversionls_default_value = p_default_df[p_default_df['PARAM'] == "Conversionls"].VALUE.iat[0]
Conversionls_specified = tuple([(str(l), str(ls)) for l, ls in zip(p_df[p_df['PARAM'] == "Conversionls"].TIMESLICE, p_df[p_df['PARAM'] == "Conversionls"].SEASON)])
Conversionls = {str(l): {str(ls): p_df[(p_df['PARAM'] == "Conversionls") & (p_df['TIMESLICE'] == l) & (p_df['SEASON'] == ls)].VALUE.iat[0] if (str(l), str(ls)) in Conversionls_specified else Conversionls_default_value for ls in SEASON} for l in TIMESLICE}

# Conversionld
Conversionld_default_value = p_default_df[p_default_df['PARAM'] == "Conversionld"].VALUE.iat[0]
Conversionld_specified = tuple([(str(l), str(ld)) for l, ld in zip(p_df[p_df['PARAM'] == "Conversionld"].TIMESLICE, p_df[p_df['PARAM'] == "Conversionld"].DAYTYPE)])
Conversionld = {str(l): {str(ld): p_df[(p_df['PARAM'] == "Conversionld") & (p_df['TIMESLICE'] == l) & (p_df['DAYTYPE'] == ld)].VALUE.iat[0] if (str(l), str(ld)) in Conversionld_specified else Conversionld_default_value for ld in DAYTYPE} for l in TIMESLICE}

# Conversionlh
Conversionlh_default_value = p_default_df[p_default_df['PARAM'] == "Conversionlh"].VALUE.iat[0]
Conversionlh_specified = tuple([(str(l), str(lh)) for l, lh in zip(p_df[p_df['PARAM'] == "Conversionlh"].TIMESLICE, p_df[p_df['PARAM'] == "Conversionlh"].DAILYTIMEBRACKET)])
Conversionlh = {str(l): {str(lh): p_df[(p_df['PARAM'] == "Conversionlh") & (p_df['TIMESLICE'] == l) & (p_df['DAILYTIMEBRACKET'] == lh)].VALUE.iat[0] if (str(l), str(lh)) in Conversionlh_specified else Conversionlh_default_value for lh in DAILYTIMEBRACKET} for l in TIMESLICE}

# DaysInDayType
DaysInDayType_default_value = p_default_df[p_default_df['PARAM'] == "DaysInDayType"].VALUE.iat[0]
DaysInDayType_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(p_df[p_df['PARAM'] == "DaysInDayType"].SEASON, p_df[p_df['PARAM'] == "DaysInDayType"].DAYTYPE, p_df[p_df['PARAM'] == "DaysInDayType"].YEAR)])
DaysInDayType = {str(ls): {str(ld): {str(y): p_df[(p_df['PARAM'] == "DaysInDayType") & (p_df['SEASON'] == ls) & (p_df['DAYTYPE'] == ld) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(ls),str(ld),str(y)) in DaysInDayType_specified else DaysInDayType_default_value for y in YEAR} for ld in DAYTYPE} for ls in SEASON}

# TradeRoute
TradeRoute_default_value = p_default_df[p_default_df['PARAM'] == "TradeRoute"].VALUE.iat[0]
TradeRoute_specified = tuple([(str(r),str(rr),str(f),str(y)) for r, rr, f, y in zip(p_df[p_df['PARAM'] == "TradeRoute"].REGION, p_df[p_df['PARAM'] == "TradeRoute"].REGION2, p_df[p_df['PARAM'] == "TradeRoute"].FUEL, p_df[p_df['PARAM'] == "TradeRoute"].YEAR)])
TradeRoute = {str(r): {str(rr): {str(f): {str(y): p_df[(p_df['PARAM'] == "TradeRoute") & (p_df['REGION'] == r) & (p_df['REGION2'] == rr) & (p_df['FUEL'] == f) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(rr),str(f),str(y)) in TradeRoute_specified else TradeRoute_default_value for y in YEAR} for f in FUEL} for rr in REGION2} for r in REGION}

# DepreciationMethod
DepreciationMethod_default_value = p_default_df[p_default_df['PARAM'] == "DepreciationMethod"].VALUE.iat[0]
DepreciationMethod_specified = tuple([(str(r)) for r in p_df[p_df['PARAM'] == "DepreciationMethod"].REGION])
DepreciationMethod = {str(r): p_df[(p_df['PARAM'] == "DepreciationMethod") & (p_df['REGION'] == r)].VALUE.iat[0] if (str(r)) in DepreciationMethod_specified else DepreciationMethod_default_value for r in REGION}


########			Demands 					#########

# SpecifiedAnnualDemand
SpecifiedAnnualDemand_default_value = p_default_df[p_default_df['PARAM'] == "SpecifiedAnnualDemand"].VALUE.iat[0]
SpecifiedAnnualDemand_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(p_df[p_df['PARAM'] == "SpecifiedAnnualDemand"].REGION, p_df[p_df['PARAM'] == "SpecifiedAnnualDemand"].FUEL, p_df[p_df['PARAM'] == "SpecifiedAnnualDemand"].YEAR)])
SpecifiedAnnualDemand = {str(r): {str(f): {str(y): p_df[(p_df['PARAM'] == "SpecifiedAnnualDemand") & (p_df['REGION'] == r) & (p_df['FUEL'] == f) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(f),str(y)) in SpecifiedAnnualDemand_specified else SpecifiedAnnualDemand_default_value for y in YEAR} for f in FUEL} for r in REGION}

# SpecifiedDemandProfile
SpecifiedDemandProfile_default_value = p_default_df[p_default_df['PARAM'] == "SpecifiedDemandProfile"].VALUE.iat[0]
SpecifiedDemandProfile_specified = tuple([(str(r),str(f),str(l),str(y)) for r, f, l, y in zip(p_df[p_df['PARAM'] == "SpecifiedDemandProfile"].REGION, p_df[p_df['PARAM'] == "SpecifiedDemandProfile"].FUEL, p_df[p_df['PARAM'] == "SpecifiedDemandProfile"].TIMESLICE, p_df[p_df['PARAM'] == "SpecifiedDemandProfile"].YEAR)])
SpecifiedDemandProfile = {str(r): {str(f): {str(l): {str(y): p_df[(p_df['PARAM'] == "SpecifiedDemandProfile") & (p_df['REGION'] == r) & (p_df['FUEL'] == f) & (p_df['TIMESLICE'] == l) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(f),str(l),str(y)) in SpecifiedDemandProfile_specified else SpecifiedDemandProfile_default_value for y in YEAR} for l in TIMESLICE} for f in FUEL} for r in REGION}

# AccumulatedAnnualDemand
AccumulatedAnnualDemand_default_value = p_default_df[p_default_df['PARAM'] == "AccumulatedAnnualDemand"].VALUE.iat[0]
AccumulatedAnnualDemand_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(p_df[p_df['PARAM'] == "AccumulatedAnnualDemand"].REGION, p_df[p_df['PARAM'] == "AccumulatedAnnualDemand"].FUEL, p_df[p_df['PARAM'] == "AccumulatedAnnualDemand"].YEAR)])
AccumulatedAnnualDemand = {str(r): {str(f): {str(y): p_df[(p_df['PARAM'] == "AccumulatedAnnualDemand") & (p_df['REGION'] == r) & (p_df['FUEL'] == f) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(f),str(y)) in AccumulatedAnnualDemand_specified else AccumulatedAnnualDemand_default_value for y in YEAR} for f in FUEL} for r in REGION}


#########			Performance					#########

# CapacityToActivityUnit
CapacityToActivityUnit_default_value = p_default_df[p_default_df['PARAM'] == "CapacityToActivityUnit"].VALUE.iat[0]
CapacityToActivityUnit_specified = tuple([(str(r), str(t)) for r, t in zip(p_df[p_df['PARAM'] == "CapacityToActivityUnit"].REGION, p_df[p_df['PARAM'] == "CapacityToActivityUnit"].TECHNOLOGY)])
CapacityToActivityUnit = {str(r): {str(t): p_df[(p_df['PARAM'] == "CapacityToActivityUnit") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in CapacityToActivityUnit_specified else CapacityToActivityUnit_default_value for t in TECHNOLOGY} for r in REGION}

# TechWithCapacityNeededToMeetPeakTS
TechWithCapacityNeededToMeetPeakTS_default_value = p_default_df[p_default_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].VALUE.iat[0]
TechWithCapacityNeededToMeetPeakTS_specified = tuple([(str(r), str(t)) for r, t in zip(p_df[p_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].REGION, p_df[p_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].TECHNOLOGY)])
TechWithCapacityNeededToMeetPeakTS = {str(r): {str(t): p_df[(p_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in TechWithCapacityNeededToMeetPeakTS_specified else TechWithCapacityNeededToMeetPeakTS_default_value for t in TECHNOLOGY} for r in REGION}

# CapacityFactor
CapacityFactor_default_value = p_default_df[p_default_df['PARAM'] == "CapacityFactor"].VALUE.iat[0]
CapacityFactor_specified = tuple([(str(r),str(t),str(l),str(y)) for r, t, l, y in zip(p_df[p_df['PARAM'] == "CapacityFactor"].REGION, p_df[p_df['PARAM'] == "CapacityFactor"].TECHNOLOGY, p_df[p_df['PARAM'] == "CapacityFactor"].TIMESLICE, p_df[p_df['PARAM'] == "CapacityFactor"].YEAR)])
CapacityFactor = {str(r): {str(t): {str(l): {str(y): p_df[(p_df['PARAM'] == "CapacityFactor") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y) & (p_df['TIMESLICE'] == l)].VALUE.iat[0] if (str(r),str(t),str(l),str(y)) in CapacityFactor_specified else CapacityFactor_default_value for y in YEAR} for l in TIMESLICE} for t in TECHNOLOGY} for r in REGION}

# AvailabilityFactor
AvailabilityFactor_default_value = p_default_df[p_default_df['PARAM'] == "AvailabilityFactor"].VALUE.iat[0]
AvailabilityFactor_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "AvailabilityFactor"].REGION, p_df[p_df['PARAM'] == "AvailabilityFactor"].TECHNOLOGY, p_df[p_df['PARAM'] == "AvailabilityFactor"].YEAR)])
AvailabilityFactor = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "AvailabilityFactor") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(y)) in AvailabilityFactor_specified else AvailabilityFactor_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# OperationalLife
OperationalLife_default_value = p_default_df[p_default_df['PARAM'] == "OperationalLife"].VALUE.iat[0]
OperationalLife_specified = tuple([(str(r), str(t)) for r, t in zip(p_df[p_df['PARAM'] == "OperationalLife"].REGION, p_df[p_df['PARAM'] == "OperationalLife"].TECHNOLOGY)])
OperationalLife = {str(r): {str(t): p_df[(p_df['PARAM'] == "OperationalLife") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in OperationalLife_specified else OperationalLife_default_value for t in TECHNOLOGY} for r in REGION}

# ResidualCapacity
ResidualCapacity_default_value = p_default_df[p_default_df['PARAM'] == "ResidualCapacity"].VALUE.iat[0]
ResidualCapacity_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "ResidualCapacity"].REGION, p_df[p_df['PARAM'] == "ResidualCapacity"].TECHNOLOGY, p_df[p_df['PARAM'] == "ResidualCapacity"].YEAR)])
ResidualCapacity = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "ResidualCapacity") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(y)) in ResidualCapacity_specified else ResidualCapacity_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# InputActivityRatio
InputActivityRatio_default_value = p_default_df[p_default_df['PARAM'] == "InputActivityRatio"].VALUE.iat[0]
InputActivityRatio_specified = tuple([(str(r),str(t),str(f),str(m),str(y)) for r, t, f, m, y in zip(p_df[p_df['PARAM'] == "InputActivityRatio"].REGION, p_df[p_df['PARAM'] == "InputActivityRatio"].TECHNOLOGY, p_df[p_df['PARAM'] == "InputActivityRatio"].FUEL, p_df[p_df['PARAM'] == "InputActivityRatio"].MODE_OF_OPERATION, p_df[p_df['PARAM'] == "InputActivityRatio"].YEAR)])
InputActivityRatio = {str(r): {str(t): {str(f): {str(m): {str(y): p_df[(p_df['PARAM'] == "InputActivityRatio") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['FUEL'] == f) & (p_df['MODE_OF_OPERATION'] == m) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(f),str(m),str(y)) in InputActivityRatio_specified else InputActivityRatio_default_value for y in YEAR} for m in MODE_OF_OPERATION} for f in FUEL} for t in TECHNOLOGY} for r in REGION}

# OutputActivityRatio
OutputActivityRatio_default_value = p_default_df[p_default_df['PARAM'] == "OutputActivityRatio"].VALUE.iat[0]
OutputActivityRatio_specified = tuple([(str(r),str(t),str(f),str(m),str(y)) for r, t, f, m, y in zip(p_df[p_df['PARAM'] == "OutputActivityRatio"].REGION, p_df[p_df['PARAM'] == "OutputActivityRatio"].TECHNOLOGY, p_df[p_df['PARAM'] == "OutputActivityRatio"].FUEL, p_df[p_df['PARAM'] == "OutputActivityRatio"].MODE_OF_OPERATION, p_df[p_df['PARAM'] == "OutputActivityRatio"].YEAR)])
OutputActivityRatio = {str(r): {str(t): {str(f): {str(m): {str(y): p_df[(p_df['PARAM'] == "OutputActivityRatio") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['FUEL'] == f) & (p_df['MODE_OF_OPERATION'] == m) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(f),str(m),str(y)) in OutputActivityRatio_specified else OutputActivityRatio_default_value for y in YEAR} for m in MODE_OF_OPERATION} for f in FUEL} for t in TECHNOLOGY} for r in REGION}


#########			Technology Costs			#########

# CapitalCost
CapitalCost_default_value = p_default_df[p_default_df['PARAM'] == "CapitalCost"].VALUE.iat[0]
CapitalCost_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "CapitalCost"].REGION, p_df[p_df['PARAM'] == "CapitalCost"].TECHNOLOGY, p_df[p_df['PARAM'] == "CapitalCost"].YEAR)])
CapitalCost = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "CapitalCost") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(y)) in CapitalCost_specified else CapitalCost_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# VariableCost
VariableCost_default_value = p_default_df[p_default_df['PARAM'] == "VariableCost"].VALUE.iat[0]
VariableCost_specified = tuple([(str(r),str(t),str(m),str(y)) for r, t, m, y in zip(p_df[p_df['PARAM'] == "VariableCost"].REGION, p_df[p_df['PARAM'] == "VariableCost"].TECHNOLOGY, p_df[p_df['PARAM'] == "VariableCost"].MODE_OF_OPERATION, p_df[p_df['PARAM'] == "VariableCost"].YEAR)])
VariableCost = {str(r): {str(t): {str(m): {str(y): p_df[(p_df['PARAM'] == "VariableCost") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['MODE_OF_OPERATION'] == m) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(m),str(y)) in VariableCost_specified else VariableCost_default_value for y in YEAR} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for r in REGION}

# FixedCost
FixedCost_default_value = p_default_df[p_default_df['PARAM'] == "FixedCost"].VALUE.iat[0]
FixedCost_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "FixedCost"].REGION, p_df[p_df['PARAM'] == "FixedCost"].TECHNOLOGY, p_df[p_df['PARAM'] == "FixedCost"].YEAR)])
FixedCost = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "FixedCost") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(y)) in FixedCost_specified else FixedCost_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}


#########			Storage                 	#########

# TechnologyToStorage
TechnologyToStorage_default_value = p_default_df[p_default_df['PARAM'] == "TechnologyToStorage"].VALUE.iat[0]
TechnologyToStorage_specified = tuple([(str(r),str(t),str(s),str(m)) for r, t, s, m in zip(p_df[p_df['PARAM'] == "TechnologyToStorage"].REGION, p_df[p_df['PARAM'] == "TechnologyToStorage"].TECHNOLOGY, p_df[p_df['PARAM'] == "TechnologyToStorage"].STORAGE, p_df[p_df['PARAM'] == "TechnologyToStorage"].MODE_OF_OPERATION)])
TechnologyToStorage = {str(r): {str(t): {str(s): {str(m): p_df[(p_df['PARAM'] == "TechnologyToStorage") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['STORAGE'] == s) & (p_df['MODE_OF_OPERATION'] == m)].VALUE.iat[0] if (str(r),str(t),str(s),str(m)) in TechnologyToStorage_specified else TechnologyToStorage_default_value for m in MODE_OF_OPERATION} for s in STORAGE} for t in TECHNOLOGY} for r in REGION}

# TechnologyFromStorage
TechnologyFromStorage_default_value = p_default_df[p_default_df['PARAM'] == "TechnologyFromStorage"].VALUE.iat[0]
TechnologyFromStorage_specified = tuple([(str(r),str(t),str(s),str(m)) for r, t, s, m in zip(p_df[p_df['PARAM'] == "TechnologyFromStorage"].REGION, p_df[p_df['PARAM'] == "TechnologyFromStorage"].TECHNOLOGY, p_df[p_df['PARAM'] == "TechnologyFromStorage"].STORAGE, p_df[p_df['PARAM'] == "TechnologyFromStorage"].MODE_OF_OPERATION)])
TechnologyFromStorage = {str(r): {str(t): {str(s): {str(m): p_df[(p_df['PARAM'] == "TechnologyFromStorage") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['STORAGE'] == s) & (p_df['MODE_OF_OPERATION'] == m)].VALUE.iat[0] if (str(r),str(t),str(s),str(m)) in TechnologyFromStorage_specified else TechnologyFromStorage_default_value for m in MODE_OF_OPERATION} for s in STORAGE} for t in TECHNOLOGY} for r in REGION}

# StorageLevelStart
StorageLevelStart_default_value = p_default_df[p_default_df['PARAM'] == "StorageLevelStart"].VALUE.iat[0]
StorageLevelStart_specified = tuple([(str(r), str(s)) for r, s in zip(p_df[p_df['PARAM'] == "StorageLevelStart"].REGION, p_df[p_df['PARAM'] == "StorageLevelStart"].STORAGE)])
StorageLevelStart = {str(r): {str(s): p_df[(p_df['PARAM'] == "StorageLevelStart") & (p_df['REGION'] == r) & (p_df['STORAGE'] == s)].VALUE.iat[0] if (str(r), str(s)) in StorageLevelStart_specified else StorageLevelStart_default_value for s in STORAGE} for r in REGION}

# StorageMaxChargeRate
StorageMaxChargeRate_default_value = p_default_df[p_default_df['PARAM'] == "StorageMaxChargeRate"].VALUE.iat[0]
StorageMaxChargeRate_specified = tuple([(str(r), str(s)) for r, s in zip(p_df[p_df['PARAM'] == "StorageMaxChargeRate"].REGION, p_df[p_df['PARAM'] == "StorageMaxChargeRate"].STORAGE)])
StorageMaxChargeRate = {str(r): {str(s): p_df[(p_df['PARAM'] == "StorageMaxChargeRate") & (p_df['REGION'] == r) & (p_df['STORAGE'] == s)].VALUE.iat[0] if (str(r), str(s)) in StorageMaxChargeRate_specified else StorageMaxChargeRate_default_value for s in STORAGE} for r in REGION}

# StorageMaxDischargeRate
StorageMaxDischargeRate_default_value = p_default_df[p_default_df['PARAM'] == "StorageMaxDischargeRate"].VALUE.iat[0]
StorageMaxDischargeRate_specified = tuple([(str(r), str(s)) for r, s in zip(p_df[p_df['PARAM'] == "StorageMaxDischargeRate"].REGION, p_df[p_df['PARAM'] == "StorageMaxDischargeRate"].STORAGE)])
StorageMaxDischargeRate = {str(r): {str(s): p_df[(p_df['PARAM'] == "StorageMaxDischargeRate") & (p_df['REGION'] == r) & (p_df['STORAGE'] == s)].VALUE.iat[0] if (str(r), str(s)) in StorageMaxDischargeRate_specified else StorageMaxDischargeRate_default_value for s in STORAGE} for r in REGION}

# MinStorageCharge
MinStorageCharge_default_value = p_default_df[p_default_df['PARAM'] == "MinStorageCharge"].VALUE.iat[0]
MinStorageCharge_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(p_df[p_df['PARAM'] == "MinStorageCharge"].REGION, p_df[p_df['PARAM'] == "MinStorageCharge"].STORAGE, p_df[p_df['PARAM'] == "MinStorageCharge"].YEAR)])
MinStorageCharge = {str(r): {str(s): {str(y): p_df[(p_df['PARAM'] == "MinStorageCharge") & (p_df['REGION'] == r) & (p_df['STORAGE'] == s) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(s), str(y)) in MinStorageCharge_specified else MinStorageCharge_default_value for y in YEAR} for s in STORAGE} for r in REGION}

# OperationalLifeStorage
OperationalLifeStorage_default_value = p_default_df[p_default_df['PARAM'] == "OperationalLifeStorage"].VALUE.iat[0]
OperationalLifeStorage_specified = tuple([(str(r), str(s)) for r, s in zip(p_df[p_df['PARAM'] == "OperationalLifeStorage"].REGION, p_df[p_df['PARAM'] == "OperationalLifeStorage"].STORAGE)])
OperationalLifeStorage = {str(r): {str(s): p_df[(p_df['PARAM'] == "OperationalLifeStorage") & (p_df['REGION'] == r) & (p_df['STORAGE'] == s)].VALUE.iat[0] if (str(r), str(s)) in OperationalLifeStorage_specified else OperationalLifeStorage_default_value for s in STORAGE} for r in REGION}

# CapitalCostStorage
CapitalCostStorage_default_value = p_default_df[p_default_df['PARAM'] == "CapitalCostStorage"].VALUE.iat[0]
CapitalCostStorage_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(p_df[p_df['PARAM'] == "CapitalCostStorage"].REGION, p_df[p_df['PARAM'] == "CapitalCostStorage"].STORAGE, p_df[p_df['PARAM'] == "CapitalCostStorage"].YEAR)])
CapitalCostStorage = {str(r): {str(s): {str(y): p_df[(p_df['PARAM'] == "CapitalCostStorage") & (p_df['REGION'] == r) & (p_df['STORAGE'] == s) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(s), str(y)) in CapitalCostStorage_specified else CapitalCostStorage_default_value for y in YEAR} for s in STORAGE} for r in REGION}

# ResidualStorageCapacity
ResidualStorageCapacity_default_value = p_default_df[p_default_df['PARAM'] == "ResidualStorageCapacity"].VALUE.iat[0]
ResidualStorageCapacity_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(p_df[p_df['PARAM'] == "ResidualStorageCapacity"].REGION, p_df[p_df['PARAM'] == "ResidualStorageCapacity"].STORAGE, p_df[p_df['PARAM'] == "ResidualStorageCapacity"].YEAR)])
ResidualStorageCapacity = {str(r): {str(s): {str(y): p_df[(p_df['PARAM'] == "ResidualStorageCapacity") & (p_df['REGION'] == r) & (p_df['STORAGE'] == s) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(s), str(y)) in ResidualStorageCapacity_specified else ResidualStorageCapacity_default_value for y in YEAR} for s in STORAGE} for r in REGION}


#########			Capacity Constraints		#########

# CapacityOfOneTechnologyUnit
CapacityOfOneTechnologyUnit_default_value = p_default_df[p_default_df['PARAM'] == "CapacityOfOneTechnologyUnit"].VALUE.iat[0]
CapacityOfOneTechnologyUnit_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "CapacityOfOneTechnologyUnit"].REGION, p_df[p_df['PARAM'] == "CapacityOfOneTechnologyUnit"].TECHNOLOGY, p_df[p_df['PARAM'] == "CapacityOfOneTechnologyUnit"].YEAR)])
CapacityOfOneTechnologyUnit = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "CapacityOfOneTechnologyUnit") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in CapacityOfOneTechnologyUnit_specified else CapacityOfOneTechnologyUnit_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalAnnualMaxCapacity
TotalAnnualMaxCapacity_default_value = p_default_df[p_default_df['PARAM'] == "TotalAnnualMaxCapacity"].VALUE.iat[0]
TotalAnnualMaxCapacity_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "TotalAnnualMaxCapacity"].REGION, p_df[p_df['PARAM'] == "TotalAnnualMaxCapacity"].TECHNOLOGY, p_df[p_df['PARAM'] == "TotalAnnualMaxCapacity"].YEAR)])
TotalAnnualMaxCapacity = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "TotalAnnualMaxCapacity") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalAnnualMaxCapacity_specified else TotalAnnualMaxCapacity_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalAnnualMinCapacity
TotalAnnualMinCapacity_default_value = p_default_df[p_default_df['PARAM'] == "TotalAnnualMinCapacity"].VALUE.iat[0]
TotalAnnualMinCapacity_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "TotalAnnualMinCapacity"].REGION, p_df[p_df['PARAM'] == "TotalAnnualMinCapacity"].TECHNOLOGY, p_df[p_df['PARAM'] == "TotalAnnualMinCapacity"].YEAR)])
TotalAnnualMinCapacity = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "TotalAnnualMinCapacity") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalAnnualMinCapacity_specified else TotalAnnualMinCapacity_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}


#########			Investment Constraints		#########

# TotalAnnualMaxCapacityInvestment
TotalAnnualMaxCapacityInvestment_default_value = p_default_df[p_default_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].VALUE.iat[0]
TotalAnnualMaxCapacityInvestment_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].REGION, p_df[p_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].TECHNOLOGY, p_df[p_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].YEAR)])
TotalAnnualMaxCapacityInvestment = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "TotalAnnualMaxCapacityInvestment") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalAnnualMaxCapacityInvestment_specified else TotalAnnualMaxCapacityInvestment_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalAnnualMinCapacityInvestment
TotalAnnualMinCapacityInvestment_default_value = p_default_df[p_default_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].VALUE.iat[0]
TotalAnnualMinCapacityInvestment_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].REGION, p_df[p_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].TECHNOLOGY, p_df[p_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].YEAR)])
TotalAnnualMinCapacityInvestment = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "TotalAnnualMinCapacityInvestment") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalAnnualMinCapacityInvestment_specified else TotalAnnualMinCapacityInvestment_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}


#########			Activity Constraints		#########

# TotalTechnologyAnnualActivityUpperLimit
TotalTechnologyAnnualActivityUpperLimit_default_value = p_default_df[p_default_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].VALUE.iat[0]
TotalTechnologyAnnualActivityUpperLimit_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].REGION, p_df[p_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].TECHNOLOGY, p_df[p_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].YEAR)])
TotalTechnologyAnnualActivityUpperLimit = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalTechnologyAnnualActivityUpperLimit_specified else TotalTechnologyAnnualActivityUpperLimit_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalTechnologyAnnualActivityLowerLimit
TotalTechnologyAnnualActivityLowerLimit_default_value = p_default_df[p_default_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].VALUE.iat[0]
TotalTechnologyAnnualActivityLowerLimit_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].REGION, p_df[p_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].TECHNOLOGY, p_df[p_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].YEAR)])
TotalTechnologyAnnualActivityLowerLimit = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalTechnologyAnnualActivityLowerLimit_specified else TotalTechnologyAnnualActivityLowerLimit_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalTechnologyModelPeriodActivityUpperLimit
TotalTechnologyModelPeriodActivityUpperLimit_default_value = p_default_df[p_default_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].VALUE.iat[0]
TotalTechnologyModelPeriodActivityUpperLimit_specified = tuple([(str(r), str(t)) for r, t in zip(p_df[p_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].REGION, p_df[p_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].TECHNOLOGY)])
TotalTechnologyModelPeriodActivityUpperLimit = {str(r): {str(t): p_df[(p_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in TotalTechnologyModelPeriodActivityUpperLimit_specified else TotalTechnologyModelPeriodActivityUpperLimit_default_value for t in TECHNOLOGY} for r in REGION}

# TotalTechnologyModelPeriodActivityLowerLimit
TotalTechnologyModelPeriodActivityLowerLimit_default_value = p_default_df[p_default_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].VALUE.iat[0]
TotalTechnologyModelPeriodActivityLowerLimit_specified = tuple([(str(r), str(t)) for r, t in zip(p_df[p_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].REGION, p_df[p_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].TECHNOLOGY)])
TotalTechnologyModelPeriodActivityLowerLimit = {str(r): {str(t): p_df[(p_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in TotalTechnologyModelPeriodActivityLowerLimit_specified else TotalTechnologyModelPeriodActivityLowerLimit_default_value for t in TECHNOLOGY} for r in REGION}


#########			Reserve Margin				#########

# ReserveMarginTagTechnology
ReserveMarginTagTechnology_default_value = p_default_df[p_default_df['PARAM'] == "ReserveMarginTagTechnology"].VALUE.iat[0]
ReserveMarginTagTechnology_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "ReserveMarginTagTechnology"].REGION, p_df[p_df['PARAM'] == "ReserveMarginTagTechnology"].TECHNOLOGY, p_df[p_df['PARAM'] == "ReserveMarginTagTechnology"].YEAR)])
ReserveMarginTagTechnology = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "ReserveMarginTagTechnology") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in ReserveMarginTagTechnology_specified else ReserveMarginTagTechnology_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# ReserveMarginTagFuel
ReserveMarginTagFuel_default_value = p_default_df[p_default_df['PARAM'] == "ReserveMarginTagFuel"].VALUE.iat[0]
ReserveMarginTagFuel_specified = tuple([(str(r), str(f), str(y)) for r, f, y in zip(p_df[p_df['PARAM'] == "ReserveMarginTagFuel"].REGION, p_df[p_df['PARAM'] == "ReserveMarginTagFuel"].FUEL, p_df[p_df['PARAM'] == "ReserveMarginTagFuel"].YEAR)])
ReserveMarginTagFuel = {str(r): {str(f): {str(y): p_df[(p_df['PARAM'] == "ReserveMarginTagFuel") & (p_df['REGION'] == r) & (p_df['FUEL'] == f) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(f), str(y)) in ReserveMarginTagFuel_specified else ReserveMarginTagFuel_default_value for y in YEAR} for f in FUEL} for r in REGION}

# ReserveMargin
ReserveMargin_default_value = p_default_df[p_default_df['PARAM'] == "ReserveMargin"].VALUE.iat[0]
ReserveMargin_specified = tuple([(str(r), str(y)) for r, y in zip(p_df[p_df['PARAM'] == "ReserveMargin"].REGION, p_df[p_df['PARAM'] == "ReserveMargin"].YEAR)])
ReserveMargin = {str(r): {str(y): p_df[(p_df['PARAM'] == "ReserveMargin") & (p_df['REGION'] == r) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(y)) in ReserveMargin_specified else ReserveMargin_default_value for y in YEAR} for r in REGION}


#########			RE Generation Target		#########

# RETagTechnology
RETagTechnology_default_value = p_default_df[p_default_df['PARAM'] == "RETagTechnology"].VALUE.iat[0]
RETagTechnology_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(p_df[p_df['PARAM'] == "RETagTechnology"].REGION, p_df[p_df['PARAM'] == "RETagTechnology"].TECHNOLOGY, p_df[p_df['PARAM'] == "RETagTechnology"].YEAR)])
RETagTechnology = {str(r): {str(t): {str(y): p_df[(p_df['PARAM'] == "RETagTechnology") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in RETagTechnology_specified else RETagTechnology_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# RETagFuel
RETagFuel_default_value = p_default_df[p_default_df['PARAM'] == "RETagFuel"].VALUE.iat[0]
RETagFuel_specified = tuple([(str(r), str(f), str(y)) for r, f, y in zip(p_df[p_df['PARAM'] == "RETagFuel"].REGION, p_df[p_df['PARAM'] == "RETagFuel"].FUEL, p_df[p_df['PARAM'] == "RETagFuel"].YEAR)])
RETagFuel = {str(r): {str(f): {str(y): p_df[(p_df['PARAM'] == "RETagFuel") & (p_df['REGION'] == r) & (p_df['FUEL'] == f) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(f), str(y)) in RETagFuel_specified else RETagFuel_default_value for y in YEAR} for f in FUEL} for r in REGION}

# REMinProductionTarget
REMinProductionTarget_default_value = p_default_df[p_default_df['PARAM'] == "REMinProductionTarget"].VALUE.iat[0]
REMinProductionTarget_specified = tuple([(str(r), str(y)) for r, y in zip(p_df[p_df['PARAM'] == "REMinProductionTarget"].REGION, p_df[p_df['PARAM'] == "REMinProductionTarget"].YEAR)])
REMinProductionTarget = {str(r): {str(y): p_df[(p_df['PARAM'] == "REMinProductionTarget") & (p_df['REGION'] == r) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(y)) in REMinProductionTarget_specified else REMinProductionTarget_default_value for y in YEAR} for r in REGION}


#########			Emissions & Penalties		#########

# EmissionActivityRatio
EmissionActivityRatio_default_value = p_default_df[p_default_df['PARAM'] == "EmissionActivityRatio"].VALUE.iat[0]
EmissionActivityRatio_specified = tuple([(str(r),str(t),str(e),str(m),str(y)) for r, t, e, m, y in zip(p_df[p_df['PARAM'] == "EmissionActivityRatio"].REGION, p_df[p_df['PARAM'] == "EmissionActivityRatio"].TECHNOLOGY, p_df[p_df['PARAM'] == "EmissionActivityRatio"].EMISSION, p_df[p_df['PARAM'] == "EmissionActivityRatio"].MODE_OF_OPERATION, p_df[p_df['PARAM'] == "EmissionActivityRatio"].YEAR)])
EmissionActivityRatio = {str(r): {str(t): {str(e): {str(m): {str(y): p_df[(p_df['PARAM'] == "EmissionActivityRatio") & (p_df['REGION'] == r) & (p_df['TECHNOLOGY'] == t) & (p_df['EMISSION'] == e) & (p_df['MODE_OF_OPERATION'] == m) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(e),str(m),str(y)) in EmissionActivityRatio_specified else EmissionActivityRatio_default_value for y in YEAR} for m in MODE_OF_OPERATION} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}

# EmissionsPenalty
EmissionsPenalty_default_value = p_default_df[p_default_df['PARAM'] == "EmissionsPenalty"].VALUE.iat[0]
EmissionsPenalty_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(p_df[p_df['PARAM'] == "EmissionsPenalty"].REGION, p_df[p_df['PARAM'] == "EmissionsPenalty"].EMISSION, p_df[p_df['PARAM'] == "EmissionsPenalty"].YEAR)])
EmissionsPenalty = {str(r): {str(e): {str(y): p_df[(p_df['PARAM'] == "EmissionsPenalty") & (p_df['REGION'] == r) & (p_df['EMISSION'] == e) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(e), str(y)) in EmissionsPenalty_specified else EmissionsPenalty_default_value for y in YEAR} for e in EMISSION} for r in REGION}

# AnnualExogenousEmission
AnnualExogenousEmission_default_value = p_default_df[p_default_df['PARAM'] == "AnnualExogenousEmission"].VALUE.iat[0]
AnnualExogenousEmission_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(p_df[p_df['PARAM'] == "AnnualExogenousEmission"].REGION, p_df[p_df['PARAM'] == "AnnualExogenousEmission"].EMISSION, p_df[p_df['PARAM'] == "AnnualExogenousEmission"].YEAR)])
AnnualExogenousEmission = {str(r): {str(e): {str(y): p_df[(p_df['PARAM'] == "AnnualExogenousEmission") & (p_df['REGION'] == r) & (p_df['EMISSION'] == e) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(e), str(y)) in AnnualExogenousEmission_specified else AnnualExogenousEmission_default_value for y in YEAR} for e in EMISSION} for r in REGION}

# AnnualEmissionLimit
AnnualEmissionLimit_default_value = p_default_df[p_default_df['PARAM'] == "AnnualEmissionLimit"].VALUE.iat[0]
AnnualEmissionLimit_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(p_df[p_df['PARAM'] == "AnnualEmissionLimit"].REGION, p_df[p_df['PARAM'] == "AnnualEmissionLimit"].EMISSION, p_df[p_df['PARAM'] == "AnnualEmissionLimit"].YEAR)])
AnnualEmissionLimit = {str(r): {str(e): {str(y): p_df[(p_df['PARAM'] == "AnnualEmissionLimit") & (p_df['REGION'] == r) & (p_df['EMISSION'] == e) & (p_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(e), str(y)) in AnnualEmissionLimit_specified else AnnualEmissionLimit_default_value for y in YEAR} for e in EMISSION} for r in REGION}

# ModelPeriodExogenousEmission
ModelPeriodExogenousEmission_default_value = p_default_df[p_default_df['PARAM'] == "ModelPeriodExogenousEmission"].VALUE.iat[0]
ModelPeriodExogenousEmission_specified = tuple([(str(r), str(e)) for r, e in zip(p_df[p_df['PARAM'] == "ModelPeriodExogenousEmission"].REGION, p_df[p_df['PARAM'] == "ModelPeriodExogenousEmission"].EMISSION)])
ModelPeriodExogenousEmission = {str(r): {str(e): p_df[(p_df['PARAM'] == "ModelPeriodExogenousEmission") & (p_df['REGION'] == r) & (p_df['EMISSION'] == e)].VALUE.iat[0] if (str(r), str(e)) in ModelPeriodExogenousEmission_specified else ModelPeriodExogenousEmission_default_value for e in EMISSION} for r in REGION}

# ModelPeriodEmissionLimit
ModelPeriodEmissionLimit_default_value = p_default_df[p_default_df['PARAM'] == "ModelPeriodEmissionLimit"].VALUE.iat[0]
ModelPeriodEmissionLimit_specified = tuple([(str(r), str(e)) for r, e in zip(p_df[p_df['PARAM'] == "ModelPeriodEmissionLimit"].REGION, p_df[p_df['PARAM'] == "ModelPeriodEmissionLimit"].EMISSION)])
ModelPeriodEmissionLimit = {str(r): {str(e): p_df[(p_df['PARAM'] == "ModelPeriodEmissionLimit") & (p_df['REGION'] == r) & (p_df['EMISSION'] == e)].VALUE.iat[0] if (str(r), str(e)) in ModelPeriodEmissionLimit_specified else ModelPeriodEmissionLimit_default_value for e in EMISSION} for r in REGION}

logging.info("{}\tParameters are created.".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

i = 0
while i <= mcs_num:

	#########			Simulation loops     #########

	logging.info("{}\tModel run #{}".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), i))

	# ------------------------------------------------------------------------------------------------------------------
	#    MODEL INITIALIZATION
	# ------------------------------------------------------------------------------------------------------------------
	
	model = pulp.LpProblem(modelName, pulp.LpMinimize)

	# ------------------------------------------------------------------------------------------------------------------
	#    MODEL VARIABLES
	# ------------------------------------------------------------------------------------------------------------------

	########			Demands 					#########
	
	RateOfDemand = {str(r): {str(l): {str(f): {str(y): newVar("RateOfDemand", 0, None, 'Continuous', r, l, f, y) for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	Demand = {str(r): {str(l): {str(f): {str(y): newVar("Demand", 0, None, 'Continuous', r, l, f, y) for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	
	########			Storage                 	#########
	
	RateOfStorageCharge = {str(r): {str(s): {str(ls): {str(ld): {str(lh): {str(y): newVar("RateOfStorageCharge", 0, None, 'Continuous', r, s, ls, ld, lh, y) for y in YEAR} for lh in DAILYTIMEBRACKET} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	RateOfStorageDischarge = {str(r): {str(s): {str(ls): {str(ld): {str(lh): {str(y): newVar("RateOfStorageDischarge", None, None, 'Continuous', r, s, ls, ld, lh, y) for y in YEAR} for lh in DAILYTIMEBRACKET} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	NetChargeWithinYear = {str(r): {str(s): {str(ls): {str(ld): {str(lh): {str(y): newVar("NetChargeWithinYear", None, None, 'Continuous', r, s, ls, ld, lh, y) for y in YEAR} for lh in DAILYTIMEBRACKET} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	NetChargeWithinDay = {str(r): {str(s): {str(ls): {str(ld): {str(lh): {str(y): newVar("NetChargeWithinDay", None, None, 'Continuous', r, s, ls, ld, lh, y) for y in YEAR} for lh in DAILYTIMEBRACKET} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	StorageLevelYearStart = {str(r): {str(s): {str(y): newVar("StorageLevelYearStart", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	StorageLevelYearFinish = {str(r): {str(s): {str(y): newVar("StorageLevelYearFinish", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	StorageLevelSeasonStart = {str(r): {str(s): {str(ls): {str(y): newVar("StorageLevelSeasonStart", 0, None, 'Continuous', r, s, ls, y) for y in YEAR} for ls in SEASON} for s in STORAGE} for r in REGION}
	StorageLevelDayTypeStart = {str(r): {str(s): {str(ls): {str(ld): {str(y): newVar("StorageLevelDayTypeStart", 0, None, 'Continuous', r, s, ls, ld, y) for y in YEAR} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	StorageLevelDayTypeFinish = {str(r): {str(s): {str(ls): {str(ld): {str(y): newVar("StorageLevelDayTypeFinish", 0, None, 'Continuous', r, s, ls, ld, y) for y in YEAR} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	StorageLowerLimit = {str(r): {str(s): {str(y): newVar("StorageLowerLimit", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	StorageUpperLimit = {str(r): {str(s): {str(y): newVar("StorageUpperLimit", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	AccumulatedNewStorageCapacity = {str(r): {str(s): {str(y): newVar("AccumulatedNewStorageCapacity", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	NewStorageCapacity = {str(r): {str(s): {str(y): newVar("NewStorageCapacity", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	CapitalInvestmentStorage = {str(r): {str(s): {str(y): newVar("CapitalInvestmentStorage", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	DiscountedCapitalInvestmentStorage = {str(r): {str(s): {str(y): newVar("DiscountedCapitalInvestmentStorage", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	SalvageValueStorage = {str(r): {str(s): {str(y): newVar("SalvageValueStorage", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	DiscountedSalvageValueStorage = {str(r): {str(s): {str(y): newVar("DiscountedSalvageValueStorage", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	TotalDiscountedStorageCost = {str(r): {str(s): {str(y): newVar("TotalDiscountedStorageCost", 0, None, 'Continuous', r, s, y) for y in YEAR} for s in STORAGE} for r in REGION}
	
	#########			Capacity Variables 			#########
	
	NumberOfNewTechnologyUnits = {str(r): {str(t): {str(y): newVar("NumberOfNewTechnologyUnits", 0, None, 'Integer', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	NewCapacity = {str(r): {str(t): {str(y): newVar("NewCapacity", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	AccumulatedNewCapacity = {str(r): {str(t): {str(y): newVar("AccumulatedNewCapacity", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	TotalCapacityAnnual = {str(r): {str(t): {str(y): newVar("TotalCapacityAnnual", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	
	#########			Activity Variables 			#########
	
	RateOfActivity = {str(r): {str(l): {str(t): {str(m): {str(y): newVar("RateOfActivity", 0, None, 'Continuous', r, l, t, m, y) for y in YEAR} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	RateOfTotalActivity = {str(r): {str(t): {str(l): {str(y): newVar("RateOfTotalActivity", 0, None, 'Continuous', r, t, l, y) for y in YEAR} for l in TIMESLICE} for t in TECHNOLOGY} for r in REGION}
	TotalTechnologyAnnualActivity = {str(r): {str(t): {str(y): newVar("TotalTechnologyAnnualActivity", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	TotalAnnualTechnologyActivityByMode = {str(r): {str(t): {str(m): {str(y): newVar("TotalAnnualTechnologyActivityByMode", 0, None, 'Continuous', r, t, m, y) for y in YEAR} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for r in REGION}
	TotalTechnologyModelPeriodActivity = {str(r): {str(t): newVar("TotalTechnologyModelPeriodActivity", None, None, 'Continuous', r, t) for t in TECHNOLOGY} for r in REGION}
	RateOfProductionByTechnologyByMode = {str(r): {str(l): {str(t): {str(m): {str(f): {str(y): newVar("RateOfProductionByTechnologyByMode", 0, None, 'Continuous', r, l, t, m, f, y) for y in YEAR} for f in FUEL} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	RateOfProductionByTechnology = {str(r): {str(l): {str(t): {str(f): {str(y): newVar("RateOfProductionByTechnology", 0, None, 'Continuous', r, l, t, f, y) for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	ProductionByTechnology = {str(r): {str(l): {str(t): {str(f): {str(y): newVar("ProductionByTechnology", 0, None, 'Continuous', r, l, t, f, y) for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	ProductionByTechnologyAnnual = {str(r): {str(t): {str(f): {str(y): newVar("ProductionByTechnologyAnnual", 0, None, 'Continuous', r, t, f, y) for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for r in REGION}
	RateOfProduction = {str(r): {str(l): {str(f): {str(y): newVar("RateOfProduction", 0, None, 'Continuous', r, l, f, y) for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	Production = {str(r): {str(l): {str(f): {str(y): newVar("Production", 0, None, 'Continuous', r, l, f, y) for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	RateOfUseByTechnologyByMode = {str(r): {str(l): {str(t): {str(m): {str(f): {str(y): newVar("RateOfUseByTechnologyByMode", 0, None, 'Continuous', r, l, t, m, f, y) for y in YEAR} for f in FUEL} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	RateOfUseByTechnology = {str(r): {str(l): {str(t): {str(f): {str(y): newVar("RateOfUseByTechnology", 0, None, 'Continuous', r, l, t, f, y) for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	UseByTechnologyAnnual = {str(r): {str(t): {str(f): {str(y): newVar("UseByTechnologyAnnual", 0, None, 'Continuous', r, t, f, y) for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for r in REGION}
	RateOfUse = {str(r): {str(l): {str(f): {str(y): newVar("RateOfUse", 0, None, 'Continuous', r, l, f, y) for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	UseByTechnology = {str(r): {str(l): {str(t): {str(f): {str(y): newVar("UseByTechnology", 0, None, 'Continuous', r, l, t, f, y) for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	Use = {str(r): {str(l): {str(f): {str(y): newVar("Use", 0, None, 'Continuous', r, l, f, y) for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	Trade = {str(r): {str(rr): {str(l): {str(f): {str(y): newVar("Trade", None, None, 'Continuous', r, rr, l, f, y) for y in YEAR} for f in FUEL} for l in TIMESLICE} for rr in REGION2} for r in REGION}
	TradeAnnual = {str(r): {str(rr): {str(f): {str(y): newVar("TradeAnnual", None, None, 'Continuous', r, rr, f, y) for y in YEAR} for f in FUEL} for rr in REGION2} for r in REGION}
	ProductionAnnual = {str(r): {str(f): {str(y): newVar("ProductionAnnual", 0, None, 'Continuous', r, f, y) for y in YEAR} for f in FUEL} for r in REGION}
	UseAnnual = {str(r): {str(f): {str(y): newVar("UseAnnual", 0, None, 'Continuous', r, f, y) for y in YEAR} for f in FUEL} for r in REGION}
	
	#########			Costing Variables 			#########
	
	CapitalInvestment = {str(r): {str(t): {str(y): newVar("CapitalInvestment", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	DiscountedCapitalInvestment = {str(r): {str(t): {str(y): newVar("DiscountedCapitalInvestment", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	SalvageValue = {str(r): {str(t): {str(y): newVar("SalvageValue", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	DiscountedSalvageValue = {str(r): {str(t): {str(y): newVar("DiscountedSalvageValue", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	OperatingCost = {str(r): {str(t): {str(y): newVar("OperatingCost", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	DiscountedOperatingCost = {str(r): {str(t): {str(y): newVar("DiscountedOperatingCost", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	AnnualVariableOperatingCost = {str(r): {str(t): {str(y): newVar("AnnualVariableOperatingCost", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	AnnualFixedOperatingCost = {str(r): {str(t): {str(y): newVar("AnnualFixedOperatingCost", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	TotalDiscountedCostByTechnology = {str(r): {str(t): {str(y): newVar("TotalDiscountedCostByTechnology", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	TotalDiscountedCost = {str(r): {str(y): newVar("TotalDiscountedCost", 0, None, 'Continuous', r, y) for y in YEAR} for r in REGION}
	ModelPeriodCostByRegion = {str(r): newVar("ModelPeriodCostByRegion", 0, None, 'Continuous', r) for r in REGION}
	
	#########			Reserve Margin				#########
	
	TotalCapacityInReserveMargin = {str(r): {str(y): newVar("TotalCapacityInReserveMargin", 0, None, 'Continuous', r, y) for y in YEAR} for r in REGION}
	DemandNeedingReserveMargin = {str(r): {str(l): {str(y): newVar("DemandNeedingReserveMargin", 0, None, 'Continuous', r, l, y) for y in YEAR} for l in TIMESLICE} for r in REGION}
	
	#########			RE Gen Target				#########
	
	TotalREProductionAnnual = {str(r): {str(y): newVar("TotalREProductionAnnual", None, None, 'Continuous', r, y) for y in YEAR} for r in REGION}
	RETotalProductionOfTargetFuelAnnual = {str(r): {str(y): newVar("RETotalProductionOfTargetFuelAnnual", None, None, 'Continuous', r, y) for y in YEAR} for r in REGION}
	
	#########			Emissions					#########
	
	AnnualTechnologyEmissionByMode = {str(r): {str(t): {str(e): {str(m): {str(y): newVar("AnnualTechnologyEmissionByMode", 0, None, 'Continuous', r, t, e, m, y) for y in YEAR} for m in MODE_OF_OPERATION} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}
	AnnualTechnologyEmission = {str(r): {str(t): {str(e): {str(y): newVar("AnnualTechnologyEmission", 0, None, 'Continuous', r, t, e, y) for y in YEAR} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}
	AnnualTechnologyEmissionPenaltyByEmission = {str(r): {str(t): {str(e): {str(y): newVar("AnnualTechnologyEmissionPenaltyByEmission", 0, None, 'Continuous', r, t, e, y) for y in YEAR} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}
	AnnualTechnologyEmissionsPenalty = {str(r): {str(t): {str(y): newVar("AnnualTechnologyEmissionsPenalty", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	DiscountedTechnologyEmissionsPenalty = {str(r): {str(t): {str(y): newVar("DiscountedTechnologyEmissionsPenalty", 0, None, 'Continuous', r, t, y) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	AnnualEmissions = {str(r): {str(e): {str(y): newVar("AnnualEmissions", 0, None, 'Continuous', r, e, y) for y in YEAR} for e in EMISSION} for r in REGION}
	ModelPeriodEmissions = {str(r): {str(e): newVar("ModelPeriodEmissions", 0, None, 'Continuous', r, e) for e in EMISSION} for r in REGION}
	
	logging.info("{}\tVariables are created".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

	# ------------------------------------------------------------------------------------------------------------------
	#    OBJECTIVE FUNCTION
	# ------------------------------------------------------------------------------------------------------------------
	
	cost = pulp.LpVariable("cost", cat='Continuous')
	model += cost, "Objective"
	model += cost == pulp.lpSum([TotalDiscountedCost[r][y] for r in REGION for y in YEAR]), "Cost_function"

	# ------------------------------------------------------------------------------------------------------------------
	#    CONSTRAINTS
	# ------------------------------------------------------------------------------------------------------------------

	for r in REGION:
		for l in TIMESLICE:
			for f in FUEL:
				for y in YEAR:
					# EQ_SpecifiedDemand
					model += RateOfDemand[r][l][f][y] == SpecifiedAnnualDemand[r][f][y] * SpecifiedDemandProfile[r][f][l][y] / YearSplit[l][y], ""
	
	#########			Capacity Adequacy A	     	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				# CAa1_TotalNewCapacity
				model += AccumulatedNewCapacity[r][t][y] == pulp.lpSum([NewCapacity[r][t][yy] for yy in YEAR if (int(y) - int(yy) < OperationalLife[r][t]) and (int(y) - int(yy) >= 0)]), ""
				# CAa2_TotalAnnualCapacity
				model += TotalCapacityAnnual[r][t][y] == AccumulatedNewCapacity[r][t][y] + ResidualCapacity[r][t][y], ""
	
				for l in TIMESLICE:
					# CAa3_TotalActivityOfEachTechnology
					model += RateOfTotalActivity[r][t][l][y] == pulp.lpSum([RateOfActivity[r][l][t][m][y] for m in MODE_OF_OPERATION]), ""
					# CAa4_Constraint_Capacity
					model += RateOfTotalActivity[r][t][l][y] <= TotalCapacityAnnual[r][t][y] * CapacityFactor[r][t][l][y] * CapacityToActivityUnit[r][t], ""
	
				if CapacityOfOneTechnologyUnit[r][t][y] != 0:
					# CAa5_TotalNewCapacity
					model += NewCapacity[r][t][y] == CapacityOfOneTechnologyUnit[r][t][y] * NumberOfNewTechnologyUnits[r][t][y], ""
	
	#########			Capacity Adequacy B		 	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				# CAb1_PlannedMaintenance
				model += pulp.lpSum([RateOfTotalActivity[r][t][l][y] * YearSplit[l][y] for l in TIMESLICE]) <= pulp.lpSum([TotalCapacityAnnual[r][t][y] * CapacityFactor[r][t][l][y] * YearSplit[l][y] for l in TIMESLICE]) * AvailabilityFactor[r][t][y] * CapacityToActivityUnit[r][t], ""
	
	#########			Energy Balance A    	 	#########
	
	for r in REGION:
		for l in TIMESLICE:
			for f in FUEL:
				for y in YEAR:
					for t in TECHNOLOGY:
						for m in MODE_OF_OPERATION:
							# EBa1_RateOfFuelProduction1
							if OutputActivityRatio[r][t][f][m][y] != 0:
								model += RateOfProductionByTechnologyByMode[r][l][t][m][f][y] == RateOfActivity[r][l][t][m][y] * OutputActivityRatio[r][t][f][m][y], ""
							else:
								model += RateOfProductionByTechnologyByMode[r][l][t][m][f][y] == 0, ""
						# EBa2_RateOfFuelProduction2
						model += RateOfProductionByTechnology[r][l][t][f][y] == pulp.lpSum([RateOfProductionByTechnologyByMode[r][l][t][m][f][y] for m in MODE_OF_OPERATION if OutputActivityRatio[r][t][f][m][y] != 0]), ""
					# EBa3_RateOfFuelProduction3
					model += RateOfProduction[r][l][f][y] == pulp.lpSum([RateOfProductionByTechnology[r][l][t][f][y] for t in TECHNOLOGY]), ""
	
					for t in TECHNOLOGY:
						for m in MODE_OF_OPERATION:
							# EBa4_RateOfFuelUse1
							if InputActivityRatio[r][t][f][m][y] != 0:
								model += RateOfUseByTechnologyByMode[r][l][t][m][f][y] == RateOfActivity[r][l][t][m][y] * InputActivityRatio[r][t][f][m][y], ""
						# EBa5_RateOfFuelUse2
						model += RateOfUseByTechnology[r][l][t][f][y] == pulp.lpSum([RateOfUseByTechnologyByMode[r][l][t][m][f][y] for m in MODE_OF_OPERATION if InputActivityRatio[r][t][f][m][y] != 0]), ""
					# EBa6_RateOfFuelUse3
					model += RateOfUse[r][l][f][y] == pulp.lpSum([RateOfUseByTechnology[r][l][t][f][y] for t in TECHNOLOGY]), ""
					# EBa7_EnergyBalanceEachTS1
					model += Production[r][l][f][y] == RateOfProduction[r][l][f][y] * YearSplit[l][y], ""
					# EBa8_EnergyBalanceEachTS2
					model += Use[r][l][f][y] == RateOfUse[r][l][f][y] * YearSplit[l][y], ""
					# EBa9_EnergyBalanceEachTS3
					model += Demand[r][l][f][y] == RateOfDemand[r][l][f][y] * YearSplit[l][y], ""

					for rr in REGION2:
						# EBa10_EnergyBalanceEachTS4
						model += Trade[r][rr][l][f][y] == -Trade[rr][r][l][f][y], ""
					# EBa11_EnergyBalanceEachTS5
					model += Production[r][l][f][y] >= Demand[r][l][f][y] + Use[r][l][f][y] + pulp.lpSum([Trade[r][rr][l][f][y] * TradeRoute[r][rr][f][y] for rr in REGION2]), ""
	
	#########        	Energy Balance B		 	#########
	
	for r in REGION:
		for f in FUEL:
			for y in YEAR:
				# EBb1_EnergyBalanceEachYear1
				model += ProductionAnnual[r][f][y] == pulp.lpSum([Production[r][l][f][y] for l in TIMESLICE]), ""
				# EBb2_EnergyBalanceEachYear2
				model += UseAnnual[r][f][y] == pulp.lpSum([Use[r][l][f][y] for l in TIMESLICE]), ""
	
				for rr in REGION2:
					# EBb3_EnergyBalanceEachYear3
					model += TradeAnnual[r][rr][f][y] == pulp.lpSum([Trade[r][rr][l][f][y] for l in TIMESLICE]), ""
				# EBb4_EnergyBalanceEachYear4
				model += ProductionAnnual[r][f][y] >= UseAnnual[r][f][y] + pulp.lpSum([TradeAnnual[r][rr][f][y] * TradeRoute[r][rr][f][y] for rr in REGION2]) + AccumulatedAnnualDemand[r][f][y], ""
	
	#########			Accounting Technology Production/Use	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				for l in TIMESLICE:
					for f in FUEL:
						# Acc1_FuelProductionByTechnology
						model += ProductionByTechnology[r][l][t][f][y] == RateOfProductionByTechnology[r][l][t][f][y] * YearSplit[l][y], ""
						# Acc2_FuelUseByTechnology
						model += UseByTechnology[r][l][t][f][y] == RateOfUseByTechnology[r][l][t][f][y] * YearSplit[l][y], ""
	
				for m in MODE_OF_OPERATION:
					# Acc3_AverageAnnualRateOfActivity
					model += TotalAnnualTechnologyActivityByMode[r][t][m][y] == pulp.lpSum([RateOfActivity[r][l][t][m][y] * YearSplit[l][y] for l in TIMESLICE]), ""
		# Acc4_ModelPeriodCostByRegion
		model += ModelPeriodCostByRegion[r] == pulp.lpSum([TotalDiscountedCost[r][y] for y in YEAR]), ""
	
	#########			Storage Equations			#########
	
	for r in REGION:
		for s in STORAGE:
			for y in YEAR:
				for ls in SEASON:
					for ld in DAYTYPE:
						for lh in DAILYTIMEBRACKET:
							# S1_RateOfStorageCharge
							model += RateOfStorageCharge[r][s][ls][ld][lh][y] == pulp.lpSum([RateOfActivity[r][l][t][m][y] * TechnologyToStorage[r][t][s][m] * Conversionls[l][ls] * Conversionld[l][ld] * Conversionlh[l][lh] for t in TECHNOLOGY for m in MODE_OF_OPERATION for l in TIMESLICE if TechnologyToStorage[r][t][s][m] > 0]), ""
							# S2_RateOfStorageDischarge
							model += RateOfStorageDischarge[r][s][ls][ld][lh][y] == pulp.lpSum([RateOfActivity[r][l][t][m][y] * TechnologyFromStorage[r][t][s][m] * Conversionls[l][ls] * Conversionld[l][ld] * Conversionlh[l][lh] for t in TECHNOLOGY for m in MODE_OF_OPERATION for l in TIMESLICE if TechnologyFromStorage[r][t][s][m] > 0]), ""
							# S3_NetChargeWithinYear
							model += NetChargeWithinYear[r][s][ls][ld][lh][y] == pulp.lpSum([(RateOfStorageCharge[r][s][ls][ld][lh][y] - RateOfStorageDischarge[r][s][ls][ld][lh][y]) * YearSplit[l][y] * Conversionls[l][ls] * Conversionld[l][ld] * Conversionlh[l][lh] for l in TIMESLICE if (Conversionls[l][ls] > 0) and (Conversionld[l][ld] > 0) and (Conversionlh[l][lh] > 0)]), ""
							# S4_NetChargeWithinDay
							model += NetChargeWithinDay[r][s][ls][ld][lh][y] == (RateOfStorageCharge[r][s][ls][ld][lh][y] - RateOfStorageDischarge[r][s][ls][ld][lh][y]) * DaySplit[lh][y], ""

				# S5_and_S6_StorageLevelYearStart
				if int(y) == min([int(yy) for yy in YEAR]):
					model += StorageLevelYearStart[r][s][y] == StorageLevelStart[r][s], ""
				else:
					model += StorageLevelYearStart[r][s][y] == StorageLevelYearStart[r][s][str(int(y)-1)] + pulp.lpSum([NetChargeWithinYear[r][s][ls][ld][lh][str(int(y)-1)] for ls in SEASON for ld in DAYTYPE for lh in DAILYTIMEBRACKET]), ""
				# S7_and_S8_StorageLevelYearFinish
				if int(y) < max([int(yy) for yy in YEAR]):
					model += StorageLevelYearFinish[r][s][y] == StorageLevelYearStart[r][s][str(int(y) + 1)], ""
				else:
					model += StorageLevelYearFinish[r][s][y] == StorageLevelYearStart[r][s][y] + pulp.lpSum([NetChargeWithinYear[r][s][ls][ld][lh][y] for ls in SEASON for ld in DAYTYPE for lh in DAILYTIMEBRACKET]), ""
	
				for ls in SEASON:
					# S9_and_S10_StorageLevelSeasonStart
					if int(ls) == min([int(lsls) for lsls in SEASON]):
						model += StorageLevelSeasonStart[r][s][ls][y] == StorageLevelYearStart[r][s][y], ""
					else:
						model += StorageLevelSeasonStart[r][s][ls][y] == StorageLevelSeasonStart[r][s][str(int(ls)-1)][y] + pulp.lpSum([NetChargeWithinYear[r][s][str(int(ls)-1)][ld][lh][y] for ld in DAYTYPE for lh in DAILYTIMEBRACKET]), ""

					for ld in DAYTYPE:
						# S11_and_S12_StorageLevelDayTypeStart
						if int(ld) == min([int(ldld) for ldld in DAYTYPE]):
							model += StorageLevelDayTypeStart[r][s][ls][ld][y] == StorageLevelSeasonStart[r][s][ls][y], ""
						else:
							model += StorageLevelDayTypeStart[r][s][ls][ld][y] == StorageLevelDayTypeStart[r][s][ls][str(int(ld)-1)][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][str(int(ld)-1)][lh][y] * DaysInDayType[ls][str(int(ld)-1)][y] for lh in DAILYTIMEBRACKET]), ""
						# S13_and_S14_and_S15_StorageLevelDayTypeFinish
						if (int(ld) == max([int(ldld) for ldld in DAYTYPE])) and (int(ls) == max([int(lsls) for lsls in SEASON])):
							model += StorageLevelDayTypeFinish[r][s][ls][ld][y] == StorageLevelYearFinish[r][s][y], ""
						elif int(ld) == max([int(ldld) for ldld in DAYTYPE]):
							model += StorageLevelDayTypeFinish[r][s][ls][ld][y] == StorageLevelSeasonStart[r][s][str(int(ls)+1)][y], ""
						else:
							model += StorageLevelDayTypeFinish[r][s][ls][ld][y] == StorageLevelDayTypeFinish[r][s][ls][str(int(ld)+1)][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][str(int(ld)+1)][lh][y] * DaysInDayType[ls][str(int(ld)+1)][y] for lh in DAILYTIMEBRACKET]), ""
	
	##########			Storage Constraints			#########
	
	for r in REGION:
		for s in STORAGE:
			for y in YEAR:
				for ls in SEASON:
					for ld in DAYTYPE:
						for lh in DAILYTIMEBRACKET:
							# SC1_LowerLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInFirstWeekConstraint
							model += (StorageLevelDayTypeStart[r][s][ls][ld][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh)-int(lhlh) > 0])) - StorageLowerLimit[r][s][y] >= 0, ""
							# SC1_UpperLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInFirstWeekConstraint
							model += (StorageLevelDayTypeStart[r][s][ls][ld][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh)-int(lhlh) > 0])) - StorageUpperLimit[r][s][y] <= 0, ""
							# SC2_LowerLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInFirstWeekConstraint
							if int(ld) > min([int(ldld) for ldld in DAYTYPE]):
								model += (StorageLevelDayTypeStart[r][s][ls][ld][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][str(int(ld)-1)][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh)-int(lhlh) < 0])) - StorageLowerLimit[r][s][y] >= 0, ""
							# SC2_LowerLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInFirstWeekConstraint
							if int(ld) > min([int(ldld) for ldld in DAYTYPE]):
								model += (StorageLevelDayTypeStart[r][s][ls][ld][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][str(int(ld)-1)][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) < 0])) - StorageUpperLimit[r][s][y] <= 0, ""
							# SC3_LowerLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInLastWeekConstraint
							model += (StorageLevelDayTypeFinish[r][s][ls][ld][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) < 0])) - StorageLowerLimit[r][s][y] >= 0, ""
							# SC3_UpperLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInLastWeekConstraint
							model += (StorageLevelDayTypeFinish[r][s][ls][ld][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) < 0])) - StorageUpperLimit[r][s][y] <= 0, ""
							# SC4_LowerLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInLastWeekConstraint
							if int(ld) > min([int(ldld) for ldld in DAYTYPE]):
								model += (StorageLevelDayTypeFinish[r][s][ls][str(int(ld)-1)][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) > 0])) - StorageLowerLimit[r][s][y] >= 0, ""
							# SC4_UpperLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInLastWeekConstraint
							if int(ld) > min([int(ldld) for ldld in DAYTYPE]):
								model += (StorageLevelDayTypeFinish[r][s][ls][str(int(ld)-1)][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) > 0])) - StorageUpperLimit[r][s][y] <= 0, ""
							# SC5_MaxChargeConstraint
							model += RateOfStorageCharge[r][s][ls][ld][lh][y] <= StorageMaxChargeRate[r][s], ""
							# SC6_MaxDischargeConstraint
							model += RateOfStorageDischarge[r][s][ls][ld][lh][y] <= StorageMaxDischargeRate[r][s], ""
	
	#########			Storage Investments			#########
	
	for r in REGION:
		for s in STORAGE:
			for y in YEAR:
				# SI1_StorageUpperLimit
				model += StorageUpperLimit[r][s][y] == AccumulatedNewStorageCapacity[r][s][y] + ResidualStorageCapacity[r][s][y], ""
				# SI2_StorageLowerLimit
				model += StorageLowerLimit[r][s][y] == MinStorageCharge[r][s][y] * StorageUpperLimit[r][s][y], ""
				# SI3_TotalNewStorage
				model += AccumulatedNewStorageCapacity[r][s][y] == pulp.lpSum([NewStorageCapacity[r][s][yy] for yy in YEAR if (int(y) - int(yy) < OperationalLifeStorage[r][s]) and (int(y)-int(yy) >= 0)]), ""
				# SI4_UndiscountedCapitalInvestmentStorage
				model += CapitalInvestmentStorage[r][s][y] == CapitalCostStorage[r][s][y] * NewStorageCapacity[r][s][y], ""
				# SI5_DiscountingCapitalInvestmentStorage
				model += DiscountedCapitalInvestmentStorage[r][s][y] == CapitalInvestmentStorage[r][s][y] * (1/ ((1+DiscountRate[r])**(int(y) - min([int(yy) for yy in YEAR])))), ""
				# SI6_SalvageValueStorageAtEndOfPeriod1
				if int(y) + OperationalLifeStorage[r][s] - 1 <= max([int(yy) for yy in YEAR]):
					model += SalvageValueStorage[r][s][y] == 0, ""
				# SI7_SalvageValueStorageAtEndOfPeriod2
				if ((DepreciationMethod[r] == 1) and (int(y)+OperationalLifeStorage[r][s]-1 > max([int(yy) for yy in YEAR])) and (DiscountRate[r] == 0)) or ((DepreciationMethod[r] == 2) and (int(y)+OperationalLifeStorage[r][s]-1 > max([int(yy) for yy in YEAR]))):
					model += SalvageValueStorage[r][s][y] == CapitalInvestmentStorage[r][s][y] * (1-(max([int(yy) for yy in YEAR])-int(y)+1))/OperationalLifeStorage[r][s], ""
				# SI8_SalvageValueStorageAtEndOfPeriod3
				if (DepreciationMethod[r] == 1) and (int(y)+OperationalLifeStorage[r][s]-1 > max([int(yy) for yy in YEAR])) and (DiscountRate[r] > 0):
					model += SalvageValueStorage[r][s][y] == CapitalInvestmentStorage[r][s][y] * (1-(((1+DiscountRate[r])**(max([int(yy) for yy in YEAR]) - int(y)+1)-1)/((1+DiscountRate[r])**OperationalLifeStorage[r][s]-1))), ""
				# SI9_SalvageValueStorageDiscountedToStartYear
				model += DiscountedSalvageValueStorage[r][s][y] == SalvageValueStorage[r][s][y] * (1 /((1+DiscountRate[r])**(max([int(yy) for yy in YEAR])-min([int(yy) for yy in YEAR])+1))), ""
				# SI10_TotalDiscountedCostByStorage
				model += TotalDiscountedStorageCost[r][s][y] == DiscountedCapitalInvestmentStorage[r][s][y]-DiscountedSalvageValueStorage[r][s][y], ""
	
	#########			Capital Costs 		     	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				# CC1_UndiscountedCapitalInvestment
				model += CapitalInvestment[r][t][y] == CapitalCost[r][t][y] * NewCapacity[r][t][y],  ""
				# CC2_DiscountingCapitalInvestment
				model += DiscountedCapitalInvestment[r][t][y] == CapitalInvestment[r][t][y] * (1/((1 + DiscountRate[r]) ** (int(y) - min([int(yy) for yy in YEAR])))), ""
	
	#########           Salvage Value            	#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				# SV1_SalvageValueAtEndOfPeriod1
				if (DepreciationMethod[r] == 1) and (int(y) + OperationalLife[r][t] - 1 > max([int(yy) for yy in YEAR])) and (DiscountRate[r] > 0):
					model += SalvageValue[r][t][y] == CapitalCost[r][t][y] * NewCapacity[r][t][y] * (1 - (((1 + DiscountRate[r]) ** (max([int(yy) for yy in YEAR]) - int(y) + 1) - 1) / ((1 + DiscountRate[r]) ** OperationalLife[r][t] - 1))), ""
				# SV2_SalvageValueAtEndOfPeriod2
				if ((DepreciationMethod[r] == 1) and (int(y) + OperationalLife[r][t] - 1 > max([int(yy) for yy in YEAR])) and (DiscountRate[r] == 0)) or ((DepreciationMethod[r] == 2) and (int(y) + OperationalLife[r][t] - 1 > max([int(yy) for yy in YEAR]))):
					model += SalvageValue[r][t][y] == CapitalCost[r][t][y] * NewCapacity[r][t][y] * (1 - (max([int(yy) for yy in YEAR]) - int(y) + 1) / OperationalLife[r][t]), ""
				# SV3_SalvageValueAtEndOfPeriod3
				if int(y) + OperationalLife[r][t] - 1 <= max([int(yy) for yy in YEAR]):
					model += SalvageValue[r][t][y] == 0, ""
				# SV4_SalvageValueDiscountedToStartYear
				model += DiscountedSalvageValue[r][t][y] == SalvageValue[r][t][y] * (1 / ((1 + DiscountRate[r]) ** (1 + max([int(yy) for yy in YEAR]) - min([int(yy) for yy in YEAR])))), ""
	
	#########        	Operating Costs 		 	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				# OC1_OperatingCostsVariable
				model += AnnualVariableOperatingCost[r][t][y] == pulp.lpSum([TotalAnnualTechnologyActivityByMode[r][t][m][y] * VariableCost[r][t][m][y] for m in MODE_OF_OPERATION]), ""
				# OC2_OperatingCostsFixedAnnual
				model += AnnualFixedOperatingCost[r][t][y] == TotalCapacityAnnual[r][t][y] * FixedCost[r][t][y], ""
				# OC3_OperatingCostsTotalAnnual
				model += OperatingCost[r][t][y] == AnnualFixedOperatingCost[r][t][y] + AnnualVariableOperatingCost[r][t][y], ""
				# OC4_DiscountedOperatingCostsTotalAnnual
				model += DiscountedOperatingCost[r][t][y] == OperatingCost[r][t][y] * (1 /((1 + DiscountRate[r]) ** (int(y) - min([int(yy) for yy in YEAR]) + 0.5))), ""
	
	#########       	Total Discounted Costs	 	#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				# TDC1_TotalDiscountedCostByTechnology
				model += TotalDiscountedCostByTechnology[r][t][y] == DiscountedOperatingCost[r][t][y] + DiscountedCapitalInvestment[r][t][y] + DiscountedTechnologyEmissionsPenalty[r][t][y] - DiscountedSalvageValue[r][t][y], ""
	
			# TDC2_TotalDiscountedCost
			model += TotalDiscountedCost[r][y] == pulp.lpSum([TotalDiscountedCostByTechnology[r][t][y] for t in TECHNOLOGY]) + pulp.lpSum([TotalDiscountedStorageCost[r][s][y] for s in STORAGE]), ""
	
	#########      		Total Capacity Constraints 	#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				# TCC1_TotalAnnualMaxCapacityConstraint
				model += TotalCapacityAnnual[r][t][y] <= TotalAnnualMaxCapacity[r][t][y], ""
				# TCC2_TotalAnnualMinCapacityConstraint
				if TotalAnnualMinCapacity[r][t][y] > 0:
					model += TotalCapacityAnnual[r][t][y] >= TotalAnnualMinCapacity[r][t][y], ""
	
	#########    		New Capacity Constraints  	#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				# NCC1_TotalAnnualMaxNewCapacityConstraint
				model += NewCapacity[r][t][y] <= TotalAnnualMaxCapacityInvestment[r][t][y], ""
				# NCC2_TotalAnnualMinNewCapacityConstraint
				if TotalAnnualMinCapacityInvestment[r][t][y] > 0:
					model += NewCapacity[r][t][y] >= TotalAnnualMinCapacityInvestment[r][t][y], ""
	
	#########   		Annual Activity Constraints	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				# AAC1_TotalAnnualTechnologyActivity
				model += TotalTechnologyAnnualActivity[r][t][y] == pulp.lpSum([RateOfTotalActivity[r][t][l][y] * YearSplit[l][y] for l in TIMESLICE]), ""
				# AAC2_TotalAnnualTechnologyActivityUpperLimit
				model += TotalTechnologyAnnualActivity[r][t][y] <= TotalTechnologyAnnualActivityUpperLimit[r][t][y], ""
				# AAC3_TotalAnnualTechnologyActivityLowerLimit
				if TotalTechnologyAnnualActivityLowerLimit[r][t][y] > 0:
					model += TotalTechnologyAnnualActivity[r][t][y] >= TotalTechnologyAnnualActivityLowerLimit[r][t][y], ""
	
	#########    		Total Activity Constraints 	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			# TAC1_TotalModelHorizonTechnologyActivity
			model += TotalTechnologyModelPeriodActivity[r][t] == pulp.lpSum([TotalTechnologyAnnualActivity[r][t][y] for y in YEAR]), ""
			# TAC2_TotalModelHorizonTechnologyActivityUpperLimit
			if TotalTechnologyModelPeriodActivityUpperLimit[r][t] > 0:
				model += TotalTechnologyModelPeriodActivity[r][t] <= TotalTechnologyModelPeriodActivityUpperLimit[r][t], ""
			# TAC3_TotalModelHorizenTechnologyActivityLowerLimit
			if TotalTechnologyModelPeriodActivityLowerLimit[r][t] > 0:
				model += TotalTechnologyModelPeriodActivity[r][t] >= TotalTechnologyModelPeriodActivityLowerLimit[r][t], ""
	
	#########   		Reserve Margin Constraint	#########
	
	for r in REGION:
		for y in YEAR:
			# RM1_ReserveMargin_TechnologiesIncluded_In_Activity_Units
			model += TotalCapacityInReserveMargin[r][y] == pulp.lpSum([TotalCapacityAnnual[r][t][y] * ReserveMarginTagTechnology[r][t][y] * CapacityToActivityUnit[r][t] for t in TECHNOLOGY]), ""
	
			for l in TIMESLICE:
				# RM2_ReserveMargin_FuelsIncluded
				model += DemandNeedingReserveMargin[r][l][y] == pulp.lpSum([RateOfProduction[r][l][f][y] * ReserveMarginTagFuel[r][f][y] for f in FUEL]), ""
				# RM3_ReserveMargin_Constraint
				model += DemandNeedingReserveMargin[r][l][y] <= TotalCapacityInReserveMargin[r][y] * (1/ReserveMargin[r][y]), ""
	
	#########   		RE Production Target		#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				for f in FUEL:
					# RE1_FuelProductionByTechnologyAnnual
					model += ProductionByTechnologyAnnual[r][t][f][y] == pulp.lpSum([ProductionByTechnology[r][l][t][f][y] for l in TIMESLICE]), ""
			# RE2_TechIncluded
			model += TotalREProductionAnnual[r][y] == pulp.lpSum([ProductionByTechnologyAnnual[r][t][f][y] * RETagTechnology[r][t][y] for t in TECHNOLOGY for f in FUEL]), ""
			# RE3_FuelIncluded
			model += RETotalProductionOfTargetFuelAnnual[r][y] == pulp.lpSum([RateOfProduction[r][l][f][y] * YearSplit[l][y] * RETagFuel[r][f][y] for l in TIMESLICE for f in FUEL]), ""
			# RE4_EnergyConstraint
			model += TotalREProductionAnnual[r][y] >= REMinProductionTarget[r][y] * RETotalProductionOfTargetFuelAnnual[r][y], ""
	
			for t in TECHNOLOGY:
				for f in FUEL:
					# RE5_FuelUseByTechnologyAnnual
					model += UseByTechnologyAnnual[r][t][f][y] == pulp.lpSum([RateOfUseByTechnology[r][l][t][f][y] * YearSplit[l][y] for l in TIMESLICE]), ""
	
	#########   		Emissions Accounting		#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				for e in EMISSION:
					for m in MODE_OF_OPERATION:
						# E1_AnnualEmissionProductionByMode
						model += AnnualTechnologyEmissionByMode[r][t][e][m][y] == EmissionActivityRatio[r][t][e][m][y] * TotalAnnualTechnologyActivityByMode[r][t][m][y], ""
					# E2_AnnualEmissionProduction
					model += AnnualTechnologyEmission[r][t][e][y] == pulp.lpSum([AnnualTechnologyEmissionByMode[r][t][e][m][y] for m in MODE_OF_OPERATION]), ""
					# E3_EmissionsPenaltyByTechAndEmission
					model += AnnualTechnologyEmissionPenaltyByEmission[r][t][e][y] == AnnualTechnologyEmission[r][t][e][y] * EmissionsPenalty[r][e][y], ""
				# E4_EmissionsPenaltyByTechnology
				model += AnnualTechnologyEmissionsPenalty[r][t][y] == pulp.lpSum([AnnualTechnologyEmissionPenaltyByEmission[r][t][e][y] for e in EMISSION]), ""
				# E5_DiscountedEmissionsPenaltyByTechnology
				model += DiscountedTechnologyEmissionsPenalty[r][t][y] == AnnualTechnologyEmissionsPenalty[r][t][y] * (1 / ((1 + DiscountRate[r]) ** (int(y) - min([int(yy) for yy in YEAR]) + 0.5))), ""
	
			for e in EMISSION:
				# E6_EmissionsAccounting1
				model += AnnualEmissions[r][e][y] == pulp.lpSum([AnnualTechnologyEmission[r][t][e][y] for t in TECHNOLOGY]), ""
	
		for e in EMISSION:
			# E7_EmissionsAccounting2
			model += pulp.lpSum([AnnualEmissions[r][e][y] for y in YEAR]) == ModelPeriodEmissions[r][e] - ModelPeriodExogenousEmission[r][e], ""
	
			for y in YEAR:
				# E8_AnnualEmissionsLimit
				model += AnnualEmissions[r][e][y] <= AnnualEmissionLimit[r][e][y] - AnnualExogenousEmission[r][e][y], ""
			# E9_ModelPeriodEmissionsLimit
			model += ModelPeriodEmissions[r][e] <= ModelPeriodEmissionLimit[r][e], ""
	
	logging.info("{}\tModel is built.".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

	# ------------------------------------------------------------------------------------------------------------------
	#    SOLVE
	# ------------------------------------------------------------------------------------------------------------------
	
	model.solve()
	logging.info("{}\tModel is solved.".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

	if str(pulp.LpStatus[model.status]) == "Optimal":
		logging.info("The optimal solution found a cost value of {}.".format(round(model.objective.value(), 2)))

		# --------------------------------------------------------------------------------------------------------------
		#    SAVE RESULTS TO DATAFRAME
		# --------------------------------------------------------------------------------------------------------------
	
		# Create dataframe to save results after the model was run the first time
		if i == 0:
			res_df = pd.DataFrame(columns=[
			'SCENARIO',
			'VAR_NAME',
			'VAR_VALUE',
			'REGION',
			'REGION2',
			'DAYTYPE',
			'EMISSION',
			'FUEL',
			'DAILYTIMEBRACKET',
			'SEASON',
			'TIMESLICE',
			'MODE_OF_OPERATION',
			'STORAGE',
			'TECHNOLOGY',
			'YEAR',
			'FLEXIBLEDEMANDTYPE'])
		
		res_df = saveResultsTemporary(res_df, model, "Scenario_" + str(i))
		logging.info("{}\tResults are saved".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
		
	else:
		logging.error("{}\tError: Optimisation status for Scenario_{} is: {}".format(
			dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pulp.LpStatus[model.status]))
	
	del model  # Delete model

	# ----------------------------------------------------------------------------------------------------------------------
	#    MONTE CARLO SIMULATION - START
	# ----------------------------------------------------------------------------------------------------------------------

	i += 1
	
	# Note: Monte Carlo Simulation is applied to all selected parameters (mcs_parameters).
	# For each parameter, the mcs_parameters is only applied to parameter values that are not equal to default values, i.e. values that were explicitly set.

	#########			Reference parameters and data     #########
	
	if (len(mcs_parameters) >= 1) and (mcs_num > 0) and (i == 1):
	
		# Copy of previous paramteres. This is used to store already generated parameters with data to enhance the performance in the mcs_parameters loops
		DiscountRate_ref = DiscountRate
		DaySplit_ref = DaySplit
		Conversionls_ref = Conversionls
		Conversionld_ref = Conversionld
		Conversionlh_ref = Conversionlh
		DaysInDayType_ref = DaysInDayType
		TradeRoute_ref = TradeRoute
		DepreciationMethod_ref = DepreciationMethod
		SpecifiedAnnualDemand_ref = SpecifiedAnnualDemand
		SpecifiedDemandProfile_ref = SpecifiedDemandProfile
		AccumulatedAnnualDemand_ref = AccumulatedAnnualDemand
		CapacityToActivityUnit_ref = CapacityToActivityUnit
		TechWithCapacityNeededToMeetPeakTS_ref = TechWithCapacityNeededToMeetPeakTS
		CapacityFactor_ref = CapacityFactor
		AvailabilityFactor_ref = AvailabilityFactor
		OperationalLife_ref = OperationalLife
		ResidualCapacity_ref = ResidualCapacity
		InputActivityRatio_ref = InputActivityRatio
		OutputActivityRatio_ref = OutputActivityRatio
		CapitalCost_ref = CapitalCost
		VariableCost_ref = VariableCost
		FixedCost_ref = FixedCost
		TechnologyToStorage_ref = TechnologyToStorage
		TechnologyFromStorage_ref = TechnologyFromStorage
		StorageLevelStart_ref = StorageLevelStart
		StorageMaxChargeRate_ref = StorageMaxChargeRate
		StorageMaxDischargeRate_ref = StorageMaxDischargeRate
		MinStorageCharge_ref = MinStorageCharge
		OperationalLifeStorage_ref = OperationalLifeStorage
		CapitalCostStorage_ref = CapitalCostStorage
		ResidualStorageCapacity_ref = ResidualStorageCapacity
		CapacityOfOneTechnologyUnit_ref = CapacityOfOneTechnologyUnit
		TotalAnnualMaxCapacity_ref = TotalAnnualMaxCapacity
		TotalAnnualMinCapacity_ref = TotalAnnualMinCapacity
		TotalAnnualMaxCapacityInvestment_ref = TotalAnnualMaxCapacityInvestment
		TotalAnnualMinCapacityInvestment_ref = TotalAnnualMinCapacityInvestment
		TotalTechnologyAnnualActivityUpperLimit_ref = TotalTechnologyAnnualActivityUpperLimit
		TotalTechnologyAnnualActivityLowerLimit_ref = TotalTechnologyAnnualActivityLowerLimit
		TotalTechnologyModelPeriodActivityUpperLimit_ref = TotalTechnologyModelPeriodActivityUpperLimit
		TotalTechnologyModelPeriodActivityLowerLimit_ref = TotalTechnologyModelPeriodActivityLowerLimit
		ReserveMarginTagTechnology_ref = ReserveMarginTagTechnology
		ReserveMarginTagFuel_ref = ReserveMarginTagFuel
		ReserveMargin_ref = ReserveMargin
		RETagTechnology_ref = RETagTechnology
		RETagFuel_ref = RETagFuel
		REMinProductionTarget_ref = REMinProductionTarget
		EmissionActivityRatio_ref = EmissionActivityRatio
		EmissionsPenalty_ref = EmissionsPenalty
		AnnualExogenousEmission_ref = AnnualExogenousEmission
		AnnualEmissionLimit_ref = AnnualEmissionLimit
		ModelPeriodExogenousEmission_ref = ModelPeriodExogenousEmission
		ModelPeriodEmissionLimit_ref = ModelPeriodEmissionLimit

	#########			Generate random data and overwrite selected parameters for next MCS run     	#########

	########			Global 								#########

	if ("DiscountRate" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			DiscountRate_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "DiscountRate") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			DiscountRate_mcs_specified = tuple([(str(r)) for r in mcs_df[mcs_df['PARAM'] == "DiscountRate"].REGION])
		
		DiscountRate = {str(r): generateRandomData(DiscountRate_ref[r], mcs_df[(mcs_df['PARAM'] == "DiscountRate") & (mcs_df['REGION'] == r)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r)) in DiscountRate_mcs_specified else generateRandomData(DiscountRate_ref[r], DiscountRate_mcs_default_list) for r in REGION}


	########			Demands 							#########

	if ("SpecifiedAnnualDemand" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			SpecifiedAnnualDemand_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "SpecifiedAnnualDemand") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			SpecifiedAnnualDemand_mcs_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(mcs_df[mcs_df['PARAM'] == "SpecifiedAnnualDemand"].REGION, mcs_df[mcs_df['PARAM'] == "SpecifiedAnnualDemand"].FUEL, mcs_df[mcs_df['PARAM'] == "SpecifiedAnnualDemand"].YEAR)])
		
		SpecifiedAnnualDemand = {str(r): {str(f): {str(y): generateRandomData(SpecifiedAnnualDemand_ref[r][f][y], mcs_df[(mcs_df['PARAM'] == "SpecifiedAnnualDemand") & (mcs_df['REGION'] == r) & (mcs_df['FUEL'] == f) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(f),str(y)) in SpecifiedAnnualDemand_mcs_specified else generateRandomData(SpecifiedAnnualDemand_ref[r][f][y], SpecifiedAnnualDemand_mcs_default_list) for y in YEAR} for f in FUEL} for r in REGION}
	
	if ("AccumulatedAnnualDemand" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			AccumulatedAnnualDemand_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "AccumulatedAnnualDemand") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			AccumulatedAnnualDemand_mcs_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(mcs_df[mcs_df['PARAM'] == "AccumulatedAnnualDemand"].REGION, mcs_df[mcs_df['PARAM'] == "AccumulatedAnnualDemand"].FUEL, mcs_df[mcs_df['PARAM'] == "AccumulatedAnnualDemand"].YEAR)])

		AccumulatedAnnualDemand = {str(r): {str(f): {str(y): generateRandomData(AccumulatedAnnualDemand_ref[r][f][y], mcs_df[(mcs_df['PARAM'] == "AccumulatedAnnualDemand") & (mcs_df['REGION'] == r) & (mcs_df['FUEL'] == f) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(f),str(y)) in AccumulatedAnnualDemand_mcs_specified else generateRandomData(AccumulatedAnnualDemand_ref[r][f][y], AccumulatedAnnualDemand_mcs_default_list) for y in YEAR} for f in FUEL} for r in REGION}

	#########			Performance					#########
	
	if ("TechWithCapacityNeededToMeetPeakTS" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			TechWithCapacityNeededToMeetPeakTS_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TechWithCapacityNeededToMeetPeakTS_mcs_specified = tuple([(str(r), str(t)) for r, t in zip(mcs_df[mcs_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].REGION, mcs_df[mcs_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].TECHNOLOGY)])
	
		TechWithCapacityNeededToMeetPeakTS = {str(r): {str(t): generateRandomData(TechWithCapacityNeededToMeetPeakTS_ref[r][t], mcs_df[(mcs_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t)) in TechWithCapacityNeededToMeetPeakTS_mcs_specified else generateRandomData(TechWithCapacityNeededToMeetPeakTS_ref[r][t], TechWithCapacityNeededToMeetPeakTS_mcs_default_list) for t in TECHNOLOGY} for r in REGION}
	
	if ("CapacityFactor" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			CapacityFactor_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "CapacityFactor") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			CapacityFactor_mcs_specified = tuple([(str(r),str(t),str(l),str(y)) for r, t, l, y in zip(mcs_df[mcs_df['PARAM'] == "CapacityFactor"].REGION, mcs_df[mcs_df['PARAM'] == "CapacityFactor"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "CapacityFactor"].TIMESLICE, mcs_df[mcs_df['PARAM'] == "CapacityFactor"].YEAR)])
		
		CapacityFactor = {str(r): {str(t): {str(l): {str(y): generateRandomData(CapacityFactor_ref[r][t][l][y], mcs_df[(mcs_df['PARAM'] == "CapacityFactor") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(l),str(y)) in CapacityFactor_mcs_specified else generateRandomData(CapacityFactor_ref[r][t][l][y], CapacityFactor_mcs_default_list) for y in YEAR} for l in TIMESLICE} for t in TECHNOLOGY} for r in REGION}
	
	if ("AvailabilityFactor" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			AvailabilityFactor_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "AvailabilityFactor") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			AvailabilityFactor_mcs_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(mcs_df[mcs_df['PARAM'] == "AvailabilityFactor"].REGION, mcs_df[mcs_df['PARAM'] == "AvailabilityFactor"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "AvailabilityFactor"].YEAR)])
		
		AvailabilityFactor = {str(r): {str(t): {str(y): generateRandomData(AvailabilityFactor_ref[r][t][y], mcs_df[(mcs_df['PARAM'] == "AvailabilityFactor") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(y)) in AvailabilityFactor_mcs_specified else generateRandomData(AvailabilityFactor_ref[r][t][y], AvailabilityFactor_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	
	if ("OperationalLife" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			OperationalLife_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "OperationalLife") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			OperationalLife_mcs_specified = tuple([(str(r), str(t)) for r, t in zip(mcs_df[mcs_df['PARAM'] == "OperationalLife"].REGION, mcs_df[mcs_df['PARAM'] == "OperationalLife"].TECHNOLOGY)])
		
		OperationalLife = {str(r): {str(t): int(generateRandomData(OperationalLife_ref[r][t], mcs_df[(mcs_df['PARAM'] == "OperationalLife") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0])) if (str(r), str(t)) in OperationalLife_mcs_specified else int(generateRandomData(OperationalLife_ref[r][t], OperationalLife_mcs_default_list)) for t in TECHNOLOGY} for r in REGION}
		
	if ("InputActivityRatio" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			InputActivityRatio_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "InputActivityRatio") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			InputActivityRatio_mcs_specified = tuple([(str(r),str(t),str(f),str(m),str(y)) for r, t, f, m, y in zip(mcs_df[mcs_df['PARAM'] == "InputActivityRatio"].REGION, mcs_df[mcs_df['PARAM'] == "InputActivityRatio"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "InputActivityRatio"].FUEL, mcs_df[mcs_df['PARAM'] == "InputActivityRatio"].MODE_OF_OPERATION, mcs_df[mcs_df['PARAM'] == "InputActivityRatio"].YEAR)])
		
		InputActivityRatio = {str(r): {str(t): {str(f): {str(m): {str(y): generateRandomData(InputActivityRatio_ref[r][t][f][m][y], mcs_df[(mcs_df['PARAM'] == "InputActivityRatio") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['FUEL'] == f) & (mcs_df['MODE_OF_OPERATION'] == m) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(f),str(m),str(y)) in InputActivityRatio_mcs_specified else generateRandomData(InputActivityRatio_ref[r][t][f][m][y], InputActivityRatio_mcs_default_list) for y in YEAR} for m in MODE_OF_OPERATION} for f in FUEL} for t in TECHNOLOGY} for r in REGION}
	
	if ("OutputActivityRatio" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			OutputActivityRatio_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "OutputActivityRatio") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			OutputActivityRatio_mcs_specified = tuple([(str(r),str(t),str(f),str(m),str(y)) for r, t, f, m, y in zip(mcs_df[mcs_df['PARAM'] == "OutputActivityRatio"].REGION, mcs_df[mcs_df['PARAM'] == "OutputActivityRatio"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "OutputActivityRatio"].FUEL, mcs_df[mcs_df['PARAM'] == "OutputActivityRatio"].MODE_OF_OPERATION, mcs_df[mcs_df['PARAM'] == "OutputActivityRatio"].YEAR)])
	
		OutputActivityRatio = {str(r): {str(t): {str(f): {str(m): {str(y): generateRandomData(OutputActivityRatio_ref[r][t][f][m][y], mcs_df[(mcs_df['PARAM'] == "OutputActivityRatio") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['FUEL'] == f) & (mcs_df['MODE_OF_OPERATION'] == m) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(f),str(m),str(y)) in OutputActivityRatio_mcs_specified else generateRandomData(OutputActivityRatio_ref[r][t][f][m][y], OutputActivityRatio_mcs_default_list) for y in YEAR} for m in MODE_OF_OPERATION} for f in FUEL} for t in TECHNOLOGY} for r in REGION}
	
	
	#########			Technology Costs			#########
	
	if ("CapitalCost" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			CapitalCost_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "CapitalCost") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			CapitalCost_mcs_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(mcs_df[mcs_df['PARAM'] == "CapitalCost"].REGION, mcs_df[mcs_df['PARAM'] == "CapitalCost"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "CapitalCost"].YEAR)])
		
		CapitalCost = {str(r): {str(t): {str(y): generateRandomData(CapitalCost_ref[r][t][y], mcs_df[(mcs_df['PARAM'] == "CapitalCost") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(y)) in CapitalCost_mcs_specified else generateRandomData(CapitalCost_ref[r][t][y], CapitalCost_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
			
	if ("VariableCost" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			VariableCost_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "VariableCost") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			VariableCost_mcs_specified = tuple([(str(r),str(t),str(m),str(y)) for r, t, m, y in zip(mcs_df[mcs_df['PARAM'] == "VariableCost"].REGION, mcs_df[mcs_df['PARAM'] == "VariableCost"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "VariableCost"].MODE_OF_OPERATION, mcs_df[mcs_df['PARAM'] == "VariableCost"].YEAR)])
		
		VariableCost = {str(r): {str(t): {str(m): {str(y): generateRandomData(VariableCost_ref[r][t][m][y], mcs_df[(mcs_df['PARAM'] == "VariableCost") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['MODE_OF_OPERATION'] == m) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(m),str(y)) in VariableCost_mcs_specified else generateRandomData(VariableCost_ref[r][t][m][y], VariableCost_mcs_default_list) for y in YEAR} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for r in REGION}
			
	if ("FixedCost" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			FixedCost_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "FixedCost") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			FixedCost_mcs_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(mcs_df[mcs_df['PARAM'] == "FixedCost"].REGION, mcs_df[mcs_df['PARAM'] == "FixedCost"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "FixedCost"].YEAR)])
		
		FixedCost = {str(r): {str(t): {str(y): generateRandomData(FixedCost_ref[r][t][y], mcs_df[(mcs_df['PARAM'] == "FixedCost") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(y)) in FixedCost_mcs_specified else generateRandomData(FixedCost_ref[r][t][y], FixedCost_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
		
	
	#########			Storage                 	#########
	
	if ("StorageLevelStart" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			StorageLevelStart_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "StorageLevelStart") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			StorageLevelStart_mcs_specified = tuple([(str(r), str(s)) for r, s in zip(mcs_df[mcs_df['PARAM'] == "StorageLevelStart"].REGION, mcs_df[mcs_df['PARAM'] == "StorageLevelStart"].STORAGE)])
		
		StorageLevelStart = {str(r): {str(s): generateRandomData(StorageLevelStart_ref[r][s], mcs_df[(mcs_df['PARAM'] == "StorageLevelStart") & (mcs_df['REGION'] == r) & (mcs_df['STORAGE'] == s)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s)) in StorageLevelStart_mcs_specified else generateRandomData(StorageLevelStart_ref[r][s], StorageLevelStart_mcs_default_list) for s in STORAGE} for r in REGION}
			
	if ("StorageMaxChargeRate" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			StorageMaxChargeRate_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "StorageMaxChargeRate") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			StorageMaxChargeRate_mcs_specified = tuple([(str(r), str(s)) for r, s in zip(mcs_df[mcs_df['PARAM'] == "StorageMaxChargeRate"].REGION, mcs_df[mcs_df['PARAM'] == "StorageMaxChargeRate"].STORAGE)])
		
		StorageMaxChargeRate = {str(r): {str(s): generateRandomData(StorageMaxChargeRate_ref[r][s], mcs_df[(mcs_df['PARAM'] == "StorageMaxChargeRate") & (mcs_df['REGION'] == r) & (mcs_df['STORAGE'] == s)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s)) in StorageMaxChargeRate_mcs_specified else generateRandomData(StorageMaxChargeRate_ref[r][s], StorageMaxChargeRate_mcs_default_list) for s in STORAGE} for r in REGION}
			
	if ("StorageMaxDischargeRate" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			StorageMaxDischargeRate_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "StorageMaxDischargeRate") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			StorageMaxDischargeRate_mcs_specified = tuple([(str(r), str(s)) for r, s in zip(mcs_df[mcs_df['PARAM'] == "StorageMaxDischargeRate"].REGION, mcs_df[mcs_df['PARAM'] == "StorageMaxDischargeRate"].STORAGE)])
		
		StorageMaxDischargeRate = {str(r): {str(s): generateRandomData(StorageMaxDischargeRate_ref[r][s], mcs_df[(mcs_df['PARAM'] == "StorageMaxDischargeRate") & (mcs_df['REGION'] == r) & (mcs_df['STORAGE'] == s)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s)) in StorageMaxDischargeRate_mcs_specified else generateRandomData(StorageMaxDischargeRate_ref[r][s], StorageMaxDischargeRate_mcs_default_list) for s in STORAGE} for r in REGION}
			
	if ("OperationalLifeStorage" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			OperationalLifeStorage_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "OperationalLifeStorage") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			OperationalLifeStorage_mcs_specified = tuple([(str(r), str(s)) for r, s in zip(mcs_df[mcs_df['PARAM'] == "OperationalLifeStorage"].REGION, mcs_df[mcs_df['PARAM'] == "OperationalLifeStorage"].STORAGE)])
		
		OperationalLifeStorage = {str(r): {str(s): generateRandomData(OperationalLifeStorage_ref[r][s], mcs_df[(mcs_df['PARAM'] == "OperationalLifeStorage") & (mcs_df['REGION'] == r) & (mcs_df['STORAGE'] == s)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s)) in OperationalLifeStorage_mcs_specified else generateRandomData(OperationalLifeStorage_ref[r][s], OperationalLifeStorage_mcs_default_list) for s in STORAGE} for r in REGION}
			
	if ("CapitalCostStorage" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			CapitalCostStorage_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "CapitalCostStorage") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			CapitalCostStorage_mcs_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(mcs_df[mcs_df['PARAM'] == "CapitalCostStorage"].REGION, mcs_df[mcs_df['PARAM'] == "CapitalCostStorage"].STORAGE, mcs_df[mcs_df['PARAM'] == "CapitalCostStorage"].YEAR)])
		
		CapitalCostStorage = {str(r): {str(s): {str(y): generateRandomData(CapitalCostStorage_ref[r][s][y], mcs_df[(mcs_df['PARAM'] == "CapitalCostStorage") & (mcs_df['REGION'] == r) & (mcs_df['STORAGE'] == s) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s), str(y)) in CapitalCostStorage_mcs_specified else generateRandomData(CapitalCostStorage_ref[r][s][y], CapitalCostStorage_mcs_default_list) for y in YEAR} for s in STORAGE} for r in REGION}
			
	if ("ResidualStorageCapacity" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			ResidualStorageCapacity_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "ResidualStorageCapacity") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			ResidualStorageCapacity_mcs_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(mcs_df[mcs_df['PARAM'] == "ResidualStorageCapacity"].REGION, mcs_df[mcs_df['PARAM'] == "ResidualStorageCapacity"].STORAGE, mcs_df[mcs_df['PARAM'] == "ResidualStorageCapacity"].YEAR)])
		
		ResidualStorageCapacity = {str(r): {str(s): {str(y): generateRandomData(ResidualStorageCapacity_ref[r][s][y], mcs_df[(mcs_df['PARAM'] == "ResidualStorageCapacity") & (mcs_df['REGION'] == r) & (mcs_df['STORAGE'] == s) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s), str(y)) in ResidualStorageCapacity_mcs_specified else generateRandomData(ResidualStorageCapacity_ref[r][s][y], ResidualStorageCapacity_mcs_default_list) for y in YEAR} for s in STORAGE} for r in REGION}
	
	
	#########			Capacity Constraints		#########
	
	if ("CapacityOfOneTechnologyUnit" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			CapacityOfOneTechnologyUnit_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "CapacityOfOneTechnologyUnit") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			CapacityOfOneTechnologyUnit_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(mcs_df[mcs_df['PARAM'] == "CapacityOfOneTechnologyUnit"].REGION, mcs_df[mcs_df['PARAM'] == "CapacityOfOneTechnologyUnit"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "CapacityOfOneTechnologyUnit"].YEAR)])
		
		CapacityOfOneTechnologyUnit = {str(r): {str(t): {str(y): generateRandomData(CapacityOfOneTechnologyUnit_ref[r][t][y], mcs_df[(mcs_df['PARAM'] == "CapacityOfOneTechnologyUnit") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in CapacityOfOneTechnologyUnit_mcs_specified else generateRandomData(CapacityOfOneTechnologyUnit_ref[r][t][y], CapacityOfOneTechnologyUnit_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}

	
	#########			Investment Constraints		#########
	
	if ("TotalAnnualMaxCapacityInvestment" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			TotalAnnualMaxCapacityInvestment_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "TotalAnnualMaxCapacityInvestment") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalAnnualMaxCapacityInvestment_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(mcs_df[mcs_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].REGION, mcs_df[mcs_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].YEAR)])
			
		TotalAnnualMaxCapacityInvestment = {str(r): {str(t): {str(y): generateRandomData(TotalAnnualMaxCapacityInvestment_ref[r][t][y], mcs_df[(mcs_df['PARAM'] == "TotalAnnualMaxCapacityInvestment") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in TotalAnnualMaxCapacityInvestment_mcs_specified else generateRandomData(TotalAnnualMaxCapacityInvestment_ref[r][t][y], TotalAnnualMaxCapacityInvestment_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
			
	if ("TotalAnnualMinCapacityInvestment" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			TotalAnnualMinCapacityInvestment_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "TotalAnnualMinCapacityInvestment") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalAnnualMinCapacityInvestment_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(mcs_df[mcs_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].REGION, mcs_df[mcs_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].YEAR)])
		
		TotalAnnualMinCapacityInvestment = {str(r): {str(t): {str(y): generateRandomData(TotalAnnualMinCapacityInvestment_ref[r][t][y], mcs_df[(mcs_df['PARAM'] == "TotalAnnualMinCapacityInvestment") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in TotalAnnualMinCapacityInvestment_mcs_specified else generateRandomData(TotalAnnualMinCapacityInvestment_ref[r][t][y], TotalAnnualMinCapacityInvestment_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
		
	
	#########			Activity Constraints		#########
	
	if ("TotalTechnologyAnnualActivityUpperLimit" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			TotalTechnologyAnnualActivityUpperLimit_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalTechnologyAnnualActivityUpperLimit_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(mcs_df[mcs_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].REGION, mcs_df[mcs_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].YEAR)])
		
		TotalTechnologyAnnualActivityUpperLimit = {str(r): {str(t): {str(y): generateRandomData(TotalTechnologyAnnualActivityUpperLimit_ref[r][t][y], mcs_df[(mcs_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in TotalTechnologyAnnualActivityUpperLimit_mcs_specified else generateRandomData(TotalTechnologyAnnualActivityUpperLimit_ref[r][t][y], TotalTechnologyAnnualActivityUpperLimit_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
			
	if ("TotalTechnologyAnnualActivityLowerLimit" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			TotalTechnologyAnnualActivityLowerLimit_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalTechnologyAnnualActivityLowerLimit_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(mcs_df[mcs_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].REGION, mcs_df[mcs_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].YEAR)])
		
		TotalTechnologyAnnualActivityLowerLimit = {str(r): {str(t): {str(y): generateRandomData(TotalTechnologyAnnualActivityLowerLimit_ref[r][t][y], mcs_df[(mcs_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in TotalTechnologyAnnualActivityLowerLimit_mcs_specified else generateRandomData(TotalTechnologyAnnualActivityLowerLimit_ref[r][t][y], TotalTechnologyAnnualActivityLowerLimit_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
			
	if ("TotalTechnologyModelPeriodActivityUpperLimit" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			TotalTechnologyModelPeriodActivityUpperLimit_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalTechnologyModelPeriodActivityUpperLimit_mcs_specified = tuple([(str(r), str(t)) for r, t in zip(mcs_df[mcs_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].REGION, mcs_df[mcs_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].TECHNOLOGY)])
		
		TotalTechnologyModelPeriodActivityUpperLimit = {str(r): {str(t): generateRandomData(TotalTechnologyModelPeriodActivityUpperLimit_ref[r][t], mcs_df[(mcs_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t)) in TotalTechnologyModelPeriodActivityUpperLimit_mcs_specified else generateRandomData(TotalTechnologyModelPeriodActivityUpperLimit_ref[r][t], TotalTechnologyModelPeriodActivityUpperLimit_mcs_default_list) for t in TECHNOLOGY} for r in REGION}
			
	if ("TotalTechnologyModelPeriodActivityLowerLimit" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			TotalTechnologyModelPeriodActivityLowerLimit_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalTechnologyModelPeriodActivityLowerLimit_mcs_specified = tuple([(str(r), str(t)) for r, t in zip(mcs_df[mcs_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].REGION, mcs_df[mcs_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].TECHNOLOGY)])
		
		TotalTechnologyModelPeriodActivityLowerLimit = {str(r): {str(t): generateRandomData(TotalTechnologyModelPeriodActivityLowerLimit_ref[r][t], mcs_df[(mcs_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t)) in TotalTechnologyModelPeriodActivityLowerLimit_mcs_specified else generateRandomData(TotalTechnologyModelPeriodActivityLowerLimit_ref[r][t], TotalTechnologyModelPeriodActivityLowerLimit_mcs_default_list) for t in TECHNOLOGY} for r in REGION}
		
	
	#########			Emissions & Penalties		#########
	
	if ("EmissionActivityRatio" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			EmissionActivityRatio_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "EmissionActivityRatio") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			EmissionActivityRatio_mcs_specified = tuple([(str(r),str(t),str(e),str(m),str(y)) for r, t, e, m, y in zip(mcs_df[mcs_df['PARAM'] == "EmissionActivityRatio"].REGION, mcs_df[mcs_df['PARAM'] == "EmissionActivityRatio"].TECHNOLOGY, mcs_df[mcs_df['PARAM'] == "EmissionActivityRatio"].EMISSION, mcs_df[mcs_df['PARAM'] == "EmissionActivityRatio"].MODE_OF_OPERATION, mcs_df[mcs_df['PARAM'] == "EmissionActivityRatio"].YEAR)])
		
		EmissionActivityRatio = {str(r): {str(t): {str(e): {str(m): {str(y): generateRandomData(EmissionActivityRatio_ref[r][t][e][m][y], mcs_df[(mcs_df['PARAM'] == "EmissionActivityRatio") & (mcs_df['REGION'] == r) & (mcs_df['TECHNOLOGY'] == t) & (mcs_df['EMISSION'] == e) & (mcs_df['MODE_OF_OPERATION'] == m) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(e),str(m),str(y)) in EmissionActivityRatio_mcs_specified else generateRandomData(EmissionActivityRatio_ref[r][t][e][m][y], EmissionActivityRatio_mcs_default_list) for y in YEAR} for m in MODE_OF_OPERATION} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}
			
	if ("EmissionsPenalty" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			EmissionsPenalty_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "EmissionsPenalty") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			EmissionsPenalty_mcs_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(mcs_df[mcs_df['PARAM'] == "EmissionsPenalty"].REGION, mcs_df[mcs_df['PARAM'] == "EmissionsPenalty"].EMISSION, mcs_df[mcs_df['PARAM'] == "EmissionsPenalty"].YEAR)])
		
		EmissionsPenalty = {str(r): {str(e): {str(y): generateRandomData(EmissionsPenalty_ref[r][e][y], mcs_df[(mcs_df['PARAM'] == "EmissionsPenalty") & (mcs_df['REGION'] == r) & (mcs_df['EMISSION'] == e) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e), str(y)) in EmissionsPenalty_mcs_specified else generateRandomData(EmissionsPenalty_ref[r][e][y], EmissionsPenalty_mcs_default_list) for y in YEAR} for e in EMISSION} for r in REGION}
			
	if ("AnnualExogenousEmission" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			AnnualExogenousEmission_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "AnnualExogenousEmission") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			AnnualExogenousEmission_mcs_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(mcs_df[mcs_df['PARAM'] == "AnnualExogenousEmission"].REGION, mcs_df[mcs_df['PARAM'] == "AnnualExogenousEmission"].EMISSION, mcs_df[mcs_df['PARAM'] == "AnnualExogenousEmission"].YEAR)])
		
		AnnualExogenousEmission = {str(r): {str(e): {str(y): generateRandomData(AnnualExogenousEmission_ref[r][e][y], mcs_df[(mcs_df['PARAM'] == "AnnualExogenousEmission") & (mcs_df['REGION'] == r) & (mcs_df['EMISSION'] == e) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e), str(y)) in AnnualExogenousEmission_mcs_specified else generateRandomData(AnnualExogenousEmission_ref[r][e][y], AnnualExogenousEmission_mcs_default_list) for y in YEAR} for e in EMISSION} for r in REGION}
			
	if ("AnnualEmissionLimit" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			AnnualEmissionLimit_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "AnnualEmissionLimit") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			AnnualEmissionLimit_mcs_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(mcs_df[mcs_df['PARAM'] == "AnnualEmissionLimit"].REGION, mcs_df[mcs_df['PARAM'] == "AnnualEmissionLimit"].EMISSION, mcs_df[mcs_df['PARAM'] == "AnnualEmissionLimit"].YEAR)])
		
		AnnualEmissionLimit = {str(r): {str(e): {str(y): generateRandomData(AnnualEmissionLimit_ref[r][e][y], mcs_df[(mcs_df['PARAM'] == "AnnualEmissionLimit") & (mcs_df['REGION'] == r) & (mcs_df['EMISSION'] == e) & (mcs_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e), str(y)) in AnnualEmissionLimit_mcs_specified else generateRandomData(AnnualEmissionLimit_ref[r][e][y], AnnualEmissionLimit_mcs_default_list) for y in YEAR} for e in EMISSION} for r in REGION}
			
	if ("ModelPeriodExogenousEmission" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			ModelPeriodExogenousEmission_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "ModelPeriodExogenousEmission") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			ModelPeriodExogenousEmission_mcs_specified = tuple([(str(r), str(e)) for r, e in zip(mcs_df[mcs_df['PARAM'] == "ModelPeriodExogenousEmission"].REGION, mcs_df[mcs_df['PARAM'] == "ModelPeriodExogenousEmission"].EMISSION)])
		
		ModelPeriodExogenousEmission = {str(r): {str(e): generateRandomData(ModelPeriodExogenousEmission_ref[r][e], mcs_df[(mcs_df['PARAM'] == "ModelPeriodExogenousEmission") & (mcs_df['REGION'] == r) & (mcs_df['EMISSION'] == e)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e)) in ModelPeriodExogenousEmission_mcs_specified else generateRandomData(ModelPeriodExogenousEmission_ref[r][e], ModelPeriodExogenousEmission_mcs_default_list) for e in EMISSION} for r in REGION}
			
	if ("ModelPeriodEmissionLimit" in mcs_parameters) and (mcs_num > 0):
		if i == 1:
			ModelPeriodEmissionLimit_mcs_default_list = mcs_df[(mcs_df['PARAM'] == "ModelPeriodEmissionLimit") & (mcs_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			ModelPeriodEmissionLimit_mcs_specified = tuple([(str(r), str(e)) for r, e in zip(mcs_df[mcs_df['PARAM'] == "ModelPeriodEmissionLimit"].REGION, mcs_df[mcs_df['PARAM'] == "ModelPeriodEmissionLimit"].EMISSION)])
		
		ModelPeriodEmissionLimit = {str(r): {str(e): generateRandomData(ModelPeriodEmissionLimit_ref[r][e], mcs_df[(mcs_df['PARAM'] == "ModelPeriodEmissionLimit") & (mcs_df['REGION'] == r) & (mcs_df['EMISSION'] == e)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e)) in ModelPeriodEmissionLimit_mcs_specified else generateRandomData(ModelPeriodEmissionLimit_ref[r][e], ModelPeriodEmissionLimit_mcs_default_list) for e in EMISSION} for r in REGION}

	
logging.info("{}\tAnalysis is finished. Please wait until the results are saved!".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# ----------------------------------------------------------------------------------------------------------------------
#	SAVE ALL RESULTS
# ----------------------------------------------------------------------------------------------------------------------

saveResults(res_df, outputDir, outputFile)
logging.info("{}\tAll results are saved".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
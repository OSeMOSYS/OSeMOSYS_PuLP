# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version was tested with the following Python version and packages:
# Python 3.6.6, PuLP 1.6.8, Pandas 0.23.4, Numpy 1.15.2, xlrd 1.1.0, openpyxl 2.5.8

# module level doc-string
__author__ = "Dennis Dreier"
__copyright__ = "Copyright 2019"
__version__ = "OSeMOSYS_2017_11_08_PuLP_2019_04_10"
__license__ = "Apache License Version 2.0"
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
#
#	Additional references to be cited (see DOI links for complete references):
#
#	Howells et al. (2011), https://doi.org/10.1016/j.enpol.2011.06.033
#	Gardumi et al. (2018), https://doi.org/10.1016/j.esr.2018.03.005
#
#
#	Other sources:
#
#	GitHub OSeMOSYS-PuLP: https://github.com/codeadminoptimus/OSeMOSYS-PuLP
#	OpTIMUS community: http://www.optimus.community/
#	OSeMOSYS modelling framework: https://github.com/KTH-dESA/OSeMOSYS/blob/master/OSeMOSYS_GNU_MathProg/osemosys.txt
#	OSeMOSYS GitHub: https://github.com/KTH-dESA/OSeMOSYS
#	OSeMOSYS website: http://www.osemosys.org/
#
# ============================================================================
#
#	OSeMOSYS-PuLP 
#	
#	Version: OSeMOSYS_2017_11_08_PuLP_2019_04_10
#	--> OSeMOSYS-PuLP code version: 2019_04_10
#	--> OSeMOSYS modelling framework version: 2017_11_08
#
# ============================================================================
#	
#	To use the script, do the following steps:
#
#	1) Provide input data to the input data file (see script section "SETUP - DATA SOURCES and MONTE CARLO SIMULATION")
#	2) Results (i.e. values of variables to be saved) must be selected through the 
#	activation of the respective variables names in the dictionary "var_dict"
#	in the function "save_results_to_dataframe" in this script (i.e. add or delete "#" in front of
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
import pulp
import pandas as pd
import numpy as np
import datetime as dt

print("Script started. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


#########################################################
#	 SETUP - DATA SOURCES and MONTE CARLO SIMULATION    #
#########################################################

# Input data
input_data_directory = ".\Input_Data\\"
input_data_file = "UTOPIA_BASE.xlsx"
sheet_name_SETS = "SETS"
sheet_name_PARAMETERS = "PARAMETERS"
sheet_name_PARAMETERS_DEFAULT = "PARAMETERS_DEFAULT"
sheet_name_MCS = "MCS"
sheet_name_MCS_num = "MCS_num"

# Output data
output_data_directory = ".\Output_data\\"
output_data_file = "UTOPIA_BASE_results.xlsx"


###################
#    FUNCTIONS    #
###################


def load_input_data(file_path, sheet_name_sets, sheet_name_parameters, sheet_name_parameters_default, sheet_name_mcs, sheet_name_mcs_num):

	# Data: SETS
	SETS_df = pd.read_excel(io=file_path, sheet_name=sheet_name_sets)
	SETS_df['SET'] = SETS_df['SET'].astype(str)
	SETS_df['ELEMENTS'] = SETS_df['ELEMENTS'].astype(str)

	# Data: PARAMETERS
	PARAM_df = pd.read_excel(io=file_path, sheet_name=sheet_name_parameters)
	PARAM_df = PARAM_df.fillna(0)
	PARAM_df['PARAM'] = PARAM_df['PARAM'].astype(str)
	PARAM_df['VALUE'] = PARAM_df['VALUE'].apply(pd.to_numeric, downcast='signed')
	PARAM_df['REGION'] = PARAM_df['REGION'].astype(str)
	PARAM_df['REGION2'] = PARAM_df['REGION2'].astype(str)
	PARAM_df['DAYTYPE'] = PARAM_df['DAYTYPE'].astype(int)
	PARAM_df['DAYTYPE'] = PARAM_df['DAYTYPE'].astype(str)
	PARAM_df['EMISSION'] = PARAM_df['EMISSION'].astype(str)
	PARAM_df['FUEL'] = PARAM_df['FUEL'].astype(str)
	PARAM_df['DAILYTIMEBRACKET'] = PARAM_df['DAILYTIMEBRACKET'].astype(int)
	PARAM_df['DAILYTIMEBRACKET'] = PARAM_df['DAILYTIMEBRACKET'].astype(str)
	PARAM_df['SEASON'] = PARAM_df['SEASON'].astype(int)
	PARAM_df['SEASON'] = PARAM_df['SEASON'].astype(str)
	PARAM_df['TIMESLICE'] = PARAM_df['TIMESLICE'].astype(str)
	PARAM_df['MODE_OF_OPERATION'] = PARAM_df['MODE_OF_OPERATION'].astype(int)
	PARAM_df['MODE_OF_OPERATION'] = PARAM_df['MODE_OF_OPERATION'].astype(str)
	PARAM_df['STORAGE'] = PARAM_df['STORAGE'].astype(str)
	PARAM_df['TECHNOLOGY'] = PARAM_df['TECHNOLOGY'].astype(str)
	PARAM_df['YEAR'] = PARAM_df['YEAR'].astype(int)
	PARAM_df['YEAR'] = PARAM_df['YEAR'].astype(str)

	# Data: Parameters default values
	PARAM_DEFAULT_df = pd.read_excel(io=file_path, sheet_name=sheet_name_parameters_default)
	PARAM_DEFAULT_df = PARAM_DEFAULT_df.fillna(0)
	PARAM_DEFAULT_df['PARAM'] = PARAM_DEFAULT_df['PARAM'].astype(str)
	PARAM_DEFAULT_df['VALUE'] = PARAM_DEFAULT_df['VALUE'].apply(pd.to_numeric, downcast='signed')

	# Data: Monte Carlo Simulation (MCS)
	MCS_df = pd.read_excel(io=file_path, sheet_name=sheet_name_mcs)
	MCS_df = MCS_df.fillna(0)
	MCS_df['DEFAULT_SETTING'] = MCS_df['DEFAULT_SETTING'].apply(pd.to_numeric, downcast='signed')
	MCS_df['DEFAULT_SETTING'] = MCS_df['DEFAULT_SETTING'].astype(int)
	MCS_df['REL_SD'] = MCS_df['REL_SD'].apply(pd.to_numeric, downcast='signed')
	MCS_df['REL_MIN'] = MCS_df['REL_MIN'].apply(pd.to_numeric, downcast='signed')
	MCS_df['REL_MAX'] = MCS_df['REL_MAX'].apply(pd.to_numeric, downcast='signed')
	MCS_df['DISTRIBUTION'] = MCS_df['DISTRIBUTION'].astype(str)
	MCS_df['ARRAY'] = [[float(i) for i in str(x).split(",")] for x in MCS_df['ARRAY']]
	MCS_df['PARAM'] = MCS_df['PARAM'].astype(str)
	MCS_df['REGION'] = MCS_df['REGION'].astype(str)
	MCS_df['DAYTYPE'] = MCS_df['DAYTYPE'].astype(int)
	MCS_df['DAYTYPE'] = MCS_df['DAYTYPE'].astype(str)
	MCS_df['EMISSION'] = MCS_df['EMISSION'].astype(str)
	MCS_df['FUEL'] = MCS_df['FUEL'].astype(str)
	MCS_df['DAILYTIMEBRACKET'] = MCS_df['DAILYTIMEBRACKET'].astype(int)
	MCS_df['DAILYTIMEBRACKET'] = MCS_df['DAILYTIMEBRACKET'].astype(str)
	MCS_df['SEASON'] = MCS_df['SEASON'].astype(int)
	MCS_df['SEASON'] = MCS_df['SEASON'].astype(str)
	MCS_df['TIMESLICE'] = MCS_df['TIMESLICE'].astype(str)
	MCS_df['MODE_OF_OPERATION'] = MCS_df['MODE_OF_OPERATION'].astype(int)
	MCS_df['MODE_OF_OPERATION'] = MCS_df['MODE_OF_OPERATION'].astype(str)
	MCS_df['STORAGE'] = MCS_df['STORAGE'].astype(str)
	MCS_df['TECHNOLOGY'] = MCS_df['TECHNOLOGY'].astype(str)
	MCS_df['YEAR'] = MCS_df['YEAR'].astype(int)
	MCS_df['YEAR'] = MCS_df['YEAR'].astype(str)
	
	# Number of MCS simulations
	MCS_num_df = pd.read_excel(io=file_path, sheet_name=sheet_name_mcs_num)
	MCS_num = MCS_num_df.at[0, 'MCS_num']

	return SETS_df, PARAM_df, PARAM_DEFAULT_df, MCS_df, MCS_num


def random_data_generation(reference, list):
	# reference (format: float): mean for normal distribution, mode for both triangular and uniform distributions
	dist, rel_sd, rel_min, rel_max, array = list[0], list[1], list[2], list[3], list[4]
	# dist: type of distribution. Choose from: "normal", "triangular", "uniform" (format: string)
	# rel_sd: relative standard deviation from mean or mode. Unit: percent as decimals (format: float)
	# rel_min: relative minimum deviation from mean or mode. Unit: percent as decimals (format: float), must be a negative value
	# rel_max: relative maximum deviation from mean or mode. Unit: percent as decimals (format: float), must be a positive value
  	# array: array with potential values. One value out of the array will be randomly chosen.
	# ==================================================================================================================
	# Note: To use the reference value without any distribution, then write as input in the excel file in the tab "MCS":
	# Columns: PARAM: "parameter name", DEFAULT_SETTING:	"1", DIST: "normal", REL_SD: "0".
	# This will make the code to choose the reference value as defined for the model without MCS.

	if dist == "normal":
		value = np.random.normal(reference, rel_sd*reference, 1)[0]  # mean, standard deviation, generate 1 value at the time
	elif dist == "triangular":
		value = np.random.triangular((1+rel_min)*reference, reference, (1+rel_max)*reference, 1)[0]  # minimum value, mode, maximum value, generate 1 value at the time
	elif dist == "uniform":
		value = np.random.uniform((1+rel_min)*reference, (1+rel_max)*reference, 1)[0]  # minimum value, maximum value, generate 1 value at the time
	elif dist == "choice":
		if len(array) > 1:
			value = np.random.choice(array)
		else:
			print("ERROR: Review MCS_df array column. Expected length of array: larger than 1, but is: 0 or 1")
	else:
		print("ERROR: Select an available distribution, review input data and/or add default input data for this parameter.")
		return

	# This if condition prevents input errors caused by negative values for the parameters
	if value >= 0:
		return value
	else:
		return 0

		
def save_results_to_dataframe(dataframe, model_name, scenario):
	
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
	df_temp = pd.DataFrame(columns=[
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

	df_temp.at[0, 'SCENARIO'] = scenario
	df_temp.at[0, 'VAR_NAME'] = "cost"
	df_temp.at[0, 'VAR_VALUE'] = model_name.objective.value()
	df_temp.at[0, 'REGION'] = " "
	df_temp.at[0, 'REGION2'] = " "
	df_temp.at[0, 'DAYTYPE'] = " "
	df_temp.at[0, 'EMISSION'] = " "
	df_temp.at[0, 'FUEL'] = " "
	df_temp.at[0, 'DAILYTIMEBRACKET'] = " "
	df_temp.at[0, 'SEASON'] = " "
	df_temp.at[0, 'TIMESLICE'] = " "
	df_temp.at[0, 'MODE_OF_OPERATION'] = " "
	df_temp.at[0, 'STORAGE'] = " "
	df_temp.at[0, 'TECHNOLOGY'] = " "
	df_temp.at[0, 'YEAR'] = " "
	df_temp.at[0, 'FLEXIBLEDEMANDTYPE'] = " "

	df = pd.concat([df, df_temp])

	# Variables values (only variables that are included in var_dict)
	selected_variables = [variable for key in var_dict.keys() for variable in model_name.variables() if key == variable.name.split("_")[0]]

	for var in selected_variables:

		# Temporal dataframe in loop
		df_temp = pd.DataFrame(columns=[
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

		# Write data to dataframe
		df_temp.at[0, 'SCENARIO'] = scenario
		df_temp.at[0, 'VAR_NAME'] = var.name.split("_")[0]
		df_temp.at[0, 'VAR_VALUE'] = var.varValue
		df_temp.at[0, 'REGION'] = data_dict["r"]
		df_temp.at[0, 'REGION2'] = data_dict["rr"]
		df_temp.at[0, 'DAYTYPE'] = data_dict["ld"]
		df_temp.at[0, 'EMISSION'] = data_dict["e"]
		df_temp.at[0, 'FUEL'] = data_dict["f"]
		df_temp.at[0, 'DAILYTIMEBRACKET'] = data_dict["lh"]
		df_temp.at[0, 'SEASON'] = data_dict["ls"]
		df_temp.at[0, 'TIMESLICE'] = data_dict["l"]
		df_temp.at[0, 'MODE_OF_OPERATION'] = data_dict["m"]
		df_temp.at[0, 'STORAGE'] = data_dict["s"]
		df_temp.at[0, 'TECHNOLOGY'] = data_dict["t"]
		df_temp.at[0, 'YEAR'] = data_dict["y"]
		df_temp.at[0, 'FLEXIBLEDEMANDTYPE'] = data_dict["fdt"]

		df = pd.concat([df, df_temp])

	return df


def save_results(dataframe, file_path):
	df = dataframe
	name_list = df['VAR_NAME'].unique()
	dataframe_list = [df[df['VAR_NAME'] == str(name)] for name in name_list]
	writer = pd.ExcelWriter(file_path)

	for df, name in zip(dataframe_list, name_list):
		df.to_excel(writer, sheet_name=name, index=False)
	writer.save()
	return


###################
#    LOAD DATA    #
###################

input_data_path = os.path.join(input_data_directory, input_data_file)
SETS_df, PARAM_df, PARAM_DEFAULT_df, MCS_df, MCS_num = load_input_data(input_data_path, sheet_name_SETS, sheet_name_PARAMETERS, sheet_name_PARAMETERS_DEFAULT, sheet_name_MCS, sheet_name_MCS_num)
mcs_parameters = MCS_df['PARAM'].unique()  # list of parameters to be included in monte carlo simulation

print("Data is loaded. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

##############
#    SETS    #
##############

YEAR = SETS_df[SETS_df['SET'] == "YEAR"].ELEMENTS.tolist()[0].split(" ")
TECHNOLOGY = SETS_df[SETS_df['SET'] == "TECHNOLOGY"].ELEMENTS.tolist()[0].split(" ")
TIMESLICE = SETS_df[SETS_df['SET'] == "TIMESLICE"].ELEMENTS.tolist()[0].split(" ")
FUEL = SETS_df[SETS_df['SET'] == "FUEL"].ELEMENTS.tolist()[0].split(" ")
EMISSION = SETS_df[SETS_df['SET'] == "EMISSION"].ELEMENTS.tolist()[0].split(" ")
MODE_OF_OPERATION = SETS_df[SETS_df['SET'] == "MODE_OF_OPERATION"].ELEMENTS.tolist()[0].split(" ")
REGION = SETS_df[SETS_df['SET'] == "REGION"].ELEMENTS.tolist()[0].split(" ")
REGION2 = SETS_df[SETS_df['SET'] == "REGION2"].ELEMENTS.tolist()[0].split(" ")
SEASON = SETS_df[SETS_df['SET'] == "SEASON"].ELEMENTS.tolist()[0].split(" ")
DAYTYPE = SETS_df[SETS_df['SET'] == "DAYTYPE"].ELEMENTS.tolist()[0].split(" ")
DAILYTIMEBRACKET = SETS_df[SETS_df['SET'] == "DAILYTIMEBRACKET"].ELEMENTS.tolist()[0].split(" ")
FLEXIBLEDEMANDTYPE = SETS_df[SETS_df['SET'] == "FLEXIBLEDEMANDTYPE"].ELEMENTS.tolist()[0].split(" ")
STORAGE = SETS_df[SETS_df['SET'] == "STORAGE"].ELEMENTS.tolist()[0].split(" ")

print("Sets are created. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

###########################
#    PARAMETERS AND DATA  #
###########################

########			Global 						#########

# YearSplit
YearSplit = PARAM_df[PARAM_df['PARAM'] == "YearSplit"][['TIMESLICE', 'YEAR', 'VALUE']].groupby('TIMESLICE').apply(lambda df: df.set_index('YEAR')['VALUE'].to_dict()).to_dict()

# DiscountRate
DiscountRate_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "DiscountRate"].VALUE.iat[0]
DiscountRate_specified = tuple([(str(r)) for r in PARAM_df[PARAM_df['PARAM'] == "DiscountRate"].REGION])
DiscountRate = {str(r): PARAM_df[(PARAM_df['PARAM'] == "DiscountRate") & (PARAM_df['REGION'] == r)].VALUE.iat[0] if (str(r)) in DiscountRate_specified else DiscountRate_default_value for r in REGION}

# DaySplit
DaySplit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "DaySplit"].VALUE.iat[0]
DaySplit_specified = tuple([(str(lh), str(y)) for lh, y in zip(PARAM_df[PARAM_df['PARAM'] == "DaySplit"].DAILYTIMEBRACKET, PARAM_df[PARAM_df['PARAM'] == "DaySplit"].YEAR)])
DaySplit = {str(lh): {str(y): PARAM_df[(PARAM_df['PARAM'] == "DaySplit") & (PARAM_df['DAILYTIMEBRACKET'] == lh) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(lh), str(y)) in DaySplit_specified else DaySplit_default_value for y in YEAR} for lh in DAILYTIMEBRACKET}

# Conversionls
Conversionls_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "Conversionls"].VALUE.iat[0]
Conversionls_specified = tuple([(str(l), str(ls)) for l, ls in zip(PARAM_df[PARAM_df['PARAM'] == "Conversionls"].TIMESLICE, PARAM_df[PARAM_df['PARAM'] == "Conversionls"].SEASON)])
Conversionls = {str(l): {str(ls): PARAM_df[(PARAM_df['PARAM'] == "Conversionls") & (PARAM_df['TIMESLICE'] == l) & (PARAM_df['SEASON'] == ls)].VALUE.iat[0] if (str(l), str(ls)) in Conversionls_specified else Conversionls_default_value for ls in SEASON} for l in TIMESLICE}

# Conversionld
Conversionld_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "Conversionld"].VALUE.iat[0]
Conversionld_specified = tuple([(str(l), str(ld)) for l, ld in zip(PARAM_df[PARAM_df['PARAM'] == "Conversionld"].TIMESLICE, PARAM_df[PARAM_df['PARAM'] == "Conversionld"].DAYTYPE)])
Conversionld = {str(l): {str(ld): PARAM_df[(PARAM_df['PARAM'] == "Conversionld") & (PARAM_df['TIMESLICE'] == l) & (PARAM_df['DAYTYPE'] == ld)].VALUE.iat[0] if (str(l), str(ld)) in Conversionld_specified else Conversionld_default_value for ld in DAYTYPE} for l in TIMESLICE}

# Conversionlh
Conversionlh_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "Conversionlh"].VALUE.iat[0]
Conversionlh_specified = tuple([(str(l), str(lh)) for l, lh in zip(PARAM_df[PARAM_df['PARAM'] == "Conversionlh"].TIMESLICE, PARAM_df[PARAM_df['PARAM'] == "Conversionlh"].DAILYTIMEBRACKET)])
Conversionlh = {str(l): {str(lh): PARAM_df[(PARAM_df['PARAM'] == "Conversionlh") & (PARAM_df['TIMESLICE'] == l) & (PARAM_df['DAILYTIMEBRACKET'] == lh)].VALUE.iat[0] if (str(l), str(lh)) in Conversionlh_specified else Conversionlh_default_value for lh in DAILYTIMEBRACKET} for l in TIMESLICE}

# DaysInDayType
DaysInDayType_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "DaysInDayType"].VALUE.iat[0]
DaysInDayType_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(PARAM_df[PARAM_df['PARAM'] == "DaysInDayType"].SEASON, PARAM_df[PARAM_df['PARAM'] == "DaysInDayType"].DAYTYPE, PARAM_df[PARAM_df['PARAM'] == "DaysInDayType"].YEAR)])
DaysInDayType = {str(ls): {str(ld): {str(y): PARAM_df[(PARAM_df['PARAM'] == "DaysInDayType") & (PARAM_df['SEASON'] == ls) & (PARAM_df['DAYTYPE'] == ld) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(ls),str(ld),str(y)) in DaysInDayType_specified else DaysInDayType_default_value for y in YEAR} for ld in DAYTYPE} for ls in SEASON}

# TradeRoute
TradeRoute_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TradeRoute"].VALUE.iat[0]
TradeRoute_specified = tuple([(str(r),str(rr),str(f),str(y)) for r, rr, f, y in zip(PARAM_df[PARAM_df['PARAM'] == "TradeRoute"].REGION, PARAM_df[PARAM_df['PARAM'] == "TradeRoute"].REGION2, PARAM_df[PARAM_df['PARAM'] == "TradeRoute"].FUEL, PARAM_df[PARAM_df['PARAM'] == "TradeRoute"].YEAR)])
TradeRoute = {str(r): {str(rr): {str(f): {str(y): PARAM_df[(PARAM_df['PARAM'] == "TradeRoute") & (PARAM_df['REGION'] == r) & (PARAM_df['REGION2'] == rr) & (PARAM_df['FUEL'] == f) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(rr),str(f),str(y)) in TradeRoute_specified else TradeRoute_default_value for y in YEAR} for f in FUEL} for rr in REGION2} for r in REGION}

# DepreciationMethod
DepreciationMethod_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "DepreciationMethod"].VALUE.iat[0]
DepreciationMethod_specified = tuple([(str(r)) for r in PARAM_df[PARAM_df['PARAM'] == "DepreciationMethod"].REGION])
DepreciationMethod = {str(r): PARAM_df[(PARAM_df['PARAM'] == "DepreciationMethod") & (PARAM_df['REGION'] == r)].VALUE.iat[0] if (str(r)) in DepreciationMethod_specified else DepreciationMethod_default_value for r in REGION}


########			Demands 					#########

# SpecifiedAnnualDemand
SpecifiedAnnualDemand_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "SpecifiedAnnualDemand"].VALUE.iat[0]
SpecifiedAnnualDemand_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(PARAM_df[PARAM_df['PARAM'] == "SpecifiedAnnualDemand"].REGION, PARAM_df[PARAM_df['PARAM'] == "SpecifiedAnnualDemand"].FUEL, PARAM_df[PARAM_df['PARAM'] == "SpecifiedAnnualDemand"].YEAR)])
SpecifiedAnnualDemand = {str(r): {str(f): {str(y): PARAM_df[(PARAM_df['PARAM'] == "SpecifiedAnnualDemand") & (PARAM_df['REGION'] == r) & (PARAM_df['FUEL'] == f) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(f),str(y)) in SpecifiedAnnualDemand_specified else SpecifiedAnnualDemand_default_value for y in YEAR} for f in FUEL} for r in REGION}

# SpecifiedDemandProfile
SpecifiedDemandProfile_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "SpecifiedDemandProfile"].VALUE.iat[0]
SpecifiedDemandProfile_specified = tuple([(str(r),str(f),str(l),str(y)) for r, f, l, y in zip(PARAM_df[PARAM_df['PARAM'] == "SpecifiedDemandProfile"].REGION, PARAM_df[PARAM_df['PARAM'] == "SpecifiedDemandProfile"].FUEL, PARAM_df[PARAM_df['PARAM'] == "SpecifiedDemandProfile"].TIMESLICE, PARAM_df[PARAM_df['PARAM'] == "SpecifiedDemandProfile"].YEAR)])
SpecifiedDemandProfile = {str(r): {str(f): {str(l): {str(y): PARAM_df[(PARAM_df['PARAM'] == "SpecifiedDemandProfile") & (PARAM_df['REGION'] == r) & (PARAM_df['FUEL'] == f) & (PARAM_df['TIMESLICE'] == l) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(f),str(l),str(y)) in SpecifiedDemandProfile_specified else SpecifiedDemandProfile_default_value for y in YEAR} for l in TIMESLICE} for f in FUEL} for r in REGION}

# AccumulatedAnnualDemand
AccumulatedAnnualDemand_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "AccumulatedAnnualDemand"].VALUE.iat[0]
AccumulatedAnnualDemand_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(PARAM_df[PARAM_df['PARAM'] == "AccumulatedAnnualDemand"].REGION, PARAM_df[PARAM_df['PARAM'] == "AccumulatedAnnualDemand"].FUEL, PARAM_df[PARAM_df['PARAM'] == "AccumulatedAnnualDemand"].YEAR)])
AccumulatedAnnualDemand = {str(r): {str(f): {str(y): PARAM_df[(PARAM_df['PARAM'] == "AccumulatedAnnualDemand") & (PARAM_df['REGION'] == r) & (PARAM_df['FUEL'] == f) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(f),str(y)) in AccumulatedAnnualDemand_specified else AccumulatedAnnualDemand_default_value for y in YEAR} for f in FUEL} for r in REGION}


#########			Performance					#########

# CapacityToActivityUnit
CapacityToActivityUnit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "CapacityToActivityUnit"].VALUE.iat[0]
CapacityToActivityUnit_specified = tuple([(str(r), str(t)) for r, t in zip(PARAM_df[PARAM_df['PARAM'] == "CapacityToActivityUnit"].REGION, PARAM_df[PARAM_df['PARAM'] == "CapacityToActivityUnit"].TECHNOLOGY)])
CapacityToActivityUnit = {str(r): {str(t): PARAM_df[(PARAM_df['PARAM'] == "CapacityToActivityUnit") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in CapacityToActivityUnit_specified else CapacityToActivityUnit_default_value for t in TECHNOLOGY} for r in REGION}

# TechWithCapacityNeededToMeetPeakTS
TechWithCapacityNeededToMeetPeakTS_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].VALUE.iat[0]
TechWithCapacityNeededToMeetPeakTS_specified = tuple([(str(r), str(t)) for r, t in zip(PARAM_df[PARAM_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].REGION, PARAM_df[PARAM_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].TECHNOLOGY)])
TechWithCapacityNeededToMeetPeakTS = {str(r): {str(t): PARAM_df[(PARAM_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in TechWithCapacityNeededToMeetPeakTS_specified else TechWithCapacityNeededToMeetPeakTS_default_value for t in TECHNOLOGY} for r in REGION}

# CapacityFactor
CapacityFactor_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "CapacityFactor"].VALUE.iat[0]
CapacityFactor_specified = tuple([(str(r),str(t),str(l),str(y)) for r, t, l, y in zip(PARAM_df[PARAM_df['PARAM'] == "CapacityFactor"].REGION, PARAM_df[PARAM_df['PARAM'] == "CapacityFactor"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "CapacityFactor"].TIMESLICE, PARAM_df[PARAM_df['PARAM'] == "CapacityFactor"].YEAR)])
CapacityFactor = {str(r): {str(t): {str(l): {str(y): PARAM_df[(PARAM_df['PARAM'] == "CapacityFactor") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(l),str(y)) in CapacityFactor_specified else CapacityFactor_default_value for y in YEAR} for l in TIMESLICE} for t in TECHNOLOGY} for r in REGION}

# AvailabilityFactor
AvailabilityFactor_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "AvailabilityFactor"].VALUE.iat[0]
AvailabilityFactor_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "AvailabilityFactor"].REGION, PARAM_df[PARAM_df['PARAM'] == "AvailabilityFactor"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "AvailabilityFactor"].YEAR)])
AvailabilityFactor = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "AvailabilityFactor") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(y)) in AvailabilityFactor_specified else AvailabilityFactor_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# OperationalLife
OperationalLife_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "OperationalLife"].VALUE.iat[0]
OperationalLife_specified = tuple([(str(r), str(t)) for r, t in zip(PARAM_df[PARAM_df['PARAM'] == "OperationalLife"].REGION, PARAM_df[PARAM_df['PARAM'] == "OperationalLife"].TECHNOLOGY)])
OperationalLife = {str(r): {str(t): PARAM_df[(PARAM_df['PARAM'] == "OperationalLife") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in OperationalLife_specified else OperationalLife_default_value for t in TECHNOLOGY} for r in REGION}

# ResidualCapacity
ResidualCapacity_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "ResidualCapacity"].VALUE.iat[0]
ResidualCapacity_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "ResidualCapacity"].REGION, PARAM_df[PARAM_df['PARAM'] == "ResidualCapacity"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "ResidualCapacity"].YEAR)])
ResidualCapacity = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "ResidualCapacity") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(y)) in ResidualCapacity_specified else ResidualCapacity_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# InputActivityRatio
InputActivityRatio_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "InputActivityRatio"].VALUE.iat[0]
InputActivityRatio_specified = tuple([(str(r),str(t),str(f),str(m),str(y)) for r, t, f, m, y in zip(PARAM_df[PARAM_df['PARAM'] == "InputActivityRatio"].REGION, PARAM_df[PARAM_df['PARAM'] == "InputActivityRatio"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "InputActivityRatio"].FUEL, PARAM_df[PARAM_df['PARAM'] == "InputActivityRatio"].MODE_OF_OPERATION, PARAM_df[PARAM_df['PARAM'] == "InputActivityRatio"].YEAR)])
InputActivityRatio = {str(r): {str(t): {str(f): {str(m): {str(y): PARAM_df[(PARAM_df['PARAM'] == "InputActivityRatio") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['FUEL'] == f) & (PARAM_df['MODE_OF_OPERATION'] == m) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(f),str(m),str(y)) in InputActivityRatio_specified else InputActivityRatio_default_value for y in YEAR} for m in MODE_OF_OPERATION} for f in FUEL} for t in TECHNOLOGY} for r in REGION}

# OutputActivityRatio
OutputActivityRatio_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "OutputActivityRatio"].VALUE.iat[0]
OutputActivityRatio_specified = tuple([(str(r),str(t),str(f),str(m),str(y)) for r, t, f, m, y in zip(PARAM_df[PARAM_df['PARAM'] == "OutputActivityRatio"].REGION, PARAM_df[PARAM_df['PARAM'] == "OutputActivityRatio"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "OutputActivityRatio"].FUEL, PARAM_df[PARAM_df['PARAM'] == "OutputActivityRatio"].MODE_OF_OPERATION, PARAM_df[PARAM_df['PARAM'] == "OutputActivityRatio"].YEAR)])
OutputActivityRatio = {str(r): {str(t): {str(f): {str(m): {str(y): PARAM_df[(PARAM_df['PARAM'] == "OutputActivityRatio") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['FUEL'] == f) & (PARAM_df['MODE_OF_OPERATION'] == m) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(f),str(m),str(y)) in OutputActivityRatio_specified else OutputActivityRatio_default_value for y in YEAR} for m in MODE_OF_OPERATION} for f in FUEL} for t in TECHNOLOGY} for r in REGION}


#########			Technology Costs			#########

# CapitalCost
CapitalCost_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "CapitalCost"].VALUE.iat[0]
CapitalCost_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "CapitalCost"].REGION, PARAM_df[PARAM_df['PARAM'] == "CapitalCost"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "CapitalCost"].YEAR)])
CapitalCost = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "CapitalCost") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(y)) in CapitalCost_specified else CapitalCost_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# VariableCost
VariableCost_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "VariableCost"].VALUE.iat[0]
VariableCost_specified = tuple([(str(r),str(t),str(m),str(y)) for r, t, m, y in zip(PARAM_df[PARAM_df['PARAM'] == "VariableCost"].REGION, PARAM_df[PARAM_df['PARAM'] == "VariableCost"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "VariableCost"].MODE_OF_OPERATION, PARAM_df[PARAM_df['PARAM'] == "VariableCost"].YEAR)])
VariableCost = {str(r): {str(t): {str(m): {str(y): PARAM_df[(PARAM_df['PARAM'] == "VariableCost") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['MODE_OF_OPERATION'] == m) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(m),str(y)) in VariableCost_specified else VariableCost_default_value for y in YEAR} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for r in REGION}

# FixedCost
FixedCost_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "FixedCost"].VALUE.iat[0]
FixedCost_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "FixedCost"].REGION, PARAM_df[PARAM_df['PARAM'] == "FixedCost"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "FixedCost"].YEAR)])
FixedCost = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "FixedCost") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(y)) in FixedCost_specified else FixedCost_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}


#########			Storage                 	#########

# TechnologyToStorage
TechnologyToStorage_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TechnologyToStorage"].VALUE.iat[0]
TechnologyToStorage_specified = tuple([(str(r),str(t),str(s),str(m)) for r, t, s, m in zip(PARAM_df[PARAM_df['PARAM'] == "TechnologyToStorage"].REGION, PARAM_df[PARAM_df['PARAM'] == "TechnologyToStorage"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "TechnologyToStorage"].STORAGE, PARAM_df[PARAM_df['PARAM'] == "TechnologyToStorage"].MODE_OF_OPERATION)])
TechnologyToStorage = {str(r): {str(t): {str(s): {str(m): PARAM_df[(PARAM_df['PARAM'] == "TechnologyToStorage") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['STORAGE'] == s) & (PARAM_df['MODE_OF_OPERATION'] == m)].VALUE.iat[0] if (str(r),str(t),str(s),str(m)) in TechnologyToStorage_specified else TechnologyToStorage_default_value for m in MODE_OF_OPERATION} for s in STORAGE} for t in TECHNOLOGY} for r in REGION}

# TechnologyFromStorage
TechnologyFromStorage_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TechnologyFromStorage"].VALUE.iat[0]
TechnologyFromStorage_specified = tuple([(str(r),str(t),str(s),str(m)) for r, t, s, m in zip(PARAM_df[PARAM_df['PARAM'] == "TechnologyFromStorage"].REGION, PARAM_df[PARAM_df['PARAM'] == "TechnologyFromStorage"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "TechnologyFromStorage"].STORAGE, PARAM_df[PARAM_df['PARAM'] == "TechnologyFromStorage"].MODE_OF_OPERATION)])
TechnologyFromStorage = {str(r): {str(t): {str(s): {str(m): PARAM_df[(PARAM_df['PARAM'] == "TechnologyFromStorage") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['STORAGE'] == s) & (PARAM_df['MODE_OF_OPERATION'] == m)].VALUE.iat[0] if (str(r),str(t),str(s),str(m)) in TechnologyFromStorage_specified else TechnologyFromStorage_default_value for m in MODE_OF_OPERATION} for s in STORAGE} for t in TECHNOLOGY} for r in REGION}

# StorageLevelStart
StorageLevelStart_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "StorageLevelStart"].VALUE.iat[0]
StorageLevelStart_specified = tuple([(str(r), str(s)) for r, s in zip(PARAM_df[PARAM_df['PARAM'] == "StorageLevelStart"].REGION, PARAM_df[PARAM_df['PARAM'] == "StorageLevelStart"].STORAGE)])
StorageLevelStart = {str(r): {str(s): PARAM_df[(PARAM_df['PARAM'] == "StorageLevelStart") & (PARAM_df['REGION'] == r) & (PARAM_df['STORAGE'] == s)].VALUE.iat[0] if (str(r), str(s)) in StorageLevelStart_specified else StorageLevelStart_default_value for s in STORAGE} for r in REGION}

# StorageMaxChargeRate
StorageMaxChargeRate_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "StorageMaxChargeRate"].VALUE.iat[0]
StorageMaxChargeRate_specified = tuple([(str(r), str(s)) for r, s in zip(PARAM_df[PARAM_df['PARAM'] == "StorageMaxChargeRate"].REGION, PARAM_df[PARAM_df['PARAM'] == "StorageMaxChargeRate"].STORAGE)])
StorageMaxChargeRate = {str(r): {str(s): PARAM_df[(PARAM_df['PARAM'] == "StorageMaxChargeRate") & (PARAM_df['REGION'] == r) & (PARAM_df['STORAGE'] == s)].VALUE.iat[0] if (str(r), str(s)) in StorageMaxChargeRate_specified else StorageMaxChargeRate_default_value for s in STORAGE} for r in REGION}

# StorageMaxDischargeRate
StorageMaxDischargeRate_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "StorageMaxDischargeRate"].VALUE.iat[0]
StorageMaxDischargeRate_specified = tuple([(str(r), str(s)) for r, s in zip(PARAM_df[PARAM_df['PARAM'] == "StorageMaxDischargeRate"].REGION, PARAM_df[PARAM_df['PARAM'] == "StorageMaxDischargeRate"].STORAGE)])
StorageMaxDischargeRate = {str(r): {str(s): PARAM_df[(PARAM_df['PARAM'] == "StorageMaxDischargeRate") & (PARAM_df['REGION'] == r) & (PARAM_df['STORAGE'] == s)].VALUE.iat[0] if (str(r), str(s)) in StorageMaxDischargeRate_specified else StorageMaxDischargeRate_default_value for s in STORAGE} for r in REGION}

# MinStorageCharge
MinStorageCharge_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "MinStorageCharge"].VALUE.iat[0]
MinStorageCharge_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(PARAM_df[PARAM_df['PARAM'] == "MinStorageCharge"].REGION, PARAM_df[PARAM_df['PARAM'] == "MinStorageCharge"].STORAGE, PARAM_df[PARAM_df['PARAM'] == "MinStorageCharge"].YEAR)])
MinStorageCharge = {str(r): {str(s): {str(y): PARAM_df[(PARAM_df['PARAM'] == "MinStorageCharge") & (PARAM_df['REGION'] == r) & (PARAM_df['STORAGE'] == s) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(s), str(y)) in MinStorageCharge_specified else MinStorageCharge_default_value for y in YEAR} for s in STORAGE} for r in REGION}

# OperationalLifeStorage
OperationalLifeStorage_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "OperationalLifeStorage"].VALUE.iat[0]
OperationalLifeStorage_specified = tuple([(str(r), str(s)) for r, s in zip(PARAM_df[PARAM_df['PARAM'] == "OperationalLifeStorage"].REGION, PARAM_df[PARAM_df['PARAM'] == "OperationalLifeStorage"].STORAGE)])
OperationalLifeStorage = {str(r): {str(s): PARAM_df[(PARAM_df['PARAM'] == "OperationalLifeStorage") & (PARAM_df['REGION'] == r) & (PARAM_df['STORAGE'] == s)].VALUE.iat[0] if (str(r), str(s)) in OperationalLifeStorage_specified else OperationalLifeStorage_default_value for s in STORAGE} for r in REGION}

# CapitalCostStorage
CapitalCostStorage_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "CapitalCostStorage"].VALUE.iat[0]
CapitalCostStorage_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(PARAM_df[PARAM_df['PARAM'] == "CapitalCostStorage"].REGION, PARAM_df[PARAM_df['PARAM'] == "CapitalCostStorage"].STORAGE, PARAM_df[PARAM_df['PARAM'] == "CapitalCostStorage"].YEAR)])
CapitalCostStorage = {str(r): {str(s): {str(y): PARAM_df[(PARAM_df['PARAM'] == "CapitalCostStorage") & (PARAM_df['REGION'] == r) & (PARAM_df['STORAGE'] == s) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(s), str(y)) in CapitalCostStorage_specified else CapitalCostStorage_default_value for y in YEAR} for s in STORAGE} for r in REGION}

# ResidualStorageCapacity
ResidualStorageCapacity_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "ResidualStorageCapacity"].VALUE.iat[0]
ResidualStorageCapacity_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(PARAM_df[PARAM_df['PARAM'] == "ResidualStorageCapacity"].REGION, PARAM_df[PARAM_df['PARAM'] == "ResidualStorageCapacity"].STORAGE, PARAM_df[PARAM_df['PARAM'] == "ResidualStorageCapacity"].YEAR)])
ResidualStorageCapacity = {str(r): {str(s): {str(y): PARAM_df[(PARAM_df['PARAM'] == "ResidualStorageCapacity") & (PARAM_df['REGION'] == r) & (PARAM_df['STORAGE'] == s) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(s), str(y)) in ResidualStorageCapacity_specified else ResidualStorageCapacity_default_value for y in YEAR} for s in STORAGE} for r in REGION}


#########			Capacity Constraints		#########

# CapacityOfOneTechnologyUnit
CapacityOfOneTechnologyUnit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "CapacityOfOneTechnologyUnit"].VALUE.iat[0]
CapacityOfOneTechnologyUnit_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "CapacityOfOneTechnologyUnit"].REGION, PARAM_df[PARAM_df['PARAM'] == "CapacityOfOneTechnologyUnit"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "CapacityOfOneTechnologyUnit"].YEAR)])
CapacityOfOneTechnologyUnit = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "CapacityOfOneTechnologyUnit") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in CapacityOfOneTechnologyUnit_specified else CapacityOfOneTechnologyUnit_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalAnnualMaxCapacity
TotalAnnualMaxCapacity_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TotalAnnualMaxCapacity"].VALUE.iat[0]
TotalAnnualMaxCapacity_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMaxCapacity"].REGION, PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMaxCapacity"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMaxCapacity"].YEAR)])
TotalAnnualMaxCapacity = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "TotalAnnualMaxCapacity") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalAnnualMaxCapacity_specified else TotalAnnualMaxCapacity_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalAnnualMinCapacity
TotalAnnualMinCapacity_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TotalAnnualMinCapacity"].VALUE.iat[0]
TotalAnnualMinCapacity_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMinCapacity"].REGION, PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMinCapacity"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMinCapacity"].YEAR)])
TotalAnnualMinCapacity = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "TotalAnnualMinCapacity") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalAnnualMinCapacity_specified else TotalAnnualMinCapacity_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}


#########			Investment Constraints		#########

# TotalAnnualMaxCapacityInvestment
TotalAnnualMaxCapacityInvestment_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].VALUE.iat[0]
TotalAnnualMaxCapacityInvestment_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].REGION, PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].YEAR)])
TotalAnnualMaxCapacityInvestment = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "TotalAnnualMaxCapacityInvestment") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalAnnualMaxCapacityInvestment_specified else TotalAnnualMaxCapacityInvestment_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalAnnualMinCapacityInvestment
TotalAnnualMinCapacityInvestment_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].VALUE.iat[0]
TotalAnnualMinCapacityInvestment_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].REGION, PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].YEAR)])
TotalAnnualMinCapacityInvestment = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "TotalAnnualMinCapacityInvestment") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalAnnualMinCapacityInvestment_specified else TotalAnnualMinCapacityInvestment_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}


#########			Activity Constraints		#########

# TotalTechnologyAnnualActivityUpperLimit
TotalTechnologyAnnualActivityUpperLimit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].VALUE.iat[0]
TotalTechnologyAnnualActivityUpperLimit_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].REGION, PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].YEAR)])
TotalTechnologyAnnualActivityUpperLimit = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalTechnologyAnnualActivityUpperLimit_specified else TotalTechnologyAnnualActivityUpperLimit_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalTechnologyAnnualActivityLowerLimit
TotalTechnologyAnnualActivityLowerLimit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].VALUE.iat[0]
TotalTechnologyAnnualActivityLowerLimit_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].REGION, PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].YEAR)])
TotalTechnologyAnnualActivityLowerLimit = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in TotalTechnologyAnnualActivityLowerLimit_specified else TotalTechnologyAnnualActivityLowerLimit_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# TotalTechnologyModelPeriodActivityUpperLimit
TotalTechnologyModelPeriodActivityUpperLimit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].VALUE.iat[0]
TotalTechnologyModelPeriodActivityUpperLimit_specified = tuple([(str(r), str(t)) for r, t in zip(PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].REGION, PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].TECHNOLOGY)])
TotalTechnologyModelPeriodActivityUpperLimit = {str(r): {str(t): PARAM_df[(PARAM_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in TotalTechnologyModelPeriodActivityUpperLimit_specified else TotalTechnologyModelPeriodActivityUpperLimit_default_value for t in TECHNOLOGY} for r in REGION}

# TotalTechnologyModelPeriodActivityLowerLimit
TotalTechnologyModelPeriodActivityLowerLimit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].VALUE.iat[0]
TotalTechnologyModelPeriodActivityLowerLimit_specified = tuple([(str(r), str(t)) for r, t in zip(PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].REGION, PARAM_df[PARAM_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].TECHNOLOGY)])
TotalTechnologyModelPeriodActivityLowerLimit = {str(r): {str(t): PARAM_df[(PARAM_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t)].VALUE.iat[0] if (str(r), str(t)) in TotalTechnologyModelPeriodActivityLowerLimit_specified else TotalTechnologyModelPeriodActivityLowerLimit_default_value for t in TECHNOLOGY} for r in REGION}


#########			Reserve Margin				#########

# ReserveMarginTagTechnology
ReserveMarginTagTechnology_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "ReserveMarginTagTechnology"].VALUE.iat[0]
ReserveMarginTagTechnology_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "ReserveMarginTagTechnology"].REGION, PARAM_df[PARAM_df['PARAM'] == "ReserveMarginTagTechnology"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "ReserveMarginTagTechnology"].YEAR)])
ReserveMarginTagTechnology = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "ReserveMarginTagTechnology") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in ReserveMarginTagTechnology_specified else ReserveMarginTagTechnology_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# ReserveMarginTagFuel
ReserveMarginTagFuel_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "ReserveMarginTagFuel"].VALUE.iat[0]
ReserveMarginTagFuel_specified = tuple([(str(r), str(f), str(y)) for r, f, y in zip(PARAM_df[PARAM_df['PARAM'] == "ReserveMarginTagFuel"].REGION, PARAM_df[PARAM_df['PARAM'] == "ReserveMarginTagFuel"].FUEL, PARAM_df[PARAM_df['PARAM'] == "ReserveMarginTagFuel"].YEAR)])
ReserveMarginTagFuel = {str(r): {str(f): {str(y): PARAM_df[(PARAM_df['PARAM'] == "ReserveMarginTagFuel") & (PARAM_df['REGION'] == r) & (PARAM_df['FUEL'] == f) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(f), str(y)) in ReserveMarginTagFuel_specified else ReserveMarginTagFuel_default_value for y in YEAR} for f in FUEL} for r in REGION}

# ReserveMargin
ReserveMargin_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "ReserveMargin"].VALUE.iat[0]
ReserveMargin_specified = tuple([(str(r), str(y)) for r, y in zip(PARAM_df[PARAM_df['PARAM'] == "ReserveMargin"].REGION, PARAM_df[PARAM_df['PARAM'] == "ReserveMargin"].YEAR)])
ReserveMargin = {str(r): {str(y): PARAM_df[(PARAM_df['PARAM'] == "ReserveMargin") & (PARAM_df['REGION'] == r) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(y)) in ReserveMargin_specified else ReserveMargin_default_value for y in YEAR} for r in REGION}


#########			RE Generation Target		#########

# RETagTechnology
RETagTechnology_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "RETagTechnology"].VALUE.iat[0]
RETagTechnology_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(PARAM_df[PARAM_df['PARAM'] == "RETagTechnology"].REGION, PARAM_df[PARAM_df['PARAM'] == "RETagTechnology"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "RETagTechnology"].YEAR)])
RETagTechnology = {str(r): {str(t): {str(y): PARAM_df[(PARAM_df['PARAM'] == "RETagTechnology") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(t), str(y)) in RETagTechnology_specified else RETagTechnology_default_value for y in YEAR} for t in TECHNOLOGY} for r in REGION}

# RETagFuel
RETagFuel_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "RETagFuel"].VALUE.iat[0]
RETagFuel_specified = tuple([(str(r), str(f), str(y)) for r, f, y in zip(PARAM_df[PARAM_df['PARAM'] == "RETagFuel"].REGION, PARAM_df[PARAM_df['PARAM'] == "RETagFuel"].FUEL, PARAM_df[PARAM_df['PARAM'] == "RETagFuel"].YEAR)])
RETagFuel = {str(r): {str(f): {str(y): PARAM_df[(PARAM_df['PARAM'] == "RETagFuel") & (PARAM_df['REGION'] == r) & (PARAM_df['FUEL'] == f) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(f), str(y)) in RETagFuel_specified else RETagFuel_default_value for y in YEAR} for f in FUEL} for r in REGION}

# REMinProductionTarget
REMinProductionTarget_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "REMinProductionTarget"].VALUE.iat[0]
REMinProductionTarget_specified = tuple([(str(r), str(y)) for r, y in zip(PARAM_df[PARAM_df['PARAM'] == "REMinProductionTarget"].REGION, PARAM_df[PARAM_df['PARAM'] == "REMinProductionTarget"].YEAR)])
REMinProductionTarget = {str(r): {str(y): PARAM_df[(PARAM_df['PARAM'] == "REMinProductionTarget") & (PARAM_df['REGION'] == r) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(y)) in REMinProductionTarget_specified else REMinProductionTarget_default_value for y in YEAR} for r in REGION}


#########			Emissions & Penalties		#########

# EmissionActivityRatio
EmissionActivityRatio_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "EmissionActivityRatio"].VALUE.iat[0]
EmissionActivityRatio_specified = tuple([(str(r),str(t),str(e),str(m),str(y)) for r, t, e, m, y in zip(PARAM_df[PARAM_df['PARAM'] == "EmissionActivityRatio"].REGION, PARAM_df[PARAM_df['PARAM'] == "EmissionActivityRatio"].TECHNOLOGY, PARAM_df[PARAM_df['PARAM'] == "EmissionActivityRatio"].EMISSION, PARAM_df[PARAM_df['PARAM'] == "EmissionActivityRatio"].MODE_OF_OPERATION, PARAM_df[PARAM_df['PARAM'] == "EmissionActivityRatio"].YEAR)])
EmissionActivityRatio = {str(r): {str(t): {str(e): {str(m): {str(y): PARAM_df[(PARAM_df['PARAM'] == "EmissionActivityRatio") & (PARAM_df['REGION'] == r) & (PARAM_df['TECHNOLOGY'] == t) & (PARAM_df['EMISSION'] == e) & (PARAM_df['MODE_OF_OPERATION'] == m) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r),str(t),str(e),str(m),str(y)) in EmissionActivityRatio_specified else EmissionActivityRatio_default_value for y in YEAR} for m in MODE_OF_OPERATION} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}

# EmissionsPenalty
EmissionsPenalty_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "EmissionsPenalty"].VALUE.iat[0]
EmissionsPenalty_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(PARAM_df[PARAM_df['PARAM'] == "EmissionsPenalty"].REGION, PARAM_df[PARAM_df['PARAM'] == "EmissionsPenalty"].EMISSION, PARAM_df[PARAM_df['PARAM'] == "EmissionsPenalty"].YEAR)])
EmissionsPenalty = {str(r): {str(e): {str(y): PARAM_df[(PARAM_df['PARAM'] == "EmissionsPenalty") & (PARAM_df['REGION'] == r) & (PARAM_df['EMISSION'] == e) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(e), str(y)) in EmissionsPenalty_specified else EmissionsPenalty_default_value for y in YEAR} for e in EMISSION} for r in REGION}

# AnnualExogenousEmission
AnnualExogenousEmission_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "AnnualExogenousEmission"].VALUE.iat[0]
AnnualExogenousEmission_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(PARAM_df[PARAM_df['PARAM'] == "AnnualExogenousEmission"].REGION, PARAM_df[PARAM_df['PARAM'] == "AnnualExogenousEmission"].EMISSION, PARAM_df[PARAM_df['PARAM'] == "AnnualExogenousEmission"].YEAR)])
AnnualExogenousEmission = {str(r): {str(e): {str(y): PARAM_df[(PARAM_df['PARAM'] == "AnnualExogenousEmission") & (PARAM_df['REGION'] == r) & (PARAM_df['EMISSION'] == e) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(e), str(y)) in AnnualExogenousEmission_specified else AnnualExogenousEmission_default_value for y in YEAR} for e in EMISSION} for r in REGION}

# AnnualEmissionLimit
AnnualEmissionLimit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "AnnualEmissionLimit"].VALUE.iat[0]
AnnualEmissionLimit_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(PARAM_df[PARAM_df['PARAM'] == "AnnualEmissionLimit"].REGION, PARAM_df[PARAM_df['PARAM'] == "AnnualEmissionLimit"].EMISSION, PARAM_df[PARAM_df['PARAM'] == "AnnualEmissionLimit"].YEAR)])
AnnualEmissionLimit = {str(r): {str(e): {str(y): PARAM_df[(PARAM_df['PARAM'] == "AnnualEmissionLimit") & (PARAM_df['REGION'] == r) & (PARAM_df['EMISSION'] == e) & (PARAM_df['YEAR'] == y)].VALUE.iat[0] if (str(r), str(e), str(y)) in AnnualEmissionLimit_specified else AnnualEmissionLimit_default_value for y in YEAR} for e in EMISSION} for r in REGION}

# ModelPeriodExogenousEmission
ModelPeriodExogenousEmission_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "ModelPeriodExogenousEmission"].VALUE.iat[0]
ModelPeriodExogenousEmission_specified = tuple([(str(r), str(e)) for r, e in zip(PARAM_df[PARAM_df['PARAM'] == "ModelPeriodExogenousEmission"].REGION, PARAM_df[PARAM_df['PARAM'] == "ModelPeriodExogenousEmission"].EMISSION)])
ModelPeriodExogenousEmission = {str(r): {str(e): PARAM_df[(PARAM_df['PARAM'] == "ModelPeriodExogenousEmission") & (PARAM_df['REGION'] == r) & (PARAM_df['EMISSION'] == e)].VALUE.iat[0] if (str(r), str(e)) in ModelPeriodExogenousEmission_specified else ModelPeriodExogenousEmission_default_value for e in EMISSION} for r in REGION}

# ModelPeriodEmissionLimit
ModelPeriodEmissionLimit_default_value = PARAM_DEFAULT_df[PARAM_DEFAULT_df['PARAM'] == "ModelPeriodEmissionLimit"].VALUE.iat[0]
ModelPeriodEmissionLimit_specified = tuple([(str(r), str(e)) for r, e in zip(PARAM_df[PARAM_df['PARAM'] == "ModelPeriodEmissionLimit"].REGION, PARAM_df[PARAM_df['PARAM'] == "ModelPeriodEmissionLimit"].EMISSION)])
ModelPeriodEmissionLimit = {str(r): {str(e): PARAM_df[(PARAM_df['PARAM'] == "ModelPeriodEmissionLimit") & (PARAM_df['REGION'] == r) & (PARAM_df['EMISSION'] == e)].VALUE.iat[0] if (str(r), str(e)) in ModelPeriodEmissionLimit_specified else ModelPeriodEmissionLimit_default_value for e in EMISSION} for r in REGION}

print("Parameters are created. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

i = 0
while i <= MCS_num:

	#########			Simulation loops     #########

	print("\nModel run: #", i, " -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

	##############################
	#    MODEL INITIALIZATION    #
	##############################
	
	model = pulp.LpProblem("Utopia model", pulp.LpMinimize)
	
	#########################
	#    MODEL VARIABLES    #
	#########################
	
	########			Demands 					#########
	
	RateOfDemand = {str(r): {str(l): {str(f): {str(y): pulp.LpVariable("RateOfDemand" + "_" + str(r) + "_" + str(l) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	Demand = {str(r): {str(l): {str(f): {str(y): pulp.LpVariable("Demand" + "_" + str(r) + "_" + str(l) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	
	########			Storage                 	#########
	
	RateOfStorageCharge = {str(r): {str(s): {str(ls): {str(ld): {str(lh): {str(y): pulp.LpVariable("RateOfStorageCharge" + "_" + str(r) + "_" + str(s) + "_" + str(ls) + "_" + str(ld) + "_" + str(lh) + "_" + str(y), cat='Continuous') for y in YEAR} for lh in DAILYTIMEBRACKET} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	RateOfStorageDischarge = {str(r): {str(s): {str(ls): {str(ld): {str(lh): {str(y): pulp.LpVariable("RateOfStorageDischarge" + "_" + str(r) + "_" + str(s) + "_" + str(ls) + "_" + str(ld) + "_" + str(lh) + "_" + str(y), cat='Continuous') for y in YEAR} for lh in DAILYTIMEBRACKET} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	NetChargeWithinYear = {str(r): {str(s): {str(ls): {str(ld): {str(lh): {str(y): pulp.LpVariable("NetChargeWithinYear" + "_" + str(r) + "_" + str(s) + "_" + str(ls) + "_" + str(ld) + "_" + str(lh) + "_" + str(y), cat='Continuous') for y in YEAR} for lh in DAILYTIMEBRACKET} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	NetChargeWithinDay = {str(r): {str(s): {str(ls): {str(ld): {str(lh): {str(y): pulp.LpVariable("NetChargeWithinDay" + "_" + str(r) + "_" + str(s) + "_" + str(ls) + "_" + str(ld) + "_" + str(lh) + "_" + str(y), cat='Continuous') for y in YEAR} for lh in DAILYTIMEBRACKET} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	StorageLevelYearStart = {str(r): {str(s): {str(y): pulp.LpVariable("StorageLevelYearStart" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	StorageLevelYearFinish = {str(r): {str(s): {str(y): pulp.LpVariable("StorageLevelYearFinish" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	StorageLevelSeasonStart = {str(r): {str(s): {str(ls): {str(y): pulp.LpVariable("StorageLevelSeasonStart" + "_" + str(r) + "_" + str(s) + "_" + str(ls) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for ls in SEASON} for s in STORAGE} for r in REGION}
	StorageLevelDayTypeStart = {str(r): {str(s): {str(ls): {str(ld): {str(y): pulp.LpVariable("StorageLevelDayTypeStart" + "_" + str(r) + "_" + str(s) + "_" + str(ls) + "_" + str(ld) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	StorageLevelDayTypeFinish = {str(r): {str(s): {str(ls): {str(ld): {str(y): pulp.LpVariable("StorageLevelDayTypeFinish" + "_" + str(r) + "_" + str(s) + "_" + str(ls) + "_" + str(ld) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for ld in DAYTYPE} for ls in SEASON} for s in STORAGE} for r in REGION}
	StorageLowerLimit = {str(r): {str(s): {str(y): pulp.LpVariable("StorageLowerLimit" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	StorageUpperLimit = {str(r): {str(s): {str(y): pulp.LpVariable("StorageUpperLimit" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	AccumulatedNewStorageCapacity = {str(r): {str(s): {str(y): pulp.LpVariable("AccumulatedNewStorageCapacity" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	NewStorageCapacity = {str(r): {str(s): {str(y): pulp.LpVariable("NewStorageCapacity" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	CapitalInvestmentStorage = {str(r): {str(s): {str(y): pulp.LpVariable("CapitalInvestmentStorage" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	DiscountedCapitalInvestmentStorage = {str(r): {str(s): {str(y): pulp.LpVariable("DiscountedCapitalInvestmentStorage" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	SalvageValueStorage = {str(r): {str(s): {str(y): pulp.LpVariable("SalvageValueStorage" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	DiscountedSalvageValueStorage = {str(r): {str(s): {str(y): pulp.LpVariable("DiscountedSalvageValueStorage" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	TotalDiscountedStorageCost = {str(r): {str(s): {str(y): pulp.LpVariable("TotalDiscountedStorageCost" + "_" + str(r) + "_" + str(s) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for s in STORAGE} for r in REGION}
	
	#########			Capacity Variables 			#########
	
	NumberOfNewTechnologyUnits = {str(r): {str(t): {str(y): pulp.LpVariable("NumberOfNewTechnologyUnits" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Integer') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	NewCapacity = {str(r): {str(t): {str(y): pulp.LpVariable("NewCapacity" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	AccumulatedNewCapacity = {str(r): {str(t): {str(y): pulp.LpVariable("AccumulatedNewCapacity" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	TotalCapacityAnnual = {str(r): {str(t): {str(y): pulp.LpVariable("TotalCapacityAnnual" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	
	#########			Activity Variables 			#########
	
	RateOfActivity = {str(r): {str(l): {str(t): {str(m): {str(y): pulp.LpVariable("RateOfActivity" + "_" + str(r) + "_" + str(l) + "_" + str(t) + "_" + str(m) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	RateOfTotalActivity = {str(r): {str(t): {str(l): {str(y): pulp.LpVariable("RateOfTotalActivity" + "_" + str(r) + "_" + str(t) + "_" + str(l) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for l in TIMESLICE} for t in TECHNOLOGY} for r in REGION}
	TotalTechnologyAnnualActivity = {str(r): {str(t): {str(y): pulp.LpVariable("TotalTechnologyAnnualActivity" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	TotalAnnualTechnologyActivityByMode = {str(r): {str(t): {str(m): {str(y): pulp.LpVariable("TotalAnnualTechnologyActivityByMode" + "_" + str(r) + "_" + str(t) + "_" + str(m) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for r in REGION}
	TotalTechnologyModelPeriodActivity = {str(r): {str(t): pulp.LpVariable("TotalTechnologyModelPeriodActivity" + "_" + str(r) + "_" + str(t), cat='Continuous') for t in TECHNOLOGY} for r in REGION}
	RateOfProductionByTechnologyByMode = {str(r): {str(l): {str(t): {str(m): {str(f): {str(y): pulp.LpVariable("RateOfProductionByTechnologyByMode" + "_" + str(r) + "_" + str(l) + "_" + str(t) + "_" + str(m) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	RateOfProductionByTechnology = {str(r): {str(l): {str(t): {str(f): {str(y): pulp.LpVariable("RateOfProductionByTechnology" + "_" + str(r) + "_" + str(l) + "_" + str(t) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	ProductionByTechnology = {str(r): {str(l): {str(t): {str(f): {str(y): pulp.LpVariable("ProductionByTechnology" + "_" + str(r) + "_" + str(l) + "_" + str(t) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	ProductionByTechnologyAnnual = {str(r): {str(t): {str(f): {str(y): pulp.LpVariable("ProductionByTechnologyAnnual" + "_" + str(r) + "_" + str(t) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for r in REGION}
	RateOfProduction = {str(r): {str(l): {str(f): {str(y): pulp.LpVariable("RateOfProduction" + "_" + str(r) + "_" + str(l) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	Production = {str(r): {str(l): {str(f): {str(y): pulp.LpVariable("Production" + "_" + str(r) + "_" + str(l) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	RateOfUseByTechnologyByMode = {str(r): {str(l): {str(t): {str(m): {str(f): {str(y): pulp.LpVariable("RateOfUseByTechnologyByMode" + "_" + str(r) + "_" + str(l) + "_" + str(t) + "_" + str(m) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	RateOfUseByTechnology = {str(r): {str(l): {str(t): {str(f): {str(y): pulp.LpVariable("RateOfUseByTechnology" + "_" + str(r) + "_" + str(l) + "_" + str(t) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	UseByTechnologyAnnual = {str(r): {str(t): {str(f): {str(y): pulp.LpVariable("UseByTechnologyAnnual" + "_" + str(r) + "_" + str(t) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for r in REGION}
	RateOfUse = {str(r): {str(l): {str(f): {str(y): pulp.LpVariable("RateOfUse" + "_" + str(r) + "_" + str(l) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	UseByTechnology = {str(r): {str(l): {str(t): {str(f): {str(y): pulp.LpVariable("UseByTechnology" + "_" + str(r) + "_" + str(l) + "_" + str(t) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for t in TECHNOLOGY} for l in TIMESLICE} for r in REGION}
	Use = {str(r): {str(l): {str(f): {str(y): pulp.LpVariable("Use" + "_" + str(r) + "_" + str(l) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for l in TIMESLICE} for r in REGION}
	Trade = {str(r): {str(rr): {str(l): {str(f): {str(y): pulp.LpVariable("Trade" + "_" + str(r) + "_" + str(rr) + "_" + str(l) + "_" + str(f) + "_" + str(y), cat='Continuous') for y in YEAR} for f in FUEL} for l in TIMESLICE} for rr in REGION2} for r in REGION}
	TradeAnnual = {str(r): {str(rr): {str(f): {str(y): pulp.LpVariable("TradeAnnual" + "_" + str(r) + "_" + str(rr) + "_" + str(f) + "_" + str(y), cat='Continuous') for y in YEAR} for f in FUEL} for rr in REGION2} for r in REGION}
	ProductionAnnual = {str(r): {str(f): {str(y): pulp.LpVariable("ProductionAnnual" + "_" + str(r) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for r in REGION}
	UseAnnual = {str(r): {str(f): {str(y): pulp.LpVariable("UseAnnual" + "_" + str(r) + "_" + str(f) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for f in FUEL} for r in REGION}
	
	#########			Costing Variables 			#########
	
	CapitalInvestment = {str(r): {str(t): {str(y): pulp.LpVariable("CapitalInvestment" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	DiscountedCapitalInvestment = {str(r): {str(t): {str(y): pulp.LpVariable("DiscountedCapitalInvestment" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	SalvageValue = {str(r): {str(t): {str(y): pulp.LpVariable("SalvageValue" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	DiscountedSalvageValue = {str(r): {str(t): {str(y): pulp.LpVariable("DiscountedSalvageValue" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	OperatingCost = {str(r): {str(t): {str(y): pulp.LpVariable("OperatingCost" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	DiscountedOperatingCost = {str(r): {str(t): {str(y): pulp.LpVariable("DiscountedOperatingCost" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	AnnualVariableOperatingCost = {str(r): {str(t): {str(y): pulp.LpVariable("AnnualVariableOperatingCost" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	AnnualFixedOperatingCost = {str(r): {str(t): {str(y): pulp.LpVariable("AnnualFixedOperatingCost" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	TotalDiscountedCostByTechnology = {str(r): {str(t): {str(y): pulp.LpVariable("TotalDiscountedCostByTechnology" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	TotalDiscountedCost = {str(r): {str(y): pulp.LpVariable("TotalDiscountedCost" + "_" + str(r) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for r in REGION}
	ModelPeriodCostByRegion = {str(r): pulp.LpVariable("ModelPeriodCostByRegion" + "_" + str(r), lowBound=0, cat='Continuous') for r in REGION}
	
	#########			Reserve Margin				#########
	
	TotalCapacityInReserveMargin = {str(r): {str(y): pulp.LpVariable("TotalCapacityInReserveMargin" + "_" + str(r) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for r in REGION}
	DemandNeedingReserveMargin = {str(r): {str(l): {str(y): pulp.LpVariable("DemandNeedingReserveMargin" + "_" + str(r) + "_" + str(l) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for l in TIMESLICE} for r in REGION}
	
	#########			RE Gen Target				#########
	
	TotalREProductionAnnual = {str(r): {str(y): pulp.LpVariable("TotalREProductionAnnual" + "_" + str(r) + "_" + str(y), cat='Continuous') for y in YEAR} for r in REGION}
	RETotalProductionOfTargetFuelAnnual = {str(r): {str(y): pulp.LpVariable("RETotalProductionOfTargetFuelAnnual" + "_" + str(r) + "_" + str(y), cat='Continuous') for y in YEAR} for r in REGION}
	
	#########			Emissions					#########
	
	AnnualTechnologyEmissionByMode = {str(r): {str(t): {str(e): {str(m): {str(y): pulp.LpVariable("AnnualTechnologyEmissionByMode" + "_" + str(r) + "_" + str(t) + "_" + str(e) + "_" + str(m) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for m in MODE_OF_OPERATION} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}
	AnnualTechnologyEmission = {str(r): {str(t): {str(e): {str(y): pulp.LpVariable("AnnualTechnologyEmission" + "_" + str(r) + "_" + str(t) + "_" + str(e) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}
	AnnualTechnologyEmissionPenaltyByEmission = {str(r): {str(t): {str(e): {str(y): pulp.LpVariable("AnnualTechnologyEmissionPenaltyByEmission" + "_" + str(r) + "_" + str(t) + "_" + str(e) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}
	AnnualTechnologyEmissionsPenalty = {str(r): {str(t): {str(y): pulp.LpVariable("AnnualTechnologyEmissionsPenalty" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	DiscountedTechnologyEmissionsPenalty = {str(r): {str(t): {str(y): pulp.LpVariable("DiscountedTechnologyEmissionsPenalty" + "_" + str(r) + "_" + str(t) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	AnnualEmissions = {str(r): {str(e): {str(y): pulp.LpVariable("AnnualEmissions" + "_" + str(r) + "_" + str(e) + "_" + str(y), lowBound=0, cat='Continuous') for y in YEAR} for e in EMISSION} for r in REGION}
	ModelPeriodEmissions = {str(r): {str(e): pulp.LpVariable("ModelPeriodEmissions" + "_" + str(r) + "_" + str(e), lowBound=0, cat='Continuous') for e in EMISSION} for r in REGION}
	
	print("Variables are created. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	
	############################
	#    OBJECTIVE FUNCTION    #
	############################
	
	cost = pulp.LpVariable("cost", cat='Continuous')  # objective
	
	model += cost, "Objective"
	model += cost == pulp.lpSum([TotalDiscountedCost[r][y] for r in REGION for y in YEAR]), "Cost_function"
	
	#####################
	#    CONSTRAINTS    #
	#####################
	
	for r in REGION:
		for l in TIMESLICE:
			for f in FUEL:
				for y in YEAR:
					model += RateOfDemand[r][l][f][y] == SpecifiedAnnualDemand[r][f][y] * SpecifiedDemandProfile[r][f][l][y] / YearSplit[l][y], "EQ_SpecifiedDemand"+"_%s"%r+"_%s"%l+"_%s"%f+"_%s"%y
	
	#########			Capacity Adequacy A	     	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				model += AccumulatedNewCapacity[r][t][y] == pulp.lpSum([NewCapacity[r][t][yy] for yy in YEAR if (int(y) - int(yy) < OperationalLife[r][t]) and (int(y) - int(yy) >= 0)]), "CAa1_TotalNewCapacity"+"_%s"%r+"_%s"%t+"_%s"%y
				model += TotalCapacityAnnual[r][t][y] == AccumulatedNewCapacity[r][t][y] + ResidualCapacity[r][t][y], "CAa2_TotalAnnualCapacity"+"_%s"%r+"_%s"%t+"_%s"%y
	
				for l in TIMESLICE:
					model += RateOfTotalActivity[r][t][l][y] == pulp.lpSum([RateOfActivity[r][l][t][m][y] for m in MODE_OF_OPERATION]), "CAa3_TotalActivityOfEachTechnology"+"_%s"%r+"_%s"%t+"_%s"%l+"_%s"%y
					model += RateOfTotalActivity[r][t][l][y] <= TotalCapacityAnnual[r][t][y] * CapacityFactor[r][t][l][y] * CapacityToActivityUnit[r][t], "CAa4_Constraint_Capacity"+"_%s"%r+"_%s"%t+"_%s"%l+"_%s"%y
	
				if CapacityOfOneTechnologyUnit[r][t][y] != 0:
					model += NewCapacity[r][t][y] == CapacityOfOneTechnologyUnit[r][t][y] * NumberOfNewTechnologyUnits[r][t][y], "CAa5_TotalNewCapacity"+"_%s"%r+"_%s"%t+"_%s"%y
	
	#########			Capacity Adequacy B		 	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				model += pulp.lpSum([RateOfTotalActivity[r][t][l][y] * YearSplit[l][y] for l in TIMESLICE]) <= pulp.lpSum([TotalCapacityAnnual[r][t][y] * CapacityFactor[r][t][l][y] * YearSplit[l][y] for l in TIMESLICE]) * AvailabilityFactor[r][t][y] * CapacityToActivityUnit[r][t], "CAb1_PlannedMaintenance"+"_%s"%r+"_%s"%t+"_%s"%y
	
	#########			Energy Balance A    	 	#########
	
	for r in REGION:
		for l in TIMESLICE:
			for f in FUEL:
				for y in YEAR:
					for t in TECHNOLOGY:
						for m in MODE_OF_OPERATION:
	
							if OutputActivityRatio[r][t][f][m][y] != 0:
								model += RateOfProductionByTechnologyByMode[r][l][t][m][f][y] == RateOfActivity[r][l][t][m][y] * OutputActivityRatio[r][t][f][m][y], "EBa1_RateOfFuelProduction1"+"_%s"%r+"_%s"%l+"_%s"%t+"_%s"%m+"_%s"%f+"_%s"%y
							else:
								model += RateOfProductionByTechnologyByMode[r][l][t][m][f][y] == 0, "EBa1_RateOfFuelProduction1" + "_%s" % r + "_%s" % l + "_%s" % t + "_%s" % m + "_%s" % f + "_%s" % y
	
						model += RateOfProductionByTechnology[r][l][t][f][y] == pulp.lpSum([RateOfProductionByTechnologyByMode[r][l][t][m][f][y] for m in MODE_OF_OPERATION if OutputActivityRatio[r][t][f][m][y] != 0]), "EBa2_RateOfFuelProduction2"+"_%s"%r+"_%s"%l+"_%s"%t+"_%s"%f+"_%s"%y
	
					model += RateOfProduction[r][l][f][y] == pulp.lpSum([RateOfProductionByTechnology[r][l][t][f][y] for t in TECHNOLOGY]), "EBa3_RateOfFuelProduction3"+"_%s"%r+"_%s"%l+"_%s"%f+"_%s"%y
	
					for t in TECHNOLOGY:
						for m in MODE_OF_OPERATION:
	
							if InputActivityRatio[r][t][f][m][y] != 0:
								model += RateOfUseByTechnologyByMode[r][l][t][m][f][y] == RateOfActivity[r][l][t][m][y] * InputActivityRatio[r][t][f][m][y], "EBa4_RateOfFuelUse1"+"_%s"%r+"_%s"%l+"_%s"%t+"_%s"%m+"_%s"%f+"_%s"%y
	
						model += RateOfUseByTechnology[r][l][t][f][y] == pulp.lpSum([RateOfUseByTechnologyByMode[r][l][t][m][f][y] for m in MODE_OF_OPERATION if InputActivityRatio[r][t][f][m][y] != 0]), "EBa5_RateOfFuelUse2"+"_%s"%r+"_%s"%l+"_%s"%t+"_%s"%f+"_%s"%y
	
					model += RateOfUse[r][l][f][y] == pulp.lpSum([RateOfUseByTechnology[r][l][t][f][y] for t in TECHNOLOGY]), "EBa6_RateOfFuelUse3"+"_%s"%r+"_%s"%l+"_%s"%f+"_%s"%y
					model += Production[r][l][f][y] == RateOfProduction[r][l][f][y] * YearSplit[l][y], "EBa7_EnergyBalanceEachTS1"+"_%s"%r+"_%s"%l+"_%s"%f+"_%s"%y
					model += Use[r][l][f][y] == RateOfUse[r][l][f][y] * YearSplit[l][y], "EBa8_EnergyBalanceEachTS2"+"_%s"%r+"_%s"%l+"_%s"%f+"_%s"%y
					model += Demand[r][l][f][y] == RateOfDemand[r][l][f][y] * YearSplit[l][y], "EBa9_EnergyBalanceEachTS3"+"_%s"%r+"_%s"%l+"_%s"%f+"_%s"%y
	
					for rr in REGION2:
						model += Trade[r][rr][l][f][y] == -Trade[rr][r][l][f][y], "EBa10_EnergyBalanceEachTS4"+"_%s"%r+"_%s"%rr+"_%s"%l+"_%s"%f+"_%s"%y
	
					model += Production[r][l][f][y] >= Demand[r][l][f][y] + Use[r][l][f][y] + pulp.lpSum([Trade[r][rr][l][f][y] * TradeRoute[r][rr][f][y] for rr in REGION2]), "EBa11_EnergyBalanceEachTS5"+"_%s"%r+"_%s"%l+"_%s"%f+"_%s"%y
	
	#########        	Energy Balance B		 	#########
	
	for r in REGION:
		for f in FUEL:
			for y in YEAR:
				model += ProductionAnnual[r][f][y] == pulp.lpSum([Production[r][l][f][y] for l in TIMESLICE]), "EBb1_EnergyBalanceEachYear1"+"_%s"%r+"_%s"%f+"_%s"%y
				model += UseAnnual[r][f][y] == pulp.lpSum([Use[r][l][f][y] for l in TIMESLICE]), "EBb2_EnergyBalanceEachYear2"+"_%s"%r+"_%s"%f+"_%s"%y
	
				for rr in REGION2:
					model += TradeAnnual[r][rr][f][y] == pulp.lpSum([Trade[r][rr][l][f][y] for l in TIMESLICE]), "EBb3_EnergyBalanceEachYear3"+"_%s"%r+"_%s"%rr+"_%s"%f+"_%s"%y
	
				model += ProductionAnnual[r][f][y] >= UseAnnual[r][f][y] + pulp.lpSum([TradeAnnual[r][rr][f][y] * TradeRoute[r][rr][f][y] for rr in REGION2]) + AccumulatedAnnualDemand[r][f][y], "EBb4_EnergyBalanceEachYear4"+"_%s"%r+"_%s"%f+"_%s"%y
	
	#########			Accounting Technology Production/Use	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				for l in TIMESLICE:
					for f in FUEL:
						model += ProductionByTechnology[r][l][t][f][y] == RateOfProductionByTechnology[r][l][t][f][y] * YearSplit[l][y], "Acc1_FuelProductionByTechnology"+"_%s"%r+"_%s"%l+"_%s"%t+"_%s"%f+"_%s"%y
						model += UseByTechnology[r][l][t][f][y] == RateOfUseByTechnology[r][l][t][f][y] * YearSplit[l][y], "Acc2_FuelUseByTechnology"+"_%s"%r+"_%s"%l+"_%s"%t+"_%s"%f+"_%s"%y
	
				for m in MODE_OF_OPERATION:
					model += TotalAnnualTechnologyActivityByMode[r][t][m][y] == pulp.lpSum([RateOfActivity[r][l][t][m][y] * YearSplit[l][y] for l in TIMESLICE]), "Acc3_AverageAnnualRateOfActivity"+"_%s"%r+"_%s"%t+"_%s"%m+"_%s"%y
	
		model += ModelPeriodCostByRegion[r] == pulp.lpSum([TotalDiscountedCost[r][y] for y in YEAR]), "Acc4_ModelPeriodCostByRegion"+"_%s"%r
	
	#########			Storage Equations			#########
	
	for r in REGION:
		for s in STORAGE:
			for y in YEAR:
				for ls in SEASON:
					for ld in DAYTYPE:
						for lh in DAILYTIMEBRACKET:
							model += RateOfStorageCharge[r][s][ls][ld][lh][y] == pulp.lpSum([RateOfActivity[r][l][t][m][y] * TechnologyToStorage[r][t][s][m] * Conversionls[l][ls] * Conversionld[l][ld] * Conversionlh[l][lh] for t in TECHNOLOGY for m in MODE_OF_OPERATION for l in TIMESLICE if TechnologyToStorage[r][t][s][m] > 0]), "S1_RateOfStorageCharge"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
							model += RateOfStorageDischarge[r][s][ls][ld][lh][y] == pulp.lpSum([RateOfActivity[r][l][t][m][y] * TechnologyFromStorage[r][t][s][m] * Conversionls[l][ls] * Conversionld[l][ld] * Conversionlh[l][lh] for t in TECHNOLOGY for m in MODE_OF_OPERATION for l in TIMESLICE if TechnologyFromStorage[r][t][s][m] > 0]), "S2_RateOfStorageDischarge"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
							model += NetChargeWithinYear[r][s][ls][ld][lh][y] == pulp.lpSum([(RateOfStorageCharge[r][s][ls][ld][lh][y] - RateOfStorageDischarge[r][s][ls][ld][lh][y]) * YearSplit[l][y] * Conversionls[l][ls] * Conversionld[l][ld] * Conversionlh[l][lh] for l in TIMESLICE if (Conversionls[l][ls] > 0) and (Conversionld[l][ld] > 0) and (Conversionlh[l][lh] > 0)]), "S3_NetChargeWithinYear"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
							model += NetChargeWithinDay[r][s][ls][ld][lh][y] == (RateOfStorageCharge[r][s][ls][ld][lh][y] - RateOfStorageDischarge[r][s][ls][ld][lh][y]) * DaySplit[lh][y], "S4_NetChargeWithinDay"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
	
				if int(y) == min([int(yy) for yy in YEAR]):
					model += StorageLevelYearStart[r][s][y] == StorageLevelStart[r][s], "S5_and_S6_StorageLevelYearStart"+"_%s"%r+"_%s"%s+"_%s"%y
				else:
					model += StorageLevelYearStart[r][s][y] == StorageLevelYearStart[r][s][str(int(y)-1)] + pulp.lpSum([NetChargeWithinYear[r][s][ls][ld][lh][str(int(y)-1)] for ls in SEASON for ld in DAYTYPE for lh in DAILYTIMEBRACKET]), "S5_and_S6_StorageLevelYearStart"+"_%s"%r+"_%s"%s+"_%s"%y
	
				if int(y) < max([int(yy) for yy in YEAR]):
					model += StorageLevelYearFinish[r][s][y] == StorageLevelYearStart[r][s][str(int(y) + 1)], "S7_and_S8_StorageLevelYearFinish"+"_%s"%r+"_%s"%s+"_%s"%y
				else:
					model += StorageLevelYearFinish[r][s][y] == StorageLevelYearStart[r][s][y] + pulp.lpSum([NetChargeWithinYear[r][s][ls][ld][lh][y] for ls in SEASON for ld in DAYTYPE for lh in DAILYTIMEBRACKET]), "S7_and_S8_StorageLevelYearFinish"+"_%s"%r+"_%s"%s+"_%s"%y
	
				for ls in SEASON:
	
					if int(ls) == min([int(lsls) for lsls in SEASON]):
						model += StorageLevelSeasonStart[r][s][ls][y] == StorageLevelYearStart[r][s][y], "S9_and_S10_StorageLevelSeasonStart"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%y
					else:
						model += StorageLevelSeasonStart[r][s][ls][y] == StorageLevelSeasonStart[r][s][str(int(ls)-1)][y] + pulp.lpSum([NetChargeWithinYear[r][s][str(int(ls)-1)][ld][lh][y] for ld in DAYTYPE for lh in DAILYTIMEBRACKET]), "S9_and_S10_StorageLevelSeasonStart"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%y
	
					for ld in DAYTYPE:
						if int(ld) == min([int(ldld) for ldld in DAYTYPE]):
							model += StorageLevelDayTypeStart[r][s][ls][ld][y] == StorageLevelSeasonStart[r][s][ls][y], "S11_and_S12_StorageLevelDayTypeStart"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%y
						else:
							model += StorageLevelDayTypeStart[r][s][ls][ld][y] == StorageLevelDayTypeStart[r][s][ls][str(int(ld)-1)][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][str(int(ld)-1)][y] * DaysInDayType[ls][ld][str(int(ld)-1)] for lh in DAILYTIMEBRACKET]), "S11_and_S12_StorageLevelDayTypeStart"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%y
	
						if (int(ld) == max([int(ldld) for ldld in DAYTYPE])) and (int(ls) == max([int(lsls) for lsls in SEASON])):
							model += StorageLevelDayTypeFinish[r][s][ls][ld][y] == StorageLevelYearFinish[r][s][y], "S13_and_S14_and_S15_StorageLevelDayTypeFinish"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%y
						elif int(ld) == max([int(ldld) for ldld in DAYTYPE]):
							model += StorageLevelDayTypeFinish[r][s][ls][ld][y] == StorageLevelSeasonStart[r][s][str(int(ls)+1)][y], "S13_and_S14_and_S15_StorageLevelDayTypeFinish"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%y
						else:
							model += StorageLevelDayTypeFinish[r][s][ls][ld][y] == StorageLevelDayTypeFinish[r][s][ls][str(int(ld)+1)][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][str(int(ld)+1)][lh][y] * DaysInDayType[ls][str(int(ld)+1)][y] for lh in DAILYTIMEBRACKET]), "S13_and_S14_and_S15_StorageLevelDayTypeFinish"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%y
	
	##########			Storage Constraints			#########
	
	for r in REGION:
		for s in STORAGE:
			for y in YEAR:
				for ls in SEASON:
					for ld in DAYTYPE:
						for lh in DAILYTIMEBRACKET:
							model += (StorageLevelDayTypeStart[r][s][ls][ld][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh)-int(lhlh) > 0])) - StorageLowerLimit[r][s][y] >= 0, "SC1_LowerLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInFirstWeekConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
							model += (StorageLevelDayTypeStart[r][s][ls][ld][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh)-int(lhlh) > 0])) - StorageUpperLimit[r][s][y] <= 0, "SC1_UpperLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInFirstWeekConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
	
							if int(ld) > min([int(ldld) for ldld in DAYTYPE]):
								model += (StorageLevelDayTypeStart[r][s][ls][ld][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][str(int(ld)-1)][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh)-int(lhlh) < 0])) - StorageLowerLimit[r][s][y] >= 0, "SC2_LowerLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInFirstWeekConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
	
							if int(ld) > min([int(ldld) for ldld in DAYTYPE]):
								model += (StorageLevelDayTypeStart[r][s][ls][ld][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][str(int(ld)-1)][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) < 0])) - StorageUpperLimit[r][s][y] <= 0, "SC2_LowerLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInFirstWeekConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
	
							model += (StorageLevelDayTypeFinish[r][s][ls][ld][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) < 0])) - StorageLowerLimit[r][s][y] >= 0, "SC3_LowerLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInLastWeekConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
							model += (StorageLevelDayTypeFinish[r][s][ls][ld][y] - pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) < 0])) - StorageUpperLimit[r][s][y] <= 0, "SC3_UpperLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInLastWeekConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
	
							if int(ld) > min([int(ldld) for ldld in DAYTYPE]):
								model += (StorageLevelDayTypeFinish[r][s][ls][str(int(ld)-1)][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) > 0])) - StorageLowerLimit[r][s][y] >= 0, "SC4_LowerLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInLastWeekConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
	
							if int(ld) > min([int(ldld) for ldld in DAYTYPE]):
								model += (StorageLevelDayTypeFinish[r][s][ls][str(int(ld)-1)][y] + pulp.lpSum([NetChargeWithinDay[r][s][ls][ld][lhlh][y] for lhlh in DAILYTIMEBRACKET if int(lh) - int(lhlh) > 0])) - StorageUpperLimit[r][s][y] <= 0, "SC4_UpperLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInLastWeekConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
	
							model += RateOfStorageCharge[r][s][ls][ld][lh][y] <= StorageMaxChargeRate[r][s], "SC5_MaxChargeConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
							model += RateOfStorageDischarge[r][s][ls][ld][lh][y] <= StorageMaxDischargeRate[r][s], "SC6_MaxDischargeConstraint"+"_%s"%r+"_%s"%s+"_%s"%ls+"_%s"%ld+"_%s"%lh+"_%s"%y
	
	#########			Storage Investments			#########
	
	for r in REGION:
		for s in STORAGE:
			for y in YEAR:
				model += StorageUpperLimit[r][s][y] == AccumulatedNewStorageCapacity[r][s][y] + ResidualStorageCapacity[r][s][y], "SI1_StorageUpperLimit"+"_%s"%r+"_%s"%s+"_%s"%y
				model += StorageLowerLimit[r][s][y] == MinStorageCharge[r][s][y] * StorageUpperLimit[r][s][y], "SI2_StorageLowerLimit"+"_%s"%r+"_%s"%s+"_%s"%y
				model += AccumulatedNewStorageCapacity[r][s][y] == pulp.lpSum([NewStorageCapacity[r][s][yy] for yy in YEAR if (int(y) - int(yy) < OperationalLifeStorage[r][s]) and (int(y)-int(yy) >= 0)]), "SI3_TotalNewStorage"+"_%s"%r+"_%s"%s+"_%s"%y
				model += CapitalInvestmentStorage[r][s][y] == CapitalCostStorage[r][s][y] * NewStorageCapacity[r][s][y], "SI4_UndiscountedCapitalInvestmentStorage"+"_%s"%r+"_%s"%s+"_%s"%y
				model += DiscountedCapitalInvestmentStorage[r][s][y] == CapitalInvestmentStorage[r][s][y] * (1/ ((1+DiscountRate[r])**(int(y) - min([int(yy) for yy in YEAR])))), "SI5_DiscountingCapitalInvestmentStorage"+"_%s"%r+"_%s"%s+"_%s"%y
	
				if int(y) + OperationalLifeStorage[r][s] - 1 <= max([int(yy) for yy in YEAR]):
					model += SalvageValueStorage[r][s][y] == 0, "SI6_SalvageValueStorageAtEndOfPeriod1"+"_%s"%r+"_%s"%s+"_%s"%y
	
				if ((DepreciationMethod[r] == 1) and (int(y)+OperationalLifeStorage[r][s]-1 > max([int(yy) for yy in YEAR])) and (DiscountRate[r] == 0)) or ((DepreciationMethod[r] == 2) and (int(y)+OperationalLifeStorage[r][s]-1 > max([int(yy) for yy in YEAR]))):
					model += SalvageValueStorage[r][s][y] == CapitalInvestmentStorage[r][s][y] * (1-(max([int(yy) for yy in YEAR])-int(y)+1))/OperationalLifeStorage[r][s], "SI7_SalvageValueStorageAtEndOfPeriod2" + "_%s" % r + "_%s" % s + "_%s" % y
	
				if (DepreciationMethod[r] == 1) and (int(y)+OperationalLifeStorage[r][s]-1 > max([int(yy) for yy in YEAR])) and (DiscountRate[r] > 0):
					model += SalvageValueStorage[r][s][y] == CapitalInvestmentStorage[r][s][y] * (1-(((1+DiscountRate[r])**(max([int(yy) for yy in YEAR]) - int(y)+1)-1)/((1+DiscountRate[r])**OperationalLifeStorage[r][s]-1))), "SI8_SalvageValueStorageAtEndOfPeriod3" + "_%s" % r + "_%s" % s + "_%s" % y
	
				model += DiscountedSalvageValueStorage[r][s][y] == SalvageValueStorage[r][s][y] * (1 /((1+DiscountRate[r])**(max([int(yy) for yy in YEAR])-min([int(yy) for yy in YEAR])+1))), "SI9_SalvageValueStorageDiscountedToStartYear" + "_%s" % r + "_%s" % s + "_%s" % y
				model += TotalDiscountedStorageCost[r][s][y] == DiscountedCapitalInvestmentStorage[r][s][y]-DiscountedSalvageValueStorage[r][s][y], "SI10_TotalDiscountedCostByStorage" + "_%s" % r + "_%s" % s + "_%s" % y
	
	#########			Capital Costs 		     	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				model += CapitalInvestment[r][t][y] == CapitalCost[r][t][y] * NewCapacity[r][t][y],  "CC1_UndiscountedCapitalInvestment"+"_%s"%r+"_%s"%t+"_%s"%y
				model += DiscountedCapitalInvestment[r][t][y] == CapitalInvestment[r][t][y] * (1/((1 + DiscountRate[r]) ** (int(y) - min([int(yy) for yy in YEAR])))), "CC2_DiscountingCapitalInvestment"+"_%s"%r+"_%s"%t+"_%s"%y
	
	#########           Salvage Value            	#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
	
				if (DepreciationMethod[r] == 1) and (int(y) + OperationalLife[r][t] - 1 > max([int(yy) for yy in YEAR])) and (DiscountRate[r] > 0):
					model += SalvageValue[r][t][y] == CapitalCost[r][t][y] * NewCapacity[r][t][y] * (1 - (((1 + DiscountRate[r]) ** (max([int(yy) for yy in YEAR]) - int(y) + 1) - 1) / ((1 + DiscountRate[r]) ** OperationalLife[r][t] - 1))), "SV1_SalvageValueAtEndOfPeriod1"+"_%s"%r+"_%s"%t+"_%s"%y
	
				if ((DepreciationMethod[r] == 1) and (int(y) + OperationalLife[r][t] - 1 > max([int(yy) for yy in YEAR])) and (DiscountRate[r] == 0)) or ((DepreciationMethod[r] == 2) and (int(y) + OperationalLife[r][t] - 1 > max([int(yy) for yy in YEAR]))):
					model += SalvageValue[r][t][y] == CapitalCost[r][t][y] * NewCapacity[r][t][y] * (1 - (max([int(yy) for yy in YEAR]) - int(y) + 1) / OperationalLife[r][t]), "SV2_SalvageValueAtEndOfPeriod2"+"_%s"%r+"_%s"%t+"_%s"%y
	
				if int(y) + OperationalLife[r][t] - 1 <= max([int(yy) for yy in YEAR]):
					model += SalvageValue[r][t][y] == 0, "SV3_SalvageValueAtEndOfPeriod3"+"_%s"%r+"_%s"%t+"_%s"%y
	
				model += DiscountedSalvageValue[r][t][y] == SalvageValue[r][t][y] * (1 / ((1 + DiscountRate[r]) ** (1 + max([int(yy) for yy in YEAR]) - min([int(yy) for yy in YEAR])))), "SV4_SalvageValueDiscountedToStartYear"+"_%s"%r+"_%s"%t+"_%s"%y
	
	#########        	Operating Costs 		 	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				model += AnnualVariableOperatingCost[r][t][y] == pulp.lpSum([TotalAnnualTechnologyActivityByMode[r][t][m][y] * VariableCost[r][t][m][y] for m in MODE_OF_OPERATION]), "OC1_OperatingCostsVariable"+"_%s"%r+"_%s"%t+"_%s"%y
				model += AnnualFixedOperatingCost[r][t][y] == TotalCapacityAnnual[r][t][y] * FixedCost[r][t][y], "OC2_OperatingCostsFixedAnnual"+"_%s"%r+"_%s"%t+"_%s"%y
				model += OperatingCost[r][t][y] == AnnualFixedOperatingCost[r][t][y] + AnnualVariableOperatingCost[r][t][y], "OC3_OperatingCostsTotalAnnual"+"_%s"%r+"_%s"%t+"_%s"%y
				model += DiscountedOperatingCost[r][t][y] == OperatingCost[r][t][y] * (1 /((1 + DiscountRate[r]) ** (int(y) - min([int(yy) for yy in YEAR]) + 0.5))), "OC4_DiscountedOperatingCostsTotalAnnual"+"_%s"%r+"_%s"%t+"_%s"%y
	
	#########       	Total Discounted Costs	 	#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				model += TotalDiscountedCostByTechnology[r][t][y] == DiscountedOperatingCost[r][t][y] + DiscountedCapitalInvestment[r][t][y] + DiscountedTechnologyEmissionsPenalty[r][t][y] - DiscountedSalvageValue[r][t][y], "TDC1_TotalDiscountedCostByTechnology"+"_%s"%r+"_%s"%t+"_%s"%y
	
			model += TotalDiscountedCost[r][y] == pulp.lpSum([TotalDiscountedCostByTechnology[r][t][y] for t in TECHNOLOGY]) + pulp.lpSum([TotalDiscountedStorageCost[r][s][y] for s in STORAGE]), "TDC2_TotalDiscountedCost"+"_%s"%r+"_%s"%y
	
	#########      		Total Capacity Constraints 	#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				model += TotalCapacityAnnual[r][t][y] <= TotalAnnualMaxCapacity[r][t][y], "TCC1_TotalAnnualMaxCapacityConstraint"+"_%s"%r+"_%s"%t+"_%s"%y
	
				if TotalAnnualMinCapacity[r][t][y] > 0:
					model += TotalCapacityAnnual[r][t][y] >= TotalAnnualMinCapacity[r][t][y], "TCC2_TotalAnnualMinCapacityConstraint"+"_%s"%r+"_%s"%t+"_%s"%y
	
	#########    		New Capacity Constraints  	#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				model += NewCapacity[r][t][y] <= TotalAnnualMaxCapacityInvestment[r][t][y], "NCC1_TotalAnnualMaxNewCapacityConstraint"+"_%s"%r+"_%s"%t+"_%s"%y
	
				if TotalAnnualMinCapacityInvestment[r][t][y] > 0:
					model += NewCapacity[r][t][y] >= TotalAnnualMinCapacityInvestment[r][t][y], "NCC2_TotalAnnualMinNewCapacityConstraint"+"_%s"%r+"_%s"%t+"_%s"%y
	
	#########   		Annual Activity Constraints	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			for y in YEAR:
				model += TotalTechnologyAnnualActivity[r][t][y] == pulp.lpSum([RateOfTotalActivity[r][t][l][y] * YearSplit[l][y] for l in TIMESLICE]), "AAC1_TotalAnnualTechnologyActivity"+"_%s"%r+"_%s"%t+"_%s"%y
				model += TotalTechnologyAnnualActivity[r][t][y] <= TotalTechnologyAnnualActivityUpperLimit[r][t][y], "AAC2_TotalAnnualTechnologyActivityUpperLimit"+"_%s"%r+"_%s"%t+"_%s"%y
	
				if TotalTechnologyAnnualActivityLowerLimit[r][t][y] > 0:
					model += TotalTechnologyAnnualActivity[r][t][y] >= TotalTechnologyAnnualActivityLowerLimit[r][t][y], "AAC3_TotalAnnualTechnologyActivityLowerLimit"+"_%s"%r+"_%s"%t+"_%s"%y
	
	#########    		Total Activity Constraints 	#########
	
	for r in REGION:
		for t in TECHNOLOGY:
			model += TotalTechnologyModelPeriodActivity[r][t] == pulp.lpSum([TotalTechnologyAnnualActivity[r][t][y] for y in YEAR]), "TAC1_TotalModelHorizonTechnologyActivity"+"_%s"%r+"_%s"%t
	
			if TotalTechnologyModelPeriodActivityUpperLimit[r][t] > 0:
				model += TotalTechnologyModelPeriodActivity[r][t] <= TotalTechnologyModelPeriodActivityUpperLimit, "TAC2_TotalModelHorizonTechnologyActivityUpperLimit"+"_%s"%r+"_%s"%t
	
			if TotalTechnologyModelPeriodActivityLowerLimit[r][t] > 0:
				model += TotalTechnologyModelPeriodActivity[r][t] >= TotalTechnologyModelPeriodActivityLowerLimit, "TAC3_TotalModelHorizenTechnologyActivityLowerLimit"+"_%s"%r+"_%s"%t
	
	#########   		Reserve Margin Constraint	#########
	
	for r in REGION:
		for y in YEAR:
			model += TotalCapacityInReserveMargin[r][y] == pulp.lpSum([TotalCapacityAnnual[r][t][y] * ReserveMarginTagTechnology[r][t][y] * CapacityToActivityUnit[r][t] for t in TECHNOLOGY]), "RM1_ReserveMargin_TechnologiesIncluded_In_Activity_Units" + "_%s" % r + "_%s" % y
	
			for l in TIMESLICE:
				model += DemandNeedingReserveMargin[r][l][y] == pulp.lpSum([RateOfProduction[r][l][f][y] * ReserveMarginTagFuel[r][f][y] for f in FUEL]), "RM2_ReserveMargin_FuelsIncluded"+"_%s"%r+"_%s"%l+"_%s"%y
				model += DemandNeedingReserveMargin[r][l][y] <= TotalCapacityInReserveMargin[r][y] * (1/ReserveMargin[r][y]), "RM3_ReserveMargin_Constraint"+"_%s"%r+"_%s"%l+"_%s"%y
	
	#########   		RE Production Target		#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				for f in FUEL:
					model += ProductionByTechnologyAnnual[r][t][f][y] == pulp.lpSum([ProductionByTechnology[r][l][t][f][y] for l in TIMESLICE]), "RE1_FuelProductionByTechnologyAnnual"+"_%s"%r+"_%s"%t+"_%s"%f+"_%s"%y
	
			model += TotalREProductionAnnual[r][y] == pulp.lpSum([ProductionByTechnologyAnnual[r][t][f][y] * RETagTechnology[r][t][y] for t in TECHNOLOGY for f in FUEL]), "RE2_TechIncluded"+"_%s"%r+"_%s"%y
			model += RETotalProductionOfTargetFuelAnnual[r][y] == pulp.lpSum([RateOfProduction[r][l][f][y] * YearSplit[l][y] * RETagFuel[r][f][y] for l in TIMESLICE for f in FUEL]), "RE3_FuelIncluded"+"_%s"%r+"_%s"%y
			model += TotalREProductionAnnual[r][y] >= REMinProductionTarget[r][y] * RETotalProductionOfTargetFuelAnnual[r][y], "RE4_EnergyConstraint"+"_%s"%r+"_%s"%y
	
			for t in TECHNOLOGY:
				for f in FUEL:
					model += UseByTechnologyAnnual[r][t][f][y] == pulp.lpSum([RateOfUseByTechnology[r][l][t][f][y] * YearSplit[l][y] for l in TIMESLICE]), "RE5_FuelUseByTechnologyAnnual"+"_%s"%r+"_%s"%t+"_%s"%f+"_%s"%y
	
	#########   		Emissions Accounting		#########
	
	for r in REGION:
		for y in YEAR:
			for t in TECHNOLOGY:
				for e in EMISSION:
					for m in MODE_OF_OPERATION:
							model += AnnualTechnologyEmissionByMode[r][t][e][m][y] == EmissionActivityRatio[r][t][e][m][y] * TotalAnnualTechnologyActivityByMode[r][t][m][y], "E1_AnnualEmissionProductionByMode"+"_%s"%r+"_%s"%t+"_%s"%e+"_%s"%m+"_%s"%y
	
					model += AnnualTechnologyEmission[r][t][e][y] == pulp.lpSum([AnnualTechnologyEmissionByMode[r][t][e][m][y] for m in MODE_OF_OPERATION]), "E2_AnnualEmissionProduction"+"_%s"%r+"_%s"%t+"_%s"%e+"_%s"%y
					model += AnnualTechnologyEmissionPenaltyByEmission[r][t][e][y] == AnnualTechnologyEmission[r][t][e][y] * EmissionsPenalty[r][e][y], "E3_EmissionsPenaltyByTechAndEmission"+"_%s"%r+"_%s"%t+"_%s"%e+"_%s"%y
	
				model += AnnualTechnologyEmissionsPenalty[r][t][y] == pulp.lpSum([AnnualTechnologyEmissionPenaltyByEmission[r][t][e][y] for e in EMISSION]), "E4_EmissionsPenaltyByTechnology"+"_%s"%r+"_%s"%t+"_%s"%y
				model += DiscountedTechnologyEmissionsPenalty[r][t][y] == AnnualTechnologyEmissionsPenalty[r][t][y] * (1 / ((1 + DiscountRate[r]) ** (int(y) - min([int(yy) for yy in YEAR]) + 0.5))), "E5_DiscountedEmissionsPenaltyByTechnology"+"_%s"%r+"_%s"%t+"_%s"%y
	
			for e in EMISSION:
				model += AnnualEmissions[r][e][y] == pulp.lpSum([AnnualTechnologyEmission[r][t][e][y] for t in TECHNOLOGY]), "E6_EmissionsAccounting1"+"_%s"%r+"_%s"%e+"_%s"%y
	
		for e in EMISSION:
			model += pulp.lpSum([AnnualEmissions[r][e][y] for y in YEAR]) == ModelPeriodEmissions[r][e] - ModelPeriodExogenousEmission[r][e], "E7_EmissionsAccounting2"+"_%s"%r+"_%s"%e
	
			for y in YEAR:
				model += AnnualEmissions[r][e][y] <= AnnualEmissionLimit[r][e][y] - AnnualExogenousEmission[r][e][y], "E8_AnnualEmissionsLimit"+"_%s"%r+"_%s"%e+"_%s"%y
	
			model += ModelPeriodEmissions[r][e] <= ModelPeriodEmissionLimit[r][e], "E9_ModelPeriodEmissionsLimit"+"_%s"%r+"_%s"%e
	
	print("Model is built. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	
	###############
	#    SOLVE    #
	###############
	
	model.solve()
	
	if str(pulp.LpStatus[model.status]) == "Optimal":
	
		print("Model is solved. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		print("Optimal solution found. The objective function value amounts to: ", round(model.objective.value(), 2))
	
		###################################
		#    SAVE RESULTS TO DATAFRAME    #
		###################################
	
		# Create dataframe to save results after the model was run the first time
		if i == 0:
			results_df = pd.DataFrame(columns=[
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
		
		results_df = save_results_to_dataframe(results_df, model, "Scenario_" + str(i))
		print("Results are saved. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		
	else:
		print("Model is solved. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		print("Error: Optimisation status for Scenario_" + str(i) + " is: ", pulp.LpStatus[model.status], "\nReview input data for the model parameters.")
	
	del model  # Delete model
	
	########################################
	#    MONTE CARLO SIMULATION - START    #
	########################################

	i += 1
	
	# Note: Monte Carlo Simulation is applied to all selected parameters (mcs_parameters).
	# For each parameter, the mcs_parameters is only applied to parameter values that are not equal to default values, i.e. values that were explicitly set.

	#########			Reference parameters and data     #########
	
	if (len(mcs_parameters) >= 1) and (MCS_num > 0) and (i == 1):
	
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

	if ("DiscountRate" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			DiscountRate_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "DiscountRate") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			DiscountRate_mcs_specified = tuple([(str(r)) for r in MCS_df[MCS_df['PARAM'] == "DiscountRate"].REGION])
		
		DiscountRate = {str(r): random_data_generation(DiscountRate_ref[r], MCS_df[(MCS_df['PARAM'] == "DiscountRate") & (MCS_df['REGION'] == r)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r)) in DiscountRate_mcs_specified else random_data_generation(DiscountRate_ref[r], DiscountRate_mcs_default_list) for r in REGION}


	########			Demands 							#########

	if ("SpecifiedAnnualDemand" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			SpecifiedAnnualDemand_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "SpecifiedAnnualDemand") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			SpecifiedAnnualDemand_mcs_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(MCS_df[MCS_df['PARAM'] == "SpecifiedAnnualDemand"].REGION, MCS_df[MCS_df['PARAM'] == "SpecifiedAnnualDemand"].FUEL, MCS_df[MCS_df['PARAM'] == "SpecifiedAnnualDemand"].YEAR)])
		
		SpecifiedAnnualDemand = {str(r): {str(f): {str(y): random_data_generation(SpecifiedAnnualDemand_ref[r][f][y], MCS_df[(MCS_df['PARAM'] == "SpecifiedAnnualDemand") & (MCS_df['REGION'] == r) & (MCS_df['FUEL'] == f) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(f),str(y)) in SpecifiedAnnualDemand_mcs_specified else random_data_generation(SpecifiedAnnualDemand_ref[r][f][y], SpecifiedAnnualDemand_mcs_default_list) for y in YEAR} for f in FUEL} for r in REGION}
	
	if ("AccumulatedAnnualDemand" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			AccumulatedAnnualDemand_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "AccumulatedAnnualDemand") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			AccumulatedAnnualDemand_mcs_specified = tuple([(str(r),str(f),str(y)) for r, f, y in zip(MCS_df[MCS_df['PARAM'] == "AccumulatedAnnualDemand"].REGION, MCS_df[MCS_df['PARAM'] == "AccumulatedAnnualDemand"].FUEL, MCS_df[MCS_df['PARAM'] == "AccumulatedAnnualDemand"].YEAR)])

		AccumulatedAnnualDemand = {str(r): {str(f): {str(y): random_data_generation(AccumulatedAnnualDemand_ref[r][f][y], MCS_df[(MCS_df['PARAM'] == "AccumulatedAnnualDemand") & (MCS_df['REGION'] == r) & (MCS_df['FUEL'] == f) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(f),str(y)) in AccumulatedAnnualDemand_mcs_specified else random_data_generation(AccumulatedAnnualDemand_ref[r][f][y], AccumulatedAnnualDemand_mcs_default_list) for y in YEAR} for f in FUEL} for r in REGION}

	#########			Performance					#########
	
	if ("TechWithCapacityNeededToMeetPeakTS" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			TechWithCapacityNeededToMeetPeakTS_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TechWithCapacityNeededToMeetPeakTS_mcs_specified = tuple([(str(r), str(t)) for r, t in zip(MCS_df[MCS_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].REGION, MCS_df[MCS_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS"].TECHNOLOGY)])
	
		TechWithCapacityNeededToMeetPeakTS = {str(r): {str(t): random_data_generation(TechWithCapacityNeededToMeetPeakTS_ref[r][t], MCS_df[(MCS_df['PARAM'] == "TechWithCapacityNeededToMeetPeakTS") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t)) in TechWithCapacityNeededToMeetPeakTS_mcs_specified else random_data_generation(TechWithCapacityNeededToMeetPeakTS_ref[r][t], TechWithCapacityNeededToMeetPeakTS_mcs_default_list) for t in TECHNOLOGY} for r in REGION}
	
	if ("CapacityFactor" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			CapacityFactor_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "CapacityFactor") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			CapacityFactor_mcs_specified = tuple([(str(r),str(t),str(l),str(y)) for r, t, l, y in zip(MCS_df[MCS_df['PARAM'] == "CapacityFactor"].REGION, MCS_df[MCS_df['PARAM'] == "CapacityFactor"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "CapacityFactor"].TIMESLICE, MCS_df[MCS_df['PARAM'] == "CapacityFactor"].YEAR)])
		
		CapacityFactor = {str(r): {str(t): {str(l): {str(y): random_data_generation(CapacityFactor_ref[r][t][l][y], MCS_df[(MCS_df['PARAM'] == "CapacityFactor") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(l),str(y)) in CapacityFactor_mcs_specified else random_data_generation(CapacityFactor_ref[r][t][l][y], CapacityFactor_mcs_default_list) for y in YEAR} for l in TIMESLICE} for t in TECHNOLOGY} for r in REGION}
	
	if ("AvailabilityFactor" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			AvailabilityFactor_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "AvailabilityFactor") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			AvailabilityFactor_mcs_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(MCS_df[MCS_df['PARAM'] == "AvailabilityFactor"].REGION, MCS_df[MCS_df['PARAM'] == "AvailabilityFactor"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "AvailabilityFactor"].YEAR)])
		
		AvailabilityFactor = {str(r): {str(t): {str(y): random_data_generation(AvailabilityFactor_ref[r][t][y], MCS_df[(MCS_df['PARAM'] == "AvailabilityFactor") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(y)) in AvailabilityFactor_mcs_specified else random_data_generation(AvailabilityFactor_ref[r][t][y], AvailabilityFactor_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
	
	if ("OperationalLife" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			OperationalLife_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "OperationalLife") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			OperationalLife_mcs_specified = tuple([(str(r), str(t)) for r, t in zip(MCS_df[MCS_df['PARAM'] == "OperationalLife"].REGION, MCS_df[MCS_df['PARAM'] == "OperationalLife"].TECHNOLOGY)])
		
		OperationalLife = {str(r): {str(t): int(random_data_generation(OperationalLife_ref[r][t], MCS_df[(MCS_df['PARAM'] == "OperationalLife") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0])) if (str(r), str(t)) in OperationalLife_mcs_specified else int(random_data_generation(OperationalLife_ref[r][t], OperationalLife_mcs_default_list)) for t in TECHNOLOGY} for r in REGION}
		
	if ("InputActivityRatio" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			InputActivityRatio_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "InputActivityRatio") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			InputActivityRatio_mcs_specified = tuple([(str(r),str(t),str(f),str(m),str(y)) for r, t, f, m, y in zip(MCS_df[MCS_df['PARAM'] == "InputActivityRatio"].REGION, MCS_df[MCS_df['PARAM'] == "InputActivityRatio"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "InputActivityRatio"].FUEL, MCS_df[MCS_df['PARAM'] == "InputActivityRatio"].MODE_OF_OPERATION, MCS_df[MCS_df['PARAM'] == "InputActivityRatio"].YEAR)])
		
		InputActivityRatio = {str(r): {str(t): {str(f): {str(m): {str(y): random_data_generation(InputActivityRatio_ref[r][t][f][m][y], MCS_df[(MCS_df['PARAM'] == "InputActivityRatio") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['FUEL'] == f) & (MCS_df['MODE_OF_OPERATION'] == m) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(f),str(m),str(y)) in InputActivityRatio_mcs_specified else random_data_generation(InputActivityRatio_ref[r][t][f][m][y], InputActivityRatio_mcs_default_list) for y in YEAR} for m in MODE_OF_OPERATION} for f in FUEL} for t in TECHNOLOGY} for r in REGION}
	
	if ("OutputActivityRatio" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			OutputActivityRatio_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "OutputActivityRatio") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			OutputActivityRatio_mcs_specified = tuple([(str(r),str(t),str(f),str(m),str(y)) for r, t, f, m, y in zip(MCS_df[MCS_df['PARAM'] == "OutputActivityRatio"].REGION, MCS_df[MCS_df['PARAM'] == "OutputActivityRatio"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "OutputActivityRatio"].FUEL, MCS_df[MCS_df['PARAM'] == "OutputActivityRatio"].MODE_OF_OPERATION, MCS_df[MCS_df['PARAM'] == "OutputActivityRatio"].YEAR)])
	
		OutputActivityRatio = {str(r): {str(t): {str(f): {str(m): {str(y): random_data_generation(OutputActivityRatio_ref[r][t][f][m][y], MCS_df[(MCS_df['PARAM'] == "OutputActivityRatio") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['FUEL'] == f) & (MCS_df['MODE_OF_OPERATION'] == m) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(f),str(m),str(y)) in OutputActivityRatio_mcs_specified else random_data_generation(OutputActivityRatio_ref[r][t][f][m][y], OutputActivityRatio_mcs_default_list) for y in YEAR} for m in MODE_OF_OPERATION} for f in FUEL} for t in TECHNOLOGY} for r in REGION}
	
	
	#########			Technology Costs			#########
	
	if ("CapitalCost" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			CapitalCost_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "CapitalCost") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			CapitalCost_mcs_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(MCS_df[MCS_df['PARAM'] == "CapitalCost"].REGION, MCS_df[MCS_df['PARAM'] == "CapitalCost"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "CapitalCost"].YEAR)])
		
		CapitalCost = {str(r): {str(t): {str(y): random_data_generation(CapitalCost_ref[r][t][y], MCS_df[(MCS_df['PARAM'] == "CapitalCost") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(y)) in CapitalCost_mcs_specified else random_data_generation(CapitalCost_ref[r][t][y], CapitalCost_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
			
	if ("VariableCost" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			VariableCost_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "VariableCost") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			VariableCost_mcs_specified = tuple([(str(r),str(t),str(m),str(y)) for r, t, m, y in zip(MCS_df[MCS_df['PARAM'] == "VariableCost"].REGION, MCS_df[MCS_df['PARAM'] == "VariableCost"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "VariableCost"].MODE_OF_OPERATION, MCS_df[MCS_df['PARAM'] == "VariableCost"].YEAR)])
		
		VariableCost = {str(r): {str(t): {str(m): {str(y): random_data_generation(VariableCost_ref[r][t][m][y], MCS_df[(MCS_df['PARAM'] == "VariableCost") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['MODE_OF_OPERATION'] == m) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(m),str(y)) in VariableCost_mcs_specified else random_data_generation(VariableCost_ref[r][t][m][y], VariableCost_mcs_default_list) for y in YEAR} for m in MODE_OF_OPERATION} for t in TECHNOLOGY} for r in REGION}
			
	if ("FixedCost" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			FixedCost_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "FixedCost") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			FixedCost_mcs_specified = tuple([(str(r),str(t),str(y)) for r, t, y in zip(MCS_df[MCS_df['PARAM'] == "FixedCost"].REGION, MCS_df[MCS_df['PARAM'] == "FixedCost"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "FixedCost"].YEAR)])
		
		FixedCost = {str(r): {str(t): {str(y): random_data_generation(FixedCost_ref[r][t][y], MCS_df[(MCS_df['PARAM'] == "FixedCost") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(y)) in FixedCost_mcs_specified else random_data_generation(FixedCost_ref[r][t][y], FixedCost_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
		
	
	#########			Storage                 	#########
	
	if ("StorageLevelStart" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			StorageLevelStart_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "StorageLevelStart") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			StorageLevelStart_mcs_specified = tuple([(str(r), str(s)) for r, s in zip(MCS_df[MCS_df['PARAM'] == "StorageLevelStart"].REGION, MCS_df[MCS_df['PARAM'] == "StorageLevelStart"].STORAGE)])
		
		StorageLevelStart = {str(r): {str(s): random_data_generation(StorageLevelStart_ref[r][s], MCS_df[(MCS_df['PARAM'] == "StorageLevelStart") & (MCS_df['REGION'] == r) & (MCS_df['STORAGE'] == s)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s)) in StorageLevelStart_mcs_specified else random_data_generation(StorageLevelStart_ref[r][s], StorageLevelStart_mcs_default_list) for s in STORAGE} for r in REGION}
			
	if ("StorageMaxChargeRate" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			StorageMaxChargeRate_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "StorageMaxChargeRate") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			StorageMaxChargeRate_mcs_specified = tuple([(str(r), str(s)) for r, s in zip(MCS_df[MCS_df['PARAM'] == "StorageMaxChargeRate"].REGION, MCS_df[MCS_df['PARAM'] == "StorageMaxChargeRate"].STORAGE)])
		
		StorageMaxChargeRate = {str(r): {str(s): random_data_generation(StorageMaxChargeRate_ref[r][s], MCS_df[(MCS_df['PARAM'] == "StorageMaxChargeRate") & (MCS_df['REGION'] == r) & (MCS_df['STORAGE'] == s)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s)) in StorageMaxChargeRate_mcs_specified else random_data_generation(StorageMaxChargeRate_ref[r][s], StorageMaxChargeRate_mcs_default_list) for s in STORAGE} for r in REGION}
			
	if ("StorageMaxDischargeRate" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			StorageMaxDischargeRate_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "StorageMaxDischargeRate") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			StorageMaxDischargeRate_mcs_specified = tuple([(str(r), str(s)) for r, s in zip(MCS_df[MCS_df['PARAM'] == "StorageMaxDischargeRate"].REGION, MCS_df[MCS_df['PARAM'] == "StorageMaxDischargeRate"].STORAGE)])
		
		StorageMaxDischargeRate = {str(r): {str(s): random_data_generation(StorageMaxDischargeRate_ref[r][s], MCS_df[(MCS_df['PARAM'] == "StorageMaxDischargeRate") & (MCS_df['REGION'] == r) & (MCS_df['STORAGE'] == s)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s)) in StorageMaxDischargeRate_mcs_specified else random_data_generation(StorageMaxDischargeRate_ref[r][s], StorageMaxDischargeRate_mcs_default_list) for s in STORAGE} for r in REGION}
			
	if ("OperationalLifeStorage" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			OperationalLifeStorage_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "OperationalLifeStorage") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			OperationalLifeStorage_mcs_specified = tuple([(str(r), str(s)) for r, s in zip(MCS_df[MCS_df['PARAM'] == "OperationalLifeStorage"].REGION, MCS_df[MCS_df['PARAM'] == "OperationalLifeStorage"].STORAGE)])
		
		OperationalLifeStorage = {str(r): {str(s): random_data_generation(OperationalLifeStorage_ref[r][s], MCS_df[(MCS_df['PARAM'] == "OperationalLifeStorage") & (MCS_df['REGION'] == r) & (MCS_df['STORAGE'] == s)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s)) in OperationalLifeStorage_mcs_specified else random_data_generation(OperationalLifeStorage_ref[r][s], OperationalLifeStorage_mcs_default_list) for s in STORAGE} for r in REGION}
			
	if ("CapitalCostStorage" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			CapitalCostStorage_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "CapitalCostStorage") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			CapitalCostStorage_mcs_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(MCS_df[MCS_df['PARAM'] == "CapitalCostStorage"].REGION, MCS_df[MCS_df['PARAM'] == "CapitalCostStorage"].STORAGE, MCS_df[MCS_df['PARAM'] == "CapitalCostStorage"].YEAR)])
		
		CapitalCostStorage = {str(r): {str(s): {str(y): random_data_generation(CapitalCostStorage_ref[r][s][y], MCS_df[(MCS_df['PARAM'] == "CapitalCostStorage") & (MCS_df['REGION'] == r) & (MCS_df['STORAGE'] == s) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s), str(y)) in CapitalCostStorage_mcs_specified else random_data_generation(CapitalCostStorage_ref[r][s][y], CapitalCostStorage_mcs_default_list) for y in YEAR} for s in STORAGE} for r in REGION}
			
	if ("ResidualStorageCapacity" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			ResidualStorageCapacity_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "ResidualStorageCapacity") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			ResidualStorageCapacity_mcs_specified = tuple([(str(r), str(s), str(y)) for r, s, y in zip(MCS_df[MCS_df['PARAM'] == "ResidualStorageCapacity"].REGION, MCS_df[MCS_df['PARAM'] == "ResidualStorageCapacity"].STORAGE, MCS_df[MCS_df['PARAM'] == "ResidualStorageCapacity"].YEAR)])
		
		ResidualStorageCapacity = {str(r): {str(s): {str(y): random_data_generation(ResidualStorageCapacity_ref[r][s][y], MCS_df[(MCS_df['PARAM'] == "ResidualStorageCapacity") & (MCS_df['REGION'] == r) & (MCS_df['STORAGE'] == s) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(s), str(y)) in ResidualStorageCapacity_mcs_specified else random_data_generation(ResidualStorageCapacity_ref[r][s][y], ResidualStorageCapacity_mcs_default_list) for y in YEAR} for s in STORAGE} for r in REGION}
	
	
	#########			Capacity Constraints		#########
	
	if ("CapacityOfOneTechnologyUnit" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			CapacityOfOneTechnologyUnit_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "CapacityOfOneTechnologyUnit") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			CapacityOfOneTechnologyUnit_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(MCS_df[MCS_df['PARAM'] == "CapacityOfOneTechnologyUnit"].REGION, MCS_df[MCS_df['PARAM'] == "CapacityOfOneTechnologyUnit"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "CapacityOfOneTechnologyUnit"].YEAR)])
		
		CapacityOfOneTechnologyUnit = {str(r): {str(t): {str(y): random_data_generation(CapacityOfOneTechnologyUnit_ref[r][t][y], MCS_df[(MCS_df['PARAM'] == "CapacityOfOneTechnologyUnit") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in CapacityOfOneTechnologyUnit_mcs_specified else random_data_generation(CapacityOfOneTechnologyUnit_ref[r][t][y], CapacityOfOneTechnologyUnit_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}

	
	#########			Investment Constraints		#########
	
	if ("TotalAnnualMaxCapacityInvestment" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			TotalAnnualMaxCapacityInvestment_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "TotalAnnualMaxCapacityInvestment") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalAnnualMaxCapacityInvestment_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(MCS_df[MCS_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].REGION, MCS_df[MCS_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "TotalAnnualMaxCapacityInvestment"].YEAR)])
			
		TotalAnnualMaxCapacityInvestment = {str(r): {str(t): {str(y): random_data_generation(TotalAnnualMaxCapacityInvestment_ref[r][t][y], MCS_df[(MCS_df['PARAM'] == "TotalAnnualMaxCapacityInvestment") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in TotalAnnualMaxCapacityInvestment_mcs_specified else random_data_generation(TotalAnnualMaxCapacityInvestment_ref[r][t][y], TotalAnnualMaxCapacityInvestment_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
			
	if ("TotalAnnualMinCapacityInvestment" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			TotalAnnualMinCapacityInvestment_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "TotalAnnualMinCapacityInvestment") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalAnnualMinCapacityInvestment_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(MCS_df[MCS_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].REGION, MCS_df[MCS_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "TotalAnnualMinCapacityInvestment"].YEAR)])
		
		TotalAnnualMinCapacityInvestment = {str(r): {str(t): {str(y): random_data_generation(TotalAnnualMinCapacityInvestment_ref[r][t][y], MCS_df[(MCS_df['PARAM'] == "TotalAnnualMinCapacityInvestment") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in TotalAnnualMinCapacityInvestment_mcs_specified else random_data_generation(TotalAnnualMinCapacityInvestment_ref[r][t][y], TotalAnnualMinCapacityInvestment_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
		
	
	#########			Activity Constraints		#########
	
	if ("TotalTechnologyAnnualActivityUpperLimit" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			TotalTechnologyAnnualActivityUpperLimit_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalTechnologyAnnualActivityUpperLimit_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(MCS_df[MCS_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].REGION, MCS_df[MCS_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit"].YEAR)])
		
		TotalTechnologyAnnualActivityUpperLimit = {str(r): {str(t): {str(y): random_data_generation(TotalTechnologyAnnualActivityUpperLimit_ref[r][t][y], MCS_df[(MCS_df['PARAM'] == "TotalTechnologyAnnualActivityUpperLimit") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in TotalTechnologyAnnualActivityUpperLimit_mcs_specified else random_data_generation(TotalTechnologyAnnualActivityUpperLimit_ref[r][t][y], TotalTechnologyAnnualActivityUpperLimit_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
			
	if ("TotalTechnologyAnnualActivityLowerLimit" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			TotalTechnologyAnnualActivityLowerLimit_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalTechnologyAnnualActivityLowerLimit_mcs_specified = tuple([(str(r), str(t), str(y)) for r, t, y in zip(MCS_df[MCS_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].REGION, MCS_df[MCS_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit"].YEAR)])
		
		TotalTechnologyAnnualActivityLowerLimit = {str(r): {str(t): {str(y): random_data_generation(TotalTechnologyAnnualActivityLowerLimit_ref[r][t][y], MCS_df[(MCS_df['PARAM'] == "TotalTechnologyAnnualActivityLowerLimit") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t), str(y)) in TotalTechnologyAnnualActivityLowerLimit_mcs_specified else random_data_generation(TotalTechnologyAnnualActivityLowerLimit_ref[r][t][y], TotalTechnologyAnnualActivityLowerLimit_mcs_default_list) for y in YEAR} for t in TECHNOLOGY} for r in REGION}
			
	if ("TotalTechnologyModelPeriodActivityUpperLimit" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			TotalTechnologyModelPeriodActivityUpperLimit_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalTechnologyModelPeriodActivityUpperLimit_mcs_specified = tuple([(str(r), str(t)) for r, t in zip(MCS_df[MCS_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].REGION, MCS_df[MCS_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit"].TECHNOLOGY)])
		
		TotalTechnologyModelPeriodActivityUpperLimit = {str(r): {str(t): random_data_generation(TotalTechnologyModelPeriodActivityUpperLimit_ref[r][t], MCS_df[(MCS_df['PARAM'] == "TotalTechnologyModelPeriodActivityUpperLimit") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t)) in TotalTechnologyModelPeriodActivityUpperLimit_mcs_specified else random_data_generation(TotalTechnologyModelPeriodActivityUpperLimit_ref[r][t], TotalTechnologyModelPeriodActivityUpperLimit_mcs_default_list) for t in TECHNOLOGY} for r in REGION}
			
	if ("TotalTechnologyModelPeriodActivityLowerLimit" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			TotalTechnologyModelPeriodActivityLowerLimit_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			TotalTechnologyModelPeriodActivityLowerLimit_mcs_specified = tuple([(str(r), str(t)) for r, t in zip(MCS_df[MCS_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].REGION, MCS_df[MCS_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit"].TECHNOLOGY)])
		
		TotalTechnologyModelPeriodActivityLowerLimit = {str(r): {str(t): random_data_generation(TotalTechnologyModelPeriodActivityLowerLimit_ref[r][t], MCS_df[(MCS_df['PARAM'] == "TotalTechnologyModelPeriodActivityLowerLimit") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(t)) in TotalTechnologyModelPeriodActivityLowerLimit_mcs_specified else random_data_generation(TotalTechnologyModelPeriodActivityLowerLimit_ref[r][t], TotalTechnologyModelPeriodActivityLowerLimit_mcs_default_list) for t in TECHNOLOGY} for r in REGION}
		
	
	#########			Emissions & Penalties		#########
	
	if ("EmissionActivityRatio" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			EmissionActivityRatio_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "EmissionActivityRatio") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			EmissionActivityRatio_mcs_specified = tuple([(str(r),str(t),str(e),str(m),str(y)) for r, t, e, m, y in zip(MCS_df[MCS_df['PARAM'] == "EmissionActivityRatio"].REGION, MCS_df[MCS_df['PARAM'] == "EmissionActivityRatio"].TECHNOLOGY, MCS_df[MCS_df['PARAM'] == "EmissionActivityRatio"].EMISSION, MCS_df[MCS_df['PARAM'] == "EmissionActivityRatio"].MODE_OF_OPERATION, MCS_df[MCS_df['PARAM'] == "EmissionActivityRatio"].YEAR)])
		
		EmissionActivityRatio = {str(r): {str(t): {str(e): {str(m): {str(y): random_data_generation(EmissionActivityRatio_ref[r][t][e][m][y], MCS_df[(MCS_df['PARAM'] == "EmissionActivityRatio") & (MCS_df['REGION'] == r) & (MCS_df['TECHNOLOGY'] == t) & (MCS_df['EMISSION'] == e) & (MCS_df['MODE_OF_OPERATION'] == m) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r),str(t),str(e),str(m),str(y)) in EmissionActivityRatio_mcs_specified else random_data_generation(EmissionActivityRatio_ref[r][t][e][m][y], EmissionActivityRatio_mcs_default_list) for y in YEAR} for m in MODE_OF_OPERATION} for e in EMISSION} for t in TECHNOLOGY} for r in REGION}
			
	if ("EmissionsPenalty" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			EmissionsPenalty_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "EmissionsPenalty") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			EmissionsPenalty_mcs_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(MCS_df[MCS_df['PARAM'] == "EmissionsPenalty"].REGION, MCS_df[MCS_df['PARAM'] == "EmissionsPenalty"].EMISSION, MCS_df[MCS_df['PARAM'] == "EmissionsPenalty"].YEAR)])
		
		EmissionsPenalty = {str(r): {str(e): {str(y): random_data_generation(EmissionsPenalty_ref[r][e][y], MCS_df[(MCS_df['PARAM'] == "EmissionsPenalty") & (MCS_df['REGION'] == r) & (MCS_df['EMISSION'] == e) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e), str(y)) in EmissionsPenalty_mcs_specified else random_data_generation(EmissionsPenalty_ref[r][e][y], EmissionsPenalty_mcs_default_list) for y in YEAR} for e in EMISSION} for r in REGION}
			
	if ("AnnualExogenousEmission" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			AnnualExogenousEmission_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "AnnualExogenousEmission") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			AnnualExogenousEmission_mcs_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(MCS_df[MCS_df['PARAM'] == "AnnualExogenousEmission"].REGION, MCS_df[MCS_df['PARAM'] == "AnnualExogenousEmission"].EMISSION, MCS_df[MCS_df['PARAM'] == "AnnualExogenousEmission"].YEAR)])
		
		AnnualExogenousEmission = {str(r): {str(e): {str(y): random_data_generation(AnnualExogenousEmission_ref[r][e][y], MCS_df[(MCS_df['PARAM'] == "AnnualExogenousEmission") & (MCS_df['REGION'] == r) & (MCS_df['EMISSION'] == e) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e), str(y)) in AnnualExogenousEmission_mcs_specified else random_data_generation(AnnualExogenousEmission_ref[r][e][y], AnnualExogenousEmission_mcs_default_list) for y in YEAR} for e in EMISSION} for r in REGION}
			
	if ("AnnualEmissionLimit" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			AnnualEmissionLimit_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "AnnualEmissionLimit") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			AnnualEmissionLimit_mcs_specified = tuple([(str(r), str(e), str(y)) for r, e, y in zip(MCS_df[MCS_df['PARAM'] == "AnnualEmissionLimit"].REGION, MCS_df[MCS_df['PARAM'] == "AnnualEmissionLimit"].EMISSION, MCS_df[MCS_df['PARAM'] == "AnnualEmissionLimit"].YEAR)])
		
		AnnualEmissionLimit = {str(r): {str(e): {str(y): random_data_generation(AnnualEmissionLimit_ref[r][e][y], MCS_df[(MCS_df['PARAM'] == "AnnualEmissionLimit") & (MCS_df['REGION'] == r) & (MCS_df['EMISSION'] == e) & (MCS_df['YEAR'] == y)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e), str(y)) in AnnualEmissionLimit_mcs_specified else random_data_generation(AnnualEmissionLimit_ref[r][e][y], AnnualEmissionLimit_mcs_default_list) for y in YEAR} for e in EMISSION} for r in REGION}
			
	if ("ModelPeriodExogenousEmission" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			ModelPeriodExogenousEmission_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "ModelPeriodExogenousEmission") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			ModelPeriodExogenousEmission_mcs_specified = tuple([(str(r), str(e)) for r, e in zip(MCS_df[MCS_df['PARAM'] == "ModelPeriodExogenousEmission"].REGION, MCS_df[MCS_df['PARAM'] == "ModelPeriodExogenousEmission"].EMISSION)])
		
		ModelPeriodExogenousEmission = {str(r): {str(e): random_data_generation(ModelPeriodExogenousEmission_ref[r][e], MCS_df[(MCS_df['PARAM'] == "ModelPeriodExogenousEmission") & (MCS_df['REGION'] == r) & (MCS_df['EMISSION'] == e)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e)) in ModelPeriodExogenousEmission_mcs_specified else random_data_generation(ModelPeriodExogenousEmission_ref[r][e], ModelPeriodExogenousEmission_mcs_default_list) for e in EMISSION} for r in REGION}
			
	if ("ModelPeriodEmissionLimit" in mcs_parameters) and (MCS_num > 0):
		if i == 1:
			ModelPeriodEmissionLimit_mcs_default_list = MCS_df[(MCS_df['PARAM'] == "ModelPeriodEmissionLimit") & (MCS_df['DEFAULT_SETTING'] == 1)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]
			ModelPeriodEmissionLimit_mcs_specified = tuple([(str(r), str(e)) for r, e in zip(MCS_df[MCS_df['PARAM'] == "ModelPeriodEmissionLimit"].REGION, MCS_df[MCS_df['PARAM'] == "ModelPeriodEmissionLimit"].EMISSION)])
		
		ModelPeriodEmissionLimit = {str(r): {str(e): random_data_generation(ModelPeriodEmissionLimit_ref[r][e], MCS_df[(MCS_df['PARAM'] == "ModelPeriodEmissionLimit") & (MCS_df['REGION'] == r) & (MCS_df['EMISSION'] == e)][['DISTRIBUTION', 'REL_SD', 'REL_MIN', 'REL_MAX', 'ARRAY']].values.tolist()[0]) if (str(r), str(e)) in ModelPeriodEmissionLimit_mcs_specified else random_data_generation(ModelPeriodEmissionLimit_ref[r][e], ModelPeriodEmissionLimit_mcs_default_list) for e in EMISSION} for r in REGION}

	
print("Analysis is finished.\nPlease wait until the results are saved!")

##############################
#	SAVE RESULTS TO EXCEL    #
##############################

output_data_path = os.path.join(output_data_directory, output_data_file)
save_results(results_df, output_data_path)

print("Results are saved. -- Current date/time:", dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

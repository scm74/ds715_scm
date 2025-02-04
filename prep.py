first_name = "Susan" # put your first name here, inside the ""
last_name  = "Mayer" # put your last name here, inside the ""
# Load libraries

import numpy as np
import pandas as pd

# Parameters

if 'min_year' not in globals():
    min_year = 1990
if 'max_year' not in globals():
    max_year = 2024

# Validate that parameters are present.
assert (min_year & max_year and max_year >= min_year)  
vaers_filebase = 'VAERSDATA.csv'
vax_filebase = 'VAERSVAX.csv'
sympt_filebase = 'VAERSSYMPTOMS.csv'

# Initialize dataframes

df_tot_vaers = pd.DataFrame()  # Create an empty DataFrame
df_tot_vax = pd.DataFrame()  # Create an empty DataFrame
df_tot_sympt = pd.DataFrame()  # Create an empty DataFrame

# Specify data file columm types
vaers_dtype = {
    "VAERS_ID": int,
    "RECVDATE": "string",
    "STATE": "string",
    "AGE_YRS": "string",
    "CAGE_YR": "string",
    "CAGE_MO": "string",
    "SEX": "string",
	"RPT_DATE": "string",
	"SYMPTOM_TEXT": "string",
	"DIED": "string",
	"DATEDIED": "string",
	"L_THREAT": "string",
	"ER_VISIT": "string",
	"HOSPITAL": "string",
	"HOSPDAYS": "string",
	"X_STAY": "string",
	"DISABLE": "string",
	"RECOVD": "string",
	"VAX_DATE": "string",
	"ONSET_DATE": "string",
	"NUMDAYS": "string",
	"LAB_DATA": "string",
	"V_ADMINBY": "string",
	"V_FUNDBY": "string",
	"OTHER_MEDS": "string",
	"CUR_ILL": "string",
	"HISTORY": "string",
	"PRIOR_VAX": "string",
	"SPLTTYPE": "string",
	"FORM_VERS": "string",
	"TODAYS_DATE": "string",
	"BIRTH_DEFECT": "string",
	"OFC_VISIT": "string",
	"ER_ED_VISIT": "string",
	"ALLERGIES": "string"
    }

vax_dtype = {
    "VAERS_ID": int,
    "VAX_TYPE": "string",
    "VAX_MANU": "string",
    "VAX_LOT": "string",
    "VAX_DOSE_SERIES": "string",
    "VAX_ROUTE": "string",
    "VAX_SITE": "string",
    "VAX_NAME": "string"
    }
sympt_dtype = {
    "VAERS_ID": int,
    "SYMPTOM1": "string",
    "SYMPTOMVERSION1": "string",
    "SYMPTOM2": "string",
    "SYMPTOMVERSION2": "string",
    "SYMPTOM3": "string",
    "SYMPTOMVERSION3": "string",
    "SYMPTOM4": "string",
    "SYMPTOMVERSION4": "string",
    "SYMPTOM5": "string",
    "SYMPTOMVERSION5": "string"
    }

# Import all files based on date range - Assumes files are unzipped in local directory

for year in range(min_year,max_year+1):
  str_year = str(year)
  vaers_filename = str_year+vaers_filebase
  vax_filename = str_year+vax_filebase
  sympt_filename = str_year+sympt_filebase
  df_vaers = pd.read_csv(vaers_filename, encoding='cp1252', dtype=vaers_dtype)
  df_tot_vaers = pd.concat([df_tot_vaers, df_vaers], ignore_index=True)
  df_vax = pd.read_csv(vax_filename, encoding='cp1252', dtype=vax_dtype)
  df_tot_vax = pd.concat([df_tot_vax, df_vax], ignore_index=True)
  df_sympt = pd.read_csv(sympt_filename, encoding='cp1252', dtype=sympt_dtype)
  df_tot_sympt = pd.concat([df_tot_sympt, df_sympt], ignore_index=True)

# Replace <NA>/UNK numeric values with NaN
def ClearNAChangeNumeric(stringcol):
#    Any non-numeric string values become nan
    return pd.to_numeric(stringcol, errors='coerce')

# For Consistancy, ensure all blank values are <NA> as that is the value used in most columns
df_tot_vaers = df_tot_vaers.fillna('UNK')
df_tot_sympt = df_tot_sympt.fillna('UNK')
df_tot_vax = df_tot_vax.fillna('UNK')

# Convert numeric columns from string to numeric - Will result in <NA> converting to nan
df_tot_vaers['AGE_YRS'] = ClearNAChangeNumeric(df_tot_vaers['AGE_YRS'])
df_tot_vaers['CAGE_YR'] = ClearNAChangeNumeric(df_tot_vaers['CAGE_YR'])
df_tot_vaers['CAGE_MO'] = ClearNAChangeNumeric(df_tot_vaers['CAGE_MO'])
df_tot_vaers['HOSPDAYS'] = ClearNAChangeNumeric(df_tot_vaers['HOSPDAYS'])
df_tot_vaers['NUMDAYS'] = ClearNAChangeNumeric(df_tot_vaers['NUMDAYS'])

df_tot_sympt['SYMPTOMVERSION1'] = ClearNAChangeNumeric(df_tot_sympt['SYMPTOMVERSION1'])
df_tot_sympt['SYMPTOMVERSION2'] = ClearNAChangeNumeric(df_tot_sympt['SYMPTOMVERSION2'])
df_tot_sympt['SYMPTOMVERSION3'] = ClearNAChangeNumeric(df_tot_sympt['SYMPTOMVERSION3'])
df_tot_sympt['SYMPTOMVERSION4'] = ClearNAChangeNumeric(df_tot_sympt['SYMPTOMVERSION4'])
df_tot_sympt['SYMPTOMVERSION5'] = ClearNAChangeNumeric(df_tot_sympt['SYMPTOMVERSION5'])

# Create Age Categories
bins = [0, 2, 13, 18, 30, 40, 50, 60, 70, 140]
labels = ['0 - 1', '2 - 12', '13 - 17', 
          '18 - 29', '30 - 39', '40 - 49',
          '50 - 59', '60 - 69','70+']
df_tot_vaers['age_block'] = pd.cut(df_tot_vaers['AGE_YRS'], bins, labels = labels,include_lowest = True)
df_tot_vaers['age_block'] = df_tot_vaers['age_block'].cat.add_categories('UNK')
df_tot_vaers['age_block'] = df_tot_vaers['age_block'].fillna('UNK')

# Add Serious Category
df_tot_vaers['Serious'] = np.where(
                         (
                            (df_tot_vaers['DIED']== 'Y') |
                            (df_tot_vaers['L_THREAT']== 'Y') | 
                            (df_tot_vaers['ER_VISIT']== 'Y') |
                            (df_tot_vaers['HOSPITAL']== 'Y') |  
                            (df_tot_vaers['X_STAY']== 'Y') | 
                            (df_tot_vaers['DISABLE']== 'Y')
                         )
                         , True, False)

    
# Add year of report
# Create a new column YearofReport based on year of receipt
df_tot_vaers['YearofReport'] = pd.to_datetime(df_tot_vaers['RECVDATE'], format='%m/%d/%Y', errors='coerce').dt.year
df_tot_sympt['YearofReport'] = df_tot_sympt['VAERS_ID'].map(df_tot_vaers.set_index('VAERS_ID')['YearofReport'])
df_tot_vax['YearofReport'] = df_tot_vax['VAERS_ID'].map(df_tot_vaers.set_index('VAERS_ID')['YearofReport'])

df_tot_sympt['Serious'] = df_tot_sympt['VAERS_ID'].map(df_tot_vaers.set_index('VAERS_ID')['Serious'])


# Check that derived years are within parameters
assert df_tot_vaers['YearofReport'].between(min_year, max_year).all(), f"Column YearofReport contains values outside the range [{min_year}, {max_year}]"
assert df_tot_sympt['YearofReport'].between(min_year, max_year).all(), f"Column YearofReport contains values outside the range [{min_year}, {max_year}]"
assert df_tot_vax['YearofReport'].between(min_year, max_year).all(), f"Column YearofReport contains values outside the range [{min_year}, {max_year}]"

# Add column for whether COVID-19 Vaccine is linked to report
df_vax_covid = df_tot_vax[df_tot_vax["VAX_TYPE"].astype(str).str.startswith("COVID")]

df_tot_vaers['COVID'] = np.where(
                        (df_tot_vaers['VAERS_ID'].isin(df_vax_covid['VAERS_ID']))
                        , True, False)
                                                     


first_name = "Susan" # put your first name here, inside the ""
last_name  = "Mayer" # put your last name here, inside the ""

# Q2: What are the top 5 most commonly reported vaccine reactions by year since 1990?
# Load libraries

import pandas as pd

# Parameters

min_year = 1990
max_year = 2024
analyzer_start = 2020
analyzer_end = 2024

# Validate that parameters are present.
assert (min_year & max_year & analyzer_start & analyzer_end and max_year >= min_year and max_year > analyzer_start and min_year <= analyzer_end)  

# Initialize dataframes

df_tot_vaers = pd.DataFrame()  # Create an empty DataFrame
df_tot_vax = pd.DataFrame()  # Create an empty DataFrame
df_tot_sympt = pd.DataFrame()  # Create an empty DataFrame

with open('prep.py') as f:
    exec(f.read()) 

# Incorporate Serious into Symptoms data frame
df_tot_sympt['Serious'] = df_tot_sympt['VAERS_ID'].map(df_tot_vaers.set_index('VAERS_ID')['Serious'])

# Create a copy of df_tot_sympt filtered analyzer_year to present
df_tot_sympt_analyzer = df_tot_sympt[(df_tot_sympt['YearofReport']>=analyzer_start) & (df_tot_sympt['YearofReport']<=analyzer_end)]
sympt_exclusion = ["Pyrexia","Injection site hypersensitivity","Rash","Injection site oedema",
                   "Injection site erythema"]

df_vax_covid = df_tot_vax[df_tot_vax["VAX_TYPE"].astype(str).str.startswith("COVID")]

# Limit data to serious adverse events where a COVID vaccination was administered and symptoms not part of common list

df_tot_sympt_analyzer = df_tot_sympt_analyzer[(df_tot_sympt_analyzer['Serious']==True) 
                                              & (~df_tot_sympt_analyzer['SYMPTOM1'].isin(sympt_exclusion))
                                              & (~df_tot_sympt_analyzer['SYMPTOM2'].isin(sympt_exclusion))
                                              & (~df_tot_sympt_analyzer['SYMPTOM3'].isin(sympt_exclusion))
                                              & (~df_tot_sympt_analyzer['SYMPTOM4'].isin(sympt_exclusion))
                                              & (~df_tot_sympt_analyzer['SYMPTOM5'].isin(sympt_exclusion))
                                              & (df_tot_sympt_analyzer['VAERS_ID'].isin(df_vax_covid['VAERS_ID']))]

# Create dataframe that is year and reaction, where one record per reaction 
# in any of reaction columns other than UNK

def sympt_pivot(symptom_columns, df_analysis):
    
    df_ret = pd.DataFrame(columns=['YearofReport', 'Symptom'])

    for index, row in df_analysis.iterrows():
        for col in symptom_columns:
            if (row[col]!="UNK"):
                df_row = pd.DataFrame([[row['YearofReport'],row[col]]]
                                  , columns=['YearofReport', 'Symptom'])
                df_ret = pd.concat([df_ret, df_row], ignore_index=True, copy=False)
    return(df_ret)

symptom_columns = ['SYMPTOM1', 'SYMPTOM2', 'SYMPTOM3', 'SYMPTOM4','SYMPTOM5']
df_sympt_pivot = sympt_pivot(symptom_columns, df_tot_sympt_analyzer)

# Pivot results to create a dataframe that is Year of Report / Symptom / Number of Records for that Year/Symptom
sympt_by_year = df_sympt_pivot.groupby('YearofReport')['Symptom'].value_counts()
sympt_by_year = sympt_by_year.sort_values(ascending=False).groupby('YearofReport').head(5)
df_sympt_by_year = sympt_by_year.to_frame()

# save dataframe to file
df_sympt_by_year.to_csv('Mayer_Susan_Q2_df_sympt_by_year.csv')




first_name = "Susan" # put your first name here, inside the ""
last_name  = "Mayer" # put your last name here, inside the ""
# How has the reporting of vaccine adverse events changed year over year?

# Load libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Parameters

min_year = 1990
max_year = 2024
analyzer_year = 1990
# Validate that parameters are present.
assert (min_year & max_year & analyzer_year and max_year >= min_year and max_year > analyzer_year and min_year <= analyzer_year)  

# Initialize dataframes

df_tot_vaers = pd.DataFrame()  # Create an empty DataFrame
df_tot_vax = pd.DataFrame()  # Create an empty DataFrame
df_tot_sympt = pd.DataFrame()  # Create an empty DataFrame

# Read in standard VAERS prep
with open('prep.py') as f:
    exec(f.read()) 
        
#Plot histogram
fig = plt.figure(figsize=(10, 10))

sns.histplot(data=df_tot_vaers, x='YearofReport', bins=max_year-analyzer_year)
plt.title('Distribution of Total Adverse Events Reported to VAERS by Year')
plt.xlabel('Year of Report')
plt.ylabel('Total Number of Reports')
plt.grid(True)
plt.show()
# save this figure 
fig.savefig("Mayer_Susan_Q1_1.pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)

# save dataframe to file
df_tot_vaers.to_csv('Mayer_Susan_Q1_df_tot_vaers.csv')

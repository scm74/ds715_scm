first_name = "Susan" # put your first name here, inside the ""
last_name  = "Mayer" # put your last name here, inside the ""
#Q5: What were the primary sources of vaccine funding (V_FUNDBY in VAERS Data) for the years 1990-2023 for the top 5 vaccine types (VAX_TYPE in VAERS Vax)?

# Load libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl 
import numpy as np

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

with open('prep.py') as f:
    exec(f.read()) 
            
# Add year of report
# Create a new column YearofReport based on year of receipt
df_tot_vaers['YearofReport'] = pd.to_datetime(df_tot_vaers['RECVDATE'], format='mixed').dt.year
df_tot_sympt['YearofReport'] = df_tot_sympt['VAERS_ID'].map(df_tot_vaers.set_index('VAERS_ID')['YearofReport'])
df_tot_vax['YearofReport'] = df_tot_vax['VAERS_ID'].map(df_tot_vaers.set_index('VAERS_ID')['YearofReport'])

# Check that derived years are within parameters
assert df_tot_vaers['YearofReport'].between(min_year, max_year).all(), f"Column YearofReport contains values outside the range [{min_year}, {max_year}]"
assert df_tot_sympt['YearofReport'].between(min_year, max_year).all(), f"Column YearofReport contains values outside the range [{min_year}, {max_year}]"
assert df_tot_vax['YearofReport'].between(min_year, max_year).all(), f"Column YearofReport contains values outside the range [{min_year}, {max_year}]"

# Transfer column V_FUNDBY to vax data frame
df_tot_vax['V_FUNDBY'] = df_tot_vax['VAERS_ID'].map(df_tot_vaers.set_index('VAERS_ID')['V_FUNDBY'])

# Create a copy of df_tot_vaers filtered to year analyzer_year to present
df_tot_vaers_analyzer = df_tot_vaers[df_tot_vaers['YearofReport']>analyzer_year]

# Perform preliminary analysis on all VAERS/VAX rows
df_fundby = df_tot_vaers[df_tot_vaers['V_FUNDBY']!='UNK']
fund_counts = df_fundby.groupby('YearofReport')['V_FUNDBY'].value_counts()
df_fund = fund_counts.to_frame()
df_fund = df_fund.reset_index()

# Plot 1:  Total Reports by year of report, color by funding source

fig = plt.figure()

df_pivot = df_fund.pivot_table(index='YearofReport', columns='V_FUNDBY', values='count')
df_pivot.plot(kind='bar', stacked=True)

# Update the title of the legend
plt.legend(title="Vaccine Funding Source")

plt.title('Distribution of Total Adverse Events Reported to VAERS by Year by Funding Source')
plt.xlabel('Year of Report')
plt.ylabel('Total Number of Reports')
plt.grid(True)

# Force to pickup the current figure
fig = plt.gcf() 

# save this figure
fig.savefig("Mayer_Susan_Q5_1..pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)
plt.show()

# save dataframe to file
df_pivot.to_csv('Mayer_Susan_Q5_df_pivot.csv')


# Plot 2: Plot by percentage of reports specifying funding by source
year_counts = df_fundby.groupby('YearofReport')['YearofReport'].value_counts()
df_year = year_counts.to_frame()

# Merge DataFrames on the 'ID' column
df_fund_year = df_fund.merge(df_year, on='YearofReport', how='left')

df_fund_year.columns = ['YearofReport', 'V_FUNDBY', 'FundCount', 'TotalCount']
df_fund_year['PctFund'] = df_fund_year['FundCount']*100/df_fund_year['TotalCount']

fig = plt.figure()
df_pivot = df_fund_year.pivot_table(index='YearofReport', columns='V_FUNDBY', values='PctFund')
df_pivot.plot(kind='bar', stacked=True)
plt.legend(title="Funding Source", loc='upper center', bbox_to_anchor=(0.5,-0.2))

plt.title('Percentage of Funding Types Reported to VAERS by Year')
plt.xlabel('Year of Report')
plt.ylabel('Percentage of Funding Reported')

plt.grid(True)
# save dataframe to file
df_pivot.to_csv('Mayer_Susan_Q5_df_pivot2.csv')

# Force to pickup the current figure
fig = plt.gcf() 

# save this figure
fig.savefig("Mayer_Susan_Q5_2.pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)


# Create an additonal dataframe grouping counts for Year of Report, Vaccine Type, and Funding Source

vax_by_year = df_tot_vax.groupby(['YearofReport','VAX_TYPE','V_FUNDBY'])['V_FUNDBY'].value_counts()
#vax_by_year = vax_by_year.sort_values(ascending=False).groupby(['YearofReport','VAX_TYPE']).head(5)
df_vax_by_year = vax_by_year.to_frame()
df_vax_by_year.rename(columns={'count': 'vax_by_year_count'}, inplace=True)

# save dataframe to file
df_vax_by_year.to_csv('Mayer_Susan_Q5_df_vax_by_year.csv')
mil_cnt = 100

# Additional investigation:  Focus on Military funding - Plot Military funded vax by year, color coded by vaxtype
df_vax_by_year = df_vax_by_year.reset_index()
df_mil = df_vax_by_year[(df_vax_by_year['V_FUNDBY']=="MIL") & (df_vax_by_year['vax_by_year_count']>mil_cnt)]

df_mil_pivot = df_mil.pivot_table(index='YearofReport', columns='VAX_TYPE', values='vax_by_year_count')
fig = plt.figure()
colormap = mpl.colormaps.get_cmap('viridis')
colors = colormap(np.linspace(0, 1, df_mil['VAX_TYPE'].nunique()))
df_mil_pivot.plot(kind='bar', stacked=True, color=colors)
plt.legend(title="Vaccine Type", loc='upper center', bbox_to_anchor=(0.5,-0.2))

plt.title(f'Military-Funded Vaccines AE Reports >{mil_cnt} by Year, Vaccine Type')
plt.xlabel('Year of Report')
plt.ylabel('Total Military-Funded Vaccines Reported')

plt.grid(True)
# save dataframe to file

# Force to pickup the current figure
fig = plt.gcf() 

# save this figure
fig.savefig("Mayer_Susan_Q5_2.pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)

# Additional investigation:  Focus on Public funding - Plot Public funded vax by year, color coded by vaxtype
pub_cnt = 1000
df_pub = df_vax_by_year[(df_vax_by_year['V_FUNDBY']=="PUB") & (df_vax_by_year['vax_by_year_count']>pub_cnt)]
df_pub_pivot = df_pub.pivot_table(index='YearofReport', columns='VAX_TYPE', values='vax_by_year_count')
fig = plt.figure()
colors = colormap(np.linspace(0, 1, df_pub['VAX_TYPE'].nunique()))
df_pub_pivot.plot(kind='bar', stacked=True, color=colors)
plt.legend(title="Vaccine Type", loc='upper center', bbox_to_anchor=(0.5,-0.2))

plt.title(f'Public-Funded Vaccines AE Reports >{pub_cnt} by Year, Vaccine Type')
plt.xlabel('Year of Report')
plt.ylabel('Total Public-Funded Vaccines Reported')

plt.grid(True)
# save dataframe to file

# Force to pickup the current figure
fig = plt.gcf() 

# save this figure
fig.savefig("Mayer_Susan_Q5_3.pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)

pvt_cnt = 1000

# Additional investigation:  Focus on Private funding - Plot Private funded vax by year, color coded by vaxtype
df_pvt = df_vax_by_year[(df_vax_by_year['V_FUNDBY']=="PVT") & (df_vax_by_year['vax_by_year_count']>pvt_cnt)]
df_pvt_pivot = df_pvt.pivot_table(index='YearofReport', columns='VAX_TYPE', values='vax_by_year_count')
fig = plt.figure()
colors = colormap(np.linspace(0, 1, df_pvt['VAX_TYPE'].nunique()))
df_pvt_pivot.plot(kind='bar', stacked=True, color=colors)
plt.legend(title="Vaccine Type", loc='upper center', bbox_to_anchor=(0.5,-0.2))

plt.title(f'Private-Funded Vaccines AE Reports >{pvt_cnt} by Year, Vaccine Type')
plt.xlabel('Year of Report')
plt.ylabel('Total Private-Funded Vaccines Reported')

plt.grid(True)
# save dataframe to file

# Force to pickup the current figure
fig = plt.gcf() 

# save this figure
fig.savefig("Mayer_Susan_Q5_4.pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)

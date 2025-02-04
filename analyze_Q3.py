first_name = "Susan" # put your first name here, inside the ""
last_name  = "Mayer" # put your last name here, inside the ""
# Q3: Are residents of specific states more likely to report serious adverse events?  More likely to report "Not adverse event" reports?
# Load libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import shapely.geometry as sgeom

# Parameters
min_year = 1990
max_year = 2024
analyzer_year = 2021
# Validate that parameters are present.
assert (min_year & max_year & analyzer_year and max_year >= min_year and max_year > analyzer_year and min_year <= analyzer_year)  


# Initialize dataframes
df_tot_vaers = pd.DataFrame()  # Create an empty DataFrame
df_tot_vax = pd.DataFrame()  # Create an empty DataFrame
df_tot_sympt = pd.DataFrame()  # Create an empty DataFrame

with open('prep.py') as f:
    exec(f.read()) 
        
# Create a copy of df_tot_vaers filtered to year analyzer_year to present
df_tot_vaers_analyzer = df_tot_vaers[df_tot_vaers['YearofReport']>analyzer_year]
    
# Create a dataframe containing the State Name, total reports, total serious reports

states_counts = df_tot_vaers_analyzer.groupby('Serious')['STATE'].value_counts()
df_states = states_counts.to_frame()

# Reset the index and rename columns for clarity
df_states = df_states.reset_index()

df_pivot_states = df_states.pivot(index='STATE', columns='Serious', values='count')
df_pivot_states = df_pivot_states.reset_index()
df_pivot_states.columns = ['STATE','Serious', 'NonSerious']
df_pivot_states.fillna(0, inplace=True)
df_pivot_states['Total'] = df_pivot_states['Serious']+df_pivot_states['NonSerious']
df_pivot_states['PctSerious'] = df_pivot_states['Serious']*100/df_pivot_states['Total']

#Remove territories other than 50 states and DC for mapping purposes and use state name for map functions
state_name_dict = {
 'AL':'Alabama',
 'AK':'Alaska',
 'AZ':'Arizona',
 'AR':'Arkansas',
 'CA':'California',
 'CO':'Colorado',
 'CT':'Connecticut',
 'DE':'Delaware',
 'FL':'Florida',
 'GA':'Georgia',
 'HI':'Hawaii',
 'ID':'Idaho',
 'IL':'Illinois',
 'IN':'Indiana',
 'IA':'Iowa',
 'KS':'Kansas',
 'KY':'Kentucky',
 'LA':'Louisiana',
 'ME':'Maine',
 'MD':'Maryland',
 'MA':'Massachusetts',
 'MI':'Michigan',
 'MN':'Minnesota',
 'MS':'Mississippi',
 'MO':'Missouri',
 'MT':'Montana',
 'NE':'Nebraska',
 'NV':'Nevada',
 'NH':'New Hampshire',
 'NJ':'New Jersey',
 'NM':'New Mexico',
 'NY':'New York',
 'NC':'North Carolina',
 'ND':'North Dakota',
 'OH':'Ohio',
 'OK':'Oklahoma',
 'OR':'Oregon',
 'PA':'Pennsylvania',
 'RI':'Rhode Island',
 'SC':'South Carolina',
 'SD':'South Dakota',
 'TN':'Tennessee',
 'TX':'Texas',
 'UT':'Utah',
 'VT':'Vermont',
 'VA':'Virginia',
 'WA':'Washington',
 'WV':'West Virginia',
 'WI':'Wisconsin',
 'WY':'Wyoming',
 'DC':'District of Columbia'
# Commenting out other territories, but retaining if needed in future
# ,
# 'AS':'American Samoa',
# 'GU':'Guam',
# 'MP':'Northern Mariana Islands',
# 'PR':'Puerto Rico',
# 'UM':'United States Minor Outlying Islands',
# 'VI':'Virgin Islands U.S.'
}
    
df_pivot_states['StateName'] = df_pivot_states['STATE'].map(state_name_dict)
    
df_pivot_states = df_pivot_states[df_pivot_states['StateName'].str.len() > 0]

# A function that draws inset map, ++
# Based on function found at:
# https://stackoverflow.com/questions/55598249/showing-alaska-and-hawaii-in-cartopy-map
# ===================================
def add_insetmap(axes_extent, map_extent, state_name, facecolor, edgecolor, geometry):
    # create new axes, set its projection
    use_projection = ccrs.Mercator()     # preserve shape well
    #use_projection = ccrs.PlateCarree()   # large distortion in E-W for Alaska
    geodetic = ccrs.Geodetic(globe=ccrs.Globe(datum='WGS84'))
    sub_ax = plt.axes(axes_extent, projection=use_projection)  # normal units
    sub_ax.set_extent(map_extent, geodetic)  # map extents

    # add basic land, coastlines of the map
    # you may comment out if you don't need them
    #sub_ax.add_feature(ccrs.feature.LAND)
    sub_ax.coastlines()

    sub_ax.set_title(state_name)

    # add map `geometry` here
    sub_ax.add_geometries([geometry], ccrs.PlateCarree(), \
                          facecolor=facecolor, edgecolor=edgecolor)
    # +++ more features can be added here +++

    # plot box around the map
    extent_box = sgeom.box(map_extent[0], map_extent[2], map_extent[1], map_extent[3])
    sub_ax.add_geometries([extent_box], ccrs.PlateCarree(), color='none', linewidth=0.05)


fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal())

ax.set_extent([-125, -66.5, 20, 50], ccrs.Geodetic())

states_shp = shpreader.natural_earth(resolution='110m'
                                     , category='cultural'
                                     , name='admin_1_states_provinces')


ax.set_title(f'Map of United States Colored by Percent of Adverse Event Reports that were Serious {analyzer_year}-{max_year}')
min_serious = df_pivot_states['PctSerious'].min() 
max_serious = df_pivot_states['PctSerious'].max() 

norm = mpl.colors.Normalize(vmin=min_serious, vmax=max_serious)
cmap = plt.cm.RdYlBu_r

for state in shpreader.Reader(states_shp).records():

    edgecolor = 'black'
    try:
        # use the name of this state to get pop_density
        df_row = df_pivot_states[df_pivot_states['StateName']==state.attributes['name']]
        state_pctser = df_row['PctSerious'].values[0]
    except:
        state_pctser = 0

    # simple scheme to assign color to each state
    facecolor = cmap(norm(state_pctser))
    
    # special handling for the 2 states
    # ---------------------------------
    if state.attributes['name'] in ("Alaska", "Hawaii"):

        state_name = state.attributes['name']

        # prep map settings
        # experiment with the numbers in both `_extents` for your best results
        if state_name == "Alaska":
            # (1) Alaska
            map_extent = (-178, -135, 46, 73)    # degrees: (lonmin,lonmax,latmin,latmax)
            axes_extent = (0.04, 0.06, 0.29, 0.275) # axes units: 0 to 1, (LLx,LLy,width,height)

        if state_name == "Hawaii":
            # (2) Hawii
            map_extent = (-162, -152, 15, 25)
            axes_extent = (0.27, 0.06, 0.15, 0.15)


    # add inset maps
        add_insetmap(axes_extent, map_extent, state_name, \
                     facecolor, \
                     edgecolor, \
                     state.geometry)

    # the other (conterminous) states go here
    else:
        # `state.geometry` is the polygon to plot
        ax.add_geometries([state.geometry], ccrs.PlateCarree(),
                          facecolor=facecolor, edgecolor=edgecolor)

cax = fig.add_axes([1.0, 0.2, 0.02, 0.6])
cb = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, spacing='proportional')
cb.set_label('Percent of AEs -> Serious')

plt.show()
# save plot SeriousPct by State dataframe to file
fig.savefig("Mayer_Susan_Q3_1.pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)

# save SeriousPct by State dataframe to file
df_pivot_states.to_csv('Mayer_Susan_Q3_df_pivot_states.csv')

# Focus on 5 states reporting lowest percentage of serious AEs
low_5_states = ['MI','KY','SD','MN','AR']
df_limit = df_tot_vaers_analyzer[(df_tot_vaers_analyzer['Serious']==False) & (df_tot_vaers_analyzer['STATE'].isin(low_5_states))]

# save state limited Non-Serious Reports to file
df_limit.to_csv('Mayer_Susan_Q3_df_limit.csv')

# Combine with symptom list

df_nonserious_sympt = df_tot_sympt[df_tot_sympt['VAERS_ID'].isin(df_limit['VAERS_ID'])]

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

df_ns_sympt_pivot = sympt_pivot(symptom_columns, df_nonserious_sympt)

df_ns_sympt_pivot_count = df_ns_sympt_pivot.groupby(['YearofReport','Symptom'])['Symptom'].value_counts()
# save non-serious symptom list to file
df_limit.to_csv('Mayer_Susan_Q3_df_limit.csv')

# Review showed a number of "No adverse event" reports - Investigate by state
noae_txt = 'No adverse event'
df_notae = df_tot_sympt[(df_tot_sympt['SYMPTOM1']==noae_txt)
                       |(df_tot_sympt['SYMPTOM2']==noae_txt)
                       |(df_tot_sympt['SYMPTOM3']==noae_txt)
                       |(df_tot_sympt['SYMPTOM4']==noae_txt)
                       |(df_tot_sympt['SYMPTOM5']==noae_txt)
                       ]
df_notae_vaers = df_tot_vaers_analyzer[df_tot_vaers_analyzer['VAERS_ID'].isin(df_notae['VAERS_ID'])]
notae_vaers_count = df_notae_vaers.groupby(['STATE'])['STATE'].value_counts()
df_notae_vaers_count = notae_vaers_count.to_frame()
df_notae_vaers_count  = df_notae_vaers_count.reset_index()

df_notae_vaers_count['Total'] = df_notae_vaers_count['STATE'].map(df_pivot_states.set_index('STATE')['Total'])
df_notae_vaers_count = df_notae_vaers_count[df_notae_vaers_count['Total'].notna()]
df_notae_vaers_count['PctNotAE'] = df_notae_vaers_count['count']*100/df_notae_vaers_count['Total']

df_notae_vaers_count.to_csv('Mayer_Susan_Q3_df_notae.csv')

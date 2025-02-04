first_name = "Susan" # put your first name here, inside the ""
last_name  = "Mayer" # put your last name here, inside the ""
#Q4 Is the tone of the free text of the report impacted by the patient’s age?
#Investigation will include reviewing the compound score results from the SentimentIntensityAnalyzer 

# Load libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('all')


# Parameters
min_year = 1990
max_year = 2024
analyzer_year = 2020
# Validate that parameters are present.
assert (min_year & max_year & analyzer_year and max_year >= min_year and max_year >= analyzer_year and min_year <= analyzer_year)  


# Initialize dataframes

df_tot_vaers = pd.DataFrame()  # Create an empty DataFrame
df_tot_vax = pd.DataFrame()  # Create an empty DataFrame
df_tot_sympt = pd.DataFrame()  # Create an empty DataFrame

with open('prep.py') as f:
    exec(f.read()) 
        
# Setup for SentimentIntensityAnalyzer
scores = []

def analyzer(pg_text):
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(str(pg_text))
    return scores

# From assignment:
# I would recommend tokenizing and removing stopwords before computing sentiment, 
# as it will give you better results.
def prepare(pg_text):
    # Tokenize
    tokenized = nltk.tokenize.word_tokenize(str(pg_text))

    # Remove Stopwords
    stopwords = nltk.corpus.stopwords.words("english")
    tokenized = [t for t in tokenized if t not in stopwords]
    return " ".join(tokenized)

# Prepare symptom text for analyzer
df_tot_vaers['SYMPTOM_TEXT'] = df_tot_vaers['SYMPTOM_TEXT'].map(prepare)

# Create a copy of df_tot_vaers filtered to year analyzer_year to present
df_tot_vaers_analyzer = df_tot_vaers[df_tot_vaers['YearofReport']>analyzer_year]

# In effort to narrow, the data was filtered to only include reports including COVID vaccinations
df_vax_covid = df_tot_vax[df_tot_vax["VAX_TYPE"].astype(str).str.startswith("COVID")]
df_covid =  df_tot_vaers_analyzer[(df_tot_vaers_analyzer['Serious'] == True) & (df_tot_vaers_analyzer['VAERS_ID'].isin(df_vax_covid['VAERS_ID']))]

# Loop through rows
for pagetext in df_covid['SYMPTOM_TEXT']:
    # Collect results temporarily in a list scores
    scores.append(analyzer(pagetext))

# Convert list score to dataframe scores_df
df_scores = pd.DataFrame(scores)
df_covid = df_covid.reset_index();
df_covid_score = pd.concat([df_covid, df_scores], axis=1)
#df_tot_vaers_analyzer = pd.concat([df_tot_vaers_analyzer, scores_df[['neg', 'neu', 'pos', 'compound']]], axis=1)
#df_covid = pd.concat([df_covid, scores_df[['neg', 'neu', 'pos', 'compound']]], axis=1)

# for the SYMPTOM_TEXT versus Age of Patient at Time of event for potential relationships.
# Create a scatterplot - Serious AEs only
fig = plt.figure()
plt.scatter(df_covid_score['AGE_YRS']
            , df_covid_score['compound'])
#plt.scatter(df_serious_analyzer['AGE_YRS']
#            , df_serious_analyzer['compound'])
plt.title(f'Compound Score vs. Patient Age ({analyzer_year}-{max_year})')
plt.xlabel('Patient Age (Years)')
plt.ylabel('Sentiment Analysis Compound Score')

# save this figure
fig.savefig("Mayer_Susan_Q4_1.pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)
plt.show()

# Create the boxplot
fig = plt.figure()
plt.figure(figsize=(10, 6))
ax = sns.boxplot(x="age_block",
                y="compound",
                data = df_covid_score)
#                data=df_serious_analyzer)
plt.title(f'Sentiment Analysis Compound Score vs. Patient Age Group ({analyzer_year}-{max_year})')
plt.xlabel('Patient Age (Years)')
plt.ylabel('Sentiment Analysis Compound Score')

# Save the plot to a file
plt.savefig("Mayer_Susan_Q4_2.pdf", format="pdf", bbox_inches="tight", dpi=fig.dpi)
plt.show()

# save dataframe to file
df_covid_score_out = df_covid_score[['VAERS_ID','age_block','SYMPTOM_TEXT','compound']]
df_covid_score.to_csv('Mayer_Susan_Q4_df_covid_score.csv')




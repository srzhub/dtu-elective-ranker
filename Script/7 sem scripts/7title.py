import pandas as pd

'''
The subject names were still not standardised so I used a script to convert them into title format and
then convert them into JSON format for use in my JS file. 
'''

pd_title = pd.read_excel("subject_data_7sem_filled.xlsx")

pd_title["title"] = pd_title["title"].str.title()
pd_title["title"] = pd_title["title"].str.strip()

pd_title.to_excel("subject_data_w_title.xlsx", index=False)


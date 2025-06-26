import pandas as pd

pd_title = pd.read_excel("subject_data_with_names2 _filter_noCount-Copy.xlsx")

pd_title["title"] = pd_title["title"].str.title()
pd_title["title"] = pd_title["title"].str.strip()

pd_title.to_excel("subject_data_w_title.xlsx", index=False)


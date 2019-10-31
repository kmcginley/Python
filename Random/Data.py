import pandas as pd
import csv
import plotly.express as px

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def getfile():
    df = pd.read_csv('EXP19000414_raw_data.csv')
    df = df[['Agent_name', 'Replicate_number', 'Wells', 'Day7_area']]
    #df = mydf[(mydf['Agent_name']!='water-man')&(mydf['Agent_name']!='water-auto')]
    new = df['Agent_name'].str.split('-', expand=True)

    df['Method']=new[1]
    df['Agent_name']=new[0]
    df = df.groupby(['Method','Agent_name', 'Replicate_number'], as_index=False).agg({'Day7_area': 'std'})

    return df


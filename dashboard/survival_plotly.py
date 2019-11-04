# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%%
#from IPython import get_ipython

#%%
#this script is to make survival curve graphs for multiple (grouped) treatments with columns 'group', 'event', and 'time'
# the data format includes 0's and 1's for each event observation
import sys
#get_ipython().system('{sys.executable} -m pip install lifelines')

#install pandas and matlab plot 
import plotly
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib
from plotly.tools import mpl_to_plotly

#install kaplan meier fit graphing
from lifelines import KaplanMeierFitter
from io import BytesIO
import base64
#plotly.offline.iplot_mpl
matplotlib.use('Agg')


def fig_to_uri(in_fig, close_all=True, **save_args):
    # type: (plt.Figure) -> str
    """
    Save a figure as a URI
    :param in_fig:
    :return:
    """
    out_img = BytesIO()
    in_fig.savefig(out_img, format='png', **save_args)
    if close_all:
        in_fig.clf()
        plt.close('all')
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)


# install lifelines package
def plot1(df):
    # import sys
    # #get_ipython().system('{sys.executable} -m pip install lifelines')

    # #install pandas and matlab plot 

    # import pandas as pd 
    # import matplotlib.pyplot as plt


    # #install kaplan meier fit graphing
    # from lifelines import KaplanMeierFitter

    # import os
    # os.chdir("/Users/MDONEGAN/Downloads")

    # import survival data from Experiment 134
    #survival= pd.read_csv("EXP240_setup.csv")
    survival = df

    # create an kmf object
    kmf = KaplanMeierFitter() 

    ax = plt.subplot(111)


    #group dataset by treatment and plot all groups (treatments) using kmf fit 
    for name, grouped_survival in survival.groupby('group'):
        kmf.fit(grouped_survival['time'], grouped_survival['event'], label=name)
        kmf.plot(ax=ax, ci_show=False, marker='o')
        
    plt.xlabel("days")
    plt.ylabel("survival proportion")
    plt.ylim(0,1.05)

    
    #return convert_plot(plt.Figure)

    #return plt.Figure

    return fig_to_uri(plt)




#%%
#this script is to make survival curve graphs for multiple (grouped) treatments
# the data format includes 0's and 1's for each observation

#subset the dataset into stacks and plot only the stacks and water
def plot2(df):
    survival = df
    kmf = KaplanMeierFitter() 

    ax = plt.subplot(111)

    stacks = ['water', 'Val1000']
        
    stacks_graph = survival.loc[survival['group'].isin(stacks)]


    for name, grouped_survival in stacks_graph.groupby('group'):
        kmf.fit(grouped_survival['time'], grouped_survival['event'], label=name)
        kmf.plot(ax=ax, ci_show=False, marker='o')
    plt.xlabel("days")
    plt.ylabel("survival proportion")
    plt.ylim(-0.05,1.05)


    #%%
    # subset the dataset into Val50 treatments and water and plot 

    kmf = KaplanMeierFitter() 

    ax = plt.subplot(111)
        
    val = ['water', 'Ryan']
        
    val_graph = survival.loc[survival['group'].isin(val)]



    for name, grouped_survival in val_graph.groupby('group'):
        kmf.fit(grouped_survival['time'], grouped_survival['event'], label=name)
        kmf.plot(ax=ax, ci_show=False, marker='o')
    plt.xlabel("days")
    plt.ylabel("survival proportion")
    plt.ylim(-0.05,1.05)


    #%%
    # subset the dataset by pumice formulations and plot 

    kmf = KaplanMeierFitter() 

    ax = plt.subplot(111)

    pumice = ['water', 'BBG']
        
    pum_graph = survival.loc[survival['group'].isin(pumice)]


    for name, grouped_survival in pum_graph.groupby('group'):
        kmf.fit(grouped_survival['time'], grouped_survival['event'], label=name)
        kmf.plot(ax=ax, ci_show=False, marker='o')

    plt.xlabel("days")
    plt.ylabel("survival proportion")
    plt.ylim(-0.05,1.05)

    return plt.show()

#%%
# This script runs a pairwise log rank test to compare multi-day survival curves between all treatments
def plot3(df):
    import sys
    #get_ipython().system('{sys.executable} -m pip install lifelines')

    #install pandas and matlab plot 

    import pandas as pd 
    import matplotlib.pyplot as plt

    from lifelines import KaplanMeierFitter

    # import os
    # os.chdir("/Users/MDONEGAN/Downloads")

    #survival= pd.read_csv("/Users/MDONEGAN/Downloads/Book2.csv", sep=',')
    survival = df
        
    from lifelines.statistics import pairwise_logrank_test


    results= pairwise_logrank_test(survival['time'], survival['group'], survival['event'])

    results.print_summary()


    #%%
    # this util converts a table with "death" and "censored" (alive) into  the lifelines format


    from lifelines import KaplanMeierFitter
    from lifelines.utils import survival_events_from_table

    kmf = KaplanMeierFitter() 
    ax = plt.subplot(111)


    #df = pd.read_csv('/Users/MDONEGAN/Downloads/counts.csv')
    df = df.set_index('time')


    T,E,W= survival_events_from_table(df, observed_deaths_col= 'death', censored_col='censored')

    kmf.fit(T,E, weights=W)

    kmf.plot(ax=ax, ci_show=True,marker='o')
    plt.xlabel("days")
    plt.ylabel("survival %")
    plt.ylim(0.4,1.05)


    #%%
    #trying to combine the grouping function and the events from table function


    from lifelines import KaplanMeierFitter
    from lifelines.utils import survival_events_from_table

    kmf = KaplanMeierFitter() 
    ax = plt.subplot(111)

    #df = pd.read_csv('/Users/MDONEGAN/Downloads/counts.csv')
    df = df.set_index('time')




    T,E,W= survival_events_from_table(df, observed_deaths_col= 'death', censored_col='censored')

    print(E)

    #group dataset by treatment and plot all groups (treatments) using kmf fit 
    for name, T_group,E_group,W_group in T,E,W.groupby('group'):
        kmf.fit(grouped_survival['T'], grouped_survival['E'], label=name)
        kmf.plot(ax=ax, ci_show=False, marker='o')
        plt.xlabel("days")
        plt.ylabel("survival %")
        plt.ylim(0.4,1.05)


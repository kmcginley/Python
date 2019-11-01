import pandas as pd
import seaborn as sns, matplotlib.pyplot as plt
import matplotlib
from statannot import add_stat_annotation

import numpy as np
from io import BytesIO
import base64
from app import leafDisk

matplotlib.use('agg')


def get_ttest_plot():
    df = pd.read_csv('/Users/kmcginley/Downloads/EXP19000414_raw_data.csv')
    df, mydf = leafDisk(df)
    ax = sns.boxplot(data=df, x='Agent_name', y='Day7_area')
    add_stat_annotation(ax, data=df, x='Day7_area', y='Agent_name',
                    box_pairs=[(('water'),('val 100'))],
                    test='t-test_ind', text_format='full', loc='inside', verbose=2)
    return fig_to_uri(in_fig = plt)

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
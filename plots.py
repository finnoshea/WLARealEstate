
import pandas as pd
import matplotlib.pyplot as plt

from .resources.defaults import DEFAULT_ZIPS, DEFAULT_LOC

from typing import Union


def make_zipcode_plot(df: pd.DataFrame,
                      plot_what: str = 'DTTSalePrice',
                      index: Union[str, None] = 'UrbanShelterIndex') -> None:
    """

    Parameters
    ----------
    df : pandas dataframe
        Dataframe of housing information produced by json_reader.
    plot_what : str
        The column name in df to plot.  Usually 'DTTSalePrice' or
        'AssessedValue'.
    index : str
        Which inflation index to use.  Usually 'LAGoodsIndex' or
        'UrbanShelterIndex'.

    Returns
    -------
    Nothing.
    """
    if index is None:
        divisor = df['ZipCode'].copy(deep=False).values.fill(1)
    else:
        divisor = df[index]
    x = df['RecordingDate']
    y = 100 * df[plot_what] / divisor

    colors = ['r', 'b', 'm']
    fig, axs = plt.subplots(3, 1, sharex='col', figsize=(8, 8))
    for zipcode, color, ax in zip(DEFAULT_ZIPS, colors, axs):
        strzc = str(zipcode)
        mask = (df['ZipCode'] == zipcode) & (df[plot_what] > 1000)
        ax.scatter(x[mask], y[mask], s=1, c=color, marker='.', label=strzc)
        ax.set_yscale('log')
        ax.set_ylabel('June 2019 Dollars')
        ax.set_title(strzc + ' : ' + index)
        if ax == axs[-1]:
            ax.set_xlabel('RecordingDate')
    plt.show()

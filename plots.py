
import pandas as pd
import matplotlib.pyplot as plt

from .resources.defaults import DEFAULT_ZIPS, DEFAULT_LOC

from typing import Union, List


def make_zipcode_plot(df: pd.DataFrame,
                      plot_what: str = 'AssessedValue',
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
    fig, axs = plt.subplots(len(DEFAULT_ZIPS), 1, sharex='col', figsize=(8, 8))
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


def make_bedroom_plots(df: pd.DataFrame,
                       beds: List[int] = [1, 2, 3],
                       plot_what: str = 'DTTSalePrice',
                       index: Union[str, None] = 'CPI-WIndex',
                       logplot: bool = True) -> None:
    """

    Parameters
    ----------
    df : pandas dataframe
        Dataframe of housing information produced by json_reader.
    beds : List[int]
        Make the plot for these numbers of bedrooms.
    plot_what : str
        The column name in df to plot.  Usually 'DTTSalePrice' or
        'AssessedValue'.
    index : str
        Which inflation index to use.  Usually 'LAGoodsIndex' or
        'UrbanShelterIndex'.
    logplot : bool
        Whether the vertical scale should be log (True) or linear (False).

    Returns
    -------
    Nothing.
    """
    if index is None:
        df['divisor'] = pd.Series(1, df.index, name='divisor')
    else:
        df['divisor'] = df[index]

    price_mask = (df[plot_what] < 1e7) & (df[plot_what] > 1e5)
    df2 = df[price_mask]

    colors = ['r', 'b', 'm']
    markers = ['o', 's', 'x']
    fig, axs = plt.subplots(len(DEFAULT_ZIPS), 1, sharex='col', figsize=(8, 8))
    for bed in beds:
        subdf = df2[df2['NumOfBeds'] == bed].dropna(inplace=False,
                                                    subset=[plot_what])
        x = subdf['RecordingDate']
        y = 100 * subdf[plot_what] / subdf['divisor']
        color = colors[bed % len(colors)]
        marker = markers[bed % len(markers)]
        for zipcode, ax in zip(DEFAULT_ZIPS, axs):
            strzc = str(zipcode)
            mask = subdf['ZipCode'] == zipcode
            meds = []
            for year in [2006, 2020]:
                year_mask = pd.DatetimeIndex(x).year == year
                meds.append(y[mask & year_mask].median())
            aprec = 100 * (meds[1] - meds[0]) / meds[0]
            label = str(bed) + ' beds ' + '{:3.1f}%'.format(aprec)
            ax.scatter(x[mask], y[mask], s=2, c=color,
                       marker=marker, label=label)
            ax.axhline(meds[0],
                       color=color, linestyle='dashed')
            if logplot:
                ax.set_yscale('log')
            ax.set_ylabel(plot_what)
            ax.set_title(strzc + ' : ' + str(index) +
                         ' : ' + 'Jan 2000 Dollars')
            ax.legend(loc='upper left')
            if ax == axs[-1]:
                ax.set_xlabel('RecordingDate')
    plt.show()





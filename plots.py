
import pandas as pd
import matplotlib.pyplot as plt

from .resources.defaults import DEFAULT_ZIPS, DEFAULT_LOC

from typing import Union, List


def median_by_year_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the median of a column grouping by year and month first.

    Parameters
    ----------
    df : pandas dataframe
        Two column dataframe with the first column a datetime and the
        second a float

    Returns
    -------
    pandas dataframe
    """
    dt = pd.DatetimeIndex(df[df.columns[0]])
    gb = df.groupby([dt.year, dt.month]).median()
    gb.index = pd.to_datetime(gb.index.map(
        lambda x: '{:d} {:d} 15'.format(x[0], x[1])
    ))
    return gb


def median_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the median of a column grouping by year.

    NOTE: The x + 1 in the format is to conform to the convention on step
    plots wherein the height of the line between points p and p + 1 is
    given by the value at p + 1.  In order for the line during 2018,
    for example, to be at the correct height, I have to set it to the date
    2019-01-01.

    Parameters
    ----------
    df : pandas dataframe
        Two column dataframe with the first column a datetime and the
        second a float

    Returns
    -------
    pandas dataframe
    """
    dt = pd.DatetimeIndex(df[df.columns[0]])
    gb = df.groupby([dt.year]).median()
    gb.index = pd.to_datetime(gb.index.map(
        lambda x: '{:d}'.format(x + 1)
    ))
    return gb

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
        xy = pd.DataFrame({'time': subdf['RecordingDate'],
                           'value': 100 * subdf[plot_what] / subdf['divisor']})
        color = colors[bed % len(colors)]
        marker = markers[bed % len(markers)]
        for zipcode, ax in zip(DEFAULT_ZIPS, axs):
            strzc = str(zipcode)
            mask = subdf['ZipCode'] == zipcode
            meds = []
            for year in [2006, 2020]:
                year_mask = pd.DatetimeIndex(xy['time']).year == year
                meds.append(xy[mask & year_mask].loc[:, 'value'].median())
            aprec = 100 * (meds[1] - meds[0]) / meds[0]
            label = str(bed) + ' beds ' + '{: 3.1f}%'.format(aprec)
            ax.scatter(xy[mask].loc[:, 'time'],
                       xy[mask].loc[:, 'value'],
                       s=2, c=color, marker=marker,
                       label=label, alpha=0.3)
            # the following makes the plot too busy
            # ax.axhline(meds[0],
            #            color=color, linestyle='dashed')
            trend = median_by_year(xy[mask])
            ax.step(x=trend.index, y=trend['value'],
                    color=color, linestyle='solid')
            if logplot:
                ax.set_yscale('log')
            ax.set_ylabel(plot_what)
            ax.set_title(strzc + ' : ' + str(index) +
                         ' : ' + 'Jan 2000 Dollars')
            ax.legend(loc='upper left')
            if ax == axs[-1]:
                ax.set_xlabel('RecordingDate')
    plt.show()





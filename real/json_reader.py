
import os
import json
from datetime import datetime
from numpy import nan

import pandas as pd
import matplotlib.pyplot as plt

from typing import Union, Any

from ..resources.defaults import DEFAULT_LOC, DEFAULT_ZIPS, coerce_details


TEST_FILE = "4248001002.json"
JSON_LOC = DEFAULT_LOC
ASSESSED_VALUES = []
FILE_COUNT = 0
DATE_COLUMNS = ["PDBEffectiveDate", "RecordingDate",
                "CreateDate", "DeleteDate"]
NUMBER_COLUMNS = ['AIN', 'Longitude', 'Latitude', 'NumOfUnits', 'YearBuilt',
                  'SqftMain', 'SqftLot', 'NumOfBeds', 'NumOfBaths',
                  'LandWidth', 'LandDepth', 'SaleNumber',
                  'AssessedValue']

def make_year_month(x: str) -> str:
    """ changes a time format of %b %Y to %Y-%m """
    if x == 'Series ID':
        return x
    dt = datetime.strptime(x, '%b %Y')
    return '{:d}-{:02d}'.format(dt.year, dt.month)

# data from: https://data.bls.gov/pdq/SurveyOutputServlet
# create an inflation dataframe from January 1975 to November 2021
# CWUR0000SAH1 = CPI for Urban Wage Earners and Clerical Workers (CPI-W)
# CWURS49ASA0 = All items in Los Angeles-Long Beach-Anaheim, CA,
# urban wage earners and clerical workers, not seasonally adjusted
inflation_df = pd.read_csv(os.sep.join([DEFAULT_LOC, 'inflation.txt']))
inflation_df.drop(
    list(inflation_df.filter(regex='Annual|HALF')),
    axis=1, inplace=True)
inflation_df = inflation_df.T
inflation_df.drop(index='Series ID', inplace=True)  # delete the series names
inflation_df.rename(columns={0: 'UrbanShelter', 1: 'LAGoods'}, inplace=True)
inflation_df.index = inflation_df.index.map(make_year_month)
inflation_df.loc['2021-12'] = inflation_df.loc['2021-11']  # use Nov for Dec
# re-index inflation to June 2019
for col in inflation_df.columns:
    inflation_df[col] = 100 * inflation_df[col] / \
                        inflation_df.loc['2019-06', col]


def get_assessed_values(filename: str, loc: str = DEFAULT_LOC) -> list:
    avs: list = []
    fn = os.sep.join([loc, filename])
    with open(fn) as f:
        dd = json.load(f)
        try:
            sales = dd["ownership"]["Parcel_OwnershipHistory"]
            details = coerce_details(dd["details"]["Parcel"])
            del details["SubPartNumber"]  # don't care about SubParts
            del details["SubParts"]
            del details["LandAcres"]  # almost always NaN
        except KeyError:
            return []  # some might not have an ownership history
        else:
            for sale in sales:  # sales is a list
                ds = {}
                try:
                    ds.update(details)
                    ds.update(sale)
                except KeyError:
                    pass
                else:
                    avs.append(ds)
    return avs


for idx, file_name in enumerate(os.listdir(JSON_LOC)):
    if '.json' in file_name:
        ASSESSED_VALUES.extend(get_assessed_values(file_name, JSON_LOC))
        FILE_COUNT += 1
    if FILE_COUNT > 100:
        break


print('Processed {:d} json files.'.format(FILE_COUNT))

df: pd.DataFrame = pd.DataFrame(ASSESSED_VALUES)
# some special cases
# df['ZipCode'] = df['SitusZipCode'].apply(lambda x: x[:5])  # 5-digit zipcodes
# for col in DATE_COLUMNS:
#     df[col] = df[col].apply(coerce_date)
# df[NUMBER_COLUMNS] = df[NUMBER_COLUMNS].apply(pd.to_numeric, errors='coerce')
# print('Shape before dropna: ', df.shape)
# df.dropna(subset=NUMBER_COLUMNS, inplace=True)
# print('Shape after dropna: ', df.shape)
# # only go back to 1980
# date_mask = df['RecordingDate'] > datetime(year=1979, month=12, day=31)
# df = df[date_mask]
# period_series = pd.to_datetime(df['RecordingDate']
#                                ).dt.to_period('M').astype(str).tolist()
# for col in inflation_df.columns:
#     df[col + 'Index'] = inflation_df.loc[period_series, col].values


def make_zipcode_plot(index: Union[str, None] = 'UrbanShelterIndex') -> None:
    if index is None:
        divisor = df['ZipCode'].copy(deep=False).values.fill(1)
    else:
        divisor = df[index]
    x = df['RecordingDate']
    y = 100 * df['AssessedValue'] / divisor

    colors = ['r', 'b', 'm']
    fig, axs = plt.subplots(3, 1, sharex='col', figsize=(8, 8))
    for zipcode, color, ax in zip(DEFAULT_ZIPS, colors, axs):
        strzc = str(zipcode)
        mask = df['ZipCode'] == strzc
        ax.scatter(x[mask], y[mask], s=1, c=color, marker='.', label=strzc)
        ax.set_yscale('log')
        ax.set_ylabel('June 2019 Dollars')
        ax.set_title(str(zipcode) + ' : ' + index)
        if ax == axs[-1]:
            ax.set_xlabel('RecordingDate')
    plt.show()

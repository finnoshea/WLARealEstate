
import numpy as np
import pandas as pd
from typing import List, Generator

from ..resources.defaults import ADDRESS_FILE, DEFAULT_ZIPS


def get_address_csv(af: str = ADDRESS_FILE) -> pd.DataFrame:
    """
    Creates a dataframe from a CSV file.

    Parameters
    ----------
    af : str
        The address file.

    Returns
    -------
    pandas dataframe
    """
    return pd.read_csv(af)


def prune_by_zipcode(df: pd.DataFrame,
                     zipcodes: List[int] = DEFAULT_ZIPS) -> pd.DataFrame:
    """
    Masks the dataframe to only contain the desired zip codes.
    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to mask
    zipcodes : List[int]
        The zip codes to keep.

    Returns
    -------
    pandas dataframe
    """
    mask = pd.Series([False] * df.shape[0], name='zip_mask', dtype=bool)
    for zipcode in zipcodes:
        new = df['ZIP_CD'] == zipcode
        mask = mask | new

    return df[mask].copy()


def yield_units(row: pd.Series) -> Generator[str, None, None]:
    """
    Yields all the unit numbers from the UNIT_RANGE column in the row.

    Parameters
    ----------
    row : pd.Series
        The row to process.

    Returns
    -------
    string generator
    """
    ur = row['UNIT_RANGE']
    # sometimes there are leading ( and trailing ), strip them
    ur = ur.split('(')[-1]
    ur = ur.split(')')[0]
    try:
        first, last = ur.split('-')
    except ValueError:  # not enough values to unpack
        first = ur
        last = ur
    try:
        int(first)  # try to coerce into an integer
    except ValueError:  # letters, deal with them
        for c in range(ord(first), ord(last) + 1):
            yield chr(c)
    else:  # deal with numbers
        for n in range(int(first), int(last) + 1):
            yield str(n)


def split_up_units(df: pd.DataFrame) -> pd.DataFrame:
    """
    Splits up the addresses to include the units (apartments) as
    separate entries.

    Parameters
    ----------
    df : pd.Dataframe
        The dataframe to parse out the units on.

    Returns
    -------
    pandas dataframe
    """
    df['UNIT'] = pd.Series(dtype=str)  # adds the UNIT column to the df

    rows = []  # this is going to grow really large
    # rows are tuples (index, columns), throw away the index
    for row in df.iterrows():
        try:
            _ = np.isnan(row[1]['UNIT_RANGE'])
        except TypeError:  # UNIT_RANGE is a string, just what we want
            for unit in yield_units(row[1]):
                t = row[1]
                t['UNIT'] = unit
                rows.append(t.copy())
        else:  # nan means no units in the building, just append
            rows.append(row[1].copy())
    return pd.DataFrame(rows).reset_index(drop=True)


def make_address_dict(row: pd.Series) -> dict:
    """
    Makes a dictionary out of an address.
    Parameters
    ----------
    row : pd.Series
        A row from an address dataframe.

    Returns
    -------
    dict
    """
    elements = ['HSE_NBR', 'HSE_FRAC_NBR', 'HSE_DIR_CD', 'STR_NM',
                'STR_SFX_CD', 'STR_SFX_DIR_CD', 'UNIT', 'ZIP_CD']
    dd = {}
    for elem in elements:
        t = row[elem]
        if not isinstance(t, float):  # NaNs are floats
            t = str(t)
        else:
            t = ''
        dd[elem] = t
    return dd


def make_address_string(row: pd.Series) -> str:
    """
    Makes a string of the address held in a row.

    Parameters
    ----------
    row : pd.Series
        A row from an address dataframe.

    Returns
    -------
    str
    """
    elements = ['HSE_NBR', 'HSE_FRAC_NBR', 'HSE_DIR_CD', 'STR_NM',
                'STR_SFX_CD', 'STR_SFX_DIR_CD', 'UNIT', 'ZIP_CD']
    adr = []
    for elem in elements:
        t = row[elem]
        if not isinstance(t, float):  # NaNs are floats
            # if elem == 'UNIT':  # special case
            #     t = 'UNIT ' + str(t)
            adr.append(str(t))
    return ' '.join(adr).replace('  ', ' ')


import requests
import json
import time
from random import random
import pandas as pd

from typing import List, Union, Tuple

from ..resources.defaults import TYPES, COLUMNS, DEFAULT_ZIPS, DEFAULT_LOC
from .addresses import (make_address_dict,
                        make_address_string
                        )

def basic_scrape(ain: int, info: str = 'details') -> Union[dict, None]:
    """ scrapes the LA Assessor's API for a particular piece of info """
    base_url = 'https://portal.assessor.lacounty.gov/api/'
    ain_url = '?ain='
    try:
        type_url = TYPES[info]
    except KeyError as e:
        print('Unknown information type {:s}'.format(info))
        print('Known types are {}'.format(list(TYPES.keys())))
        print(e)
    else:
        url = base_url + type_url + ain_url + str(ain)
        return requests.get(url).json()
    return None


def scrape(ain: int,
           infos: List[str] = list(TYPES.keys()),
           base_sleep: float = 1.0) -> dict:
    """
    Scrapes the LA Assessor's API for all information requested in infos.

    Parameters
    ----------
    ain : int
        The Assessor's ID Number (AIN) for the property.
    infos : List[str]
        The list of keys in TYPES variable to fetch from the server.
    base_sleep : float
        How long to sleep after an API call.  Prevents hammering the server.
        Time between calls is (random.random() + 1) * base_sleep

    Returns
    -------
    dict of json information
    """
    data = {}
    for info in infos:
        data[info] = basic_scrape(ain, info)
        time.sleep((random() + 1) * base_sleep)
    return data


def save_json(data: dict, name: str, location: str) -> None:
    """
    Dumps data to the json file.  Will overwrite the target file.

    Parameters
    ----------
    data : dict
        The data to save.
    name : str
        What to name the file.  .json will be appended.
    location: str
        Where to put the data.
    """
    fn = '/'.join([location, name + '.json'])
    with open(fn, 'w') as jf:
        json.dump(data, jf, indent=4)


def make_address_search_string(addr: dict) -> str:
    """
    Turns a dictionary address from .addresses.make_address_dict into a
    website compliant search string.

    Parameters
    ----------
    addr : dict
        A dictionary of the address.

    Returns
    -------
    str
    """
    base_url = 'https://portal.assessor.lacounty.gov/api/search?search='
    return base_url + '%20'.join(list(addr.values()))


def fuzzy_match(parcel: dict) -> bool:
    zipcode = parcel['SitusZipCode'][:5]
    try:
        zc = int(zipcode)
    except ValueError:
        return False  # not a valid zip code
    else:
        if zc not in DEFAULT_ZIPS:
            return False
    return True


def get_ain_from_address(new_rows: dict, addr: dict) -> dict:
    """
    Looks through the results of an LA Assessor's website search and tries
    to get an Assessor's ID Number (AIN) for the address given.

    Parameters
    ----------
    new_rows : dict
        Dictionary to append the new ains to
    addr : dict
        Address from .addresses.make_address_dict

    Returns
    -------
    new_rows with possibly new information added
    """
    # search for the address in the LA Assessor's database
    result = requests.get(make_address_search_string(addr)).json()
    for parcel in result['Parcels']:
        # do a fuzzy match on the address strings
        if fuzzy_match(parcel):
            # print('{} matched!'.format(make_address_string(addr)))
            # append the new value to new_rows
            for key, value in new_rows.items():
                value.append(parcel[key])
    return new_rows


def scrape_ains(address_df: pd.DataFrame,
                results_df: Union[pd.DataFrame, None] = None,
                number: Union[int, None] = None,
                base_sleep: float = 1.0
                ) -> Tuple[bool, pd.DataFrame, pd.DataFrame]:
    """
    Scrapes the Assessor's ID numbers (AINs) for "number" of the entries in df.

    Parameters
    ----------
    address_df : pd.DataFrame
        Pandas dataframe with addresses to scrape for.
    results_df : pd.DataFrame
        Dataframe to add discovered addresses to.
    number : int
        The number of previously un-scraped rows to scrape.
    base_sleep : float
        How long to sleep after an API call.  Prevents hammering the server.
        Time between calls is (random.random() + 1) * base_sleep

    Returns
    -------
    bool that is True if any scrapes were attempted and the pandas dataframe
    with new AINs added
    """
    # create the column for new dataframes
    if 'Searched' not in address_df.columns:
        address_df['Searched'] = pd.Series([False] * address_df.shape[0],
                                           dtype=bool)
    if results_df is None:  # create a new dataframe if necessary
        results_df = pd.DataFrame(columns=COLUMNS)

    # start the counter and break conditions
    if number is None:
        number = 9999999999999999
    count = 0
    scraped_any = False
    new_rows = {c: [] for c in COLUMNS}

    for index, row in address_df.iterrows():
        if row['Searched']:  # if this row has been searched already
            continue  # skip this row
        addr = make_address_dict(row)
        addr_str = make_address_string(addr)
        print('Searching for ({:d}/{:d}): {:s}'.format(index + 1,
                                                       address_df.shape[0],
                                                       addr_str))
        new_rows = get_ain_from_address(new_rows, addr)
        # update the address dataframe
        address_df.loc[index, 'Searched'] = True  # mark it searched
        count += 1
        scraped_any = True
        if count >= number:
            break  # all done
        time.sleep((random() + 1) * base_sleep)

    # add the new rows to results
    results_df = pd.concat([results_df, pd.DataFrame(new_rows)])\
        .drop_duplicates('AIN').reset_index(drop=True)
    return scraped_any, address_df, results_df


class AINData:
    """
    """
    def __init__(self, filename: str, ain_type: str = 'results'):
        """

        Parameters
        ----------
        filename : str
            File name to open.
        ain_type : str
            'results' for a results-type file: allows creation of an empty file
            'address' for an address-type file: must be populated before hand
        """
        self.filename = filename
        self.ain_type = ain_type
        self._df: Union[pd.DataFrame, None] = None

    def __enter__(self):
        try:
            self.df = pd.read_pickle(self.filename)
        except FileNotFoundError as e:  # if not found, create it maybe
            if self.ain_type == 'results':
                self.df = pd.DataFrame(columns=COLUMNS)
            else:
                print('ain_type="address" must be created before scraping')
                print(e)
                raise FileNotFoundError
        return self

    def __exit__(self, etype, evalue, etraceback):
        self.df.to_pickle(self.filename)


def scrape_ains_for_file(address_file: str,
                         results_file: Union[str, None] = None,
                         chunk_size: int = 100,
                         chunks: Union[int, None] = None,
                         base_sleep: float = 1.0
                         ) -> None:
    """
    Scrapes the LA Assessor's office website for Assessor's ID Numbers (AINs)
    in chunks.
    Parameters
    ----------
    address_file : str
        File to open and scrape with.  Pandas data pickle file.
    results_file : str
        File to add discovered AINs to.  Pandas data pickle file.
    chunk_size : int
        How many AINs to scrape between saves.
    chunks : int
        How many times to run chunk_size scrapes and then save.
    base_sleep : float
        How long to sleep after an API call.  Prevents hammering the server.
        Time between calls is (random.random() + 1) * base_sleep

    Returns
    -------
    Nothing.
    """
    if chunks is None:
        chunks = 999999999999999999
    chunk = 0
    keep_scraping = True
    with AINData(address_file, 'address') as add, \
            AINData(results_file, 'results') as res:
        while chunk < chunks and keep_scraping:
            keep_scraping, add.df, res.df = scrape_ains(address_df=add.df,
                                                        results_df=res.df,
                                                        number=chunk_size,
                                                        base_sleep=base_sleep
                                                        )
            chunk += 1
            print('results_df is now {:d} long'.format(res.df.shape[0]))


def scrape_data_for_ains(ain_df: pd.DataFrame,
                         number: int = 100,
                         location: Union[str, None] = None,
                         infos: List[str] = list(TYPES.keys()),
                         base_sleep: float = 1
                         ) -> bool:
    """
    Scrapes the data requested in infos for the rows in ain_df.
    This method is meant to be used with an AINData context manager.

    Parameters
    ----------
    ain_df : pd.DataFrame
        Dataframe with Assessor's ID Numbers to search for.
    number : int
        The number of records to scrape.
    location : str
        Directory where to store the scraped data.
    infos : dict
        dictionary of types to scrape for.  See defaults.py
    base_sleep : float
        How long to sleep after an API call.  Prevents hammering the server.
        Time between calls is (random.random() + 1) * base_sleep

    Returns
    -------
    Boolean: true if any data was scraped
    """
    # create the column for new dataframes
    if 'Scraped' not in ain_df.columns:
        ain_df['Scraped'] = pd.Series([False] * ain_df.shape[0], dtype=bool)
    if location is None:
        location = DEFAULT_LOC

    scraped = False
    count = 0
    for index, row in ain_df.iterrows():
        if row['Scraped']:  # if this row has been searched already
            continue  # skip this row
        elif count >= number:
            break
        rs = '{:s}, {:s}'.format(row['AIN'], row['SitusStreet'])
        print('scraping info for ({:d}/{:d}): {:s}'.format(index + 1,
                                                           ain_df.shape[0],
                                                           rs))
        data = scrape(row['AIN'], infos=infos, base_sleep=base_sleep)
        save_json(data=data,
                  name=str(row['AIN']),
                  location=location)
        ain_df.loc[index, 'Scraped'] = True
        scraped = True
        count += 1
    return scraped

def scrape_chunks_for_ains(ain_df: str,
                           chunk_size: int = 100,
                           chunks: Union[int, None] = None,
                           location: Union[str, None] = None,
                           infos: List[str] = list(TYPES.keys()),
                           base_sleep: float = 1
                           ) -> None:
    if chunks is None:
        chunks = 999999999999999999
    chunk = 0
    keep_scraping = True

    while chunk < chunks and keep_scraping:
        with AINData(ain_df) as ain:
            keep_scraping = scrape_data_for_ains(ain_df=ain.df,
                                                 number=chunk_size,
                                                 location=location,
                                                 infos=infos,
                                                 base_sleep=base_sleep)
        chunk += 1

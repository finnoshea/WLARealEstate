
import os
import pandas as pd
from .real.addresses import (get_address_csv,
                             prune_by_zipcode
                             )
from .real.scraper import (scrape_ains_for_file,
                           scrape_data_for_ains,
                           AINData
                           )

LOCATION = os.sep.join(__file__.split(os.sep)[:-1] + ['resources'])

ADDRESS_FILE = os.sep.join(__file__.split(os.sep)[:-1] +
                           ['resources', 'address_dataframe.pkl'])
AIN_FILE = os.sep.join(__file__.split(os.sep)[:-1] +
                       ['resources', 'ain_dataframe.pkl'])

def create_dataframe():
    all_df = get_address_csv()
    small_df = prune_by_zipcode(all_df)
    # only keep entries without fractional numbers
    # small_df = small_df[small_df['HSE_FRAC_NBR'].isnull()].copy()
    small_df.reset_index(inplace=True)
    return small_df


if os.path.isfile(ADDRESS_FILE):
    df = pd.read_pickle(ADDRESS_FILE)
else:
    df = create_dataframe()
    df.to_pickle(ADDRESS_FILE)

# for testing:
tiny_df = df.head(5).copy()  # keep only the first 50 entries
tiny_df.to_pickle('test_df.pkl')

scrape_ains_for_file('test_df.pkl', 'new_ain_df.pkl',
                     chunk_size=15, chunks=3)

td = pd.read_pickle('test_df.pkl')
ta = pd.read_pickle('new_ain_df.pkl')
# ts = ta.head(5).copy()
# ts.to_pickle('small_ain_df.pkl')
#
# with AINData('small_ain_df.pkl') as ain:
#     scrape_data_for_ains(ain_df=ain.df)

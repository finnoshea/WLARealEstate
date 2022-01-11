
import os
import pandas as pd
from .real.addresses import (get_address_csv,
                             prune_by_zipcode
                             )
from .real.scraper import (scrape_ains_for_file,
                           scrape_data_for_ains,
                           AINData,
                           scrape_chunks_for_ains
                           )
import time

LOCATION = os.sep.join(__file__.split(os.sep)[:-1] + ['resources'])

ADDRESS_FILE = os.sep.join(__file__.split(os.sep)[:-1] +
                           ['resources', 'address_dataframe.pkl'])
AIN_FILE = os.sep.join(__file__.split(os.sep)[:-1] +
                       ['resources', 'ain_dataframe.pkl'])

# build a west LA address dataframe
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


t0 = time.time()
# scrape all the AIN numbers you can find from the Assessor's website
scrape_ains_for_file(ADDRESS_FILE, AIN_FILE, chunk_size=100, chunks=5)
# scrape all the information for each of the ains that you can find
scrape_chunks_for_ains(AIN_FILE, chunk_size=100, chunks=5)
t1 = time.time()
print('Time to run: {:4.3f} hours'.format((t1 - t0) / 3600.0))

# for testing:
# tiny_df = df.head(5).copy()  # keep only the first 5 entries
# tiny_df.to_pickle('test_df.pkl')
#
# scrape_ains_for_file('test_df.pkl', 'new_ain_df.pkl',
#                      chunk_size=15, chunks=3)
#
# td = pd.read_pickle('test_df.pkl')
# ta = pd.read_pickle('new_ain_df.pkl')
# ts = ta.head(5).copy()
# ts.to_pickle('small_ain_df.pkl')
#
# _ = scrape_chunks_for_ains('small_ain_df.pkl', chunk_size=2, chunks=2)
#
# tx = pd.read_pickle('small_ain_df.pkl')
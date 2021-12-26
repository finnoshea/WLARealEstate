
import os

ADDRESS_PARTS = [os.sep.join(__file__.split(os.sep)[:-2]),
                 'resources',
                 'Addresses_in_the_City_of_Los_Angeles.csv']
ADDRESS_FILE = os.sep.join(ADDRESS_PARTS)

DEFAULT_ZIPS = [90025, 90064, 90049]

DEFAULT_LOC = os.sep.join(__file__.split(os.sep)[:-1])

TYPES = {'details': 'parceldetail',
         'ownership': 'parcel_ownershiphistory',
         'assessment': 'parcel_assessmenthistory'}

COLUMNS = ['AIN', 'SitusStreet',
           'SitusCity', 'SitusZipCode',
           'LegalDescription']

# these are the names of columns in the address book
ROW_ELEMENTS = ['HSE_NBR', 'HSE_FRAC_NBR', 'HSE_DIR_CD', 'STR_NM',
                'STR_SFX_CD', 'STR_SFX_DIR_CD', 'ZIP_CD']

import os
from datetime import datetime
from numpy import nan

from typing import Union


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


def coerce_date(input_date: str) -> Union[datetime, float]:
    try:
        return datetime.strptime(input_date, '%m/%d/%Y')
    except ValueError:
        return nan


def yn_to_bool(x: str) -> Union[bool, None]:
    if x == "Y":
        return True
    elif x == "None":
        return None
    return False


def zipcode_to_int(x: str) -> int:
    """ converts the 9-digit string zip to an int """
    try:
        zipcode = int(x[:-5])
    except ValueError:
        zipcode = x
    return zipcode


# items found in the json files ['details']['parcel'] dict
# but not here are to be left as strings.
TYPE_COERCION = {'AIN': int, 'Longitude': float, 'Latitude': float,
                 'ZipCode': zipcode_to_int,  # this one is created here
                 'CreateDate': coerce_date, 'DeleteDate': coerce_date,
                 'NumOfUnits': int, 'YearBuilt': int, 'EffectiveYear': int,
                 'SqftMain': int, 'SqftLot': int, 'NumOfBeds': int,
                 'NumOfBaths': int, 'RollPreparation_BaseYear': int,
                 'RollPreparation_LandValue': int,
                 'RollPreparation_ImpValue': int,
                 'RollPreparation_ImpReasonCode': int,
                 'RollPreparation_LandBaseYear': int,
                 'RollPreparation_ImpBaseYear': int,
                 'CurrentRoll_BaseYear': int,
                 'CurrentRoll_LandValue': int,
                 'CurrentRoll_ImpValue': int,
                 'CurrentRoll_LandBaseYear': int,
                 'CurrentRoll_ImpBaseYear': int,
                 'TrendedBaseValue_Land': int,
                 'TrendedBaseValue_Imp': int,
                 'BaseValue_Land': int,
                 'BaseValue_Imp': int,
                 'BaseValue_Year': int,
                 'UsableSqftLot': int,
                 'LandWidth': int,
                 'LandDepth': int,
                 'LandAcres': int,
                 'LotCodeSplit': yn_to_bool,
                 'LotImpairment': yn_to_bool,  # definitely update me
                 'LotCorner': yn_to_bool,
                 'LotSewer': yn_to_bool,
                 'LotTraffic': yn_to_bool,
                 'LotFreeway': yn_to_bool,
                 'LotFlight': yn_to_bool,
                 'LotGolf': yn_to_bool,
                 'LotHorse': yn_to_bool,
                 'PDBEffectiveDate': coerce_date
                 }


def coerce_details(details: dict) -> dict:
    """
    coerces the values in a json file's details/parcel dictionary
    to have 'good' types
    """
    for key, func in TYPE_COERCION.items():
        try:
            details[key] = func(details[key])
        except KeyError:  # key doesn't exist for some reason
            if key == 'ZipCode':  # create this entry
                details[key] = func(details['SitusZipCode'])
        except ValueError:  # strange format, I guess?
            if func == int:
                details[key] = -1
            elif func == float:
                details[key] = -1.0
            elif func == yn_to_bool:
                details[key] = None
    return details


SALE_COERCION = {'SaleNumber': int, 'RecordingDate': coerce_date,
                 'SequenceNumber': int, 'DocumentNumber': int,
                 'NumberOfParcels': int, 'DTTSalePrice': int,
                 'AssessedValue': int
                 }


def coerce_sale(sale: dict) -> dict:
    """
    coerces the values in a json file's ownership/Parcel_OwnershipHistory
    dictionary to have 'good' types
    """
    for key, func in SALE_COERCION.items():
        try:
            sale[key] = func(sale[key])
        except KeyError:  # key doesn't exist for some reason
            pass
        except ValueError:  # strange format, I guess?
            if func == int:
                sale[key] = -1
            elif func == float:
                sale[key] = -1.0
            elif func == yn_to_bool:
                sale[key] = None
    return sale
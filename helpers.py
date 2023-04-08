from bs4 import BeautifulSoup
import requests
import os
import ast

# Constants
PORTAL_URL = 'https://www.portalinmobiliario.com/'
HOUSE_PATH = "casa/"
APPARTMENT_PATH = "departamento/"
SALE_PATH = "venta/"
RENT_PATH = "arriendo/"
PUBLISHED_TODAY_PATH = "_PublishedToday_YES"
PRICE_FILTER = '_PriceRange_%sCLP-%sCLP'
PRICE_FILTER_UF = '_PriceRange_%sCLF-%sCLF'
BEDROOM_FILTER = '_BEDROOMS_%s-%s'
BATHROOM_FILTER = '_BATHROOMS_%s-%s'

def uf_to_clp(uf_value):
    return uf_value * round(float(os.environ.get('UF_VALUE')))

def set_uf_value_in_clp():
    # Make a request to the Banco Central de Chile website
    url = 'https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx'
    try:
        response = requests.get(url)
        # Parse the HTML response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the current UF value in the parsed HTML
        uf_value_tag = soup.find('label', {'id': 'lblValor1_1'})

        # Return the current UF value as a float
        uf_value = float(uf_value_tag.text.replace('.', '').replace(',', '.'))
    except Exception as e:
        uf_value = os.environ.get('UF_DEFAULT')
        print(f"Error obtaining UF value, setting default as {uf_value}")
    print(f"UF set as: {uf_value}")
    os.environ['UF_VALUE'] = str(uf_value)

def get_bool_env(env_name):
    return ast.literal_eval(os.environ.get(env_name))

def build_search_url(district):
    # Build the search URL based on the specified criteria
    url = PORTAL_URL
    transaction_type = 'SALE' if get_bool_env('SALE') and not get_bool_env('RENT') else 'RENT'
    property_type = 'HOUSE' if get_bool_env('HOUSE') and not get_bool_env('APPARTMENT') else 'APPARTMENT'

    url += SALE_PATH if transaction_type == 'SALE' else RENT_PATH
    url += HOUSE_PATH if property_type == 'HOUSE' else APPARTMENT_PATH
    url += district

    if get_bool_env('PRICE_FILTER'):
        price_filter = PRICE_FILTER_UF if get_bool_env(f'{transaction_type}_PRICE_UF') else PRICE_FILTER
        url += price_filter % (os.environ.get(f'MIN_{transaction_type}_PRICE'), os.environ.get(f'MAX_{transaction_type}_PRICE'))

    if get_bool_env('BEDROOM_FILTER'):
        url += BEDROOM_FILTER % (os.environ.get('MIN_BEDROOMS'), os.environ.get('MAX_BEDROOMS'))

    if get_bool_env('BATHROOM_FILTER'):
        url += BATHROOM_FILTER % (os.environ.get('MIN_BATHROOMS'), os.environ.get('MAX_BATHROOMS'))
    
    if get_bool_env('PUBLISHED_TODAY'):
        url += PUBLISHED_TODAY_PATH

    return url
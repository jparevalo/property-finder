import os
import ast
from bs4 import BeautifulSoup
import requests
import smtplib
import itertools
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from helpers import set_uf_value_in_clp, uf_to_clp, build_search_url, get_bool_env

# CLASSES
CONTENT_DIV_CLASS = 'ui-search-result'
PRICE_TAG_CLASS = 'price-tag-text-sr-only'
URL_ANCHOR_CLASS = 'ui-search-link'
ATTRIBUTE_CLASS = 'ui-search-card-attributes'
LOCATION_CLASS = 'ui-search-item__location'
TYPE_CLASS = 'ui-search-item__subtitle'

def get_properties(district):
    properties = []
    property_type = 'SALE' if get_bool_env('SALE') else 'RENT'
    print(f"* GETTING {property_type} PROPERTIES FOR {district.upper()} *")
    url = build_search_url(district)
    request = requests.get(url)
    soup = BeautifulSoup(request.text, features='html.parser')
    for content_div in soup.findAll("div",{ "class": CONTENT_DIV_CLASS }):
        try:
            area, attributes = content_div.find("ul", { "class": ATTRIBUTE_CLASS }).text.split('útiles')
            price = content_div.find("span", { "class": PRICE_TAG_CLASS }).text.replace('undefined', 'UF')
            anchor_with_link = content_div.find("a", { "class": URL_ANCHOR_CLASS })
            location = content_div.find("p", { "class": LOCATION_CLASS }).text
            type_desc = content_div.find("span", { "class": TYPE_CLASS }).text
            link = anchor_with_link.get('href')
            properties.append({
                'area': format_area(area),
                'price': price, 
                'price_in_clp': format_price_in_clp(price),
                'attributes': attributes,
                'ratio': format_price_in_clp(price) / format_area(area),
                'location': location,
                'type': type_desc,
                'link': link })
        except Exception as e:
            print(f'Error getting properties: { str(e) }')
            pass
    return properties

def format_price_in_clp(raw_price_value):
    integer_value = round(float(raw_price_value.split()[0]))
    if 'pesos' in raw_price_value:
        return integer_value
    return uf_to_clp(integer_value)

def format_area(raw_area_value):
    return int(raw_area_value.split()[0].replace(',',''))

def group_properties_by_type(properties):
    # sort the list by the grouping field
    properties.sort(key=lambda x: x['type'])

    # group the list by the grouping field
    properties_grouped = {}
    for key, group in itertools.groupby(properties, key=lambda x: x['type']):
        properties_grouped[key] = list(group)
    
    return properties_grouped

def get_top_properties(properties):
    print(f"* GETTING TOP PROPERTIES *")
    top_properties = []
    for property in properties:
        if property['ratio'] <= float(os.environ.get('THRESHOLD_RATIO')):
            top_properties.append(property)
    return group_properties_by_type(top_properties)

def build_property_message(property):
    message = ""
    message += f"<h4>{property['location']}</h4>"
    message += f"<h5>{property['attributes']} | {property['area']} m² útiles</h5>"
    message += f"<p><b>{property['price']} | ${property['price_in_clp']:,.0f} CLP </b></p>"
    message += f"<a href={property['link']}>VER PROPIEDAD</a>"
    message += f"<hr/>"
    return message

def send_email(top_properties):
    # Get SMTP server settings and email credentials from environment variables
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = os.environ.get('SMTP_PORT')
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_emails = ast.literal_eval(os.environ.get('RECIPIENT_EMAILS'))

    # Define email subject and message body
    property_type = 'SALE' if get_bool_env('SALE') else 'RENT'
    subject = f"🏘 [{property_type}] Here's Your Daily Property Digest! 🏘"
    body = f"<p>Hello there! Here's a list of properties you might be interested in:</p><br/>"
    for property_type in top_properties.keys():
        body += f"<h2 style='color:red'>{property_type.split(' ')[0].upper()}S {property_type.split(' ', 1)[1].upper()}</h2><hr/><br/>"
        for property in top_properties[property_type]:
            body += build_property_message(property)

    # Create a multi-part message with the email headers and body
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
    message.attach(MIMEText(body, 'html'))

    # Connect to the SMTP server, authenticate, and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_emails, message.as_string())

def is_selection_valid():
    # User must select SALE OR RENT, not both
    return not (get_bool_env('SALE') and get_bool_env('RENT'))

if __name__ == '__main__':
    # Get UF Value for CLP mapping
    set_uf_value_in_clp()
    if not is_selection_valid():
        raise Exception('You must set the SALE env OR the RENT env to TRUE, not both.')
    districts = ast.literal_eval(os.environ.get('DISTRICTS'))
    properties = []
    for district in districts:
        properties.extend(get_properties(district))
    top_properties = get_top_properties(properties)
    send_email(top_properties)
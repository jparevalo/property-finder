# Description
Property finder, collects properties from [Portal Inmobiliario](https://www.portalinmobiliario.com/) that match your requirements and then sends a digest email to the specified recipients.

Original idea and development by [@Mvalenzuela](https://www.github.com/Mvalenzuela). 

This wouldn't be up here if it weren't for him 💪

# Building with Docker

## Prerequisites

[Install Docker](https://docs.docker.com/engine/install/)

[Install Docker Compose on Linux](https://docs.docker.com/compose/install/#install-compose-on-linux-systems) (Not necessary for **Docker Desktop for Mac** / **Docker Desktop for Windows**)

[Install Jinja2 Command-Line Tool](https://pypi.org/project/j2cli/)

## Configure environment

Fill in email credentials and property filter params to narrow down your property query on a file called **env.json**.
You can use the _sample-env.json_ sample file to build your own env.json.

### Env params

* service_name: The name of your docker service
* email: Email-related env variables:
    * SENDER_EMAIL: The e-mail you'll be using to log in to the SMTP
    * SENDER_PASSWORD: The app-password related to that email ([Here's a Tutorial](https://evermap.com/Tutorial_ADM_UsingAppPasswordsGmail.asp))
    * SMTP_SERVER: The SMTP server you'll be using (if using gmail, no need to change it)
    * SMTP_PORT: The SMTP port you'll be using (if using gmail, no need to change it)
    * RECIPIENT_EMAILS: List of emails that will be receiving the property digest email
* threshold_ratio: Ratio to narrow down the results, ratio is calculated by dividing the price (in CLP) by the square meters of the property. (If you want to use another ratio, feel free to change line 39 of main.py)
* uf_default: Default UF value in CLP, in case the [Banco Central Services](https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx) are down.
* filters: Possible filters to narrow down your property digest:
    * SALE: Filter for properties for SALE (boolean), if SALE=True, RENT must be False
    * RENT: Filter for properties for RENT (boolean), if RENT=True, SALE must be False
    * APPARTMENT: Filter for Appartments (boolean)
    * HOUSE: Filter for Houses (boolean)
    * DISTRICTS: District slug list for filtering by district on portalinmobiliario's site. You can find it by filtering on the site and copying the slug.
    * PRICE_FILTER: Filter by Price (boolean)
    * PRICES_SALE: Price filters for SALE properties:
        * MIN: Min price for SALE properties
        * MAX: Max price for SALE properties
        * UF: The SALE env prices are set in UF (boolean)
    * PRICES_RENT: Price filters for RENT properties:
        * MIN: Min price for RENT properties
        * MAX: Max price for RENT properties
        * UF: The RENT env prices are set in UF (boolean)
    * BEDROOM_FILTER: Filter by Bedrooms (boolean)
    * BEDROOMS: Bedroom filters:
        * MIN: Min bedrooms
        * MAX: Max bedrooms
    * BATHROOM_FILTER: Filter by Bathrooms (boolean)
    * BATHROOMS: Bathroom filters:
        * MIN: Min bathrooms
        * MAX: Max bathrooms
    * PUBLISHED_TODAY: Filter for properties that were published today (boolean). This is recommended to be set to True.
    
## Build

By executing the _run.sh_ script, the service will build and start.

```
./run.sh
```

## Run the service.

You can run with _run.sh_ or by executing:

```
docker-compose down
```

## Stop the service.

```
docker-compose down
```

# "Production" setup with crontab

You can execute this via crontab to send you daily email digests at any desired frequency.

For example, to execute the service every day at 23:59, the crontab would look like this:

```
59 23 * * * myuser docker-compose -f /home/myuser/property-finder/docker-compose.yml up
```

Just make sure the crontab user executing the service has the correct permissions and software installed (ie. Docker, Docker-Compose, Jinja2). 

In my case I had to directly modify the _/etc/crontab_ file instead of executing _crontab -e_. And it was necessary to add the "myuser" user on the command to specify that the service should be started using the "mysuder" user.


# Questions?

Just ask!

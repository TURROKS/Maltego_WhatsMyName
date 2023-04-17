import os
import requests
from requests.auth import HTTPProxyAuth
import threading
import time
from urllib import parse
import urllib3

from dotenv import load_dotenv
import tldextract

from extensions import registry, whatsmyname_set
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform

# Load Environment Variables
load_dotenv()

# Disable Warnings
urllib3.disable_warnings()


# Get website logo for the new Entities
def get_site_logo(domain_name):
    logo = f"https://logo.clearbit.com/{domain_name}"
    return logo


# Normalize URL and extract Domain
def domain_extract(input_url):
    tld_result = tldextract.extract(input_url)
    domain = f"{tld_result.domain}.{tld_result.suffix}"
    return domain


@registry.register_transform(display_name="To Online Group [WhatsMyName]", input_entity="maltego.Alias",
                             description='Returns a list of website where an Alias has been found',
                             output_entities=["maltego.OnlineGroup"],
                             transform_set=whatsmyname_set)
class AliasToSites(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        person_name = request.Value
        raw_sites_file = requests.get(os.getenv("SITES_JSON"))
        json_data = raw_sites_file.json()
        threads = []
        num_threads = int(os.getenv("THREADS"))

        for site in json_data.get('sites'):
            t = threading.Thread(target=cls.check_site, args=(site, person_name, response))
            threads.append(t)
            t.start()

        while len(threads) >= num_threads:
            for t in threads:
                if not t.is_alive():
                    threads.remove(t)
            time.sleep(0.1)

        for t in threads:
            t.join()

    @classmethod
    def check_site(cls, site, person_name, response: MaltegoTransform):

        # Load required variables
        user = os.getenv("USER")
        passwd = os.getenv("PASS")
        auth = HTTPProxyAuth(user, passwd)
        headers = {'User-Agent': os.getenv("USER_AGENT")}
        proxies = {'http': os.getenv("PROXY")}

        # Normalize URL
        test_url = site.get('uri_check').replace('{account}', parse.quote_plus(person_name))
        domain = domain_extract(test_url)

        try:
            # r = requests.get(test_url.strip(), verify=False, timeout=5, headers=headers, proxies=proxies,
            #                  auth=auth)
            r = requests.get(test_url.strip(), verify=False, timeout=5, headers=headers)
            # Check if user exists on website
            if r.status_code == site.get('e_code') and r.text.find(site.get('e_string')) != -1 and site.get('valid'):

                # Remove False Positives
                if person_name not in r.url:
                    pass
                else:
                    # Check if the check_uri is for an API, this OPTIONAL element can show a human-readable page
                    if site.get('uri_pretty'):

                        # Normalize pretty_uri
                        test_url = site.get('uri_pretty').replace('{account}', parse.quote_plus(person_name))
                        domain = domain_extract(test_url)

                        # Create Entity
                        ent = response.addEntity("maltego.OnlineGroup", site.get("name"))
                        ent.addProperty(fieldName='url', displayName='URL', matchingRule='loose', value=test_url)
                        ent.addProperty(fieldName='cat', displayName='Category', matchingRule='loose',
                                        value=str(site.get('cat')).upper())
                        ent.addDisplayInformation(content=f'<a href="{test_url}">Open in Browser</a>',
                                                  title="Profile")
                        ent.setIconURL(get_site_logo(domain))
                    else:
                        # Create Entity
                        ent = response.addEntity("maltego.OnlineGroup", site.get("name"))
                        ent.addProperty(fieldName='url', displayName='URL', matchingRule='loose', value=r.url)
                        ent.setIconURL(get_site_logo(domain))
                        ent.addProperty(fieldName='cat', displayName='Category', matchingRule='loose',
                                        value=str(site.get('cat')).upper())
                        ent.addDisplayInformation(content=f'<a href="{test_url}">Open in Browser</a>',
                                                  title="Profile")
            # Status code is correct but test string does not match
            elif r.status_code == site.get('e_code') and r.text.find(site.get('e_string')) == -1:
                response.addUIMessage(f"Potential False Positive for {domain}")
            # Status code does not match but test string does
            elif not r.status_code == site.get('e_code') and r.text.find(site.get('e_string')) != -1:
                response.addUIMessage(f"Response code received {r.status_code} expected {site.get('e_code')} for {domain}")
        # Other Exceptions
        except requests.exceptions.RequestException as e:
            # response.addUIMessage(f"Other error for {domain}")
            pass

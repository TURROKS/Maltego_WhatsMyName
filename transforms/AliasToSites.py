import os
import requests
import threading
import time
from urllib import parse
import urllib3

from dotenv import load_dotenv
import tldextract

from extensions import registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform

# Load Environment Variables
load_dotenv()

# Disable Warnings
urllib3.disable_warnings()


@registry.register_transform(display_name="Greet Person", input_entity="maltego.Phrase",
                             description='Returns a Phrase greeting a Person on the Graph.',
                             output_entities=["maltego.Phrase"])
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

        user = os.getenv("USER")
        passwd = os.getenv("PASS")
        headers = {'User-Agent': os.getenv("USER_AGENT")}
        proxies = {'http': os.getenv("PROXY")}

        # Normalize URL
        test_url = site.get('uri_check').replace('{account}', parse.quote_plus(person_name))
        tld_result = tldextract.extract(test_url)
        domain = f"{tld_result.domain}.{tld_result.suffix}"

        try:
            r = requests.get(test_url.strip(), verify=False, timeout=5, headers=headers, proxies=proxies, auth=(user, passwd))

            # Check if user exists on website
            if r.status_code == site.get('e_code') and r.text.find(site.get('e_string')) != -1:

                # Remove False Positives
                if person_name not in r.url:
                    pass
                else:
                    # Check if the check_uri is for an API, this OPTIONAL element can show a human-readable page
                    if site.get('uri_pretty'):

                        # Normalize pretty_uri
                        test_url = site.get('uri_pretty').replace('{account}', parse.quote_plus(person_name))
                        tld_result = tldextract.extract(test_url)
                        domain = f"{tld_result.domain}.{tld_result.suffix}"

                        # Create Entity
                        ent = response.addEntity("maltego.OnlineGroup", site.get("name"))
                        ent.addProperty(fieldName='url', displayName='URL', matchingRule='loose', value=test_url)
                        ent.addProperty(fieldName='cat', displayName='Category', matchingRule='loose',
                                        value=str(site.get('cat')).upper())
                        ent.setIconURL(f"https://logo.clearbit.com/{domain}")
                    else:
                        # Create Entity
                        ent = response.addEntity("maltego.OnlineGroup", site.get("name"))
                        ent.addProperty(fieldName='url', displayName='URL', matchingRule='loose', value=r.url)
                        ent.setIconURL(f"https://logo.clearbit.com/{domain}")
                        ent.addProperty(fieldName='cat', displayName='Category', matchingRule='loose',
                                        value=str(site.get('cat')).upper())
            # Status code is correct but test string does not match
            elif r.status_code == site.get('e_code') and r.text.find(site.get('e_string')) == -1:
                response.addUIMessage(f"Bad detection string {site.get('e_string')} for {domain}")
            # Status code does not match but test string does
            elif not r.status_code == site.get('e_code') and r.text.find(site.get('e_string')) != -1:
                response.addUIMessage(f"Response code received {r.status_code} expected {site.get('e_code')} for {domain}")
        # Other Exceptions
        except requests.exceptions.RequestException as e:
            response.addUIMessage(f"Other error for {domain}")

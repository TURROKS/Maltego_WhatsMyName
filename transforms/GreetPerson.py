import json
import requests

from extensions import registry
from maltego_trx.entities import Phrase
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform


def identity_check(username):
    with open(".\\wmn-data.json", 'r', encoding="utf8") as inp:
        parsed = json.load(inp)

        for site in parsed.get('sites'):
            test_url = site.get('uri_check')
            new_url = test_url.replace('{account}', username)

            try:
                data = requests.get(new_url)
                if data.status_code == site.get('e_code') and data.text.find(site.get('e_string')) != -1:
                    return data.url
                else:
                    pass
            except:
                print('error')


@registry.register_transform(display_name="Greet Person", input_entity="maltego.Phrase",
                             description='Returns a Phrase greeting a Person on the Graph.',
                             output_entities=["maltego.Phrase"])
class GreetPerson(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        person_name = request.Value

        found = identity_check(person_name)

        response.addEntity(Phrase, found)

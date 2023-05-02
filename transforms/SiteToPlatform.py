from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from extensions import registry, whatsmyname_set
import tldextract

from maltego_trx.transform import DiscoverableTransform


def domain_extract(input_url):
    tld_result = tldextract.extract(input_url)
    domain = f"{tld_result.domain}.{tld_result.suffix}"
    return domain


@registry.register_transform(display_name="To Social Media Platform [WhatsMyName]", input_entity="maltego.OnlineGroup",
                             description='Returns the main website associated with the Social Media Platform.',
                             output_entities=["maltego.Website"],
                             transform_set=whatsmyname_set)
class SiteToPlatform(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        website = request.getProperty('url')

        if website:
            domain = domain_extract(website)
            response.addEntity('maltego.Website', domain)

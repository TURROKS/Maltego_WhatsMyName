from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from extensions import registry, whatsmyname_set
from settings import language_setting

from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="To Profile URL [WhatsMyName]", input_entity="maltego.OnlineGroup",
                             description='Returns the Profile URL.',
                             output_entities=["maltego.URL"],
                             transform_set=whatsmyname_set)
class ProfileToURL(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        profile_url = request.getProperty('url')
        title = request.getProperty('webTitle')

        if title:
            ent = response.addEntity("maltego.URL", title)
            ent.addProperty('url', 'URL', 'loose', profile_url)
        else:
            ent = response.addEntity("maltego.URL", profile_url)
            ent.addProperty('url', 'URL', 'loose', profile_url)

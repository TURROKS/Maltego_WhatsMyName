from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from extensions import registry, whatsmyname_set
from settings import language_setting

from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="To Category [WhatsMyName]", input_entity="maltego.OnlineGroup",
                             description='Returns the category of an Online Group.',
                             output_entities=["onlinegroup.Category"],
                             transform_set=whatsmyname_set)
class SiteToCategory(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        person_name = request.getProperty('cat')

        if person_name:
            response.addEntity("onlinegroup.Category", person_name)

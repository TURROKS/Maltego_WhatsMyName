from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.template_dir.extensions import registry
from maltego_trx.template_dir.settings import language_setting

from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="Greet Person (localized)", input_entity="maltego.Phrase",
                             description='Returns a localized phrase greeting a person on the graph.',
                             settings=[language_setting],
                             output_entities=["maltego.Phrase"])
class SiteToCategory(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        person_name = request.getProperty('cat')

        if person_name:
            response.addEntity("my.SiteCategory", person_name)

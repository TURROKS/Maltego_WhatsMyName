from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from extensions import registry, whatsmyname_set

from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="To Alias [WhatsMyName]", input_entity="maltego.EmailAddress",
                             description='Extracts the potential username from an Email address.',
                             output_entities=["maltego.Alias"],
                             transform_set=whatsmyname_set)
class EmailToAlias(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        full_user_name = request.Value
        user_name = full_user_name.split('@')[0]

        if user_name:
            response.addEntity("maltego.Alias", user_name)

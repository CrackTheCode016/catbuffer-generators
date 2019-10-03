from .RestNameHelper import set_type


class RestSchemaObjectGenerator():
    def __init__(self, code, schema, type_descriptor):
        self.code = code
        self.current_schema = schema
        self.type_descriptor = type_descriptor

    def is_struct(self, entity):
        return entity['type'] is "struct"

    def is_obj(self, entity):
        return 'size' in entity

    def is_array(self, entity):
        return 'sort_key' in entity

    def is_parameter(self, entity):
        return 'name' in entity

    def build_register_schema_contents(self, entity, schema_obj):
        obj_base_param = "{}: {{ type: ModelType.{}, schemaName: '{}'}},"
        non_obj_base_param = "{}: ModelType.{},"
        entity_type = set_type(entity)
        if 'signedness' not in entity:
            if self.is_array(entity):
                param_schema_name = "{}".format(entity['name'])
                schema_obj += [obj_base_param.format(
                    entity['name'], "array", self.type_descriptor, param_schema_name)]
            elif self.is_obj(entity):
                param_schema_name = "{}.{}".format(
                    self.type_descriptor, entity['name'])
                schema_obj += [obj_base_param.format(
                    entity['name'], "object", param_schema_name)]
            else:
                schema_obj += [non_obj_base_param.format(
                    entity['name'], entity_type)]

    def build_register_schema(self, func_name, return_type):

        # The next step is to generate the addSchema() portion of the plugin. 
        # They are essentially subsequent 'depenency' schemas.
        # It may be done by inferring the types of some of the arrays / other schema objects.
        # Once they are validated as being a dependency, their type may be called and the contents added
        # as per the plugin model.

        schema_obj = []
        schema_obj += ["{} : {} => {{".format(func_name, return_type)]
        if self.is_struct(self.current_schema):
            schema_obj += ["{}.addTransactionSupport(EntityType.{}, {{".format(
                return_type, self.type_descriptor)]
            for entity in self.current_schema['layout']:
                if self.is_parameter(entity):
                    self.build_register_schema_contents(entity, schema_obj)
            schema_obj += ["});"]
        return schema_obj

        # # conform to catapult-rest CatapultPlugin registerCodecs
        # def build_register_codec(self, func_name, return_type):
        #     pass

    def generate_block_obj(self, plugin_name):
        register_schema = self.build_register_schema(
            "registerSchema", "builder")
        # register_codecs = self.build_register_codec(
        #     "registerCodecs", "codecBuilder")

        self.code += ['const {}Plugin = {{'.format(plugin_name)]
        self.code.extend(register_schema)
        self.code += ['}', '};']

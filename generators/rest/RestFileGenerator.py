from collections import namedtuple
import os
from .RestNameHelper import set_type, set_schema_name
from .RestSchemaObjectGenerator import RestSchemaObjectGenerator
# from .RestBaseSchemaGenerator import RestBaseSchemaGenerator
Descriptor = namedtuple('Descriptor', ['filename', 'code'])


Import = namedtuple('Import', ['importname', 'path'])


class RestFileGenerator():

    def __init__(self, schema, options):
        self.schema = schema
        self.code = []
        self.schema = schema
        self.current = None
        self.options = options

    def __next__(self):
        self.code = []
        code, name = next(self.current)
        return Descriptor(name + '.js', code)

    def __iter__(self):
        self.current = self.generate()
        return self

    def generate(self):
        for type_descriptor, value in self.schema.items():
            schema_descriptor = set_schema_name(type_descriptor)
            self.prepare_base(self.options, schema_descriptor)
            schema = RestSchemaObjectGenerator(
                self.code, value, schema_descriptor)
            schema.generate_block_obj(schema_descriptor)
            yield self.code, schema_descriptor

    def prepare_base(self, options, schema_descriptor):
        self.prepend_copyright(options['copyright'])
        self.add_module(schema_descriptor)
        self.generate_imports()
        self.add_plugin(schema_descriptor)

    def generate_imports(self):
        base_imports = [
            Import('EntityType', '../model/EntityType'),
            Import('ModelType', '../model/ModelType'),
            Import('sizes', '../modelBinary/sizes'),
        ]
        for importname, path in base_imports:
            self.code += ["const {} = require('{}');".format(importname, path)]

    def add_module(self, name):
        self.code += ['/** @module plugins/{} */'.format(name)] + ['\n']

    def add_plugin(self, name):
        self.code += [
            "/**",
            "* Creates a {} plugin.".format(name),
            "* @type {module:plugins/CatapultPlugin}",
            "*/"
        ]

    def prepend_copyright(self, copyright_file):
        if os.path.isfile(copyright_file):
            with open(copyright_file) as header:
                self.code = [line.strip() for line in header]

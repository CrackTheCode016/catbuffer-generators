from collections import OrderedDict
from .AliasParser import AliasParserFactory
from .CatsParseException import CatsParseException
from .CommentParser import CommentParser
from .EnumParser import EnumParserFactory
from .ImportParser import ImportParserFactory
from .ScopeManager import ScopeManager
from .StructParser import StructParserFactory


class CatsParser(ScopeManager):
    """Parser used to parse CATS files line by line"""
    def __init__(self, import_resolver):
        super().__init__()
        self.import_resolver = import_resolver

        self.aspect_parser = CommentParser()
        self.type_parser_factories = [
            AliasParserFactory(),
            EnumParserFactory(),
            ImportParserFactory(),
            StructParserFactory()
        ]

        self.wip_type_descriptors = OrderedDict()
        self.active_parser = None

    def process_line(self, line):
        """Processes the next line of input"""
        try:
            self._process_line(line)
        except Exception as ex:
            raise CatsParseException('\n'.join(self.scope()), ex)

    def _process_line(self, line):
        self.increment_line_number()

        # check if current line is a cross cutting concern
        line_stripped = line.strip()
        if self.aspect_parser.try_process_line(line_stripped):
            return

        # something else, so attach current aspect state to it
        partial_descriptor = self.aspect_parser.commit()

        # ignore blank lines
        if not line_stripped:
            return

        # close a type iff an unindented non-empty line is found
        if self.active_parser and not line.startswith('\t'):
            self._close_type()

        active_factories = self.type_parser_factories if not self.active_parser else self.active_parser.factories()

        factory = next(factory for factory in active_factories if factory.is_match(line_stripped))
        parser = factory.create()
        parse_result = parser.process_line(line_stripped)

        # create a new scope if the current symbol is a composite
        if not parse_result:
            self.active_parser = parser
            self.active_parser.partial_descriptor = partial_descriptor
            return

        if self.active_parser:
            if 'type' in parse_result:
                self._require_known_type(parse_result['type'])

            self.active_parser.append({**parse_result, **partial_descriptor})
        elif hasattr(parse_result, 'import_file'):
            self.import_resolver(parse_result.import_file)
        else:
            self._set_type_descriptor(parse_result[0], {**parse_result[1], **partial_descriptor})

    def _close_type(self):
        if not self.active_parser:
            return

        parsed_tuple = self.active_parser.commit()
        self._set_type_descriptor(parsed_tuple[0], {**parsed_tuple[1], **self.active_parser.partial_descriptor})
        self.active_parser = None

    def _require_known_type(self, type_name):
        if type_name not in self.wip_type_descriptors and 'byte' != type_name:
            raise CatsParseException('no definition for linked type "{0}"'.format(type_name))

        return type_name

    def _set_type_descriptor(self, type_name, type_descriptor):
        if type_name in self.wip_type_descriptors:
            raise CatsParseException('duplicate definition for type "{0}"'.format(type_name))

        self.wip_type_descriptors[type_name] = type_descriptor

    def type_descriptors(self):
        """Returns all parsed type descriptors"""
        self._close_type()
        return self.wip_type_descriptors

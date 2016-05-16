from ..utils import cached_property
from .base import BaseRecord
from ..exceptions import ReferenceSyntaxError

class RISRecord(BaseRecord):
    @classmethod
    def parse(cls, data):
        in_record = False
        record = ''

        for line in data:
            if line.startswith('TY  - '):
                if in_record:
                    raise ReferenceSyntaxError
                record = line
                in_record = True
            elif line.startswith('ER  - '):
                if not in_record:
                    raise ReferenceSyntaxError
                record += line
                in_record = False
                yield cls(record)
            else:
                if in_record:
                    record += line

        if in_record:
            # reached end of file with an open record
            raise ReferenceSyntaxError

    def raw_fields(self):
        'Returns a generator of tuples containing each raw fields name and value.'
        for line in self._raw_data.splitlines():
            try:
                field, value = line.split('  - ', 1)
                if len(field) == 2:
                    yield (field, value)
            except ValueError: # couldn't split into 2
                pass

    @cached_property
    def title(self):
        return self._first_raw_value('TI', 'T1')

    @cached_property
    def abstract(self):
        value = self._first_raw_aggregate('AB', 'N2')

        # some records break the abstract into several records
        if value: return '\n'.join(value)

    @cached_property
    def authors(self):
        return self._all_raw_values('AU', 'A1', 'A2', 'A3')

    @cached_property
    def journal_names(self):
        # a record may include multiple names (eg, abbreviated & full)
        value = self._all_raw_values('JA', 'JO', 'JF')
        if value:
            return set(value)

    @cached_property
    def issn(self):
        return self._first_raw_value('SN')

    @cached_property
    def volume(self):
        return self._first_raw_value('VL')

    @cached_property
    def issue(self):
        return self._first_raw_value('IS')

    @cached_property
    def pages(self):
        start = self._first_raw_value('SP')
        end = self._first_raw_value('EP')
        if start and not end:
            if '-' in start:
                start, end = start.split('-', 1)
        return (start, end)

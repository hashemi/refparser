from ..utils import cached_property
from .base import BaseRecord

class MedlineRecord(BaseRecord):
    @classmethod
    def parse(cls, data):
        record = ''
        for line in data:
            if line.strip() == '':
                # records are seperated by empty lines
                if record != '':
                    yield cls(record)
                    record = ''
            else:
                record += line
        if record != '':
            yield cls(record)

    def raw_fields(self):
        'Returns a generator of tuples containing each raw fields name and value.'
        current_field = ''
        current_value = ''
        for line in self._raw_data.splitlines():
            if line.startswith('      '):
                current_value += '\n' + line[6:]
            else:
                try:
                    field, value = line.split('- ', 1)
                    if len(field) == 4:
                        if current_field:
                            yield(current_field, current_value)
                        current_field = field.strip()
                        current_value = value
                except ValueError:
                    pass
        if current_field:
            yield(current_field, current_value)

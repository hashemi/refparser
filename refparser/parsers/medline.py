import re
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
        """Returns a generator of tuples containing each raw fields name and
        value."""
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
                            yield(current_field, current_value.strip())
                        current_field = field.strip()
                        current_value = value
                except ValueError:
                    pass
        if current_field:
            yield(current_field, current_value.strip())

    @cached_property
    def title(self):
        return self._first_raw_value('TI')

    @cached_property
    def abstract(self):
        return self._first_raw_value('AB')

    @cached_property
    def authors(self):
        # FAU is full author name. PubMed recrods often have both FAU and AU
        return self._first_raw_aggregate('FAU', 'AU')

    @cached_property
    def journal_names(self):
        # a record may include multiple names (eg, abbreviated & full)
        value = self._all_raw_values('TA', 'JT')
        if value:
            return set(value)

    @cached_property
    def issn(self):
        value = self._first_raw_value('IS')
        if value:
            # remove details of the ISSN which appear after a space
            value = value.split(' ', 1)[0]
        return value

    @cached_property
    def volume(self):
        return self._first_raw_value('VI')

    @cached_property
    def issue(self):
        return self._first_raw_value('IP')

    @cached_property
    def pages(self):
        pagination = self._first_raw_value('PG').strip()

        # remove extra comments that can appear after space, comma or semicolon
        pagination = re.sub('[ ,;].*$', '', pagination)

        if '-' in pagination:
            start, end = pagination.split('-', 1)
        else:
            start, end = (pagination, None)

        return (start, end)

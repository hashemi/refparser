# refparser

`refparser` is a Python 3 library for parsing academic references in RIS or MEDLINE formats.

```
from refparser.parsers import RISRecord

raw_record = """
TY  - JOUR
ID  - 123456
A1  - Cushing, Harvey
ER  - 
"""

record = RISRecord(raw_record)

record.title
record.authors
record.journal_names
record.issn
record.volume
record.issue
record.pages
```

## License
MIT

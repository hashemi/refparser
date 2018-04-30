"""
With this web app, you upload two citation files and it will find duplicate
citations and display them side-by-side.

This app depends on the Bottle micro web-framework. You can install bottle with
something like:

    $ pip install bottle
"""

try:
    from bottle import run, request, get, post
except ImportError:
    import sys
    sys.exit('Unable to run the web app: bottle is missing.\n' + __doc__)

from refparser.parsers import RISRecord, MedlineRecord

accepted_file_formats = {
    'RIS': RISRecord,
    'Medline': MedlineRecord,
}

@get('/')
def index():
    return \
"""
<html>
<body>

<form action="/" method="post" enctype="multipart/form-data">
    <p>File 1
        <input type="file" name="file1">
        <select name="type1">
            <option>RIS
            <option>Medline
        </select>
    </p>
    <p>File 2
        <input type="file" name="file2">
        <select name="type2">
            <option>RIS
            <option>Medline
        </select>
    </p>
    <p><input type="submit" value="Find Duplicates"></p>
</form>

</body>
</html>
"""


pre_json = \
"""
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/2.2.2/diff.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/mustache.js/2.2.1/mustache.min.js"></script>
  <style>
    #diff_view td {
      padding: 5px;
      border: 1px solid grey;
    }
    .first .first-only, .second .second-only {
      background-color: yellow;
    }
    .first .second-only, .second .first-only {
      display: none;
    }
    .title {
      font-weight: bold;
    }
    .authors {
      color: #777;
    }
  </style>
</head>
<body>
  <script id="diff_template" type="x-tmpl-mustache">
  {{#items}}
  <tr><td class='first {{field}}'>{{{diff}}}</td><td class='second {{field}}'>{{{diff}}}</td></td>
  {{/items}}
  </script>

  <table id="diff_view"></table>

  <script type='text/javascript'>
    var view = {
      items : [
"""

post_json = \
"""
      ],
      diff: function() {
        var diff = JsDiff.diffChars(this.first, this.second);
        result = '';
        diff.forEach(function(part) {
          if (part.removed) {
            result += '<span class="first-only">';
          } else if (part.added) {
            result += '<span class="second-only">';
          }
          result += part.value;
          if (part.added || part.removed) {
            result += '</span>';
          }
        });
        return result;
      }
    };
    var template = document.getElementById('diff_template').innerHTML;
    var output = Mustache.render(template, view);
    document.getElementById('diff_view').innerHTML = output;
  </script>
</body>
</html>
"""

def _decoded_lines(lines):
    yield from (line.decode('utf-8') for line in lines)

def all_matches(list1, list2):
    list1_location_idx = {}
    list1_title_authors_idx = {}
    for record in list1:
        if record.location_fingerprint:
            list1_location_idx[record.location_fingerprint] = record
        if record.title_authors_fingerprint:
            list1_title_authors_idx[record.title_authors_fingerprint] = record

    for record in list2:
        match = None
        if record.location_fingerprint:
            match = list1_location_idx.get(record.location_fingerprint)

        if not match and record.title_authors_fingerprint:
            match = list1_title_authors_idx.get(record.title_authors_fingerprint)

        if match:
            try:
                del list1_location_idx[match.location_fingerprint]
                del list1_title_authors_idx[match.title_authors_fingerprint]
            except KeyError:
                pass
            yield (record, match)

import json
def side_by_side_json(record1, record2):
    for field in ('title', 'authors', 'abstract', 'journal_names', 'issn', 'volume', 'issue', 'pages'):
        yield json.dumps({
            'field': field,
            'first': str(getattr(record1, field)),
            'second': str(getattr(record2, field)),
        }) + ',\n'

@post('/')
def handle_post():
    record_types = (
        accepted_file_formats[request.forms.type1],
        accepted_file_formats[request.forms.type2]
    )

    files = (
        _decoded_lines(request.files.file1.file),
        _decoded_lines(request.files.file2.file)
    )

    record_lists = (
        list(record_types[0].parse(files[0])),
        list(record_types[1].parse(files[1])),
    )

    yield pre_json
    for record1, record2 in all_matches(*record_lists):
        yield from side_by_side_json(record1, record2)
    yield post_json

    # yield '<html><body>'
    # yield '<p>Checking {} against {} citations for duplicates...</p>'.format(len(record_lists[0]), len(record_lists[1]))
    # yield '<table>'
    # for record1, record2 in all_matches(*record_lists):
    #     yield '<tr><td>{}</td><td>{}</td></tr>'.format(record1.title, record2.title)
    # yield '</html></body></table>'

run(debug=True, reloader=True)

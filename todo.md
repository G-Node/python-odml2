odML TODO list:
===============

  - [x] Public API for
    - [x] namespaces
    - [x] tests for namespaces
    - [x] type definitions
    - [x] tests for type definitions
    - [x] property definitions
    - [x] tests for property definitions
  - [x] Implement `__str__` for all front-end classes 
  - [x] Implement Value.from_obj() as replacement for value_from()
  - [x] Move TODOs from the code to this document (if possible)
  - [x] Use sortedcontainers.SortedMap instead of dict in the mem back-end.
  - [x] Remove DictLike class and inherit from collections.Mapping or collections.MutableMapping
  - [x] Use suffix Map instead of Dict in the back-end
  - [x] Make use of itertools.chain() to concatenate generators (value properties and section properties)
  - [x] Maybe use immutable front-end classes NameSpace, TypeDef, PropertyDef also in the back-end
    - ~~Deprecate add/set methods on MutableMapping/accessor classes in the back-end (and front-end?)~~
  - [x] Check the input for URIs, names, type names, prefixes etc (in the front-end)
  - [ ] Better name for SB for example: SecB, SecBuilder ...
  - [x] Nicer yaml output (sort things by type and name)
  - [x] Raise error when changing a read only document
  - [x] Improve loading and storing of documents
    - [x] Load documents over HTTP
    - [x] Use six.move.urllib.parse.urlparse to read paths and uris
    - [x] Choose back-end based on file extension
    - [x] Choose back-end based on mime type
  - [x] Implement modes that define how the terminology is handled:
        STRICT, UNCHECKED, CREATE
  - [x] Add support for namespaces
    - [x] NameSpace can have documents (in back-end only?)
  - [x] Add support for links
  - [ ] Access and manipulate property and type definitions from sections directly
  - [ ] Better intro notebook
  - [ ] Public API documentation
  - [ ] Update readme
  - [ ] JSON back-end
  - [ ] RDF back-end

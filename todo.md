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
  - [ ] Use suffix Access or Accessor instead of Dict in the back-end
  - [x] Make use of itertools.chain() to concatenate generators (value properties and section properties)
  - [x] Maybe use immutable front-end classes NameSpace, TypeDef, PropertyDef also in the back-end
    - [ ] Deprecate add/set methods on MutableMapping/accessor classes in the back-end (and front-end?)
  - [ ] Check the input for URIs, names, type names, prefixes etc (if possible in the back-end)
  - [ ] Better name for SB for example: SecB, SecBuilder ...
  - [ ] Nicer yaml output (sort things by type and name)
  - [ ] Raise errors when trying to change a read only document
  - [ ] Load and store YAML documents over HTTP
    - [ ] Use six.move.urllib.parse.urlparse to read paths and uris
  - [ ] Add support for namespaces
    - [ ] Implement NameSpace.from_str()
  - [ ] Add support for links
  - [ ] Implement modes that define how the terminology is handled:
        STRICT, UNCHECKED, CREATE
  - [ ] Access and manipulate property and type definitions from sections directly
  - [ ] Better intro notebook
  - [ ] Public API documentation
  - [ ] YAML format

```
            terms:
                <prefix>:
                    properties:
                        p1:
                        p2:
                    types:
                        t1:
                        t2:
```

  - [ ] JSON back-end
  - [ ] RDF back-end

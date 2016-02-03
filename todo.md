odML TODO list:
===============

  - [x] Public API for
    - [x] namespaces
    - [x] tests for namespaces
    - [x] type definitions
    - [x] tests for type definitions
    - [x] property definitions
    - [x] tests for property definitions
  - [ ] Implement `__str__` for all-front end classes 
  - [ ] Move TODOs from the code to this document (if possible)
  - [ ] Use sortedcontainers.SortedMap instead of dict in the mem back-end.
  - [ ] Remove DictLike class and inherit from collections.Mapping or collections.MutableMapping
  - [ ] Use suffix Access or Accessor instead of Dict in the back-end
  - [ ] Make use of itertools.chain() to concatenate generators (value properties and section properties)
  - [ ] Maybe use immutable front-end classes NameSpace, TypeDef, PropertyDef also in the back-end
  - [ ] Check the input for URIs, names, type names, prefixes etc (if possible in the back-end)
  - [ ] Better name for SB for example: SecB, SecBuilder ...
  - [ ] Nicer yaml output (sort things by type and name)
  - [ ] Implement modes that define how the terminology is handled:
        STRICT, UNCHECKED, CREATE
  - [ ] Access and manipulate property and type definitions from sections directly
  - [ ] Add support for namespaces
  - [ ] Add support for links
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

Components of a odML2 document
------------------------------

### Document properties

* date: the creation date of the document
* uri: the uri where this document is available (not stored in the file)
* author: the author of the document (optional)
* document_version: the version of the document (optional)
* namespaces: associative array where the key is the namespace and the value the uri to another odML2 document
* definitions: associative array where the key is the name of a property or 
* metadata: associative array representing the root section

###### Example:

```yaml
date: 2004-06-14T23:34:30
author: null
document_version: null
suggested_prefix: null
namespaces: null
definitions: null
metadata: null
```

### Namespaces

A namespace makes the content (terms and metadata) from other documents available from this 
document under a certain prefix. 
Does is make sense to restrict the possibility to define terms a document if another document 
was included with the default namespace?

###### Example:

```yaml
namespaces:
  ephys: http://portal.g-node.org/odml/terminologies/v2.0/terminologies.yml
  myterms: ../myterms.yml
```

### Term definitions:

Term definitions can either be type definitions or property definitions. 
Term definitions inside a document reside always inside the default namespace.

#### Type definition:

A type definition consists of a list of properties associated with this type and an optional textual definition. 
Properties might be prefixed with a namespace.

##### Example:

```yaml
definitions:
  RecordingSession:
    definition: Something I do in the lab
    properties:
    - date
    - experimenter
    - ephys:stimuli
  MinimalType:
    properties: []
```

#### Property definition:

A property definition consists of a list of allowed literal or section types and an optional textual definition. 
Section types might be prefixed with a namespace.

###### Example:

```yaml
definitions:
  date:
    definition: The date something was created or an activity or event happened.
    types:
    - xsd:date
    - xsd:dateTime
  experimenter:
    types:
    - ephys:Person
```

### Metadata

#### Sections

Metadata is stored in hierarchically grouped sections. Each section contains the following attributes.

* uuid: A unique identifier consisting of alphanumeric characters and '-'.
* type: A type that may or may not correspond to a type definition in the document or another within 
  another introduced by a namespace.
* label: A human readable identifier consisting of alphanumeric characters, space characters and '-' or '_'.
* reference: An uri to a file that contains data about this section.

##### Example

```yaml
metadata:
  type: RecordingSession
  uuid: bar-bla-foo
  label: Session 1
```

Further a section can have any number of arbitrary properties. 
The name of the property is represented as a key in the associative array representing the section. 
Each property name may or may not correspond to a property definition in the document or within 
another document introduced by a namespace.

#### Value properties

Data properties refer to a plain literal or a composite value consisting of a value a unit and an uncertainty. 
Literals can be strings, iso formatted date times, boolean values, integers or floats. 
The value of a composite value must be an integer or a float.

##### Example:

```yaml
metadata:
  type: RecordingSession
  uuid: bar-bla-foo
  label: Session 1
  # this is a value property with a literal
  date: 2004-06-14T23:34:30
  # this is a value property with a composite value
  duration: 5s+-0.001
```

#### Section properties

Section properties refer to either one single child section or a list of child sections. 
Each section is represented as an associative array with the above mentioned attributes:

##### Example:

```yaml
metadata:
  type: RecordingSession
  uuid: bar-bla-foo
  label: Session 1
  # section property pointing to one single section
  experimenter:
    type: gnode:Person
    uuid: def78ab
```

#### Properties with section links

Instead of referring to an actual section a section property might just contain a uuid of 
another section of the document.
The uuid might be prefixed with a namespace when pointing to a section from another document.

##### Example

```yaml
metadata:
  type: RecordingSession
  uuid: bar-bla-foo
  label: Session 1
  # section property pointing another section of the same document
  experimenter: dazng-gr3ld-83df
```

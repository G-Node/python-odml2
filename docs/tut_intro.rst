Introduction
============

The code in this tutorial can also be found in the `introduction ipython notebook`_.

.. _introduction ipython notebook: https://github.com/G-Node/python-odml2/blob/master/docs/notebooks/tut_intro.ipynb

Create an empty document
------------------------

Working with *odML 2* always starts the creation of an empty :class:`~.Document`.

.. code-block:: python

    import datetime as dt
    from odml2 import Document, SB, Value

    doc = Document()


Basic document properties
-------------------------

Each *odML 2* document has a set of basic attributes which provide additional information.
Some of those are read-only and automatically set to a certain value.
The attribute `location` for example is set when a document is loaded or saved,
it is always none for newly created documents.
Other attributes are writable and meant to be defined by the user.

The following listing shows how those attributes can be accessed:

.. code-block:: python

    # automatically filled properties
    print("doc.is_writable: %s" % doc.is_writable)
    print("doc.is_attached: %s" % doc.is_attached)
    print("doc.location: %s" % doc.location)

    # user defined properties
    doc.author = "John Doe"
    doc.version = 3
    doc.date = dt.datetime.now()

    print("doc.author: %s" % doc.author)
    print("doc.version: %s" % doc.version)
    print("doc.date: %s" % doc.date)

odML value objects
------------------

In *odML 2* all values of non section properties are represented as :class:`~.Value` objects.
In most places where :class:`~.Value` objects are expected as an argument one can also use a plain literal
or variable of the respective type.
But if one wants to define with values additional information such as `unit` or `uncertainty` it is useful
to know how to use them.

The following codes shows how values can be created:

.. code-block:: python

    v = Value(10)
    print(v)
    print(repr(v))

    v = Value(200, unit="µm", uncertainty=0.002)
    print(repr(v))

    v = Value.from_obj("42 +-0.002 mV")
    print(repr(v))

:class:`~.Value` objects are immutable. If one needs a modified instance of a certain value the :meth:`~.Value.copy`
method can used.

.. code-block:: python

    v = v.copy(unit="V")

:class:`~.Value` objects can further be hashed (and therefore be used as keys in dicts) and support all kinds of
comparison operations.

Add a section as document root
------------------------------

To populate an *odML 2* document with metadata one has to create a root :class:`~.Section` which represents
the entry point to the metadata.
:class:`~.Section` instances are usually not created directly.
Instead the section builder class :class:`~.SB` can be used.
It provides a much more convenient and less verbose way to create sections and even entire metadata structures.

.. code-block:: python

    doc.root = SB("RecordingSession", label="session 2")
    doc.root


Add properties to a section
---------------------------

A :class:`~.Section` is basically a dict or map of properties.
There are two different kinds of properties: value properties point to a single :class:`~.Value`,
whereas section properties point to one or many child :class:`~.Section` objects.

The following example shows how both kinds of properties can be added to a parent section:

.. code-block:: python

    sec = doc.root

    sec["recording_date"] = dt.date.today()
    sec["time_delay"] = Value(10, unit="ms", uncertainty=0.001)
    sec["experimenter"] = SB(
            "Person",
            first_name="John",
            last_name="Doe"
    )


Access section properties
-------------------------

Although a section can be seen as a dict with values being either lists of sections or single :class:`~.Value` objects,
the :class:`~.Section` class acts a bit differently in order to make some common uses-cases a bit easier.

.. code-block:: python

    sec["recording_date"]

If a value property is accessed via `square brackets`, the section does actually not return the :class:`~.Value` object,
but instead the values value.
In the above example the returned value would be the a date.

.. code-block:: python

    sec.get("recording_date")

In contrast to the `square brackets` operator the :meth:`~.Section.get` method returns always the :class:`~.Value` object
(if it's a value property).

.. code-block:: python

    sec["experimenter"]

If a section property is accessed via `square brackets` the returned object is either a list of sections or a single
section (in cases where the property points to a list of sections with only one entry).

.. code-block:: python

    sec.get("experimenter")

The :meth:`~.Section.get` method returns always a list of sections when it is used to access a section property.

Generally accessing properties via `square brackets` is more convenient, especially if the type of a property is
already known.
Access via :meth:`~.Section.get` in contrast is more reliable and should be used when unknown documents are processed.

Save the odML document
----------------------

.. code-block:: python

    doc.save("intro.yml")

    with open("intro.yml") as f:
        print(f.read())

::

    date: 2016-02-17 11:59:15.587085
    document_version: 3
    format_version: 2
    author: John Doe
    namespaces: null
    definitions: null
    metadata:
      type: RecordingSession
      uuid: 941350b3-a4e9-42d1-ad76-85def35120b0
      label: session 2
      recording_date: 2016-02-17
      experimenter:
        type: Person
        uuid: f1473908-6a84-420a-9c25-d288a44715ef
        first_name: John
        last_name: Doe

Load a document
---------------

.. code-block:: python

    new_doc = Document()
    new_doc.load("intro.yml")
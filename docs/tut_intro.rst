Introduction
============

The code in this tutorial can also be found in the `introduction ipython notebook`_.

*TODO* write some text for each code listing

.. _introduction ipython notebook: https://github.com/G-Node/python-odml2/blob/master/docs/notebooks/tut_intro.ipynb

Create an empty document
------------------------

.. code-block:: python

    import datetime as dt
    from odml2 import Document, SB, Value

    doc = Document()


Basic document properties
-------------------------

.. code-block:: python

    # automatically filled properties
    print("doc.is_writable: %s" % doc.is_writable)
    print("doc.is_attached: %s" % doc.is_attached)
    print("doc.location: %s" % doc.location)

    # user defined properties
    doc.author = "Jhon Doe"
    doc.version = 3
    doc.date = dt.datetime.now()

    print("doc.author: %s" % doc.author)
    print("doc.version: %s" % doc.version)
    print("doc.date: %s" % doc.date)

odML value objects
------------------

.. code-block:: python

    v = Value(10)
    print(v)
    print(repr(v))

    v = Value(200, unit="µm", uncertainty=0.002)
    print(repr(v))

    v = Value.from_obj("42 +-0.002 mV")
    print(repr(v))


Add a section as document root
------------------------------

.. code-block:: python

    doc.root = SB("RecordingSession", label="session 2")
    doc.root


Add add properties to a section
-------------------------------

.. code-block:: python

    sec = doc.root

    sec["recording_date"] = dt.date.today()
    sec["time_delay"] = Value(10, unit="ms", uncertainty=0.001)
    sec["experimenter"] = SB(
            "Person",
            first_name="Jhon",
            last_name="Doe"
    )


Access section properties
-------------------------

.. code-block:: python

    sec["recording_date"]

.. code-block:: python

    sec.get("recording_date")

.. code-block:: python

    sec["experimenter"]

.. code-block:: python

    exp = sec["experimenter"]
    print(exp["first_name"])
    print(exp["last_name"])

.. code-block:: python

    sec.get("experimenter")

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
    author: Jhon Doe
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
        first_name: Jhon
        last_name: Doe

Load a document
---------------

.. code-block:: python

    new_doc = Document()
    new_doc.load("intro.yml")
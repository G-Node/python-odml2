Advanced Tutorial
=================

he code in this tutorial can also be found in the `advanced ipython notebook`_.

*TODO* write some text for each code listing

.. _advanced ipython notebook: https://github.com/G-Node/python-odml2/blob/master/docs/notebooks/tut_advanced.ipynb

Create a document with global information
-----------------------------------------

.. code-block:: python

    import datetime as dt
    from odml2 import Document, SB, Value

    glob = Document()

.. code-block:: python

    glob.root = SB(
        "ResearchLab",
        name="Dr. Doe Lab",
        researchers=[
            SB("Person",
                label="Doe,
                Jhon",
                first_name="Jhon",
                last_name="Doe"
            ),
            SB("Person",
                label="Foo,
                Bar",
                first_name="Bar",
                last_name="Foo"
            )
        ],
        animals=[
            SB("Animal",
                label="subj 11",
                subject_id=11,
                date_of_birth=dt.date(2015, 11, 24),
                species="Mus musculus"
            ),
            SB("Animal",
                label="subj 12",
                subject_id=12,
                date_of_birth=dt.date(2015, 11, 25),
                species="Mus musculus"
            )
        ]
    )

.. code-block:: python

    glob.save("global.yml")

    with open("global.yml") as f:
        print(f.read())


::

    date: null
    document_version: 1
    format_version: 2
    author: null
    namespaces: null
    definitions: null
    metadata:
      type: ResearchLab
      uuid: 49301a53-13de-44bd-bbf8-0a8756acbd67
      name: Dr. Doe Lab
      animals:
      - type: Animal
        uuid: 510520c9-a2af-479c-81dd-1448500d3222
        label: subj 11
        date_of_birth: 2015-11-24
        species: Mus musculus
        subject_id: 11
      - type: Animal
        uuid: a5b1167c-bce2-4ef7-97be-522060f75557
        label: subj 12
        date_of_birth: 2015-11-25
        species: Mus musculus
        subject_id: 12
      researchers:
      - type: Person
        uuid: 81dbf66f-80b5-444b-a57e-64868765a57d
        label: Doe, Jhon
        first_name: Jhon
        last_name: Doe
      - type: Person
        uuid: ddd2717c-de93-482b-90e0-b281b46ac1e0
        label: Foo, Bar
        first_name: Bar
        last_name: Foo

Select data from documents
--------------------------

.. code-block:: python

    # select a person with last name 'Doe' from all sections
    experimenter = (s for s in glob.iter_sections()
                    if s.type == "Person" and
                       s["last_name"] == "Doe").next()

    # select the animal with id 11 from all animals
    animal = (a for a in glob.root["animals"]
              if a["subject_id"] == 11).next()

Crate a document with session information
-----------------------------------------

.. code-block:: python

    session = Document()
    session.root = SB("RecordingSession",
        label="session 42",
        session_nr=42,
        recording_date=dt.date.today()
    )

    session.save("session.yml")

Copy data from other documents
------------------------------

.. code-block:: python

    session = Document()
    session.load("session.yml")

    # copy global data to session document
    session.root["experimenter"] = experimenter
    session.root["subject"] = animal

    session.root["subject"]["health"] = "good"
    if "health" not in animal:
        print("It's a copy")

::

    It's a copy

Link data from other documents
------------------------------

.. code-block:: python

    session = Document()
    session.load("session.yml")

    session.namespaces.set("glob", "global.yml")

    # copy global data to session document
    session.root["experimenter"] = experimenter
    session.root["subject"] = animal

    try:
        session.root["subject"]["health"] = "good"
    except:
        print("It's a link, can't change a section" +
              "from another document")

::

    It's a link, can't change a section from another document

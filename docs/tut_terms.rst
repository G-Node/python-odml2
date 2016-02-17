Terminology Tutorial
====================

The code in this tutorial can also be found in the `terminology ipython notebook`_.

*TODO* write some text for each code listing

.. _terminology ipython notebook: https://github.com/G-Node/python-odml2/blob/master/docs/notebooks/tut_terms.ipynb


Create a document with terms
----------------------------

.. code-block:: python

    import datetime as dt
    from odml2 import Document, TerminologyStrategy, SB, Value

    terms = Document()

    # some section types with their properties
    terms.type_definitions.set("RecordingSession",
                               "An experimental procedure",
                               properties=[
                                    "subject",
                                    "recording_date",
                                    "session_nr"])
    terms.type_definitions.set("Animal",
                               "A non human, animal individual",
                               properties=[
                                    "subject_id",
                                    "date_of_birth",
                                    "species"])

.. code-block:: python

    # define properties with their types
    terms.property_definitions.set("subject",
                                   types=["Animal"])
    terms.property_definitions.set("session_nr",
                                   types=["int"])
    terms.property_definitions.set("recording_date",
                                   types=["date", "datetime"])
    terms.property_definitions.set("subject_id",
                                   types=["int"])
    terms.property_definitions.set("species",
                                   types=["string"])
    terms.property_definitions.set("date_of_birth",
                                   types=["date", "datetime"])

.. code-block:: python

    terms.save("terms.yml")

    with open("terms.yml") as f:
        print(f.read())

::

    date: null
    document_version: 1
    format_version: 2
    author: null
    namespaces: null
    definitions:
      date_of_birth:
        types:
        - date
        - datetime
      recording_date:
        types:
        - date
        - datetime
      session_nr:
        types:
        - int
      species:
        types:
        - string
      subject:
        types:
        - Animal
      subject_id:
        types:
        - int
      Animal:
        properties:
        - subject_id
        - date_of_birth
        - species
        definition: A non human, animal individual
      RecordingSession:
        properties:
        - session_nr
        - recording_date
        - subject
        definition: An experimental procedure
    metadata: null

Alter existing terms
--------------------

.. code-block:: python

    recd = terms.property_definitions["recording_date"]
    terms.property_definitions["recording_date"] = recd.copy(definition="Date of a recording")

    terms.save("terms.yml")

Use terms from another document
-------------------------------

.. code-block:: python

    session = Document(strategy=TerminologyStrategy.Ignore)
    session.namespaces.set("terms", "terms.yml")

    session.root = SB(
        "terms:RecordingSession",
        **{
            "terms:session_nr": 42,
            "terms:recording_date": dt.date.today(),
            "terms:subject": SB(
                "terms:Animal",
                **{
                    "terms:subject_id": 12,
                    "terms:date_of_birth": dt.date(2015, 11, 25),
                    "terms:species": "Mus musculus"
                }
            )
        }
    )

    # It's ok to add things not defined in a terminology
    session.root["quality_level"] = "medium"

Make sure a document sticks to known terms
------------------------------------------

.. code-block:: python

    session = Document(strategy=TerminologyStrategy.Strict)

    try:
        session.root = SB(
            "terms:RecordingSession",
            **{
                "terms:session_nr": 42,
                "terms:recording_date": dt.date.today(),
                "terms:subject": SB(
                    "terms:Animal",
                    **{
                        "terms:subject_id": 12,
                        "terms:date_of_birth": dt.date(2015, 11, 25),
                        "terms:species": "Mus musculus"
                    }
                )
            }
        )
    except Exception as e:
        print(e.message)
        print("Does not work because no terms are not defined")

::


    The namespace 'terms:RecordingSession' is not known in this document
    Does not work because no terms are not defined

.. code-block:: python

    session.namespaces.set("terms", "terms.yml")
    session.root = SB(
        "terms:RecordingSession",
        **{
            "terms:session_nr": 42,
            "terms:recording_date": dt.date.today(),
            "terms:subject": SB(
                "terms:Animal",
                **{
                    "terms:subject_id": 12,
                    "terms:date_of_birth": dt.date(2015, 11, 25),
                    "terms:species": "Mus musculus"
                }
            )
        }
    )

.. code-block:: python

    try:
        session.root["quality_level"] = "medium"
    except Exception as e:
        print(e.message)
        print("Does not work because no property is not defined")

::

    The property 'quality_level' is not defined for type 'terms:RecordingSession'
    Does not work because no property is not defined

"""
Annotation source registry

A second, separate registry from sourcerer.Sources: annotation databases
(IEDB, and others to follow) are SourceBase subclasses too, but are kept apart
from repertoire sources so the commandline can mount them under their own
`sourcerer annotation <db>` tree instead of `sourcerer <source>`.
"""

# Info
__author__ = 'Pramod Shinde'

# Sourcerer imports
from sourcerer.Annotations.Iedb import IedbSource

#: Every annotation source sourcerer knows about, by commandline name.
REGISTRY = {IedbSource.name: IedbSource}


def getAnnotationSource(name, client, schema=None):
    """
    Instantiate an annotation source by name.

    Arguments:
      name (str): the source name.
      client (HttpClient): the shared HTTP client.
      schema (SourceSchema): a preloaded snapshot, or None to load on demand.

    Returns:
      SourceBase: the source.

    Raises:
      KeyError: if the name is not registered.
    """
    if name not in REGISTRY:
        raise KeyError("unknown annotation source '%s'; known: %s"
                       % (name, ', '.join(sorted(REGISTRY))))

    return REGISTRY[name](client, schema=schema)

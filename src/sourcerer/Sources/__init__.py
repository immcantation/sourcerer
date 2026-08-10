"""
Source registry

A plain dictionary. Entry point based plugin discovery is a small change to make
later, once a second source exists to justify it.
"""

# Info
__author__ = 'Susanna Marquez'

# Sourcerer imports
from sourcerer.Sources.Oas import OasSource

#: Every source sourcerer knows about, by commandline name.
REGISTRY = {OasSource.name: OasSource}


def getSource(name, client, schema=None):
    """
    Instantiate a source by name.

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
        raise KeyError("unknown source '%s'; known sources: %s"
                       % (name, ', '.join(sorted(REGISTRY))))

    return REGISTRY[name](client, schema=schema)

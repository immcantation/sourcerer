.. _Usage:

Commandline Usage
================================================================================

``sourcerer`` is a single command with a subcommand tree: one subcommand per
external source (``oas`` today), a ``schema`` subcommand to inspect and
re-harvest the stored snapshot each source is built from, and a ``sources``
subcommand that lists what is registered.

Every source subcommand exposes the same two actions, ``search`` and
``download``, each taking a collection (for example ``paired`` or
``unpaired``) as a further subcommand. The filter flags under a collection —
``--species``, ``--disease``, and so on — are not hardcoded: they are
generated at parser-construction time from the checked-in schema snapshot
described in :ref:`API`, which is also why they appear below exactly as they
would in ``--help`` on the machine building these docs.

Commands are documented one page per top level subcommand, mirroring how the
commandline itself groups them: :doc:`sources` and :doc:`schema` apply
across every source, and each remaining page below documents one source
module's own ``search``/``download`` tree. Adding a new source means adding
one page here alongside it.

.. toctree::
   :maxdepth: 2

   sources
   schema
   oas

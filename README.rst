nfdocs-parser
=============

A `Sphinx <https://www.sphinx-doc.org>`_ Extension for automatically generating
documentation from `Nextflow <https://nextflow.io>`_ workflows, processes, and
functions with YAML docstrings.

Usage
-----

I'm not putting this on `PyPi <https://pypi.org>`_ just yet, so you'll have to
use this as a Git submodule. In your documentation project, run

.. code-block:: bash

    mkdir _ext
    git submodule https://github.com/MillironX/nfdocs-parser.git _ext/nfdocs-parser.git


Then update your ``conf.py`` to include the following lines:

.. code-block:: python

    import os
    import sys
    sys.path.append(os.path.abspath('./_ext'))

    extensions = [
        # Keep any other extensions, like InterSphinx and AutoSectionLabel here
        'nfdocs-parser.nfdocs-parser',
    ]

Inside your documentation file, include the following directive:

.. code-block:: rst

    .. nfdocs:: ../path/to/nextflow/project/directory

The extension will look for properly-formatted docstrings in all of your
Nextflow files (extension ``.nf``) within that directory and its subdirectories
and output the documentation in that file.

Example
-------

Take a simple Nextflow process, this is a pared-down example from
`nf-core/modules <https://github.com/nf-core/modules>`_.

.. code-block:: groovy

    process KRAKEN2 {
        input:
        tuple val(prefix), path(reads)
        path(db)

        output:
        tuple val(prefix), path("*classified*"), emit: classified
        tuple val(prefix), path("*unclassified*"), emit: unclassified
        tuple val(prefix), path("*report.txt"), emit: report

        script:
        """
        kraken2 \\
            --db ${db} \\
            --classified-out ${prefix}.classified.fastq \\
            --unclassified-out ${prefix}.unclassified.fastq \\
            --report ${prefix}.kraken2.report.txt \\
            ${reads}
        """
    }

This process still has a lot of unique inputs and outputs, so we annotate it
using triple slashes (``///``) and YAML notation

.. code-block:: groovy

    /// summary: Classifies metagenomic sequence data
    /// input:
    ///   - tuple:
    ///       - name: prefix
    ///         type: val(String)
    ///         description: Sample identifier
    ///       - name: reads
    ///         type: path
    ///         description: List of input FastQ files
    ///   - name: db
    ///     type: path
    ///     description: Kraken2 database directory
    /// output:
    ///   - name: classified
    ///     tuple:
    ///       - type: val(String)
    ///         description: Sample identifier
    ///       - type: path
    ///         description: |
    ///           Reads classified to belong to any of the taxa in the Kraken2
    ///           database
    ///   - name: unclassified
    ///     tuple:
    ///       - type: val(String)
    ///         description: Sample identifier
    ///       - type: path
    ///         description: |
    ///           Reads not classified to belong to any of the taxa in the
    ///           Kraken2 database
    ///   - name: txt
    ///     tuple:
    ///       - type: val(String)
    ///         description: Sample identifier
    ///       - type: path
    ///         description: |
    ///           Kraken2 report containing stats about classified and not
    ///           classified reads
    process KRAKEN2 {
        ...
    }

You will get output that looks something like this:

Input
'''''

+-------------------------+-------------------------------------------------------------------+
| **Tuple**               |                                                                   |
|                         | +--------------------------+----------------------------------+   |
|                         | | **prefix** (val(String)) | Sample identifier                |   |
|                         | +--------------------------+----------------------------------+   |
|                         | | **reads** (path)         | List of input FastQ files        |   |
|                         | +--------------------------+----------------------------------+   |
|                         |                                                                   |
+-------------------------+-------------------------------------------------------------------+
| **db** (path)           | Kraken2 database directory                                        |
+-------------------------+-------------------------------------------------------------------+

Output
''''''

+--------------------------+-------------------------------------------------------------------+
| **classified** (Tuple)   |                                                                   |
|                          | +--------------------------+----------------------------------+   |
|                          | | val(String)              | Sample identifier                |   |
|                          | +--------------------------+----------------------------------+   |
|                          | | path                     | Reads classified to belong to    |   |
|                          | |                          | any of the taxa in the Kraken2   |   |
|                          | |                          | database                         |   |
|                          | +--------------------------+----------------------------------+   |
|                          |                                                                   |
+--------------------------+-------------------------------------------------------------------+
| **unclassified** (Tuple) |                                                                   |
|                          | +--------------------------+----------------------------------+   |
|                          | | val(String)              | Sample identifier                |   |
|                          | +--------------------------+----------------------------------+   |
|                          | | path                     | Reads not classified to belong   |   |
|                          | |                          | to any of the taxa in the        |   |
|                          | |                          | Kraken2 database                 |   |
|                          | +--------------------------+----------------------------------+   |
|                          |                                                                   |
+--------------------------+-------------------------------------------------------------------+
| **txt** (Tuple)          |                                                                   |
|                          | +--------------------------+----------------------------------+   |
|                          | | val(String)              | Sample identifier                |   |
|                          | +--------------------------+----------------------------------+   |
|                          | | path                     | Kraken2 report containing stats  |   |
|                          | |                          | about classified and not         |   |
|                          | |                          | classified reads                 |   |
|                          | +--------------------------+----------------------------------+   |
|                          |                                                                   |
+--------------------------+-------------------------------------------------------------------+

Motivation
----------

I liked using the XML documentation blocks in VB.NET because it worked so well
with IntelliSense. I often find myself scrolling through Nextflow code to
remember what the form of the input tuple for a particular process was or how
many outputs I need to account for. YAML seemed like a far superior language for
documentation, and as most of my Nextflow projects were already using Sphinx,
parsing the docstrings as part of my Sphinx documentation seemed like the
logical thing to do.

Why don't you just use a sidecar ``meta.yml`` file like nf-core does?
---------------------------------------------------------------------

Honestly, because I started using my own format before realizing what the
``meta.yml`` file had in it. After some consideration, however, I like my system
better and am not planning to add compatibility for ``meta.yml`` files.

Reasons my system is better:

* No need for sidecar files: everything is in one place
* Tuple channels are noted as being different that the components that make them
  up, e.g. knowing that a process requires a tuple of ``val(prefix), file(reads)`` and
  a file of ``reference_genome`` is more informative than knowing that a
  process needs a ``val(prefix)``, ``file(reads)`` and
  ``file(reference_genome)``

#!/usr/bin/env python
import sys

# Declare the docstring starting characters
DOC_STARTER = "/// "

# Take path as single argument for now
nextflow_path = sys.argv[1]
with open(nextflow_path) as nextflow_file:

    # Split by lines
    nextflow_lines = nextflow_file.readlines()

    # Declare some variables to keep track of where the docstrings begin and end
    doc_start = 0
    doc_end = 0

    # Declare dictionaries to keep track of the docstrings
    docstring_positions = []

    # Calculate the start and end positions of each docstring
    for i, line in enumerate(nextflow_lines):
        # Check if this is a docstring
        if line.startswith(DOC_STARTER):
            # It is: check the next and previous lines to see if this is part of a block
            line_previous = nextflow_lines[i-1]
            line_next = nextflow_lines[i+1]
            if not line_previous.startswith(DOC_STARTER):
                doc_start = i
            if not line_next.startswith(DOC_STARTER):
                doc_end = i

            # Check if we've reached the end of a docstring block
            if doc_end == i:
                # Add this docstring position to the array
                docstring_positions.append(range(doc_start, doc_end))

    # Display the results so far
    print(docstring_positions)

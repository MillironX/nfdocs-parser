#!/usr/bin/env python
import sys
import yaml
from docutils import nodes

# Declare the docstring starting characters
DOC_STARTER = "/// "

def definition_type(signature):
    # Returns "name", workflow|process|function
    def_type = "unknown"
    if "workflow" in signature:
        def_type = "workflow"
    elif "process" in signature:
        def_type = "process"
    elif "function" in signature:
        def_type = "function"

    # Check if any signature was recognized
    if def_type == "unknown":
        return "unknown", "an error occurred"

    # Parse out the definition name
    def_name = signature.replace(def_type, "").replace("{", "").strip()

    # Return the results
    return def_name, def_type

def params_to_list(params):
    if "tuple" in params.keys():
        tuple_item = nodes.list_item()
        if "name" in params.keys():
            tuple_item += nodes.paragraph(text=params["name"])
        tuple_item += nodes.paragraph(text="Tuple:")
        tuple_list = nodes.bullet_list()
        for io in params["tuple"]:
            tuple_list += params_to_list(io)
        tuple_item += tuple_list
        return tuple_item
    else:
        io_item = nodes.list_item()
        if "name" in params.keys():
            io_item += nodes.paragraph(text=params["name"])
        io_item += nodes.paragraph(text=f"Type: {params['type']}")
        io_item += nodes.paragraph(text=params["description"])
        return io_item

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
                docstring_positions.append(range(doc_start, doc_end+1))

    # Create dictionaries for each of the block types
    docstrings = {
        "process": {},
        "workflow": {},
        "function": {}
    }

    # Parse out the docstrings and put them in the appropriate dictionary
    for pos in docstring_positions:
        proc_name, proc_type = definition_type(nextflow_lines[pos[-1]+1])
        doc_yaml = ""
        for i in pos:
            doc_yaml = doc_yaml + nextflow_lines[i].replace(DOC_STARTER, "")
        docstrings[proc_type][proc_name] = yaml.safe_load(doc_yaml)

    # Display the results so far
    print(docstrings)

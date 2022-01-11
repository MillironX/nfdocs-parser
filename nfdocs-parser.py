#!/usr/bin/env python
import inflect
import os
import yaml
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives

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

class NFDocs(Directive):
    # Class default overrides
    required_arguments = 1

    # Declare the docstring starting characters
    DOC_STARTER = "/// "

    pe = inflect.engine()

    def params_to_table(self, type, params):
        # Create a table
        params_table = nodes.table()
        if type:
            params_table += nodes.title(text=type.capitalize())

        # Make it two columns wide
        params_tgroup = nodes.tgroup(cols=2)
        for _ in range(2):
            colspec = nodes.colspec(colwidth=1)
            params_tgroup.append(colspec)

        # Create the row definitions
        params_rows = []

        for param in params:
            # Create a new row
            param_row = nodes.row()

            # If this parameter is a tuple, the new row takes on the form
            # +-------+------------------+
            # |       | +--------------+ |
            # | Tuple | | Params Table | |
            # |       | +--------------+ |
            # +-------+------------------+
            # via recursion
            if "tuple" in param.keys():
                # Tuple title
                param_name_entry = nodes.entry()
                param_name_entry += nodes.strong(text="Tuple")
                param_row += param_name_entry

                # Params table
                sub_params_entry = nodes.entry()
                sub_params_entry += self.params_to_table("", param["tuple"])
                param_row += sub_params_entry

            # If this is actually a parameter, the new row takes on the form
            # +------------+-------------+
            # | Name(Type) | Description |
            # +------------+-------------+
            # or
            # +------+-------------+
            # | Type | Description |
            # +------+-------------+
            else:
                # Parameter title
                param_name_entry = nodes.entry()
                if "name" in param.keys():
                    param_name_entry += nodes.strong(text=param["name"])
                    param_name_entry += nodes.Text(f"({param['type']})")
                else:
                    param_name_entry += nodes.Text(param["type"])
                param_row += param_name_entry

                # Parameter description
                param_description_entry = nodes.entry()
                param_description = nodes.paragraph(text=param["description"])
                self.state.nested_parse(self.content, self.content_offset, param_description)
                param_description_entry += param_description
                param_row += param_description_entry

            # Add this row to the vector
            params_rows.append(param_row)

        # Convert the rows to a table
        params_table_body = nodes.tbody()
        params_table_body.extend(params_rows)
        params_tgroup += params_table_body
        params_table += params_tgroup
        return params_table

    def run(self):
        # Take path as single argument for now
        nextflow_path = self.arguments[0]
        print(nextflow_path)

        # Create dictionaries for each of the block types
        docstrings = {
            "workflow": {},
            "process": {},
            "function": {}
        }

        # Create any array to return from the plugin
        return_nodes = []

        for root, dirs, files in os.walk(nextflow_path):
            for f in files:
                if f.endswith(".nf"):
                    with open(os.path.join(root,f)) as nextflow_file:

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
                            if line.startswith(self.DOC_STARTER):
                                # It is: check the next and previous lines to see if this is part of a block
                                line_previous = nextflow_lines[i-1]
                                line_next = nextflow_lines[i+1]
                                if not line_previous.startswith(self.DOC_STARTER):
                                    doc_start = i
                                if not line_next.startswith(self.DOC_STARTER):
                                    doc_end = i

                                # Check if we've reached the end of a docstring block
                                if doc_end == i:
                                    # Add this docstring position to the array
                                    docstring_positions.append(range(doc_start, doc_end+1))

                        # Parse out the docstrings and put them in the appropriate dictionary
                        for pos in docstring_positions:
                            proc_name, proc_type = definition_type(nextflow_lines[pos[-1]+1])
                            doc_yaml = ""
                            for i in pos:
                                doc_yaml = doc_yaml + nextflow_lines[i].replace(self.DOC_STARTER, "")
                            docstrings[proc_type][proc_name] = yaml.safe_load(doc_yaml)

        # Try to convert each definition to a node
        for block_type, block_docs in docstrings.items():
            # Check if there are any blocks of this type
            if len(block_docs) > 0:
                # Create a new section for this type of block
                block_section = nodes.section()
                block_section += nodes.title(text=self.pe.plural(block_type.capitalize(), len(block_docs)))

                # Sort the blocks alphabetically
                sorted_block_docs = {key: val for key, val in sorted(block_docs.items(), key = lambda ele: ele[0])}

                # Create a subsection for each block
                for proc_name, proc_docs in sorted_block_docs.items():
                    # Create the section and heading
                    proc_section = nodes.section()
                    proc_section += nodes.title(text=proc_name)
                    proc_section += nodes.paragraph(text=proc_docs["summary"])

                    # Create the io tables
                    io_methods = ["input", "output"]
                    for met in io_methods:
                        if met in proc_docs.keys():
                            io_table = self.params_to_table(met, proc_docs[met])
                            proc_section += io_table

                    # Add the block section to the parent node
                    self.state_machine.document.note_implicit_target(proc_section)
                    block_section += proc_section

                # Add the type of block section to the document
                self.state_machine.document.note_implicit_target(block_section)
                return_nodes.append(block_section)

        return return_nodes

def setup(app):
    app.add_directive('nfdocs', NFDocs)
    return {
        "version": "0.1.0"
    }

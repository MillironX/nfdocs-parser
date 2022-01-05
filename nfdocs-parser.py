#!/usr/bin/env python
import sys

# Take path as single argument for now
nextflow_path = sys.argv[1]
with open(nextflow_path) as nextflow_file:

    # Split by lines
    nextflow_lines = nextflow_file.readlines()

    # Print the first few lines
    for i in range(1, 10):
        print(nextflow_lines[i])

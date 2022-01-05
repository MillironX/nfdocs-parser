#!/usr/bin/env python
import sys

nextflow_path = sys.argv[1]
with open(nextflow_path) as nextflow_file:
    nextflow_lines = nextflow_file.readlines()
    for i in range(1, 10):
        print(nextflow_lines[i])

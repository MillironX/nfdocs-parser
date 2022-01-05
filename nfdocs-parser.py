#!/usr/bin/env python
import sys

nextflow_path = sys.argv[1]
with open(nextflow_path) as nextflow_file:
    print(nextflow_file)

#!/usr/bin/env python

from __future__ import division

import sys
import copy
import json

from interpreter import *

def run(ast, setting):
	entry = setting["function"]
	args = setting["args"]
	vars = setting["vars"]
	var_names = vars.keys()
	var_ranges = vars.values()
	nvars = len(var_names)

	counters = []
	for r in var_ranges:
		counters.append(r[0])

	while True:
		
		# setup root
		v = RootVisitor()
		v.visit(ast)
		
		# set variables
		for i in range(nvars):
			v.setVariable(var_names[i], counters[i])
		
		# call function
		if v.callFunction(entry, args) == False:
			print("func %s not found" % entry)
		else:
			# print variables
			print ""
			for key, value in v.v.records.items():
				print key.name, value["min"], value["max"]
		
		# update counter
		counters[0] += 1
		for i in range(nvars):
			if counters[i] > var_ranges[i][1]: # if exceeds max
				if i+1 >= nvars:
					return
				counters[i] = var_ranges[i][0] # init to min
				counters[i+1] += 1 # increment upper-level counter
			else:
				break
	

if len(sys.argv) < 2:
	print("specify setting file")
	sys.exit()

f = open(sys.argv[1])
setting = json.load(f)
f.close()

ast = parse_file(
    setting["file"],
    use_cpp=True,
    cpp_path=r'./pycparser/utils/cpp.exe',
    cpp_args=r'-I./pycparser/utils/fake_libc_include'
    )
#ast.show()

run(ast, setting)


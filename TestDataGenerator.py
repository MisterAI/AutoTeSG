#!/usr/bin/python

from ast import *
import BranchCollector
from CodeRunner import *
from CustomExceptions import *
from AVM import AVM

class TestDataGenerator(NodeVisitor):
	def visit_FunctionDef(self, node):
		"""
		Visit all functions to generate test inputs.
		"""
		header_string = ('Generating data for function '
			+ str(node.name) 
			+ '\n\nBranch, Corresponding input values ')
		variable_names = []
		for in_param in node.args.args:
			try:
				variable_names.append(in_param.id)
			except AttributeError as e:
				variable_names.append(in_param.arg)
		header_string += str(variable_names)
		print(header_string)

		# get all possible branches of function
		branches = BranchCollector.collect_branches(node)
		
		# save successful inputs for every branching line as 
		# Tupel:(lineno, input_list)
		input_tuples = []
		
		for branch in branches:
			# print('Searching covering input for branch ' + str(branch))
			AVM().AVMsearch(node, branch, input_tuples)
		print('\n')

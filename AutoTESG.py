#!/usr/bin/python

import sys, getopt
import astor
from ast import walk, FunctionDef
from CodeInstrumentator import CodeInstrumentator, RemovePrintStmts
from TestDataGenerator import TestDataGenerator
import BranchCollector
from AVM import AVM

__version__ = '0.0.1'


def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hv")
	except getopt.GetoptError:
		print('Usage: AutoTeSG.py [-h] [-v] FILE...')
		sys.exit(1)
	for opt, arg in opts:
		if opt == '-h':
			print('Usage: AutoTeSG.py [-h] [-v] FILE...')
			sys.exit()
		elif opt == '-v':
			print('AutoTeSG ' + __version__)
			print('')
			print('Written by Tobias P., 2018')
			sys.exit()

	if not len(args) > 0:
		print('Please specify an input file!')
		sys.exit()

	for input_file in args:
		try:
			myAST = astor.code_to_ast.parse_file(input_file)
		except Exception as e:
			raise e

		print('Analysing file ' + str(input_file))

		RemovePrintStmts().visit(myAST)
		CodeInstrumentator().visit(myAST)

		for node in walk(myAST):
			if isinstance(node, FunctionDef):
				header_string = ('Generating test data for function \''
					+ str(node.name) 
					+ '\'\n\nBranch, Corresponding input values ')
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
					AVM().AVMsearch(myAST, node, branch, input_tuples)
				print('\n')


if __name__ == "__main__":
	main(sys.argv[1:])





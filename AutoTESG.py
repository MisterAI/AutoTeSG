#!/usr/bin/python

import sys, getopt
import astor
from CodeInstrumentator import CodeInstrumentator, RemovePrintStmts
from TestDataGenerator import TestDataGenerator

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

		RemovePrintStmts().visit(myAST)
		CodeInstrumentator().visit(myAST)

		TestDataGenerator().visit(myAST)



if __name__ == "__main__":
	main(sys.argv[1:])





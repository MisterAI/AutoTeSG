#!/usr/bin/python

import sys, getopt
import astor
import ast
import BranchCollector

__version__ = '0.0.1'


def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hv")
	except getopt.GetoptError:
		print 'Usage: AutoTeSG.py [-h] [-v] FILE...'
		sys.exit(1)
	for opt, arg in opts:
		if opt == '-h':
			print 'Usage: AutoTeSG.py [-h] [-v] FILE...'
			sys.exit()
		elif opt == '-v':
			print('AutoTeSG ' + __version__)
			print('')
			print('Written by Tobias P., 2018')
			sys.exit()

	if not len(args) > 0:
		print("Please specify an input file!")
		sys.exit()

	for input_file in args:
		try:
			myAST = astor.parsefile(input_file)
		except Exception as e:
			raise e
		# print(astor.dump(myAST))
		for listi in BranchCollector.collect_branches(myAST):
			print(listi)
		# myTreeWalk = astor.TreeWalk()
		# for node in ast.iter_child_nodes(myAST):
		# 	pass
		# 	# print(node.__)
		# print(ast.iter_child_nodes(myAST))


if __name__ == "__main__":
	main(sys.argv[1:])





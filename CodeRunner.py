#!/usr/bin/python

import sys
import astor
from ast import parse

if sys.version_info[0] < 3:
	from io import BytesIO
else:
	from io import StringIO

def doRun(codeTree):
	compiled_code = compile(astor.to_source(codeTree), filename="<ast>", 
		mode="exec")
	exec(compiled_code)

def runCode(codeTree):
	"""
	Run code and return output, generated on stdout.
	"""

	# Temporarily redirect output to own IO
	old_stdout = sys.stdout
	if sys.version_info[0] < 3:
		my_output = sys.stdout = BytesIO()
	else:
		my_output = sys.stdout = StringIO()

	compiled_code = compile(astor.to_source(codeTree), filename="<ast>", 
		mode="exec")
	try:
		# use the same dictionary for local and global variables to prevent 
		# scope issues
		dictionary = {}
		exec(compiled_code, dictionary, dictionary)
	except:
		sys.stdout = old_stdout
		raise

	# Restore sys stdout
	sys.stdout = old_stdout

	return my_output.getvalue()

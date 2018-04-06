#!/usr/bin/python

import sys
import ast

if sys.version_info[0] < 3:
	from io import BytesIO
else:
	from io import StringIO

def getCodeOutput(codeTree):
	"""
	Temporarily redirect output to own IO
	"""
	old_stdout = sys.stdout
	if sys.version_info[0] < 3:
		my_output = sys.stdout = BytesIO()
	else:
		my_output = sys.stdout = StringIO()

	compiled_code = compile(codeTree, filename="<ast>", mode="exec")
	exec(compiled_code)
	
	# Restore sys stdout
	sys.stdout = old_stdout

	return my_output.getvalue()

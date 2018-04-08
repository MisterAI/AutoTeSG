#!/usr/bin/python

import sys
import astor

if sys.version_info[0] < 3:
	from io import BytesIO
else:
	from io import StringIO

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

	# instru_source = astor.to_source(codeTree)
	# source_file = open('test.py', 'w')
	# source_file.write(instru_source)
	# source_file.close()

	compiled_code = compile(astor.to_source(codeTree), filename="<ast>", mode="exec")
	exec(compiled_code)
	
	# Restore sys stdout
	sys.stdout = old_stdout

	return my_output.getvalue()

#!/usr/bin/python

from ast import *
import astor

class RemovePrintStmts(NodeTransformer):
	"""
	Removes all print statements so they don't interfere 
	with the instrumentation
	"""
	def visit_Print(self, node):
		self.generic_visit(node)
		node = Expr(value=Tuple(elts=node.values, ctx=Load()))
		fix_missing_locations(node)
		return node
		# return None

	def visit_Expr(self, node):
		self.generic_visit(node)
		if hasattr(node.value, 'func'):
			if hasattr(node.value.func, 'id'):
				if node.value.func.id == 'print':
					new_expr = Expr(value=Tuple(elts=node.value.args, ctx=Load()))
					node = new_expr
					fix_missing_locations(node)
					return node
		return node

class CodeInstrumentator(NodeTransformer):
	def get_print_stmt(self, lineno):
		return parse('print(' + str(lineno) + ')').body[0]

	def insert_print(self, node):
		node.body.insert(0, self.get_print_stmt(node.lineno))
		fix_missing_locations(node.body[0])

	def visit_If(self, node):
		self.insert_print(node)
		self.generic_visit(node)
		return node

	def visit_For(self, node):
		self.insert_print(node)
		self.generic_visit(node)
		return node

	def visit_While(self, node):
		self.insert_print(node)
		self.generic_visit(node)
		return node

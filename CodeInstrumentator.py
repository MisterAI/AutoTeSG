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
		new_node = []
		for i_node in node.values:
			new_node.append(Expr(value=i_node, ctx=Load()))
			fix_missing_locations(new_node[-1])
		return new_node

	def visit_Expr(self, node):
		self.generic_visit(node)
		if hasattr(node.value, 'func'):
			if hasattr(node.value.func, 'id'):
				if node.value.func.id == 'print':
					new_node = []
					for i_node in node.value.args:
 						new_node.append(Expr(value=i_node, ctx=Load()))
 						fix_missing_locations(new_node[-1])
					return new_node
		return node

class CodeInstrumentator(NodeTransformer):
	def get_print_stmt(self, lineno):
		return parse('print(' + str(lineno) + ')').body[0]

	def insert_print(self, node):
		node.body.insert(0, self.get_print_stmt(node.lineno))
		fix_missing_locations(node.body[0])
		if hasattr(node, 'orelse'):
			if node.orelse:
				node.orelse.insert(0, 
					self.get_print_stmt(node.orelse[0].lineno - 1))
				fix_missing_locations(node.orelse[0])

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

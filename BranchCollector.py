#!/usr/bin/python

import astor
import ast

def add_childs(node, branch_list, parents_list):
	"""
	Recursively adds the child_nodes
	"""
	for child_node in ast.iter_child_nodes(node):
		if check_instance(child_node):
			tmp_list = parents_list[:]
			if not child_node in node.body:
				# node is part of orelse list
				tmp_list[-1] = node.orelse[0].lineno - 1
			tmp_list.append(child_node.lineno)
			branch_list.append(tmp_list[:])

			if hasattr(child_node, 'orelse'):
				if child_node.orelse:
					else_list = tmp_list[:]
					else_list[-1] = child_node.orelse[0].lineno - 1
 					branch_list.append(else_list[:])
			add_childs(child_node, branch_list, tmp_list)

def check_instance(node):
	"""
	Checks, if the node is relevant for the control flow
	"""
	if (isinstance(node, ast.If)
		or isinstance(node, ast.For) 
		or isinstance(node, ast.While)):
		# or isinstance(node, ast.FunctionDef)):
		# relevant type
		return True
	else:
		return False

def collect_branches(ast_tree):
	"""
	Returns a list of all branches in the program
	Output is a list of lists, each list containing the parents 
	of the branch as well as the predicate itself.
	"""
	branch_list = []
	for node in ast.iter_child_nodes(ast_tree):
		if check_instance(node):
			branch_list.append([node.lineno])
			if hasattr(node, 'orelse'):
				if node.orelse:
 					branch_list.append([node.orelse[0].lineno - 1])
			add_childs(node, branch_list, [node.lineno])
	return branch_list

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
			tmp_list.append(child_node.__class__.__name__)
			# tmp_list.append(child_node)
			branch_list.append(tmp_list)
			add_childs(child_node, branch_list, tmp_list)


def check_instance(node):
	"""
	Checks, if the node is relevant for the control flow
	"""
	if (isinstance(node, ast.If)
		or isinstance(node, ast.For) 
		or isinstance(node, ast.While)
		or isinstance(node, ast.FunctionDef)
		or isinstance(node, ast.Call)):
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
			branch_list.append([node.__class__.__name__])
			add_childs(node, branch_list, [node.__class__.__name__])
			# branch_list.append([node])
			# add_childs(node, branch_list, [node])
	return branch_list

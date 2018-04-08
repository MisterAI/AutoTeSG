#!/usr/bin/python

import astor
import ast

def break_check(node):
	"""
	Returns integer, telling if there was a break found in the tree.
	It is encoded the following way:
	0: no break found
	1: break found only inside a child node of the top-level for-loop
	2: break found only inside the body of the top-level for-loop
	3: break found in a child node of the top-level for-loop as well as 
	   inside the body of the top-level for-loop
	"""
	break_loc = 0
	for child_node in ast.iter_child_nodes(node):
		if isinstance(child_node, ast.Break):
			if isinstance(node, ast.For):
				break_loc = break_loc | 2
			else:
				break_loc = break_loc | 1
		if not isinstance(child_node, ast.For):
			break_loc = break_loc | break_check(child_node)
	return break_loc

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
				if len(child_node.orelse) > 1:
					# there is a non-empty else clause ,containing more than 
					# our print statement for coverage and distance calculation
					skip_else_branch = False
					if isinstance(child_node, ast.For):
						# check for existence of breaks in for-loop 
						break_loc = break_check(child_node)
						print('BranchCollector, break_loc', break_loc, 'child_node', astor.dump_tree(child_node))
						if not break_loc == 1:
							# break found not only inside a child node of the 
							# top-level for-loop
							skip_else_branch = True

					if not skip_else_branch:
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
	add_childs(ast_tree, branch_list, [])
	return branch_list

#!/usr/bin/python

import ast
import sys
from CodeRunner import runCode
from CustomExceptions import *

class DistanceCalculator():
	def normalise_branch_distance(self, branch_distance):
		try:
			return 1 - pow(1.001, -branch_distance)
		except OverflowError as e:
			print(branch_distance)
			raise e

	def calc_branch_distance(self, goal_branch, covered_branches, code_output):
		# find first unpenetrated lvl
		first_unpenetrated = 0
		for line in goal_branch:
			if not line in covered_branches:
				first_unpenetrated = line
				break
		# print('first_unpenetrated', first_unpenetrated)
		# print('code_output', code_output)
		# return minimal distance for corresponding line to first unpenetrated line
		return min([distance for lineno, distance in code_output if lineno == -first_unpenetrated])

	def calc_approach_lvl(self, goal_branch, covered_branch):
		# count lines in goal_branches not covered by covered_branch
		return len([line for line in goal_branch if not line in covered_branch])

	def calc_distance(self, code_tree, goal_branch):
		# run the function body
		code_output = runCode(code_tree).split('\n')
		# remove empty lines
		code_output = [num for num in code_output if num != '']
		# map from string to tuples
		if not sys.version_info[0] >= 3:
			code_output = map(eval, code_output)
		else:
			code_output = [list(map(float, line.split(' '))) for line in code_output]
		
		# get the covered branches and their respective branch distance	
		try:
			covered_branches = [line[0] for line in code_output]
		except SyntaxError as e:
			print(code_output)
			raise e
		branch_distances = [line[1] for line in code_output]

		# print('covered_branches', covered_branches)

		for branch_lineno in goal_branch:
			if not branch_lineno in covered_branches:
				break
		else:
			# print('Terminated: goal_branch is ' 
			# 	+ str(goal_branch) 
			# 	+ ', covered_branches are ' 
			# 	+ str(covered_branches))
			# the branch is fully covered
			raise TerminationException("Terminated!", None)

		approach_lvl = self.calc_approach_lvl(goal_branch, covered_branches)
		branch_distance = self.calc_branch_distance(goal_branch, covered_branches, code_output)
		branch_distance = self.normalise_branch_distance(branch_distance)

		return approach_lvl + branch_distance

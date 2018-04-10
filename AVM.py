#!/usr/bin/python

from ast import *
import astor
import copy
import random
from DistanceCalculator import DistanceCalculator
from CustomExceptions import *

class AVM:
	def prepare_func_node(self, full_tree, func_name):
		# copy AST to modify it
		new_node = copy.deepcopy(full_tree)

		# apend function call to body
		new_node.body.append(Call(
			func=Name(id=func_name, ctx=Load()), 
			args=[], 
			keywords=[], 
			starargs=None, 
			kwargs=None))
		for var in self.input_assignmnt:
			new_node.body[-1].args.append(Num(n=var))
		copy_location(new_node.body[-1], full_tree.body[-1])
		increment_lineno(new_node.body[-1])

		return new_node

	def initialise_input_vars(self, rand=False):
		if not rand:
			# look for best input variables-assignment so far
			for lineno in self.branch:
				if lineno in [in_line for in_line, in_vars in self.input_tuples]:
					self.input_assignmnt = [in_vars for in_line, in_vars 
						in self.input_tuples][0][:]
			
		if rand or not self.input_assignmnt:
			self.input_assignmnt = [random.randint(0, 10) for i in 
				range(0, self.num_in_vars)]

	def exploratory_move(self, full_tree, func_name, var_i):
		"""
		Determines the distance if increasing and decreasing the variable var_i
		and returns the direction which led to a better distance value as well 
		as the distance value itself.
		direction =  1: increase
		direction = -1: decrease
		"""
		self.input_assignmnt[var_i] = self.input_assignmnt[var_i] + 1
		test_node = self.prepare_func_node(full_tree, func_name)
		incr_distance = DistanceCalculator().calc_distance(test_node, self.branch)

		self.input_assignmnt[var_i] = self.input_assignmnt[var_i] - 2
		test_node = self.prepare_func_node(full_tree, func_name)
		decr_distance = DistanceCalculator().calc_distance(test_node, self.branch)

		return ((1, incr_distance) if incr_distance < decr_distance 
			else (-1, decr_distance))

	def pattern_move(self, full_tree, func_name, var_i, direction, distance):
		"""
		Increases the value of variable var_i with doubling step size until 
		there's no more increase in distance.
		"""
		step_size = direction
		if 1 == direction:
			self.input_assignmnt[var_i] = self.input_assignmnt[var_i] + 2

		while True:
			step_size *= 2
			self.input_assignmnt[var_i] = self.input_assignmnt[var_i] + step_size
			# print('Pattern move: variable is '
			# 	+ str(var_i)
			# 	 + ', step_size is ' 
			# 	+ str(step_size) 
			# 	+ ', input is '
			# 	+ str(self.input_assignmnt))
			test_node = self.prepare_func_node(full_tree, func_name)
			new_distance = DistanceCalculator().calc_distance(test_node, self.branch)
			if new_distance < distance:
				# print('Pattern move: improved by ' + str(distance - new_distance))
				distance = new_distance
			else:
				self.input_assignmnt[var_i] = (self.input_assignmnt[var_i] 
					- step_size)
				return distance

	def get_branch_string(self, func_node, branch):
		"""
		If the lineno is negative, the line is inside an else-block. Return 
		lineno appended by F accordingly.
		"""
		if branch[-1] < 0:
			return str(-branch[-1]) + 'F: '
		else:
			return str(branch[-1]) + 'T: '

	def AVMsearch(self, full_tree, func_node, branch, input_tuples):
		# get the number of input variables
		self.num_in_vars = len(func_node.args.args)
		self.input_tuples = input_tuples
		self.branch = branch
		self.input_assignmnt = None

		self.initialise_input_vars()

		old_distance = 0
		non_improvements = 0
		restarts = 0

		try:
			while True:
				for var_i in range(0, self.num_in_vars):
					# print('Optimising distance for variable number '
						# + str(var_i))
					direction, distance = self.exploratory_move(full_tree, 
						func_node.name, var_i)
					# print('Finished exploration move with distance ' 
					# 	+ str(distance))
					new_distance = self.pattern_move(full_tree, func_node.name, 
						var_i, direction, distance)
					# print('Finished pattern move with distance ' 
					# 	+ str(new_distance))
					if not new_distance < old_distance:
						non_improvements += 1
					else:
						# print('Improvement is ' 
						# 	+ str(old_distance-new_distance))
						old_distance = new_distance
					if non_improvements > self.num_in_vars:
						if not restarts >= 3:
							# print('Restarting AVM search')
							restarts += 1
							self.initialise_input_vars(rand=True)
							break
						else:
							raise NoSolutionException('Tried to restart for \
								three times', None)

		except TerminationException:
			branch_string = self.get_branch_string(func_node, branch)
			print( branch_string + ', '.join(map(str, self.input_assignmnt)))
			# print('Got TerminationException!\n')
		except NoSolutionException as e:
			branch_string = self.get_branch_string(func_node, branch)
			print( branch_string + '-')
			# print('Didn\'t find any solution for branch ' + str(branch))

#!/usr/bin/python

from ast import *
import copy
import random
from DistanceCalculator import DistanceCalculator
from CustomExceptions import *

class AVM:
	def prepare_func_node(self, func_node):
		# copy function body to execute it
		new_node = Module(body=copy.deepcopy(func_node.body))
		
		# make parameters of function a variable
		for i in range(0, len(func_node.args.args)):
			try:
				# Python3
				new_node.body.insert(0, Assign(
					targets=[Name(
						id=func_node.args.args[i].arg, 
						ctx=Store())], 
					value=Num(n=self.input_assignmnt[i])))
			except Exception as e:
				# Python2
				new_node.body.insert(0, Assign(
					targets=[Name(
						id=func_node.args.args[i].id,
						ctx=Store())],
					value=Num(n=self.input_assignmnt[i])))
			fix_missing_locations(new_node.body[0])
		
		# replace return statements by exit()
		RemoveReturn().visit(new_node)
		fix_missing_locations(new_node)

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

	def exploratory_move(self, func_node, var_i):
		"""
		Determines the distance if increasing and decreasing the variable var_i
		and returns the direction which led to a better distance value as well 
		as the distance value itself.
		direction =  1: increase
		direction = -1: decrease
		"""
		self.input_assignmnt[var_i] = self.input_assignmnt[var_i] + 1
		test_node = self.prepare_func_node(func_node)
		incr_distance = DistanceCalculator().calc_distance(test_node, self.branch)

		self.input_assignmnt[var_i] = self.input_assignmnt[var_i] - 2
		test_node = self.prepare_func_node(func_node)
		decr_distance = DistanceCalculator().calc_distance(test_node, self.branch)

		return ((1, incr_distance) if incr_distance < decr_distance 
			else (-1, decr_distance))

	def pattern_move(self, func_node, var_i, direction, distance):
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
			test_node = self.prepare_func_node(func_node)
			new_distance = DistanceCalculator().calc_distance(test_node, self.branch)
			if new_distance < distance:
				# print('Pattern move: improved by ' + str(distance - new_distance))
				distance = new_distance
			else:
				self.input_assignmnt[var_i] = (self.input_assignmnt[var_i] 
					- step_size)
				return distance

	def AVMsearch(self, func_node, branch, input_tuples):
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
					# print('Optimising distance for variable number ' + str(var_i))
					direction, distance = self.exploratory_move(func_node, var_i)
					# print('Finished exploration move with distance ' + str(distance))
					new_distance = self.pattern_move(func_node, var_i, direction, distance)
					# print('Finished pattern move with distance ' + str(new_distance))
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
							raise NoSolutionException('Tried to restart for three times', None)

		except TerminationException:
			print(str(branch) + ': ' + str(self.input_assignmnt))
			# print('Got TerminationException!\n')
		except NoSolutionException as e:
			print(str(branch) + ': Search failed or branch unreachable')
			# print('Didn\'t find any solution for branch ' + str(branch))
			# TODO handle this better
			# raise e

class RemoveReturn(NodeTransformer):
	def visit_Return(self, node):
		return parse('exit()').body[0]

class NodePrinter(NodeVisitor):
	"""Debug"""
	def generic_visit(self, node):
		print(node)
		for child_node in iter_child_nodes(node):
			self.generic_visit(child_node)

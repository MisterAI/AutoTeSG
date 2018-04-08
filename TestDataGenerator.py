#!/usr/bin/python

from ast import *
import astor
import copy
import random
import BranchCollector
from CodeRunner import *
from FitnessCalculator import FitnessCalculator

class RemoveReturn(NodeTransformer):
	def visit_Return(self, node):
		return parse('exit()').body[0]

class NodePrinter(NodeVisitor):
	"""Debug"""
	def generic_visit(self, node):
		print(node)
		for child_node in iter_child_nodes(node):
			self.generic_visit(child_node)		

class TerminationException(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(TerminationException, self).__init__(message, errors)

class NoSolutionException(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(NoSolutionException, self).__init__(message, errors)

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
		Determines the fitness if increasing and decreasing the variable var_i
		and returns the direction which led to a better fitness value as well 
		as the fitness value itself.
		direction =  1: increase
		direction = -1: decrease
		"""
		self.input_assignmnt[var_i] = self.input_assignmnt[var_i] + 1
		test_node = self.prepare_func_node(func_node)
		incr_fitness = FitnessCalculator().calc_fitness(test_node, self.branch)

		self.input_assignmnt[var_i] = self.input_assignmnt[var_i] - 2
		test_node = self.prepare_func_node(func_node)
		decr_fitness = FitnessCalculator().calc_fitness(test_node, self.branch)

		return ((1, incr_fitness) if incr_fitness > decr_fitness 
			else (-1, decr_fitness))

	def pattern_move(self, func_node, var_i, direction, fitness):
		"""
		Increases the value of variable var_i with doubling step size until 
		there's no more increase in fitness.
		"""
		step_size = direction
		if 1 == direction:
			self.input_assignmnt[var_i] = self.input_assignmnt[var_i] + 2

		while True:
			step_size *= 2
			self.input_assignmnt[var_i] = self.input_assignmnt[var_i] + step_size
			test_node = self.prepare_func_node(func_node)
			new_fitness = FitnessCalculator().calc_fitness(test_node, self.branch)
			if new_fitness > fitness:
				fitness = new_fitness
			else:
				self.input_assignmnt[var_i] = (self.input_assignmnt[var_i] 
					- step_size)
				return fitness

	def AVMsearch(self, func_node, branch, input_tuples):
		# get the number of input variables
		self.num_in_vars = len(node.args.args)
		self.input_tuples = input_tuples
		self.branch = branch
		self.input_assignmnt = None

		self.initialise_input_vars()

		old_fitness = 0
		non_improvements = 0
		restarts = 0

		try:
			while True:
				for var_i in range(0, self.num_in_vars):
					direction, fitness = self.exploratory_move(func_node, var_i)
					new_fitness = pattern_move(func_node, var_i, direction, fitness)
					if not new_fitness > old_fitness:
						non_improvements += 1
					else:
						old_fitness = new_fitness
					if non_improvements > self.num_in_vars:
						if not restarts >= 3:
							restarts += 3
							self.initialise_input_vars(rand=True)
							break

		except TerminationException:
			pass
		except NoSolutionException:
			# handle this
			pass


class TestDataGenerator(NodeVisitor):
	def visit_FunctionDef(self, node):
		"""
		Visit all functions to generate test inputs.
		"""
		# get all possible branches of function
		branches = BranchCollector.collect_branches(node)
		input_assignmnt = [0 for i in range(0, len(node.args.args))]
		# save successful inputs for every branching line as 
		# Tupel:(lineno, input_list)
		input_tuples = []
		
		for branch in branches:
			AVM().AVMsearch(branch, input_tuples)

			# DEBUG
			break

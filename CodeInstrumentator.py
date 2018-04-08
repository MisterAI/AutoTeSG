#!/usr/bin/python

from ast import *
import astor

class RemovePrintStmts(NodeTransformer):
	"""
	Removes all print statements so they don't interfere 
	with the instrumentation
	"""
	def visit_Print(self, node):
		new_node = []
		for i_node in node.values:
			new_node.append(Expr(value=i_node, ctx=Load()))
			copy_location(new_node[-1], node)
		return new_node

	def visit_Expr(self, node):
		self.generic_visit(node)
		if hasattr(node.value, 'func'):
			if hasattr(node.value.func, 'id'):
				if node.value.func.id == 'print':
					new_node = []
					for i_node in node.value.args:
						new_node.append(Expr(value=i_node, ctx=Load()))
						copy_location(new_node[-1], node.value.func)
					return new_node
		return node

class CodeInstrumentator(NodeTransformer):
	comparison_thresh = 0.01

	def dist_Eq(self, left, right):
		# distance = abs(left-right)
		return Call(func=Name(id='abs', ctx=Load()),
					args=[BinOp(
						left=left,
						op=Sub(),
						right=right)],
					keywords=[],
					starargs=None,
					kwargs=None)
	
	def dist_NotEq(self, left, right):
		# distance = -abs(left-right)
		return UnaryOp(op=USub(),
					operand=Call(
						func=Name(id='abs', ctx=Load()),
						args=[BinOp(left=left, op=Sub(), right=right)],
						keywords=[],
						starargs=None,
						kwargs=None)
					)

	def dist_Lt(self, left, right):
		# distance = left-right + threshold
		return BinOp(
			left=BinOp(
				left=left, 
				op=Sub(), 
				right=right), 
			op=Add(), 
			right=Num(n=self.comparison_thresh))

	def dist_LtE(self, left, right):
		# use same as Lt
		return self.dist_Lt(left, right)

	def dist_Gt(self, left, right):
		# turn around args
		return self.dist_Lt(right, left)

	def dist_GtE(self, left, right):
		# turn around args
		return self.dist_LtE(right, left)

	def dist_Is(self, left, right):
		# distance cannot be quantified easily; return 1 for now 
		return Num(n=1)

	def dist_IsNot(self, left, right):
		# distance cannot be quantified easily; return 1 for now 
		return Num(n=1)

	def dist_In(self, left, right):
		# approximate distance by distance to nearest item in list
		print('Instru, dist_In', dump(right))
		return Call(
			func=Name(id='min', ctx=Load()),
			args=[
				ListComp(
					elt=Call(func=Name(id='abs', ctx=Load()),
						args=[BinOp(left=left, op=Sub(), right=Name(id='item', ctx=Load()))],
						keywords=[],
						starargs=None,
						kwargs=None),
					generators=[comprehension(target=Name(id='item', ctx=Store()), iter=right, ifs=[])])],
			keywords=[],
			starargs=None,
			kwargs=None)

	def dist_NotIn(self, left, right):
		# distance is 1 for integer
		# we only consider the case 'left not in right'
		return Num(n=1)

	def dist_functs(self, op):
		dist_functs = {
			'Eq': self.dist_Eq,
			'NotEq': self.dist_NotEq,
			'Lt': self.dist_Lt,
			'LtE': self.dist_LtE,
			'Gt': self.dist_Gt,
			'GtE': self.dist_GtE,
			'Is': self.dist_Is,
			'IsNot': self.dist_IsNot,
			'In': self.dist_In,
			'NotIn': self.dist_NotIn
		}
		return dist_functs[op]

	def calc_dist(self, node):
		if isinstance(node, If) or isinstance(node, While):
			if isinstance(node.test, Compare):
				distance = None
				for i in range(0, len(node.test.ops)):
					# sum up distances of all comparisons
					operation = astor.dump_tree(node.test.ops[0])
					if i == 0:
						distance = self.dist_functs(operation)(
							node.test.left, 
							node.test.comparators[0])
					else:
						distance = BinOp(
							left=distance,
							op=Add(),
							right=self.dist_functs(operation)(
								node.test.comparators[i-1], 
								node.test.comparators[i])
							)
				return distance
			else:
				# no compare node; return 1 for now
				# TODO consider simple integer variable
				return Num(n=1)
		else:
			if isinstance(node, For):
				# distance equivalent to 'if(a in b)'
				return self.dist_In(node.target, node.iter)

	def get_print_stmt(self, lineno, node, else_branch):
		if else_branch:
			# else-branches get the inverse line number of the parent
			print_node = parse('print('+ str(-lineno) + ',' + 'tmp' 
				+ ')').body[0]
			# invert distance for else branch
			try:
				# Python2
				print_node.values[0].elts[1] = UnaryOp(
					op=USub(), 
					operand=self.calc_dist(node))
			except AttributeError as e:
				# Python3
				print_node.value.args[1] = UnaryOp(
					op=USub(), 
					operand=self.calc_dist(node))
			
			return print_node
		else:
			print_node = parse('print(' + str(lineno) + ',' + 'tmp' + ')').body[0]
			try:
				# Python2
				print_node.values[0].elts[1] = self.calc_dist(node)
			except AttributeError as e:
				print_node.value.args[1] = self.calc_dist(node)
			
			return print_node

	def insert_print(self, node):
		node.body.insert(0, self.get_print_stmt(node.lineno, node, False))
		try:
			copy_location(node.body[0], node.body[1])
		except IndexError as e:
			fix_missing_locations(node)

		if hasattr(node, 'orelse'):
			node.orelse.insert(0, 
				self.get_print_stmt(node.lineno, node, True))
			try:
				copy_location(node.orelse[0], node.orelse[1])
			except IndexError as e:
				fix_missing_locations(node)
				
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

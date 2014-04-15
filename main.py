#!/usr/bin/env python

from __future__ import division

import sys
import copy
import json

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', 'pycparser'])

from collections import OrderedDict
from value import *

from pycparser import parse_file
from pycparser.c_ast import *
from pycparser.c_parser import CParser, Coord, ParseError
from pycparser.c_lexer import CLexer

class Interpreter(NodeVisitor):
	
	def __init__(self):
		self.vars = {}
		self.vars_stack = [[]]
		self.eval_stack = []
		self.depth = 0
		self.compound_depth = 0
		self.break_flag = False
		self.continue_flag = False
		self.return_flag = False
		
		self.records = OrderedDict()
	
	def push(self, v):
		self.eval_stack.append(v)
#		print "eval_stack pushed %s" % v
#		print "eval_stack len %d" % len(self.eval_stack)
		
	def pop(self):
		if not len(self.eval_stack):
			return None
#		print "eval_stack popped"
		return self.eval_stack.pop()
	
	def log(self, node, var, val):
		key = var
		coord = node.coord
		if not key in self.records:
			self.records[key] = {
				"min" : val,
				"max" : val,
				"min_coord" : coord,
				"max_coord" : coord
			}
		else:
			rec = self.records[key]
			if val < rec["min"]:
				rec["min"] = val
				rec["min_coord"] = coord
			elif val > rec["max"]:
				rec["max"] = val
				rec["max_coord"] = coord
	
	def eval(self, node):
		if not node:
			return None
		else:
			self.visit(node)
			
	def ope(self, lhs, op, rhs):
		print(lhs, op, rhs)
		
		if lhs is None:
			print("lhs None")
			sys.exit()
		
		if rhs is None:
			print("rhs None")
			sys.exit()
		
		ret = None
		if op == '+':		ret = lhs + rhs
		elif op == "-":		ret = lhs - rhs
		elif op == "*":		ret = lhs * rhs
		elif op == "/":		ret = lhs / rhs
		elif op == "%":		ret = lhs % rhs
		elif op == "^":		ret = lhs ^ rhs
		elif op == "|":		ret = lhs | rhs
		elif op == "&":		ret = lhs & rhs
		elif op == "==":	ret = lhs == rhs
		elif op == "!=":	ret = lhs != rhs
		elif op == "<<":	ret = lhs << rhs
		elif op == ">>":	ret = lhs >> rhs
		elif op == "&&":	ret = lhs and rhs
		elif op == "||":	ret = lhs or rhs
		elif op == "<":		ret = lhs < rhs
		elif op == "<=":	ret = lhs <= rhs
		elif op == ">":		ret = lhs > rhs
		elif op == ">=":	ret = lhs >= rhs
		else:
			print "op %s not supported" % op
		return ret
		
	def visit(self, node):
		if node is None:
			return
#		node.show()
		self.depth += 1
		ret = super(Interpreter, self).visit(node)
		self.depth -= 1
		if self.depth == self.compound_depth:
#			print("delete eval_stack")
			del self.eval_stack[:]
		return
	
	def visit_FuncDef(self, node):
		params = node.decl.type.args.params
		arg_values = []
		if len(self.eval_stack) < len(params):
			print("not enough arguments pushed on stack")
			sys.exit()
		for i in range(len(params)):
			arg_values.append(self.pop())
#		print("arg_values", arg_values)
		for param in params:
			self.visit(param)
			l = self.vars[param.name][-1]
			if l is None:
				print("None")
				sys.exit()
			r = arg_values.pop()
			rv = r.value if isinstance(r, Variable) else r
			l.value = rv
			
		self.visit(node.body)
		return
	
	def visit_Compound(self, node):
#		node.show()
		items = node.block_items
		if items is None:
			return
		self.compound_depth += 1
		self.vars_stack.append([])
		for item in items:
			self.visit(item)
			if self.break_flag or self.return_flag:
				break
			if self.continue_flag:
				if hasattr(node, 'parent_node_is_loop'):
					self.continue_flag = False
				break
		local_vars = self.vars_stack.pop()
		for name in local_vars:
			print("%s pop" % name)
			self.vars[name].pop()
		self.compound_depth -= 1
	
	def visit_Decl(self, node):
		node.show()
	
		type = node.type
		name = node.name #type.declname
#		typeName = type.type.names[0]
		self.eval(node.init)
		if name not in self.vars:
			self.vars[name] = []
		var = self.pop()
		var = var.value if isinstance(var, Variable) else var
		var = Variable(name, node.coord, var)
		if var.value is not None:
			self.log(node, var, var.value.value)
		print("%s push" % name)
		self.vars[name].append(var)
		self.vars_stack[-1].append(name)
		
	def visit_Constant(self, node):
#		node.show()
		v = Value(node.type, int(node.value))
		self.push(v)
	
	def visit_ID(self, node):
		name = node.name
		if name not in self.vars:
			print("at %s %s not found" % (node.coord, name))
			sys.exit()
		lst = self.vars[name]
		lstlen = len(lst)
		if lstlen == 0:
			print("var %s not found" % name)
			sys.exit()
		v = lst[-1]
		self.push(v)
	
	def visit_Cast(self, node):
		self.visit(node.expr)
		v = self.pop()
		# TODO: validate type
#		node.to_type.type.type.show()
		v.type = node.to_type.type.type.names[0]
		self.push(v)
		
	def visit_Assignment(self, node):
#		node.show()
		self.visit(node.lvalue)
		self.visit(node.rvalue)

		r = self.pop()
		l = self.pop()
		print("assign", l, node.op, r)
		rv = r.value if isinstance(r, Variable) else r
		if node.op != "=":
			lv = l.value if isinstance(l, Variable) else l
			op = node.op[:-1] # remove tail =
			rv = self.ope(lv, op, rv)
		l.value = rv
		self.log(node, l, rv.value)
	
	def visit_UnaryOp(self, node):
		self.visit(node.expr)
		var = self.pop()
		
		if isinstance(var, Variable):
			if var.value is None:
				print("%s is not initialized" % var.name)
				sys.exit()
			value = var.value
		else:
			value = var
		op = node.op
		
		post = op[0] == "p"
		op = op[-2:]
		nv = None
		if op == "++":
			value.increment()
			self.log(node, var, value.value)
		elif op == "--":
			value.decrement()
			self.log(node, var, value.value)
		elif op == "+":		nv = +vv
		elif op == "-":		nv = -vv
		elif op == "&":		nv = v.addressof()
		elif op == "*":		nv = v.indirection()
		elif op == "~":		nv = ~v
		elif op == "!":		nv = not v
		else:
			a = 0
		self.push(nv)
			
	def visit_BinaryOp(self, node):
		self.visit(node.left)
		self.visit(node.right)
		r = self.pop()
		l = self.pop()
		lv = l.value if isinstance(l, Variable) else l
		rv = r.value if isinstance(r, Variable) else r
		result = self.ope(lv, node.op, rv)
		self.push(result)
	
	def visit_TernaryOp(self, node):
#		node.show()
		self.visit(node.cond)
		cond = self.pop()
		if cond.value:
			self.visit(node.iftrue)
		else:
			self.visit(node.iffalse)
	
	def visit_Union(self, node):
		# TODO: 
		return
	
	def visit_ArrayDecl(self, node):
		# TODO: 
		return
	
	def visit_PtrDecl(self, node):
		# TODO: 
		return
	
	def visit_Struct(self, node):
		# TODO: 
		return
	
	def visit_If(self, node):
		self.visit(node.cond)
		cond = self.pop()
		if cond.value:
			self.visit(node.iftrue)
		else:
			self.visit(node.iffalse)
	
	def visit_Switch(self, node):
#		node.show()
		self.visit(node.cond)
		cond = self.pop()
		cond = cond.value if isinstance(cond, Variable) else cond
		matched = False
		default = None
		for item in node.stmt.block_items:
			if isinstance(item, Default):
				default = item
				continue
			elif isinstance(item, Case):
				self.visit(item.expr)
				expr = self.pop()
				if not matched and  not (cond == expr).value:
					continue
				matched = True
				for stmt in item.stmts:
					self.visit(stmt)
					if self.break_flag:
						break
				if self.break_flag:
					self.break_flag = False
					break
				elif self.return_flag:
					break
			else:
				print("illegal block item in switch")
				sys.exit()
		if matched or default is None:
			return
		for item in default.stmts:
			self.visit(item)
			if self.break_flag:
				self.break_flag = False
				break
			elif self.return_flag:
				break

	def visit_Break(self, node):
#		node.show()
		self.break_flag = True
	
	def visit_Continue(self, node):
#		node.show()
		self.continue_flag = True
	
	def visit_For(self, node):
		self.visit(node.init)
		node.stmt.parent_node_is_loop = True
		while True:
			self.visit(node.cond)
			cond = self.pop()
			if not cond.value:
				break
#			node.stmt.show()
			self.visit(node.stmt)
			if self.break_flag:
				self.break_flag = False
				break
			elif self.return_flag:
				break
			self.visit(node.next)
	
	def visit_While(self, node):
		node.stmt.parent_node_is_loop = True
		while True:
			self.visit(node.cond)
			cond = self.pop()
			if not cond.value:
				break
			self.visit(node.stmt)
			if self.break_flag:
				self.break_flag = False
				break
			elif self.return_flag:
				break
	
	def visit_DoWhile(self, node):
		node.stmt.parent_node_is_loop = True
		while True:
			self.visit(node.stmt)
			if self.break_flag:
				self.break_flag = False
				break
			elif self.return_flag:
				break
			self.visit(node.cond)
			cond = self.pop()
			if not cond.value:
				break
	
	def visit_Return(self, node):
		self.return_flag = True
		return
	
	def visit_Goto(self, node):
		# TODO: 
		return
	
	def visit_Label(self, node):
		# TODO: 
		return
	
	def visit_FuncCall(self, node):
		node.show()
		self.visit(node.name)
		func = self.pop()
		self.visit(node.args)
		self.visit(func)
	
	def callFunction(self, name, args):
		if not name in self.vars:
			return False
		for arg in args:
			self.push(Value("int", int(arg)));
		self.visit(self.vars[name][0])
	

class RootVisitor(NodeVisitor):
	def __init__(self):
		self.v = Interpreter()
	
	def visit_Decl(self, node):
		self.v.visit(node);
		return
	
	def visit_Typedef(self, node):
		# TODO: register typedef
		return
#		node.show()
	
	def visit_Struct(self, node):
		return
#		node.show()
	
	def visit_FuncDef(self, node):
#		print('%s at %s' % (node.decl.name, node.decl.coord))
#		print node.show()
		self.v.vars[node.decl.name] = [node]
	
	def callFunction(self, name, args):
		return self.v.callFunction(name, args)
		
	def setVariable(self, name, value):
		self.v.vars[name][0].value = Value("int", value)

def run(ast, setting):
	entry = setting["function"]
	args = setting["args"]
	vars = setting["vars"]
	var_names = vars.keys()
	var_ranges = vars.values()
	nvars = len(var_names)

	counters = []
	for r in var_ranges:
		counters.append(r[0])

	while True:
		
		# setup root
		v = RootVisitor()
		v.visit(ast)
		
		# set variables
		for i in range(nvars):
			v.setVariable(var_names[i], counters[i])
		
		# call function
		if v.callFunction(entry, args) == False:
			print("func %s not found" % entry)
		else:
			# print variables
			print ""
			for key, value in v.v.records.items():
				print key.name, value["min"], value["max"]
		
		# update counter
		counters[0] += 1
		for i in range(nvars):
			if counters[i] > var_ranges[i][1]: # if exceeds max
				if i+1 >= nvars:
					return
				counters[i] = var_ranges[i][0] # init to min
				counters[i+1] += 1 # increment upper-level counter
			else:
				break
	

if len(sys.argv) < 2:
	print("specify setting file")
	sys.exit()

f = open(sys.argv[1])
setting = json.load(f)
f.close()

ast = parse_file(
    setting["file"],
    use_cpp=True,
    cpp_path=r'./pycparser/utils/cpp.exe',
    cpp_args=r'-I./pycparser/utils/fake_libc_include'
    )
#ast.show()

run(ast, setting)


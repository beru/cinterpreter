#!/usr/bin/env python

from __future__ import division

import sys
from value import *

from pycparser import parse_file
from pycparser.c_ast import *
from pycparser.c_parser import CParser, Coord, ParseError
from pycparser.c_lexer import CLexer

class Verifier(NodeVisitor):
	
	def __init__(self):
		self.vars = {}
		self.vars_stack = []
		self.eval_stack = []
		self.depth = 0
		self.compound_depth = 0
		self.break_flag = False
		self.continue_flag = False
		self.return_flag = False
	
	def push(self, v):
		self.eval_stack.append(v)
#		print "eval_stack pushed %s" % v
#		print "eval_stack len %d" % len(self.eval_stack)
		
	def pop(self):
		if not len(self.eval_stack):
			return None
#		print "eval_stack popped"
		return self.eval_stack.pop()
		
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
		
		if op == '+':			return lhs + rhs
		elif op == "-":			return lhs - rhs
		elif op == "*":			return lhs * rhs
		elif op == "/":			return lhs / rhs
		elif op == "%":			return lhs % rhs
		elif op == "^":			return lhs ^ rhs
		elif op == "|":			return lhs | rhs
		elif op == "&":			return lhs & rhs
		elif op == "==":		return lhs == rhs
		elif op == "!=":		return lhs != rhs
		elif op == "<<":		return lhs << rhs
		elif op == ">>":		return lhs >> rhs
		elif op == "&&":		return lhs and rhs
		elif op == "||":		return lhs or rhs
		elif op == "<":			return lhs < rhs
		elif op == "<=":		return lhs <= rhs
		elif op == ">":			return lhs > rhs
		elif op == ">=":		return lhs >= rhs
		else:
			print "op %s not supported" % op
	
	def visit(self, node):
		if node is None:
			return
#		node.show()
		self.depth += 1
		ret = super(Verifier, self).visit(node)
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
		name = type.declname
		typeName = type.type.names[0]
		self.eval(node.init)
		if name not in self.vars:
			self.vars[name] = []
		var = self.pop()
		var = var.value if isinstance(var, Variable) else var
		var = Variable(name, var)
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
		if node.op == "=":
			l.value = rv
		else:
			lv = l.value if isinstance(l, Variable) else l
			op = node.op[:-1]
			result = self.ope(lv, op, rv) # remove tail =
			l.value = result
	
	def visit_UnaryOp(self, node):
		self.visit(node.expr)
		v = self.pop()
		
		if isinstance(v, Variable):
			if v.value is None:
				print("%s is not initialized" % v.name)
				sys.exit()
			vv = v.value
		else:
			vv = v
		op = node.op
		
		print(op, vv)
		
		post = op[0] == "p"
		op = op[-2:]
		if op == "++":		self.push(vv.increment())
		elif op == "--":	self.push(vv.decrement())
		elif op == "+":		self.push(+vv)
		elif op == "-":		self.push(-vv)
		elif op == "&":		self.push(v.addressof())
		elif op == "*":		self.push(v.indirection())
		elif op == "~":		self.push(~v)
		elif op == "!":		self.push(not v)
		else:
			a = 0
			
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
	

class RootVisitor(NodeVisitor):
	def __init__(self):
		self.v = Verifier()
		self.v.vars_stack.append([])
	
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

if len(sys.argv) < 2:
	print("specify c file")
	sys.exit()
	
ast = parse_file(sys.argv[1], use_cpp=True, cpp_args=r'-I../pycparser-master/utils/fake_libc_include')
#ast.show()

v = RootVisitor()
v.visit(ast)

if len(sys.argv) >= 3:
	entry = sys.argv[2]
else:
	entry = "main"
	
if not entry in v.v.vars:
	print("entry func %s not found" % entry)
	sys.exit()
v.v.push(Value("int", 99));
v.v.push(Value("int", 50));
v.v.visit(v.v.vars[entry][0])


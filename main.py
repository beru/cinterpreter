#!/usr/bin/env python

from __future__ import division
import sys
from pycparser import parse_file
from pycparser.c_ast import *
from pycparser.c_parser import CParser, Coord, ParseError
from pycparser.c_lexer import CLexer

parser = CParser()

class Variable:
	def __init__(self, name, value = None):
		self.name = name
		self.value = value
	def __repr__(self):
		return "%s %s" % (self.name, self.value)

class Value:
	def __init__(self, type, value = None):
		self.type = type
		self.value = value
	
	def __repr__(self):
		return "%s %s" % (self.type, self.value)
	
	def __pos__(self):
		ret = Value(self.type, self.value)
		return ret
	
	def __neg__(self):
		ret = Value(self.type, -self.value)
		return ret
		
	def __not__(self):
		ret = Value(self.type, not self.value)
		return ret
		
	# interval arithmetic
	def __add__(self, rhs):
		ret = Value(self.type, self.value + rhs.value)
		return ret
	
	def __sub__(self, rhs):
		ret = Value(self.type, self.value - rhs.value)
		return ret
	
	def __mul__(self, rhs):
		ret = Value(self.type, self.value * rhs.value)
		return ret
	
	def __truediv__(self, rhs):
		ret = Value(self.type, int(self.value / rhs.value))
		return ret
	
	def __mod__(self, rhs):
		ret = Value(self.type, self.value % rhs.value)
		return ret
	
	def __eq__(self, rhs):
		ret = Value(self.type, self.value == rhs.value)
		return ret
	
	def __ne__(self, rhs):
		ret = Value(self.type, self.value != rhs.value)
		return ret
	
	def __lshift__(self, rhs):
		ret = Value(self.type, self.value << rhs.value)
		return ret
	
	def __rshift__(self, rhs):
		ret = Value(self.type, self.value >> rhs.value)
		return ret
		
	def truth(self):
		ret = Value(self.type, self.value != 0)
		return ret
	
	def increment(self):
		self.value += 1
		return self
	
	def decrement(self):
		self.value -= 1
		return self
		
	def addressof(self):
		return
		
	def indirection(self):
		return
	
class Verifier(NodeVisitor):
	
	def __init__(self):
		self.vars = {}
		self.stack = []
		self.depth = 0
		self.compound_depth = 0
	
	def push(self, v):
		self.stack.append(v)
#		print "stack len %d\n" % len(self.stack)
		
	def pop(self):
		if not len(self.stack):
			return None
		return self.stack.pop()
		
	def eval(self, node):
		if not node:
			return None
		else:
			self.visit(node)
			
	def ope(self, lhs, op, rhs):
		print(lhs, op, rhs)
		
		if lhs is None:
			print("lhs None\n")
			sys.exit()
		
		if rhs is None:
			print("rhs None\n")
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
			print "op %s not supported\n" % op
	
	def visit(self, node):
		self.depth += 1
		ret = super(Verifier, self).visit(node)
		self.depth -= 1
		
		if self.depth == self.compound_depth:
#			print("delete stack\n")
			del self.stack[:]

		return ret
	
	def visit_Compound(self, node):
		self.compound_depth += 1
		ret = self.generic_visit(node)
		self.compound_depth -= 1
	
	def visit_Decl(self, node):
		type = node.type
		name = type.declname
		typeName = type.type.names[0]
		self.eval(node.init)
#		print(name)
		self.vars[name] = Variable(name, self.pop())
		
	def visit_Constant(self, node):
#		node.show()
		v = Value(node.type, int(node.value))
		self.push(v)
	
	def visit_ID(self, node):
		name = node.name
		if not name in self.vars:
			print("at %s %s not found\n" % (node.coord, name))
			sys.exit()
		else:
			self.push(self.vars[name])
	
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
		print(l, node.op, r)

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
		vv = v.value if isinstance(v, Variable) else v
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
		# TODO: 
		return
	
	def visit_Switch(self, node):
		# TODO: 
		return
	
	def visit_For(self, node):
		# TODO: 
		return
	
	def visit_While(self, node):
		# TODO: 
		return
	
	def visit_DoWhile(self, node):
		# TODO: 
		return
	
	def visit_Return(self, node):
		# TODO: 
		return
	
	def visit_Goto(self, node):
		# TODO: 
		return
	
	def visit_Label(self, node):
		# TODO: 
		return
	
	def visit_FuncCall(self, node):
		# TODO: 
		return
	
	
class FuncDefVisitor(NodeVisitor):
    def visit_FuncDef(self, node):
#        print('%s at %s' % (node.decl.name, node.decl.coord))
#        node.show()
        v = Verifier()
        v.visit(node.body)

ast = parse_file('sample.c', use_cpp=True,
	cpp_args=r'-I../pycparser-master/utils/fake_libc_include')
#ast.show()

v = FuncDefVisitor()
v.visit(ast)


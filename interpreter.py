from __future__ import division

import sys
import copy
from ctypes import *
from collections import OrderedDict

from dump import *
from variable import *

# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', 'pycparser'])

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
		
		self.structs = {}
		self.unnamed_struct_counter = 0
		
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
				"min" : val.value,
				"max" : val.value,
				"min_coord" : coord,
				"max_coord" : coord
			}
		else:
			rec = self.records[key]
			if val.value < rec["min"]:
				rec["min"] = val.value
				rec["min_coord"] = coord
			elif val.value > rec["max"]:
				rec["max"] = val.value
				rec["max_coord"] = coord
	
	def eval(self, node):
		if not node:
			return None
		else:
			self.visit(node)
			
	def ope(self, lhs, op, rhs):
#		print(lhs, op, rhs)
		
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
			
#		print ret
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
#		node.show()
		if node.decl.type.args != None:
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
				l.assign(r)
		
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
			self.vars[name].pop()
		self.compound_depth -= 1
	
	def visit_Decl(self, node):
#		node.show()
#		var_dump(node)
		name = node.name
		
		if type(node.type) == FuncDecl:
			return
		
		ctype = self.decl_to_ctype_type(node.type)
		if name == None:
			return
		if name not in self.vars:
			self.vars[name] = []
		var = Variable(name, node.coord, ctype, None)
		if node.init != None:
			self.eval(node.init)
			init_value = self.pop()
			var.assign(init_value)
			self.log(node, var, var.value)
#		print("%s push" % name)
		self.vars[name].append(var)
		self.vars_stack[-1].append(name)
		
	def visit_Constant(self, node):
#		node.show()
		# TODO: support many types of literals
		v = Variable(None, None, c_int, c_int(int(node.value)))
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

		if node.op == "=":
			l.assign(r)
		else:
			op = node.op[:-1] # remove tail =
			l.assign(self.ope(l, op, r))
		self.log(node, l, r.value)
	
	def visit_UnaryOp(self, node):
		self.visit(node.expr)
		var = self.pop()
		if var.value is None:
			print("%s is not initialized" % var.name)
			sys.exit()
		op = node.op
		
		post = op[0] == "p"
		op = op[-2:]
		nv = None
		if op == "++":
			var.increment()
			self.log(node, var, var.value)
		elif op == "--":
			var.decrement()
			self.log(node, var, var.value)
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
		result = self.ope(l, node.op, r)
		self.push(result)
	
	def visit_TernaryOp(self, node):
#		node.show()
		self.visit(node.cond)
		cond = self.pop()
		if cond:
			self.visit(node.iftrue)
		else:
			self.visit(node.iffalse)
	
	def visit_Union(self, node):
		# TODO: 
#		var_dump(node)
		return
	
	def decl_to_ctype_type(self, decl):
		t = type(decl)
		if t == Struct:
			tag_name = decl.name
			if tag_name is None:
				tag_name = "<unnamed%d>" % self.unnamed_struct_counter
				self.unnamed_struct_counter += 1
			
			if tag_name not in self.structs:
				self.structs[tag_name] = type(tag_name, (Structure,), {})
			st = self.structs[tag_name]
			if decl.decls is not None:
				st._fields_ = []
				for decl in decl.decls:
					st._fields_.append((decl.name, self.decl_to_ctype_type(decl.type)))
			return st
		elif t == ArrayDecl:
			return self.decl_to_ctype_type(decl.type) * int(decl.dim.value)
		elif t == PtrDecl:
			return POINTER(self.decl_to_ctype_type(decl.type))
		elif t == TypeDecl:
			decl_type = type(decl.type)
			if decl_type == IdentifierType:
				names = decl.type.names
				unsigned = "unsigned" in names
				for name in names:
					if 0:
						pass
					elif name == "char":
						return c_ubyte if unsigned else c_char
					elif name == "wchar_t":
						return c_wchar
					elif name == "short":
						return c_ushort if unsigned else c_short
					elif name == "int":
						return c_uint if unsigned else c_int
					elif name == "long":
						cnt = names.count("long")
						if cnt == 1:
							return c_ulong if unsigned else c_long
						elif cnt == 2:
							return c_ulonglong if unsigned else c_longlong
						else:
							print "invalid long count %s" % ','.join(names)
							sys.exit()
					elif name == "_Bool":
						return c_bool
					elif name == "float":
						return c_float
					elif name == "double":
						return c_double
					else:
						pass
			else:
				return self.decl_to_ctype_type(decl.type)
			return c_int
		else:
			print "other type ", t
			sys.exit()
	
	def visit_Struct(self, node):
		
#		sys.exit()
		return
	
	def visit_Typedef(self, node):
		# TODO: 
#		var_dump(node)
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
		matched = False
		default = None
		for item in node.stmt.block_items:
			if isinstance(item, Default):
				default = item
				continue
			elif isinstance(item, Case):
				self.visit(item.expr)
				expr = self.pop()
				if not matched and not cond.equals(expr).value:
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
#		node.show()
		self.visit(node.name)
		func = self.pop()
		
#		node.args.show()
		
		self.visit(node.args)
		self.visit(func)
	
	def callFunction(self, name, args):
		self.records.clear()
		if not name in self.vars:
			return False
		for arg in args:
			v = Variable(None, None, c_int, c_int(int(arg)))
			self.push(v);
		self.visit(self.vars[name][0])

class RootVisitor(NodeVisitor):
	def __init__(self):
		self.v = Interpreter()
	
	def visit_Decl(self, node):
		self.v.visit(node);
		return
	
	def visit_Typedef(self, node):
		self.v.visit(node);
		return
	
	def visit_FuncDef(self, node):
#		print('%s at %s' % (node.decl.name, node.decl.coord))
#		print node.show()
		self.v.vars[node.decl.name] = [node]
	
	def callFunction(self, name, args):
		self.v.callFunction(name, args)
		
	def setVariable(self, name, value):
		self.v.vars[name][0].assign(Variable(None, None, c_int, c_int(value)))


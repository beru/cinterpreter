
import sys
import operator
from ctypes import *

class Variable:
	def __init__(self, name, coord, type, value):
		self.name = name
		self.coord = coord
		self.type = type
		if value is None:
			self.value = type()
		else:
			self.value = value
	
	def make(self, typeV, value):
		nv = typeV()
		nv.value = value.value
		return Variable(None, None, typeV, nv)
	
	def makeValue(self, typeV, value):
		nv = typeV()
		nv.value = value.value
		return nv
	
	def promote(self, lhs, rhs):
		if lhs.type == c_ulonglong or rhs.type == c_ulonglong:
			return (self.makeValue(c_ulonglong, lhs.value), self.makeValue(c_ulonglong, rhs.value))
		elif lhs.type == c_longlong or rhs.type == c_longlong:
			return (self.makeValue(c_longlong, lhs.value), self.makeValue(c_longlong, rhs.value))
		elif lhs.type == c_ulong or rhs.type == c_ulong:
			return (self.makeValue(c_ulong, lhs.value), self.makeValue(c_ulong, rhs.value))
		elif lhs.type == c_long or rhs.type == c_long:
			return (self.makeValue(c_long, lhs.value), self.makeValue(c_long, rhs.value))
		elif lhs.type == c_uint or rhs.type == c_uint:
			return (self.makeValue(c_uint, lhs.value), self.makeValue(c_uint, rhs.value))
		else:
			return (self.makeValue(c_int, lhs.value), self.makeValue(c_int, rhs.value))
	
	def operate(self, lhs, rhs, operator):
		operands = self.promote(lhs, rhs)
		new_lhs = operands[0]
		new_rhs = operands[1]
		new_lhs.value = operator(new_lhs.value, new_rhs.value)
		return new_lhs
	
	def __repr__(self):
		return "name:%s type:%s value:%s" % (self.name, self.type, self.value)
		
	def __hash__(self):
		return self.coord.__hash__()
		
	def __eq__(self, rhs):
		return self.coord.__eq__(other)
	
	def assign(self, rhs):
		self.value.value = rhs.value.value
	
	def __pos__(self):
		return self.make(self.type, self.value)
	
	def __neg__(self):
		return self.make(self.type, -self.value)
		
	def __not__(self):
		return self.make(self.type, not self.value)
		
	def __add__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.add))
	
	def __sub__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.sub))
	
	def __mul__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.mul))
	
	def __truediv__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.div))
	
	def __mod__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.mod))
	
	def equals(self, rhs):
#	def __eq__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.eq))
	
	def __ne__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.ne))
	
	def __lshift__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.lshift))
	
	def __rshift__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.rshift))
		
	def truth(self):
		return self.make(self.type, self.value != 0)
	
	def __lt__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.lt))
	
	def __le__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.le))
	
	def __ge__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.ge))
	
	def __gt__(self, rhs):
		return self.make(self.type, self.operate(self, rhs, operator.gt))
	
	def increment(self):
		self.value.value += 1
		return self
	
	def decrement(self):
		self.value.value -= 1
		return self
		
	def addressof(self):
		return
		
	def indirection(self):
		return

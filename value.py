
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
	
	def __lt__(self, rhs):
		ret = Value(self.type, self.value < rhs.value)
		return ret
	
	def __le__(self, rhs):
		ret = Value(self.type, self.value <= rhs.value)
		return ret
	
	def __ge__(self, rhs):
		ret = Value(self.type, self.value >= rhs.value)
		return ret
	
	def __gt__(self, rhs):
		ret = Value(self.type, self.value > rhs.value)
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
		
	

class Variable:
	def __init__(self, name, value = None):
		self.name = name
		self.value = value
	def __repr__(self):
		return "%s %s" % (self.name, self.value)


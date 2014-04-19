
from interpreter import *

class CInterpreterRunner(object):
	
	def Load(self, filepath, cpp_path=r'./pycparser/utils/cpp.exe', cpp_args=r'-I./pycparser/utils/fake_libc_include'):
		self.ast = parse_file(
			filepath,
			use_cpp=True,
			cpp_path=cpp_path,
			cpp_args=cpp_args
			)
		
		# setup root
		self.rootVisitor = RootVisitor()
		self.rootVisitor.visit(self.ast)

	def SetVariable(self, name, value):
		self.rootVisitor.setVariable(name, value)
	
	def GetVariables(self):
		return self.rootVisitor.v.vars

	def CallFunction(self, name, args):
		self.rootVisitor.callFunction(name, args)
		return self.rootVisitor.v.records

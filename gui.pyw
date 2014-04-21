#!/usr/bin/env python

import os
import sys
import wx
import wx.lib.anchors as anchors

from runner import *
from dump import *

class AppForm(wx.Frame):
	def __init__(self, parent, id):
		wx.Frame.__init__(self, parent, id, "CInterpreter", style = wx.DEFAULT_FRAME_STYLE | wx.CLIP_CHILDREN)
		self.SetSize((450, 600))
		panel = wx.Panel(self, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE)
		panel.SetAutoLayout(True)

		# filename
		wx.StaticText(panel, -1, "filename:", (15,15))
		self.fileText = wx.TextCtrl(panel, -1, "", (80, 15), (300, -1))

		self.Bind(wx.EVT_TEXT, self.onFileText, self.fileText)
		self.fileSelectButton = wx.Button(panel, -1, "...", (390, 15), (30, 30))
		self.Bind(wx.EVT_BUTTON, self.onFileSelectButton, self.fileSelectButton)

		# cpp path
		wx.StaticText(panel, -1, "cpp path:", (15, 50))
		self.cppPathText = wx.TextCtrl(panel, -1, "", (80, 50), (300, -1))
		self.cppPathSelectButton = wx.Button(panel, -1, "...", (390, 50), (30, 30))
		self.Bind(wx.EVT_BUTTON, self.onCppPathSelectButton, self.cppPathSelectButton);

		# cpp args
		wx.StaticText(panel, -1, "cpp args:", (15, 85))
		self.cppArgsText = wx.TextCtrl(panel, -1, "", (80, 85), (300, -1))

		self.Bind(wx.EVT_BUTTON, self.onParseButton , wx.Button(panel, -1, "parse", (80, 120)))

		self.controlPanel = wx.Panel(panel, -1, (0, 155), (450, 450))

		# function
		wx.StaticText(self.controlPanel, -1, "functions:", (15, 15))
		self.functionChoice = wx.Choice(self.controlPanel, -1, (80, 15), (300, -1))
		self.Bind(wx.EVT_CHOICE, self.onFunctionChoice, self.functionChoice)

		# variable
		wx.StaticText(self.controlPanel, -1, "variables:", (15, 50))
		self.variableChoice = wx.Choice(self.controlPanel, -1, (80, 50), (300, -1))
		self.Bind(wx.EVT_CHOICE, self.onVariableChoice, self.variableChoice)
		
		# range
		self.rangeText = wx.TextCtrl(self.controlPanel, -1, "", (15, 85), (200, -1))
		self.Bind(wx.EVT_TEXT, self.onRangeText, self.rangeText)

		self.rangeSetButton = wx.Button(self.controlPanel, -1, "Set", (230, 85))
		self.Bind(wx.EVT_BUTTON, self.onRangeSetButton, self.rangeSetButton)
		
		self.rangeSlider = wx.Slider(self.controlPanel, 100, 25, 1, 100, (15, 120), (400, -1), wx.SL_HORIZONTAL)
		self.rangeSlider.SetTickFreq(5, 1)
		self.Bind(wx.EVT_SLIDER, self.onRangeSlider, self.rangeSlider)

		# result
		self.resultText = wx.TextCtrl(self.controlPanel, -1, "", (15, 155), (400, 240), wx.TE_MULTILINE)
		
		self.runner = CInterpreterRunner()

	def SetUp(self):
		# TODO: rewrite
		
		self.fileText.SetConstraints(anchors.LayoutAnchors(self.fileText, 1, 1, 1, 0))
		self.fileSelectButton.SetConstraints(anchors.LayoutAnchors(self.fileSelectButton, 0, 1, 1, 0))
		self.cppPathText.SetConstraints(anchors.LayoutAnchors(self.cppPathText, 1, 1, 1, 0))
		self.cppPathSelectButton.SetConstraints(anchors.LayoutAnchors(self.cppPathSelectButton, 0, 1, 1, 0))
		self.cppArgsText.SetConstraints(anchors.LayoutAnchors(self.cppArgsText, 1, 1, 1, 0))

		self.controlPanel.SetConstraints(anchors.LayoutAnchors(self.controlPanel, 1, 1, 1, 1))

		self.functionChoice.SetConstraints(anchors.LayoutAnchors(self.functionChoice, 1, 1, 1, 0))
		self.variableChoice.SetConstraints(anchors.LayoutAnchors(self.variableChoice, 1, 1, 1, 0))
		self.rangeSlider.SetConstraints(anchors.LayoutAnchors(self.rangeSlider, 1, 1, 1, 0))
		self.resultText.SetConstraints(anchors.LayoutAnchors(self.resultText, 1, 1, 1, 1))
		
		self.cppPathText.SetValue(r'./pycparser/utils/cpp.exe')
		self.cppArgsText.SetValue(r'-I./pycparser/utils/fake_libc_include')

		pass
		
	def onFileText(self, event):
#		self.fileText.SetConstraints(anchors.LayoutAnchors(self.fileText, 1, 1, 1, 0))
		pass

	def onCloseWindow(self, event):
		self.Destroy()

	def onRangeSetButton(self, event):
		val = self.rangeText.Value
		pair = val.split(',')
		if len(pair) < 2:
			return
		self.rangeSlider.SetRange(int(pair[0]), int(pair[1]))
		pass

	def onRangeSlider(self, event):
		selIdx = self.functionChoice.GetSelection()
		if selIdx == -1:
			return
		funcName = self.functionChoice.GetItems()[selIdx]
		varName = self.variableChoice.GetItems()[self.variableChoice.GetSelection()]
		value = self.rangeSlider.GetValue()
		self.runner.SetVariable(varName, value)
		result = self.runner.CallFunction(funcName, [])
		
		list = []
		for key, value in result.items():
			list.append("%s %s %s" % (key.name, value["min"], value["max"]))
		self.resultText.SetValue("\n".join(list))

		pass

	def onFileSelectButton(self, event):
		dlg = wx.FileDialog(
			self, message="Choose a file",
			defaultDir=os.getcwd(), 
			defaultFile="",
			wildcard="C file (*.c)|*.c||",
			style=wx.OPEN
			)
		ret = dlg.ShowModal()
		if ret != wx.ID_OK:
			return
		self.fileText.SetValue(dlg.GetPath())
	
	def onParseButton(self, event):
		self.runner.Load(self.fileText.GetValue(), self.cppPathText.GetValue(), self.cppArgsText.GetValue())
		vars = self.runner.GetVariables()
		funcNames = []
		varNames = []
		for k,v in vars.items():
			if isinstance(v[0], FuncDef):
				funcNames.append(k)
			elif isinstance(v[0], Variable):
				varNames.append(k)
		self.functionChoice.Set(funcNames)
		self.variableChoice.Set(varNames)

	def onCppPathSelectButton(self, event):
		pass

	def onRangeText(self, event):
		pass

	def onFunctionChoice(self, event):
		pass

	def onVariableChoice(self, event):
		pass

app = wx.App(False)

try:
	win = AppForm(None, -1)
	win.Show(True)
	win.SetUp()
	app.MainLoop()
	
except:
    
	pass



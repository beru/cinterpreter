#!/usr/bin/env python

import os
import wx
import sys
import json

from runner import *
from dump import *

class MyFrame(wx.Frame):
	def __init__(self, parent, ID, title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
		wx.Frame.__init__(self, parent, ID, title, pos, size, style)
		panel = wx.Panel(self, -1)

		button2 = wx.Button(panel, -1, "Select target")
		button2.SetPosition((150, 15))
		self.Bind(wx.EVT_BUTTON, self.onButton2, button2)

		self.functionChoice = wx.Choice(panel)
		self.functionChoice.SetSize((200, -1))
		self.functionChoice.SetPosition((20, 60))
		self.Bind(wx.EVT_CHOICE, self.onFunctionChoice, self.functionChoice)

		self.variableList = wx.ListBox(panel)
		self.variableList.SetSize((100, 300))
		self.variableList.SetPosition((20, 110))
		self.Bind(wx.EVT_LISTBOX, self.onVariableList, self.variableList)
		
		self.rangeText = wx.TextCtrl(panel, -1, "", (140, 120))
		self.rangeText.SetSize((200, -1))
		self.Bind(wx.EVT_TEXT, self.onRangeText, self.rangeText)

		self.rangeSetButton = wx.Button(panel, -1, "Set")
		self.rangeSetButton.SetPosition((350, 120))
		self.Bind(wx.EVT_BUTTON, self.onRangeSetButton, self.rangeSetButton)

		self.rangeSlider = wx.Slider(
			panel, 100, 25, 1, 100, (140, 160), (400, -1), 
			wx.SL_HORIZONTAL
			)
		self.rangeSlider.SetTickFreq(5, 1)
		self.Bind(wx.EVT_SLIDER, self.onRangeSlider, self.rangeSlider)

		self.resultText = wx.TextCtrl(panel, -1, "", (150, 200), (400, 400), wx.TE_MULTILINE)
		
		self.runner = CInterpreterRunner()
		
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
		varName = self.variableList.GetItems()[self.variableList.GetSelection()]
		value = self.rangeSlider.GetValue()
		self.runner.SetVariable(varName, value)
		result = self.runner.CallFunction(funcName, [])
		
		list = []
		for key, value in result.items():
			list.append("%s %d %d" % (key.name, value["min"], value["max"]))
		self.resultText.SetValue("\n".join(list))

		pass

	def onButton2(self, event):
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
		
		self.runner.Load(dlg.GetPath())
		vars = self.runner.GetVariables()
		funcNames = []
		varNames = []
		for k,v in vars.items():
			if isinstance(v[0], FuncDef):
				funcNames.append(k)
			elif isinstance(v[0], Variable):
				varNames.append(k)
		self.functionChoice.Set(funcNames)
		self.variableList.Set(varNames)
	
	def onRangeText(self, event):
		pass

	def onFunctionChoice(self, event):
		pass

	def onVariableList(self, event):
		pass

app = wx.App(False)

try:
	win = MyFrame(None, -1, "CInterpreter", size=(700, 600), style = wx.DEFAULT_FRAME_STYLE)
	win.Show(True)
	app.MainLoop()

except:
    
	pass



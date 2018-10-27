"""Demo based on the demo mclist included with tk source distribution."""
import tkinter as tk
import tkinter.font
from tkinter import ttk
import csv
from tkinter import messagebox
from dgInterface import *

def setTaxCodeFilename(outpath, modifier):
	return outpath + "taxCodes_" + modifier + ".csv"


def sortby(tree, col, descending):
	"""Sort tree contents when a column is clicked on."""
	# grab values to sort
	data = [(tree.set(child, col), child) for child in tree.get_children('')]

	# reorder data
	data.sort(reverse=descending)
	for indx, item in enumerate(data):
		tree.move(item[1], '', indx)

	# switch the heading so that it will sort in the opposite direction
	tree.heading(col,
		command=lambda col=col: sortby(tree, col, int(not descending)))

class TaxReadIn:
	def __init__(self, parent):
		self.taxonomy_columns = ("Code", "Grouping", "Classification", "Specialization", "Definition", "Notes")
		self.file = "C:\\Users\\angel.hernandez\\Desktop\\hcp_taxonomy_codes.csv"
		self.taxonomy_file = open(self.file)
		self.taxonomy_file = csv.reader(self.taxonomy_file)
		self.specialCharacters = '[\\/*?:"<>|]!@#$%^&+=}{\''

		def getPath(file):
			if "\\" in file:
				filename_split = file.split("\\")
			else:
				filename_split = file.split("/")
			path = ""
			for i in range(0, len(filename_split) - 1):
				path = path + filename_split[i] + "\\"
			return path

		self.outpath = getPath(self.file)


class App(TaxReadIn):
	def __init__(self, parent):
		TaxReadIn.__init__(self, parent)
		self.parent = parent
		self.frame = ttk.Frame(self.parent, width=1100, height=800, padding=(10, 10, 10, 10))
		# self.tree = None
		self._setup_widgets()
		self._build_tree()


	def addToSource(self):
		for item in self.tree.selection():
			full_item = self.tree.item(item,"values")[0] + " - " + self.tree.item(item,"values")[2] + " - " + self.tree.item(item,"values")[3]
			partial_item =  self.tree.item(item,"values")[0] + " - " + self.tree.item(item,"values")[2]
			if full_item not in self.srcBox.get(0, 'end') and partial_item not in self.srcBox.get(0, 'end'):
				if self.tree.item(item,"values")[3] != "":
					self.srcBox.insert(0, full_item)
				else:
					self.srcBox.insert(0, partial_item)

	def addToTarget(self):
		for item in self.tree.selection():
			full_item = self.tree.item(item,"values")[0] + " - " + self.tree.item(item,"values")[2] + " - " + self.tree.item(item,"values")[3]
			partial_item =  self.tree.item(item,"values")[0] + " - " + self.tree.item(item,"values")[2]
			if full_item not in self.tgtBox.get(0, 'end') and partial_item not in self.tgtBox.get(0, 'end'):
				if self.tree.item(item,"values")[3] != "":
					self.tgtBox.insert(0, full_item)
				else:
					self.tgtBox.insert(0, partial_item)


	def clearSelection(self):
		for item in self.srcBox.curselection():
			self.srcBox.delete(item)
		for item in self.tgtBox.curselection():
			self.tgtBox.delete(item)
   
	def clearAll(self):
		self.srcBox.delete(0, 'end')
		self.tgtBox.delete(0, 'end')

	def submitTaxonomy(self):
		breakFlag = 0
		#run validation
		for character in self.specialCharacters:
			if character in self.srcAlias.get().lower() or character in self.tgtAlias.get().lower():
				breakFlag = 1
				return self.userMessage("specialCharacters")
			elif self.srcAlias.get() == '' or self.tgtAlias.get() == '':
				breakFlag = 1
				return self.userMessage("blankAlias")
			elif self.srcAlias.get() == self.tgtAlias.get():
				breakFlag = 1
				return self.userMessage("sameAlias")
			else:
				for item in self.srcBox.get(0, 'end'):
					if item in self.tgtBox.get(0, 'end'):
						return self.userMessage("srcInTarget")
				for item in self.tgtBox.get(0, 'end'):
					if item in self.srcBox.get(0, 'end'):
						return self.userMessage("tgtInSource")
		if breakFlag == 0:
			#source        
			src = self.srcAlias.get().lower()
			with open(setTaxCodeFilename(self.outpath, src), 'w') as src_csvfile:
				srcWriter = csv.writer(src_csvfile, lineterminator='\n')
				srcWriter.writerow([src])
				srcRows = zip(self.srcBox.get(0, 'end'))
				for item in srcRows:
					srcWriter.writerow([item[0].split(" - ")[0]])
			#targets
			tgt = self.tgtAlias.get().lower()
			with open(setTaxCodeFilename(self.outpath, tgt), 'w') as tgt_csvfile:
				tgtWriter = csv.writer(tgt_csvfile, lineterminator='\n')
				tgtWriter.writerow([tgt])
				tgtRows = zip(self.tgtBox.get(0, 'end'))
				for item in tgtRows:
					tgtWriter.writerow([item[0].split(" - ")[0]])
			self.parent.destroy()  

	def userMessage(self, messageType):
		if messageType == "specialCharacters":
			messagebox.showwarning("Special Character Warning", "Filename cannot inlcude the following special characters: " + self.specialCharacters)
		elif messageType == "blankAlias":
			messagebox.showwarning("Blank Alias Warning", "Source/Target alias was left blank. Please include an alias.")
		elif messageType == "sameAlias":
			messagebox.showwarning("File Overwrite Warning", "Source and Target alias names cannot be the same.")
		elif messageType == "srcInTarget":
			messagebox.showwarning("Self Reference Warning", "Source Taxonomy Codes were found in Target Taxonomy Codes. Please ensure Source and Target Codes are mutually exclusive.")
		elif messageType == "tgtInSource":
			messagebox.showwarning("Self Reference Warning", "Target Taxonomy Codes were found in Source Taxonomy Codes. Please ensure Source and Target Codes are mutually exclusive.")
			
	
	def setTgtAlias(self):
		self.tgtAliasSet = self.tgtAlias.get()

	
	def setSrcAlias(self):
		self.srcAliasSet = self.srcAlias.get()

	def cancel(self):
		self.parent.destroy()

	def columnResizerFilter(self):
		for child in self.tree.get_children(): 
			max_lengths = [0] * len(self.tree.item(child, 'values'))
			for child in self.tree.get_children(): 
				for index, value in enumerate(self.tree.item(child, 'values')):
					ilen = tk.font.Font().measure(value)
					if ilen > max_lengths[index]:
						max_lengths[index] = ilen
					self.tree.column(self.taxonomy_columns[index], width=max_lengths[index])


			# adjust columns lenghts if necessary
	def columnResizerReset(self):
		for child in self.tree.get_children(): 
			for index, value in enumerate(self.tree.item(child, 'values')):
				ilen = tk.font.Font().measure(value)
				if self.tree.column(self.taxonomy_columns[index], width=None) < ilen:
					if self.taxonomy_columns[index] == "Definition" or self.taxonomy_columns[index] == "Notes":
						self.tree.column(self.taxonomy_columns[index], width=200)
					else: 
						self.tree.column(self.taxonomy_columns[index], width=ilen, stretch='no')
	
	def _setup_widgets(self):
		# self.msg = ttk.Label(self.frame, wraplength="4i", justify="left", anchor="n",
		#     padding=(10, 2, 10, 6),
		#     text=("Select the Source and Target Taxonomy Codes for Analysis."))
		# self.msg.grid(row=0, column=2, sticky="ew")

		#a treeview with scrollbars.
		self.tree = ttk.Treeview(self.frame, columns=self.taxonomy_columns, show="headings", selectmode='extended')
		vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
		hsb = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
		self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
		self.tree.grid(column=0, row=1, columnspan=4, sticky='nws')
		vsb.grid(column=3, row=1, sticky="NE" + "SE")
		hsb.grid(column=0, row=2, columnspan=4, sticky='ew')

	   
		self.filterLabel = tk.Label(self.frame, text="Filter by:")
		self.filterEntry = tk.Entry(self.frame)
		# self.filterLabel.pack(side='left', fill='x')
		# self.filterEntry.pack(side='left', fill='x')
		self.filterEntry.grid(row=0, column=1, sticky='W')
		self.filterLabel.grid(row=0,column=0, sticky='E')

		self.srcAliasLabel = tk.Label(self.frame, text="Enter alias name for Source Taxonomies (i.e., derm, gastro, etc...)")
		self.srcAlias = tk.Entry(self.frame)
		# self.srcAliasLabel.pack(side='top', fill='x')
		# self.srcAlias.pack(side='bottom', fill='x')
		self.srcAliasLabel.grid(row=5,column=0)
		self.srcAlias.grid(row=6,column=0, sticky="ew")
		self.srcAliasButton = tk.Button(self.frame,text="Set", command=self.setSrcAlias)
		self.srcAliasButton.grid(row=7,column=0, sticky="ew")
		
	

		self.tgtAlias = tk.Entry(self.frame)
		self.tgtAliasLabel = tk.Label(self.frame, text="Enter alias name for Target Taxonomies (i.e., hep, onc, etc...)")
		# self.tgtAliasLabel.pack(side='top', fill='x')
		# self.tgtAlias.pack(side='bottom', fill='x')
		self.tgtAliasLabel.grid(row=5,column=3)
		self.tgtAlias.grid(row=6,column=3, sticky = "ew")
		self.tgtAliasButton = tk.Button(self.frame, text="Set", command=self.setTgtAlias)
		self.tgtAliasButton.grid(row=7,column=3, sticky="ew")
		
		self.filterButton = tk.Button(self.frame, text="Filter", command=self.filterTree)
		self.filterButton.grid(row=0,column=2, sticky = "we", padx = 4)

		self.resetButton = tk.Button(self.frame, text="Reset Filters", command=self.resetFilter)
		self.resetButton.grid(row=0, column=3, sticky= "w")

		self.removeButtonSelect = tk.Button(self.frame, text="Clear Selection", command=self.clearSelection)
		self.removeButtonSelect.grid(row=4, column=1)

		self.removeButtonAll = tk.Button(self.frame, text="Clear All", command=self.clearAll)
		self.removeButtonAll.grid(row=4, column=2)
		
		self.submitTaxonomyButton = tk.Button(self.frame, text="Submit", command=self.submitTaxonomy)
		self.submitTaxonomyButton.grid(row=8,column=2, sticky="ew")

		self.cancelButton = tk.Button(self.frame, text="    Cancel    ", command=self.cancel)
		self.cancelButton.grid(row=8,column=1, sticky="w")


		#Getting and Storing Taxonomy Codes
		self.srcButton = tk.Button(self.frame, text="Add to Source", command=self.addToSource)
		self.srcButton.grid(row=3, column=0, sticky="ew")

		self.srcBox = tk.Listbox(self.frame, width=40, height=10, selectmode='extended')
		self.srcBox.grid(row=4, column=0, sticky="news")
		srcVSB = tk.Scrollbar(self.frame, orient="vertical", command=self.srcBox.yview)
		self.srcBox.configure(yscrollcommand=srcVSB.set, xscrollcommand=srcVSB.set)
		srcVSB.grid(column=0, row=4, sticky='ens')


		self.tgtButton = tk.Button(self.frame, text="Add to Target", command=self.addToTarget, padx=10)
		self.tgtButton.grid(row=3, column=3, sticky="ew")

		self.tgtBox = tk.Listbox(self.frame, width=40, height=10, selectmode='extended')
		self.tgtBox.grid(row=4, column=3, sticky="news")
		tgtVSB = tk.Scrollbar(self.frame, orient="vertical", command=self.tgtBox.yview)
		self.tgtBox.configure(yscrollcommand=tgtVSB.set, xscrollcommand=tgtVSB.set)
		tgtVSB.grid(column=3, row=4, sticky='ens')

	  
		self.frame.pack(fill="both", expand=False)
		
		for i in range(0, 6):
			self.frame.grid_columnconfigure(i, weight=1)
		for i in range(0, 9):	
			self.frame.grid_rowconfigure(i, weight=1)

		
		self.saved_children = [] 
	def filterTree(self):        
		children = self.tree.get_children()
		
		for child in children:
			for i in range(0, len(self.tree.item(child,'values'))):
				if self.filterEntry.get().lower().strip() not in [value.lower().strip() for value in self.tree.item(child, 'values')]:
					self.saved_children.append(self.tree.item(child, 'values'))
					self.tree.detach(child)
					break
		for child in self.saved_children:
			for value in [child[1], child[2], child[3]]:
				if self.filterEntry.get().lower().strip() in value.lower().strip():
					self.tree.insert('', 'end', values=child)
					self.saved_children.remove(child)
					break
		self.columnResizerFilter()

	def resetFilter(self):
		for child in self.saved_children:
			self.tree.insert('', 'end', values=child)
		data = [(self.tree.set(child, "Code"), child) for child in self.tree.get_children('')]
		# reorder data
		data.sort(reverse=0)
		for indx, item in enumerate(data):
			self.tree.move(item[1], '', indx)
		#reset children
		self.saved_children = []
		self.columnResizerReset()
	

	def _build_tree(self):
		for col in self.taxonomy_columns:
			self.tree.heading(col, text=col.title(),
				command=lambda c=col: sortby(self.tree, c, 0))
			self.tree.column(col, width=tk.font.Font().measure(col.title()))

		for item in self.taxonomy_file:
			if item[0] == "Code":
				continue
			else:    
				self.tree.insert('', 'end', values=item)
				# adjust columns lenghts if necessary
				for indx, val in enumerate(item):
					ilen = tk.font.Font().measure(val)
					if self.tree.column(self.taxonomy_columns[indx], width=None) < ilen:
						if self.taxonomy_columns[indx] == "Definition" or self.taxonomy_columns[indx] == "Notes":
							self.tree.column(self.taxonomy_columns[indx], width=200)
						else:
							self.tree.column(self.taxonomy_columns[indx], width=ilen)
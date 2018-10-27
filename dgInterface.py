import tkinter as tk
from tkinter import *
from tkinter import ttk
from TaxonomyInterface import *
from pathlib import Path
import glob
import os
from tkinter import messagebox

#validation variables
valid_types = ['30', '60', '90', '180']
valid_years = ['2009', '2010', '2011', '2012', '2013', '2014', '2015']


def checkFileExists(srcZipPath, key, fileType):
	filenames = []
	for root, dirs, files in os.walk(srcZipPath):
		for directory in dirs:
			curr_file = glob.glob(os.path.join(root, directory, "*." + fileType))
			for file in curr_file:
				if file.find(key) >= 0:
					filenames.append(file)
					return True, filenames
	return False, ""

class CustomWidget(tk.Frame):
	def __init__(self, parent, label, default=""):
		tk.Frame.__init__(self, parent)

		self.label = tk.Label(self, text=label, anchor="w")
		self.entry = tk.Entry(self)
		self.entry.insert(0, default)

		self.label.pack(side="top", fill="x")
		self.entry.pack(side="bottom", fill="x", padx=4)
	def get(self):
		return self.entry.get()

class DocGraphImport:
	def __init__(self, parent):
		self.parent = parent
		self.frame = ttk.Frame(self.parent, padding=(10, 10, 10, 10))
		self.label =  ttk.Label(self.frame, wraplength="4i", justify="left", anchor="n",padding=(0, 2, 10, 6), text=("Set the desired Year (2009, 2010, etc...) and Type (30, 60, 90, or 180). Delimit by comma for multiple years and types. Set the desired options for the DocGraph Process (Unzip, infile, etc...). The 'Generate Graph Data' checkbox will generate a table of Source and Target NPIs based on the selected Taxonomies."))
		self.year = CustomWidget(self.frame, "Year:", "")
		self.type = CustomWidget(self.frame, "Type:", "")
		self.unzipVar = IntVar()
		self.unzip = tk.Checkbutton(self.frame, text="Unzip Data", variable=self.unzipVar)
		self.infileVar = IntVar()
		self.infile = tk.Checkbutton(self.frame, text="Infile Data", variable=self.infileVar)
		self.wideVar = IntVar()
		self.wide = tk.Checkbutton(self.frame, text="Wide", variable=self.wideVar)
		self.longVar = IntVar() 
		self.long =tk.Checkbutton(self.frame, text="Long", variable=self.longVar)
		self.submit = tk.Button(self.frame, text="Submit", command=self.submit)
		self.taxonomy = tk.Button(self.frame, text="Taxonomy", command=self.taxonomy)
		self.graphVar = IntVar()
		self.generateGraphSet=tk.Checkbutton(self.frame, text="Generate Graph Set", variable=self.graphVar, command=self.selectTaxCodeFiles)
		self.graphSetFlag = 0

		self.intVar = IntVar()
		self.full = tk.Radiobutton(self.frame, text="Complete Dataset", variable=self.intVar, value=1)
		self.rand = tk.Radiobutton(self.frame, text="Sampled Dataset", variable=self.intVar, value=2)
		self.year.grid(row=1, column=0, sticky="W")
		self.type.grid(row=2, column=0, sticky="W")
		self.label.grid(row=0, column=0, columnspan=2, sticky="W")
		self.unzip.grid(row=4, column=0, sticky="W")
		self.infile.grid(row=4, column=1, sticky="W")
		self.wide.grid(row=5,column=0, sticky="W")
		self.long.grid(row=5,column=1, sticky="W")

		self.full.grid(row=6,column=0, sticky="W")
		self.rand.grid(row=6,column=1, sticky="W")
		self.generateGraphSet.grid(row=7, column=0, sticky="W")
		self.taxonomy.grid(row=8, column=0, sticky="W", padx=30)
		self.submit.grid(row=8, column=1, sticky="W", padx=30)

		self.frame.pack()
		# self.frame.grid_columnconfigure(1, weight=1)
		# self.frame.grid_rowconfigure(10, weight=1)

	def submit(self):
		self.validYearFlag = 0
		self.validTypeFlag = 0
		def existenceCheck(year_vars, type_vars, fileType, path):
			filenames = []
			for _year in year_vars:
				for _type in type_vars:
					if fileType == "sas7bdat":
						key = _year + "_" + _type
					elif fileType == "lw_sas7bdat":
						key = "dg_" + _year
					else:
						key = _year + "-days" + _type
					exists = checkFileExists(path, key, fileType)
					if not exists[0]:
						self.userMessage(fileType + "FileNotExists", "Year: " + _year + " and Type: " + _type)
					else:
						filenames.append(exists[1][0])
			return filenames

		self.yearVars = self.year.get().replace(" ", "").split(",")
		self.typeVars = self.type.get().replace(" ", "").split(",")
		self.countYears = len(self.yearVars)
		self.countTypes = len(self.typeVars)
		self.total = self.countYears * self.countTypes
		def validator(filesToCheck):
			if self.total == len(filesToCheck):
				return True
			return False

		#default is to Pass All
		yearPass = True
		typePass = True
		optionPass = True
		zipPass = True
		infilePass = True
		lwPass = True
		crPass = True
		graphPass = True
		sas7bdatPass = True

		if self.unzipVar.get() == 0 and self.infileVar.get() == 0 and self.wideVar.get() == 0 and self.longVar.get() == 0 and self.intVar.get() == 0 and self.graphVar.get() == 0:
			optionPass = False
			self.userMessage("selectOption")

		#run validation
		for year in self.yearVars:
			if year not in valid_years:
				self.validYearFlag = 1
				yearPass = False
				self.userMessage("invalidYears")

		for type in self.typeVars:
			if type not in valid_types:
				self.validTypeFlag = 1
				typePass = False
				self.userMessage("invalidTypes")

		if self.unzipVar.get() == 1:
			#check if dataset exists
			if self.validYearFlag != 1 and self.validTypeFlag != 1:
				path = "C:\\Users\\angel.hernandez\\Desktop\\test_dir\\load\\gdg"
				# real_path = "\\Vmbcevwwps01\\wpsdata_at_01\\Clients\\DocGraph\\DocGraph_DW\\load\\GDG\\YER" + year + "\\input"
				fileType = "zip"
				zipExistence = existenceCheck(self.yearVars, self.typeVars, fileType, path)
				zipPass = validator(zipExistence)

		if self.infileVar.get() == 1 and self.unzipVar.get() == 0:
			if self.validYearFlag != 1 and self.validTypeFlag != 1:
				path = "C:\\Users\\angel.hernandez\\Desktop\\test_dir\\load\\gdg"
				fileType = "txt"
				txtExistence = existenceCheck(self.yearVars, self.typeVars, fileType, path)
				infilePass = validator(txtExistence)
		
		if self.infileVar.get() == 0 and (self.wideVar.get() == 1 or self.longVar.get() == 1):
			if self.validYearFlag != 1 and self.validTypeFlag != 1:
				path = "C:\\Users\\angel.hernandez\\Desktop\\test_dir\\load\\gdg"
				fileType = "sas7bdat"
				sas7bdatExistence = existenceCheck(self.yearVars, self.typeVars, fileType, path)
				sas7bdatPass = validator(sas7bdatExistence)

		if self.intVar.get() != 0 and self.wideVar.get() == 0 and self.longVar.get() == 0:
			if self.validYearFlag != 1 and self.validTypeFlag != 1:
				if self.userMessage("selectLongWide") == False:
					lwPass = False

		if self.intVar.get() == 0 and (self.wideVar.get() != 0 or self.longVar.get() != 0):
			if self.validYearFlag != 1 and self.validTypeFlag != 1:
				if self.userMessage("selectFullRand") == False:
					crPass = False

		if self.graphVar.get() == 1 and (self.wideVar.get() == 0 and self.longVar.get() ==0):
			if self.validYearFlag != 1 and self.validTypeFlag != 1:
				path = "C:\\Users\\angel.hernandez\\Desktop\\test_dir\\process\\gdg"
				fileType = "lw_sas7bdat"
				lw_sas7bdatExistence = existenceCheck(self.yearVars, self.typeVars, fileType, path)
				lw_sas7bdatPass = validator(lw_sas7bdatExistence)

		try:
			if len(self.app.taxonomyFiles) != 2 and self.graphVar.get() == 1:
				graphPass = False
				self.userMessage("invalidSelection")
		except AttributeError:
			if self.graphVar.get() == 1:
				graphPass = False
				self.userMessage("invalidSelection")
		
		validationPass = yearPass and typePass and optionPass
		if self.unzipVar.get() == 1:
			validationPass = validationPass and zipPass
		if self.infileVar.get() ==1:
			validationPass = validationPass and infilePass
		if self.wideVar.get() == 1 or self.longVar.get() == 1:
			validationPass = validationPass and sas7bdatPass
		if self.intVar.get() != 0 or self.intVar.get() == 0:
			validationPass = validationPass and crPass and lwPass
		if self.graphVar.get() == 1:
			validationPass = validationPass and graphPass

		if validationPass: 
			#will execute script if yes is hit:
			filesToUnzip = ""
			if self.unzipVar.get() == 1:
				for i, file in enumerate(zipExistence):
					filesToUnzip = filesToUnzip + "   " + str(i + 1) + ". " + file.split("\\")[-1] + "\n"
			else:
				for i, file in enumerate(txtExistence):
					filesToUnzip = filesToUnzip + "   " + str(i + 1) + ". " + file.split("\\")[-1] + "\n"

			datasetsToCreate = ""
			i = 1
			for year in self.yearVars:
				for type in self.typeVars:
					if self.intVar.get() == 1:
						dsType = "full"
					elif self.intVar.get() == 2:
						dsType = "rand"

					if self.infileVar.get() == 1:
						datasetsToCreate = datasetsToCreate + "   " + str(i) + ". docgraph" + year + "_" + type + "_raw.sas7bdat" + "\n"
						i = i + 1
					if self.wideVar.get() == 1:
						datasetsToCreate = datasetsToCreate + "   " + str(i) + ". dg_" + year + "_wide_"+ dsType +".sas7bdat" + "\n"
						i = i + 1
					if self.longVar.get() == 1:
						datasetsToCreate = datasetsToCreate + "   " + str(i) + ". dg_" + year + "_long_"+ dsType +".sas7bdat" + "\n"
						i = i + 1
					try:
						if (self.wideVar.get() == 1 and self.graphVar.get() == 1) or ("wide" in "".join(lw_sas7bdatExistence) and self.graphVar.get() == 1):
							datasetsToCreate = datasetsToCreate + "   " + str(i) + ". dg_" + year + "_wide_taxonomy_"+ dsType +".sas7bdat" + "\n"
							i = i + 1
						if self.longVar.get() == 1 and self.graphVar.get() == 1 or ("long" in "".join(lw_sas7bdatExistence) and self.graphVar.get() == 1):
							datasetsToCreate = datasetsToCreate + "   " + str(i) + ". dg_" + year + "_long_taxonomy_"+ dsType +".sas7bdat" + "\n"
							i = i + 1
					except UnboundLocalError:
						pass

			if self.unzipVar.get() == 1 and (self.wideVar.get() == 1 or self.longVar.get() == 1):
				user_message = "The following files will be unzipped and/or infiled:\n" + filesToUnzip + "The following datasets will be created:\n" + datasetsToCreate + "Are you sure you want proceed?"
			elif self.wideVar.get() != 1 and self.longVar.get() != 1 and self.graphVar.get() != 1:
				user_message = "The following files will be unzipped and/or infiled:\n" + filesToUnzip + "Are you sure you want proceed?"

			if messagebox.askyesno("Confirm Selection", user_message):
				print("Success")
				#store vars and call sas

	def taxonomy(self):
		self.taxFrame = tk.Toplevel(self.parent)
		self.taxApp = App(self.taxFrame)
		self.taxFrame.geometry('{}x{}'.format(1100, 600))
		# tax = tk.Tk()
		# tax.wm_title("Taxonomy Selection")
		# tax.wm_iconname("Taxonomy Selection")
		# taxInterface = App(tax)
		# tax.geometry('{}x{}'.format(1100, 600))
		# tax.mainloop()

	def selectTaxCodeFiles(self):
		if self.graphSetFlag == 0:
			self.newFrame = tk.Toplevel(self.parent)
			self.app = TaxonomyCodes(self.newFrame)
			self.graphSetFlag = 1
		else:
			self.graphVar.set(0)
			self.graphSetFlag = 0
	
	def userMessage(self, messageType, params=None):
		if messageType == "invalidSelection":
			messagebox.showwarning("Invalid Selection", "Taxonomy Code Files must be selected.")
		elif messageType == "invalidYears":
			messagebox.showwarning("Invalid Year Entry", "Entry in Year is not recognized or is blank.")
		elif messageType == "invalidTypes":
			messagebox.showwarning("Invalid Year Entry", "Entry in Type is not recognized or is blank.")
		elif messageType == "zipFileNotExists":
			messagebox.showwarning("File Not Found", "The ZIP file for " + params + " was not found.")
		elif messageType == "txtFileNotExists":
			messagebox.showwarning("File Not Found", "The raw data text file for " + params + " was not found. Please select option to Unzip.")
		elif messageType == "sas7bdatFileNotExists":
			messagebox.showwarning("File Not Found", "The raw SAS dataset for " + params + " was not found. Please select option to Infile.")
		elif messageType == "selectLongWide":
			messagebox.showwarning("Select Long and/or Wide", "The Complete/Sampled Dataset option requires Long and/or Wide to be selected.")
		elif messageType == "lw_sas7bdatFileNotExists":
			messagebox.showwarning("File Not Found", "The Wide/Long dataset for " + params + " was not found. Please selection Wide/Long option to create.")
		elif messageType == "selectFullRand":
			messagebox.showwarning("Select Complete or Random", "The Completed or Sampled option must be selected when creating the Wide, Long, or Graph datasets.")
		elif messageType == "selectOption":
			messagebox.showwarning("No Options Selected", "No options selected.")
		return False

class TaxonomyCodes(DocGraphImport):
	def __init__(self, parent):
		self.parent = parent
		self.frame = ttk.Frame(self.parent, width=400, height=330, padding=(10, 10, 10, 10))
		self.taxCodeBox = tk.Listbox(self.frame, width=50, height=10, selectmode='extended')
		self.taxCodeBox.grid(row=0, column=0, columnspan=2, sticky="news")
		self.taxnomyButton = tk.Button(self.frame, text="Create New Taxonomy File", command=self.taxonomy)
		self.taxnomyButton.grid(row=1, column = 0, sticky = "news")
		self.refreshButton = tk.Button(self.frame, text="Refresh", command=self.getTaxCodeFiles)
		self.refreshButton.grid(row=1, column=1, sticky="news")
		self.cancelButton = tk.Button(self.frame, text="Cancel", command=self.cancel)
		self.cancelButton.grid(row=2, column=0, sticky="news")
		self.selectButton = tk.Button(self.frame, text="Select", command=self.saveInput)
		self.selectButton.grid(row=2, column=1, sticky="news")

		self.getTaxCodeFiles()
		self.frame.pack()

	def getTaxCodeFiles(self):
		self.taxCodefile = glob.glob("C:\\Users\\angel.hernandez\\Desktop\\taxCodes*")
		for file in self.taxCodefile:
			if file not in self.taxCodeBox.get(0, 'end'):
				self.taxCodeBox.insert(0, file)

	def saveInput(self):
		if len(self.taxCodeBox.curselection()) != 2:
			messagebox.showwarning("Invalid Selection", "Exactly 2 Taxonomy Code files must be selected.")
		else:
			self.taxonomyFiles = []
			for selection in self.taxCodeBox.curselection():
				self.taxonomyFiles.append(self.taxCodeBox.get(selection))
			self.parent.destroy()

	def cancel(self):
		dgInstance.graphVar.set(0)
		dgInstance.graphSetFlag = 0
		self.parent.destroy()

if __name__ == "__main__":
	root = tk.Tk()
	root.wm_title("DocGraph Interface")
	root.wm_iconname("DocGraph")
	dgInstance = DocGraphImport(root)
	root.geometry('{}x{}'.format(400, 320))
	root.mainloop()
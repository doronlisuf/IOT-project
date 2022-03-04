import socket
import struct
import sys
import json
import os
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QFormLayout, QApplication, QBoxLayout, QTableWidget, QTableWidgetItem, QWidget, QTextEdit, QTabWidget, QComboBox, QLabel,
    QPushButton, QLineEdit, QCheckBox, QFileDialog
)
from PyQt5.QtCore import (
    Qt
)
from PyQt5.sip import delete
from backend.app import App

from backend.atlasObjects import Service, Thing, Relationship
from backend.globals import Globals
from backend.tweetParser import Parser
import time
class Main(QTabWidget):
    def __init__(self):
        super(Main, self).__init__()
        self.setWindowTitle("IoT IDE")
        self.resize(1759, 1225)

        self.things = QWidget(self)
        self.things.setObjectName("Things")
        self.addTab(self.things, "Things")
        self.thingsLayoutOuter = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.thingsLayoutRow1 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.thingsLayoutRow2 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.thingsLayoutOuter.addLayout(self.thingsLayoutRow1)
        self.thingsLayoutOuter.addLayout(self.thingsLayoutRow2)
        self.things.setLayout(self.thingsLayoutOuter)

        self.services = QWidget(self)
        self.services.setObjectName("Services")
        self.addTab(self.services, "Services")
        self.servicesLayoutOuter = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.servicesFilterLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.servicesLayoutRow1 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.servicesLayoutRow2 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.servicesLayoutOuter.addLayout(self.servicesFilterLayout)
        self.servicesLayoutOuter.addLayout(self.servicesLayoutRow1)
        self.servicesLayoutOuter.addLayout(self.servicesLayoutRow2)
        self.services.setLayout(self.servicesLayoutOuter)

        self.relationships = QTabWidget(self)
        self.relationships.setObjectName("Relationships")
        self.addTab(self.relationships, "Relationships")
        self.availableRelationships = QWidget(self.relationships)
        self.unboundedRelationships = QWidget(self.relationships)
        self.relationships.addTab(self.availableRelationships, "Available Relationships")
        self.relationships.addTab(self.unboundedRelationships, "Unbounded Relationships")
        self.availableRelationshipsLayoutOuter = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.relationshipsFilterLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.availableRelationshipsLayoutRow1 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.availableRelationshipsLayoutRow2 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.availableRelationshipsLayoutOuter.addLayout(self.relationshipsFilterLayout)
        self.availableRelationshipsLayoutOuter.addLayout(self.availableRelationshipsLayoutRow1)
        self.availableRelationshipsLayoutOuter.addLayout(self.availableRelationshipsLayoutRow2)
        self.availableRelationships.setLayout(self.availableRelationshipsLayoutOuter)
        self.unboundedRelationshipsLayoutOuter = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.unboundedRelationshipsLayoutRow1 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.unboundedRelationshipsLayoutRow2 = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.unboundedRelationshipsLayoutOuter.addLayout(self.unboundedRelationshipsLayoutRow1)
        self.unboundedRelationshipsLayoutOuter.addLayout(self.unboundedRelationshipsLayoutRow2)
        self.unboundedRelationships.setLayout(self.unboundedRelationshipsLayoutOuter)

        # Recipe tab
        self.recipes = QTabWidget(self)
        self.recipes.setObjectName("Recipes")
        self.addTab(self.recipes, "Recipes")

        # Sub tabs
        self.availableRecipes = QWidget(self.recipes)
        self.createRecipe = QWidget(self.recipes)
        self.editRecipe = QWidget(self.recipes)

        # Activate existing recipe tab
        self.recipes.addTab(self.availableRecipes, "Available Recipes")
        self.availableRecipesLayoutOuter = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.availableRecipesLayoutRow = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.availableRecipesLayoutOuter.addLayout(self.availableRecipesLayoutRow)
        self.availableRecipes.setLayout(self.availableRecipesLayoutOuter)

        # Create new recipe tab
        self.recipes.addTab(self.createRecipe, "Create New Recipe")
        self.createRecipeLayoutOuter = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.createRecipeLayoutRow = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.createRecipeLayoutOuter.addLayout(self.createRecipeLayoutRow)
        self.createRecipe.setLayout(self.createRecipeLayoutOuter)

        # Edit existing recipe
        self.recipes.addTab(self.editRecipe, "Edit existing Recipe")
        self.editRecipeLayoutOuter = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.editRecipeLayoutRow = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.editRecipeLayoutOuter.addLayout(self.editRecipeLayoutRow)
        self.editRecipe.setLayout(self.editRecipeLayoutOuter)
        ### layout for recipes tab ###

        self.worker = Worker()
        self.workerThread = QtCore.QThread()
        self.worker.moveToThread(self.workerThread)
        self.workerThread.started.connect(self.worker.run)
        self.worker.finished.connect(self.workerThread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.workerThread.finished.connect(self.workerThread.deleteLater)
        self.worker.addThingSignal.connect(self.addThing)
        self.worker.addServicesSignal.connect(self.addService)
        self.worker.addRelationshipSignal.connect(self.addRelationship)
        self.worker.addUnboundedRelationshipSignal.connect(self.addUnboundedRelationship)
        self.worker.addRecipeSignal.connect(self.addApps)
        self.worker.addCreateRecipeSignal.connect(self.createRecipeTab)
        self.worker.addServiceRowSignal.connect(self.addServiceRow)
        self.worker.addRelationshipRowSignal.connect(self.addRelationshipRow)
        self.worker.addEditRecipeSignal.connect(self.createEditTab)
        self.workerThread.start()

        QtCore.QMetaObject.connectSlotsByName(self)

    def addThing(self, id, ip, services):
        widget = QTextEdit()
        widget.setReadOnly(True)
        widget.setObjectName(id)
        html = "<b>Thing ID: </b> {}<br>" \
               "<b>IP Address: </b> {}<br>" \
               "<b>Services: </b><br>".format(id, ip)
        for service in services:
            html = html + "- " + service.name + "<br>"
        widget.setHtml(html)
        if self.thingsLayoutRow1.count() > self.thingsLayoutRow2.count():
            self.thingsLayoutRow2.addWidget(widget)
        else:
            self.thingsLayoutRow1.addWidget(widget)
        servicesFilter = QCheckBox(text=id)
        servicesFilter.stateChanged.connect(self.filterServices)
        self.servicesFilterLayout.addWidget(servicesFilter)
        relationshipsFilter = QCheckBox(text=id)
        relationshipsFilter.stateChanged.connect(self.filterRelationships)
        self.relationshipsFilterLayout.addWidget(relationshipsFilter)

    def addService(self, name, thingID, inputs):
        widget = QWidget(self.services)
        widget.setObjectName(name)
        layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        widget.setLayout(layout)
        text = QTextEdit(widget)
        text.setReadOnly(True)
        html = "<b>Service Name: </b> {}<br>" \
               "<b>Owner (Thing ID): </b> {}<br>" \
               "<b>Output: </b><br>".format(name, thingID)
        for inp in inputs:
            html = html + "- " + inp + "<br>"
        text.setHtml(html)
        invokeButton = QPushButton("Invoke", widget)
        invoke = lambda: text.setHtml(html + Globals.allServices[name].invoke())
        invokeButton.clicked.connect(invoke)
        layout.addWidget(text)
        layout.addWidget(invokeButton)
        if self.servicesLayoutRow1.count() > self.servicesLayoutRow2.count():
            self.servicesLayoutRow2.addWidget(widget)
        else:
            self.servicesLayoutRow1.addWidget(widget)
        widget.hide()
        self.updateThing(thingID)
        self.addServiceRow(name)

    def updateThing(self, id):
        thing = Globals.allThings[id]
        widget = self.things.findChild(QTextEdit, name=id)
        html = "<b>Thing ID: </b> {}<br>" \
               "<b>IP Address: </b> {}<br>" \
               "<b>Services: </b><br>".format(id, thing.getHostname())
        for service in list(thing.services.values()):
            html = html + "- " + service.name + "<br>"
        widget.setHtml(html)

    def addRelationship(self, name, serv1, serv2, type):
        widget = QWidget(self.availableRelationships)
        layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        widget.setObjectName(name)
        widget.setLayout(layout)
        text = QTextEdit(widget)
        text.setReadOnly(True)
        html = "<b>Relationship Name: </b> {}<br>" \
               "<b>Service 1: </b> {}<br>" \
               "<b>Service 2: </b> {}<br>" \
               "<b>Type: </b> {}<br>" \
               "<b>Output:</b><br>".format(name, serv1, serv2, type)
        text.setHtml(html)
        layout.addWidget(text)
        if Globals.allRelationships[name].invokable:
            invokeButton = QPushButton("Invoke", widget)
            invoke = lambda: text.setHtml(html + Globals.allRelationships[name].invoke())
            invokeButton.clicked.connect(invoke)
            layout.addWidget(invokeButton)
        if self.availableRelationshipsLayoutRow1.count() > self.availableRelationshipsLayoutRow2.count():
            self.availableRelationshipsLayoutRow2.addWidget(widget)
        else:
            self.availableRelationshipsLayoutRow1.addWidget(widget)
        widget.hide()
        self.addRelationshipRow(name)

    def addUnboundedRelationship(self, name, serv1, serv2, type):
        relationship = Globals.allUnboundedRelationships[name]
        widget = QWidget()
        widget.setObjectName(name)
        form = QFormLayout()
        widget.setLayout(form)
        nameLabel = QLabel("<b>Relationship Name:</b> " + name, widget)
        nameLabel.setTextFormat(Qt.RichText)
        serv1Label = QLabel("<b>Service 1</b>: " + serv1 + " ", widget)
        serv1Label.setTextFormat(Qt.RichText)
        serv2Label = QLabel("<b>Service 2</b>: " + serv2 + " ", widget)
        serv2Label.setTextFormat(Qt.RichText)
        typeLabel = QLabel("<b>Type:</b> " + type, widget)
        typeLabel.setTextFormat(Qt.RichText)
        form.addRow(nameLabel)
        serv1PushButton = QPushButton("Link 1")
        serv2PushButton = QPushButton("Link 2")

        if not relationship.linkedService1:
            serv1Dropdown = self.getServicesDropdown()
            serv1Dropdown.setObjectName("serv1Dropdown")
            serv1Dropdown.setParent(widget)
            serv1PushButton.setParent(widget)
            serv1PushButton.clicked.connect(self.linkServ1)
            form.addRow(serv1Label, serv1Dropdown)
            form.addRow(serv1PushButton)
        else:
            form.addRow(serv1Label)
        if not relationship.linkedService2:
            serv2Dropdown = self.getServicesDropdown()
            serv2Dropdown.setObjectName("serv2Dropdown")
            serv2Dropdown.setParent(widget)
            serv2PushButton.setParent(widget)
            serv2PushButton.clicked.connect(self.linkServ2)
            form.addRow(serv2Label, serv2Dropdown)
            form.addRow(serv2PushButton)
        else:
            form.addRow(serv2Label)
        form.addRow(typeLabel)
        if self.unboundedRelationshipsLayoutRow1.count() > self.unboundedRelationshipsLayoutRow2.count():
            self.unboundedRelationshipsLayoutRow2.addWidget(widget)
        else:
            self.unboundedRelationshipsLayoutRow1.addWidget(widget)

    def getServicesDropdown(self):
        dropdown = QComboBox()
        for service in Globals.allServices.values():
            dropdown.addItem(service.name)
        return dropdown

    def updateUnbounded(self, name, serv1, serv2, type):
        print("updating unbounded relationship", name)

    def linkServ1(self):
        caller = self.sender()
        widget = caller.parentWidget()
        layout = widget.layout()
        relationship = Globals.allUnboundedRelationships[widget.objectName()]
        serv1Dropdown = widget.findChild(QComboBox, "serv1Dropdown")
        relationship.linkService1(Globals.allServices[serv1Dropdown.currentText()])
        if relationship.invokable:
            self.addRelationship(relationship.name, relationship.service1.name, relationship.service2.name, relationship.type)
            layout.removeWidget(widget)
            del widget
        else:
            self.updateUnbounded(relationship.name, relationship.service1, relationship.service2, relationship.type)

    def linkServ2(self):
        caller = self.sender()
        widget = caller.parentWidget()
        layout = widget.layout()
        relationship = Globals.allUnboundedRelationships[widget.objectName()]
        serv2Dropdown = widget.findChild(QComboBox, "serv2Dropdown")
        relationship.linkService2(Globals.allServices[serv2Dropdown.currentText()])
        if relationship.invokable:
            self.addRelationship(relationship.name, relationship.service1.name, relationship.service2.name, relationship.type)
            layout.removeWidget(widget)
            del widget
        else:
            self.updateUnbounded(relationship.name, relationship.service1, relationship.service2, relationship.type)

    def filterServices(self, state):
        caller = self.sender()
        thingName = caller.text()
        for service in Globals.allServices.values():
            if service.thing == thingName:
                serviceWidget = self.services.findChild(QWidget, service.name)
                if state == 0:
                    serviceWidget.hide()
                elif state == 2:
                    serviceWidget.show()


    def logServiceCall(self, type, name, status, output):
        statusWidget = self.availableRecipes.findChild(QTextEdit, 'Status')
        html = statusWidget.toHtml()
        now = datetime.now()
        currentTime = now.strftime('%H:%M:%S')
        if status == 'Running':
            html = html + f'<b>{currentTime} Running</b> {type} {name} <br>'
        elif status == 'Done':
            html = html + f'<b>{currentTime} Finished running </b> {name}. Finished with output: {output} <br>'
        elif status == 'Failed':
            html = html + f'<b>{name}</b> not found on network! <br>Please wait for all Relationships/Services to be detected or verify that Service/Relationship exists on network! <br>'
        elif status == 'Finished': 
            html = html + f'<b>{currentTime} Finished running recipe!</b><br>'
        elif status == 'First':
            html = html + f'<b>{currentTime} Running  Recipe {name}</b><br>'
        elif status == 'Stopped':
            html = html + f'<b>{currentTime} Stopped service!</b><br>'
        elif status == 'Stopping':
            html = html + f'<b>{currentTime} Stopping service...</b><br>'
        statusWidget.setHtml(html)


    def addApps(self, name, services, relationships, conditionals):

        # Read in exisiting recipes in directory and add to global map of apps
        recipesFolder = os.getcwd() + r'/backend/apps'
        files = os.listdir(recipesFolder)
        recipeTable = QTableWidget(self.availableRecipes)
        recipeTable.setColumnCount(1)
        recipeTable.setRowCount(len(files))
        recipeTable.setHorizontalHeaderLabels(['App'])
        recipeTable.setSelectionMode(QTableWidget.SingleSelection)
        recipeTable.selectionModel().selectionChanged.connect(self.selectedApp)
        recipeTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers) 
        header = recipeTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch) 
        
        for row, file in enumerate(files):
            recipeFile = open(recipesFolder +  r'/' + file)
            recipeData = json.load(recipeFile)

            relationships = recipeData["relationships"]
            services = recipeData["services"]
            conditionals = recipeData["conditionals"]

            recipeName = file.split('.')
            recipeName = recipeName[0]

            newApp = App(recipeName, services, relationships, conditionals)
            Globals.allApps[recipeName] = newApp

            cell = QTableWidgetItem(recipeName)
            recipeTable.setItem(row, 0, cell)

        self.availableRecipesLayoutRow.addWidget(recipeTable)
 
        activateButton = QPushButton('Activate', self.availableRecipes)
        activateButton.setToolTip('Activate')
        activateButton.move(250, 250)
        activateButton.clicked.connect(self.onClick_activate)
        self.availableRecipesLayoutRow.addWidget(activateButton)

        clearButton = QPushButton('Clear', self.availableRecipes)
        clearButton.setToolTip('Clear')
        clearButton.clicked.connect(self.onClick_clear)
        self.availableRecipesLayoutRow.addWidget(clearButton)

        refreshButton = QPushButton('Refresh', self.availableRecipes)
        refreshButton.clicked.connect(self.onClick_refresh)
        self.availableRecipesLayoutRow.addWidget(refreshButton)

        stopButton = QPushButton('Stop Service', self.availableRecipes)
        stopButton.clicked.connect(self.onClick_stop)
        self.availableRecipesLayoutRow.addWidget(stopButton)

        deleteButton = QPushButton('Delete App', self.availableRecipes)
        deleteButton.clicked.connect(self.onClick_delete)
        self.availableRecipesLayoutRow.addWidget(deleteButton)
        
        statusWidget = QTextEdit()
        statusWidget.setObjectName('Status')
        html = "<br>"
        statusWidget.setHtml(html)
        self.availableRecipesLayoutRow.addWidget(statusWidget)
        Globals.recipeTable = recipeTable

    # Delete app
    def onClick_delete(self):
        currentRow = Globals.selectedAppRow
        currentColumn = Globals.selectedAppColumn
        currentSelectedAppName = Globals.recipeTable.item(currentRow, currentColumn).text()
        recipesFolder = os.getcwd() + r'/backend/apps'
        appPath = recipesFolder + r'/' + currentSelectedAppName + r'.txt'

        # Check that path exists to file to be deleted 
        if os.path.exists(appPath):
            os.remove(appPath) # Removes app File
            del Globals.allApps[currentSelectedAppName] # Delete app from dictionary
            Globals.recipeTable.removeRow(currentRow) # Delete app from recipes table
        else:
            print('File does not exist')        


    def onClick_refresh(self):
        recipesFolder = os.getcwd() + r'/backend/apps'
        files = os.listdir(recipesFolder)

        appNames = [file.split('.')[0] for file in files] # convert from NAME.txt to NAME
        if all(app in Globals.allApps for app in appNames): # check if any new files have been added
            print('No new files')                           # otherwise return 
            return 
        
        # Check if number of files has changed

        currNumRows = Globals.recipeTable.rowCount()
        Globals.recipeTable.setRowCount(currNumRows + 1)
        for row, file in enumerate(files):
            recipeFile = open(recipesFolder +  r'/' + file)
            recipeData = json.load(recipeFile)

            relationships = recipeData["relationships"]
            services = recipeData["services"]
            conditionals = recipeData["conditionals"]

            recipeName = file.split('.')
            recipeName = recipeName[0]

            newApp = App(recipeName, services, relationships, conditionals)
            Globals.allApps[recipeName] = newApp

            cell = QTableWidgetItem(recipeName)
            Globals.recipeTable.setItem(row, 0, cell)

    def onClick_clear(self):
        statusWidget = self.availableRecipes.findChild(QTextEdit, 'Status')
        html = '<br>'
        statusWidget.setHtml(html)


    def onClick_activate(self):
        # Run API calls on seperate thread to avoid freezing up the GUI
        self.callWorker = CallsWorker()
        Globals.callsInstance = self.callWorker
        self.callsWorkerThread = QtCore.QThread()
        Globals.callThread = self.callsWorkerThread
        self.callWorker.moveToThread(self.callsWorkerThread)
        self.callsWorkerThread.started.connect(self.callWorker.run)
        self.callWorker.finished.connect(self.callsWorkerThread.quit)
        self.callWorker.finished.connect(self.callWorker.deleteLater)
        self.callWorker.progress.connect(self.logServiceCall)
        self.callsWorkerThread.start()


    def onClick_stop(self):
        if self.callsWorkerThread and self.callsWorkerThread.isRunning():
            self.logServiceCall('Message', 'No name', 'Stopping', 'No output')
            Globals.runThread = False


    def selectedApp(self, selected, deselected):
        for i in selected.indexes():
            Globals.selectedAppRow = i.row()
            Globals.selectedAppColumn = i.column()

    def selectedService(self, service):
        appStatus = self.createRecipe.findChild(QTextEdit, 'RecipeStatus')
        html = appStatus.toHtml()
        html = html + f'<b>Added Service</b> {service.text()} <br>'
        appStatus.setHtml(html)
        Globals.selectedServicesList.append(service.text())

    def selectedRelationship(self, relationship):
        appStatus = self.createRecipe.findChild(QTextEdit, 'RecipeStatus')
        html = appStatus.toHtml()
        html = html + f'<b>Added Relationship</b> {relationship.text()} <br>'
        appStatus.setHtml(html)
        Globals.selectedRelationshipsList.append(relationship.text())

    # Create 'createRecipe' tab, such as table, and buttons
    def createRecipeTab(self):
        # Services Table
        servicesTable = QTableWidget(self.createRecipe)
        servicesTable.setColumnCount(1)
        servicesTable.setHorizontalHeaderLabels(['Services'])
        servicesTable.setSelectionMode(QTableWidget.SingleSelection)
        servicesTable.itemDoubleClicked.connect(self.selectedService) # Double click service to add
        # servicesTable.selectionModel().selectionChanged.connect(self.selectedService)
        servicesTable.setObjectName('ServicesTable')
        header = servicesTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        # Add in services
        servicesTable.setRowCount(0) # Add dynamically
        servicesTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
         
        # Add to layout and to global services table
        self.createRecipeLayoutRow.addWidget(servicesTable)
        Globals.servicesTable = servicesTable

        # Relationships Table
        relationshipsTable = QTableWidget(self.createRecipe)
        relationshipsTable.setColumnCount(1)
        relationshipsTable.setHorizontalHeaderLabels(['Relationships'])
        relationshipsTable.setSelectionMode(QTableWidget.SingleSelection)
        relationshipsTable.itemDoubleClicked.connect(self.selectedRelationship) # Double click relationship to add
        # relationshipsTable.selectionModel().selectionChanged.connect(self.selectedRelationship)
        header = relationshipsTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        relationshipsTable.setObjectName('RelationshipsTable')

        relationshipsTable.setRowCount(0)
        relationshipsTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers) 
        # Add to layout and to global relationships table
        self.createRecipeLayoutRow.addWidget(relationshipsTable)
        Globals.relationshipsTable = relationshipsTable

        # Display current services/relationships added
        addedAppWidget = QTextEdit()
        addedAppWidget.setObjectName('Status')
        html = "<b>Current Services/Relationships added to Recipe</b><br>Double click to add to recipe <br>"
        addedAppWidget.setHtml(html)
        addedAppWidget.setObjectName('RecipeStatus')
        self.createRecipeLayoutRow.addWidget(addedAppWidget)

        # Add 'add' button
        addButton = QPushButton('Add', self.createRecipe)
        addButton.clicked.connect(self.onClick_add)
        self.createRecipeLayoutRow.addWidget(addButton)


    def onClick_add(self):
        recipesFolder = os.getcwd() + r'/backend/apps'
        name = QFileDialog.getSaveFileName(self, 'Save File', directory=recipesFolder,  filter='Text files (*.txt)')
        filePath = name[0]


        file = open(filePath, 'w')
        jsonObject = {'services' : Globals.selectedServicesList, 'relationships' : Globals.selectedRelationshipsList, 'conditionals' : []}
        dataStr = json.dumps(jsonObject)
        file.write(dataStr)
        file.close()

        # Reset 
        Globals.selectedServicesList = []
        Globals.selectedRelationshipsList = []
        appStatus = self.createRecipe.findChild(QTextEdit, 'RecipeStatus')
        appStatus.setHtml('<b>Current Services/Relationships added to Recipe</b><br>Double click to add to recipe <br>')
        self.onClick_refresh()

    # Add row when new service is found
    def addServiceRow(self, service):
        currRowCount = Globals.servicesTable.rowCount()
        Globals.servicesTable.setRowCount(currRowCount + 1)

        cell = QTableWidgetItem(service)
        Globals.servicesTable.setItem(currRowCount, 0, cell)
    
        # Add service row to edit existing recipes service table
        newCell =  QTableWidgetItem(service)
        networkServiceTable = self.editRecipe.findChild(QTableWidget, 'networkServices')
        currRowCount = networkServiceTable.rowCount()
        networkServiceTable.setRowCount(currRowCount + 1)
        networkServiceTable.setItem(currRowCount, 0, newCell)


    def addRelationshipRow(self, relationship):
        currRowCount = Globals.relationshipsTable.rowCount()
        Globals.relationshipsTable.setRowCount(currRowCount + 1)

        cell = QTableWidgetItem(relationship)
        Globals.relationshipsTable.setItem(currRowCount , 0, cell)

        # Add relationship row to edit existing recipes relationship table
        newCell = QTableWidgetItem(relationship)
        networkRelationshipsTable = self.editRecipe.findChild(QTableWidget, 'networkRelationships')
        currRowCount = networkRelationshipsTable.rowCount()
        networkRelationshipsTable.setRowCount(currRowCount + 1)
        networkRelationshipsTable.setItem(currRowCount, 0, newCell)
        

    def filterRelationships(self, state):
        caller = self.sender()
        thingName = caller.text()
        for relationship in Globals.allRelationships.values():
            if relationship.service1.thing == thingName or relationship.service2.thing == thingName:
                relationshipWidget = self.availableRelationships.findChild(QWidget, relationship.name)
                if state == 0:
                    relationshipWidget.hide()
                elif state == 2:
                    relationshipWidget.show()
    
    def onClick_open(self):
        file = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileNames()', '', 'Text Files (*.txt)')
        filePath = file[0]
        fileName = filePath.split('/')
        fileName = fileName[len(fileName) - 1]
        appName = fileName.split('.')
        appName = appName[0]

        if not os.path.exists(filePath):
            print('No file was chosen')
            return

        data = ''
        with open(filePath, 'r') as appFile:
            data = appFile.read()
        
        data = json.loads(data)
        
        services = data['services']
        relationships = data['relationships']

        appServiceTable = self.editRecipe.findChild(QTableWidget, 'AppServices')
        appRelationshipsTable = self.editRecipe.findChild(QTableWidget, 'AppRelationships')
        
        # Add in services from app file
        for rowIndex, service in enumerate(services):
            cell = QTableWidgetItem(service)
            appServiceTable.setRowCount(rowIndex + 1)
            appServiceTable.setItem(rowIndex, 0, cell)
        
        for rowIndex, relationship in enumerate(relationships):
            cell = QTableWidgetItem(relationship)
            appRelationshipsTable.setRowCount(rowIndex + 1)
            appRelationshipsTable.setItem(rowIndex, 0, cell)


    def addServiceToApp(self, service):
        serviceName = service.text()
        cell = QTableWidgetItem(serviceName)
        appServiceTable = self.editRecipe.findChild(QTableWidget, 'AppServices')
        rowCount = appServiceTable.rowCount()
        appServiceTable.setRowCount(rowCount + 1)
        appServiceTable.setItem(rowCount, 0, cell)

    
    def addRelationshipToApp(self, relationship):
        relationshipName = relationship.text()
        cell = QTableWidgetItem(relationshipName)
        appRelationshipsTable = self.editRecipe.findChild(QTableWidget, 'AppRelationships')
        rowCount = appRelationshipsTable.rowCount()
        appRelationshipsTable.setRowCount(rowCount + 1)
        appRelationshipsTable.setItem(rowCount, 0, cell)
    
    def removeServiceFromApp(self, service):
        rowPos = self.existingServicesTable.row(service)
        self.existingServicesTable.removeRow(rowPos)
         
    def removeRelationshipFromApp(self, relationship):
        rowPos = self.existingRelationshipsTable.row(relationship)
        self.existingRelationshipsTable.removeRow(rowPos)
    
    def onClick_save(self):
        servicesRowCount = self.existingServicesTable.rowCount()
        relationshipsRowCount = self.existingRelationshipsTable.rowCount()
        
        services = []
        relationships = []
        for rowIndex in range(servicesRowCount):
            item = self.existingServicesTable.item(rowIndex, 0)
            services.append(item.text())
        
        for rowIndex in range(relationshipsRowCount):
            item = self.existingRelationshipsTable.item(rowIndex, 0)
            relationships.append(item.text())
        
        data = {'services' : services, 'relationships' : relationships, 'conditionals' : []}
        dataStr = json.dumps(data)

        

        recipesFolder = os.getcwd() + r'/backend/apps'
        name = QFileDialog.getSaveFileName(self, 'Save File', directory=recipesFolder, filter='Text files (*.txt)')
        filePath = name[0]

        file = open(filePath, 'w')
        file.write(dataStr)
        file.close()

        # Reset table
        self.existingServicesTable.clearContents()
        self.existingRelationshipsTable.clearContents()
        self.existingServicesTable.setRowCount(0)
        self.existingRelationshipsTable.setRowCount(0)

        self.onClick_refresh() # Update available recipes tab


    def createEditTab(self):
        # Services present on network
        networkServicesTable = QTableWidget(self.createRecipe)
        networkServicesTable.setColumnCount(1)
        networkServicesTable.setHorizontalHeaderLabels(['Services on Network'])
        networkServicesTable.setSelectionMode(QTableWidget.SingleSelection)
        networkServicesTable.itemDoubleClicked.connect(self.addServiceToApp) # Double click service to add
        # servicesTable.selectionModel().selectionChanged.connect(self.selectedService)
        networkServicesTable.setObjectName('networkServices')
        networkServicesTable.setRowCount(0)
        networkServicesTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers) 
        header = networkServicesTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.editRecipeLayoutRow.addWidget(networkServicesTable)

        # Relationships present on network
        networkRelationshipsTable = QTableWidget(self.createRecipe)
        networkRelationshipsTable.setColumnCount(1)
        networkRelationshipsTable.setHorizontalHeaderLabels(['Relationships on Network'])
        networkRelationshipsTable.setSelectionMode(QTableWidget.SingleSelection)
        networkRelationshipsTable.itemDoubleClicked.connect(self.addRelationshipToApp) # Double click service to add
        # servicesTable.selectionModel().selectionChanged.connect(self.selectedService)
        networkRelationshipsTable.setObjectName('networkRelationships')
        networkRelationshipsTable.setRowCount(0)
        networkRelationshipsTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers) 
        header = networkRelationshipsTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.editRecipeLayoutRow.addWidget(networkRelationshipsTable)
        
        # App Services Table
        self.existingServicesTable = QTableWidget(self.createRecipe)
        self.existingServicesTable.setColumnCount(1)
        self.existingServicesTable.setHorizontalHeaderLabels(['App Services'])
        self.existingServicesTable.setSelectionMode(QTableWidget.SingleSelection)
        # existingServicesTable.itemDoubleClicked.connect(self.selectedService) # Double click service to add
        # servicesTable.selectionModel().selectionChanged.connect(self.selectedService)
        self.existingServicesTable.setObjectName('AppServices')
        self.existingServicesTable.setRowCount(0)
        self.existingServicesTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.existingServicesTable.itemDoubleClicked.connect(self.removeServiceFromApp)
        header = self.existingServicesTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch) 
        self.editRecipeLayoutRow.addWidget(self.existingServicesTable)

        # App relationships table
        self.existingRelationshipsTable = QTableWidget(self.createRecipe)
        self.existingRelationshipsTable.setColumnCount(1)
        self.existingRelationshipsTable.setHorizontalHeaderLabels(['App Relationships'])
        self.existingRelationshipsTable.setSelectionMode(QTableWidget.SingleSelection)
        self.existingRelationshipsTable.setObjectName('AppRelationships')
        self.existingRelationshipsTable.setRowCount(0) 
        self.existingRelationshipsTable.itemDoubleClicked.connect(self.removeRelationshipFromApp)
        header = self.existingRelationshipsTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.existingRelationshipsTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.editRecipeLayoutRow.addWidget(self.existingRelationshipsTable)

        # Open existing file
        openButton = QPushButton('Open', self.editRecipe)
        openButton.clicked.connect(self.onClick_open)
        self.editRecipeLayoutRow.addWidget(openButton)

        saveButton = QPushButton('Save', self.editRecipe)
        saveButton.clicked.connect(self.onClick_save)
        self.editRecipeLayoutRow.addWidget(saveButton)
        


class CallsWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str, str, str, str)

    def run(self):
        currentRow = Globals.selectedAppRow
        currentColumn = Globals.selectedAppColumn
        currentSelectedAppName = Globals.recipeTable.item(currentRow, currentColumn).text()
        appObject = Globals.allApps[currentSelectedAppName]
        print(f"Selected App: {appObject}")
        appObject.run()
    


# Current code contains finalized code necessary for reading in current state of network
class Worker(QtCore.QObject):
    addThingSignal = QtCore.pyqtSignal(str, str, list)
    addServicesSignal = QtCore.pyqtSignal(str, str, list)
    addRelationshipSignal = QtCore.pyqtSignal(str, str, str, str)
    addUnboundedRelationshipSignal = QtCore.pyqtSignal(str, str, str, str)
    addRecipeSignal = QtCore.pyqtSignal(str, list, list, list)
    addCreateRecipeSignal = QtCore.pyqtSignal()
    addServiceRowSignal = QtCore.pyqtSignal(str)
    addRelationshipRowSignal = QtCore.pyqtSignal(str)
    addEditRecipeSignal = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    parser = Parser()
    def run(self):

        #Before while true loop, set up recipe tab
        self.addRecipeSignal.emit('Hello', ['hello', 'world'], [], [])
        self.addCreateRecipeSignal.emit()
        self.addEditRecipeSignal.emit()
    

        #Assign this instance of worker to parser to be able to access signal methods
        Parser.guiInstance = self
        Globals.guiInstance = self

        #QtCore.QThread.sleep(5)
        '''----------------------Open Socket----------------------'''
        multicast_group = '232.1.1.1'
        server_address = ('', 1235)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.bind(server_address)
       

        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        '''----------------------Loop to read in tweets----------------------'''

        while True:
            data, address = sock.recvfrom(1024)
            decode = data.decode()

            # Update data structures within each class's variables
            Service.allThings = Globals.allThings
            Relationship.allRelationships = Globals.allRelationships
            Relationship.allServices = Globals.allServices
            App.allRelationships = Globals.allRelationships
            App.allServices = Globals.allServices
            App.allThings = Globals.allThings
            App.allUnlinkedRelationships = Globals.allUnboundedRelationships

            json_data = json.loads(data)

            if json_data["Tweet Type"] == "Service":
                type(self).parser.parseServiceTweet(json_data, address)

            elif json_data["Tweet Type"] == 'Relationship':
                type(self).parser.parseRelationshipTweet(json_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec())


import json
import os
from backend.globals import Globals
development_mode = 0

# App class 

class App:
    allServices = {}
    allThings = {} 
    allRelationships = {}
    allUnlinkedRelationships = {}
    def __init__(self, name, appServices, appRelationships, appConditionals): # Might change it so this class inherits from parser to access all the necessary data structures
        self.name = name
        self.services = appServices
        self.relationships = appRelationships
        self.conditionals = appConditionals
        self.srvToRel = {}
        self.results = {}
        self.control = {}
        self.drive = {}
        self.support = {}
        self.extend = {}
        self.contest = {}
        self.interfere = {}
        self.interactions = ''
    
    def __str__(self):
        return f"Name: {self.name}, Services: {self.services}, Relationships: {self.relationships}, Conditionals: {self.conditionals}"
    

    def run(self):
        Globals.runThread = True
        if self.verifyServices() and self.verifyRelationships() and self.verifyConditionals():
            Globals.callsInstance.progress.emit('App', self.name, 'First', 'No Output')
            for service in self.services: # Run all services
                if not Globals.runThread:
                    Globals.callsInstance.progress.emit('Message', 'No name', 'Stopped', 'No output')
                    Globals.callsInstance.finished.emit()
                    return
                Globals.callsInstance.progress.emit('Service', service, 'Running', 'No output')
                response = Globals.allServices[service].invoke()
                Globals.callsInstance.progress.emit('Service', service, 'Done', response)
                if service in self.results: 
                    self.results[service].append(response)
                else:
                    self.results[service] = [response]      

            for relationship in self.relationships: # Run all relationships
                if not Globals.runThread:
                    Globals.callsInstance.progress.emit('Message', 'No name', 'Stopped', 'No output')
                    Globals.callsInstance.finished.emit()
                    return 
                Globals.callsInstance.progress.emit('Relationship', relationship, 'Running', 'No output')
                response = Globals.allRelationships[relationship].invoke()
                Globals.callsInstance.progress.emit('Relationship', relationship, 'Done', response)

            for conditional in self.conditionals: # Run all conditionals
                if not Globals.runThread:
                    Globals.callsInstance.progress.emit('Message', 'No name', 'Stopped', 'No output')
                    Globals.callsInstance.finished.emit()
                    return
                condition = conditional["if"]
                execution = conditional["then"] 
                
                if condition in Globals.allServices: 
                    Globals.allServices[condition].invoke()
                elif condition in Globals.allRelationships:
                    Globals.allRelationships[condition].invoke()
                
                if execution in Globals.allServices: 
                    Globals.allServices[execution].invoke()
                elif execution in Globals.allRelationships:
                    Globals.allRelationships[execution].invoke()

            Globals.callsInstance.progress.emit('Finished', 'None ', 'Finished', 'No output')
        else:
            print("Could not run selected app!")
    
        # Close thread when done
        Globals.callsInstance.finished.emit()
        print("Done running app!")
    
   
        
    def verifyServices(self):
        for service in self.services:
            if service not in Globals.allServices:
                Globals.callsInstance.progress.emit('Service', service, 'Failed', 'No Output')
                print("Compile Error: Service not present on network!")
                return False
            
        
        print("All services present!")
        return True
    
    def verifyRelationships(self):
        for relationship in self.relationships:
            if relationship not in Globals.allRelationships:
                Globals.callsInstance.progress.emit('Relationship', relationship, 'Failed', 'No Output')
                print("Compile Error: Relationship not present on network!")
                return False

        print("All relationships present!")
        return True
    
    def verifyConditionals(self):
        for conditional in self.conditionals:
            condition = conditional["if"]
            execution = conditional["then"]

            if condition not in Globals.allServices and condition not in Globals.allRelationships:
                print("Compile Error: Service or Relationship in conditional not found on network!")
                return False
            if execution not in Globals.allServices and execution not in Globals.allRelationships:
                print("Compile Error: Service or Relationship in conditional not found on network!")
                return False

        print("All conditional's elements present!")
        return True


    def change_mode(self):
        global development_mode
        if development_mode == 0:
            development_mode = 1
            print('App Manager is in Developement Mode')
        else:
            development_mode = 0
            print('App Manager is not in Developement Mode')    
    

    def save(self, fileName , appServices):#should add appRelationships
        
        if development_mode == 0:
            print('Error , App saving is possible only in Developement Mode')
        else: 
            directory = os.path.dirname(__file__)
            filePath =  directory + r'/apps/' + fileName # Change to any 

            json_dict = {'services': appServices}#should add appRelationships
            jsonStr = json.dumps(json_dict) #converting to json format

            file = open(filePath, 'w')
            file.write(jsonStr)
            file.close() 
            print("file is saved")

    def print_results(self):
        print(self.results)



    

        
        
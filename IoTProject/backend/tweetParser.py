from backend.atlasObjects import Service
from backend.atlasObjects import Relationship
from backend.atlasObjects import Thing
from backend.globals import Globals


#Parser class to parse incoming tweets

class Parser:
    guiInstance = None
    def __init__(self):
        self.allServices = {}
        self.allThings = {}
        self.allUnbounded = {}
        self.allUnboundedRelationships = {}
        self.allRelationships = {}
        self.allApps = {}

    # Parse Tweets of type 'Service'
    def parseServiceTweet(self, json_data, address):
        thing = None
        # add Thing ID, Service name to thing dict
        if not (json_data["Thing ID"] in self.allThings):
            thing = Thing(json_data["Thing ID"], address)
            self.allThings[json_data["Thing ID"]] = thing
            Globals.allThings[json_data["Thing ID"]] = thing

            # Add thing to GUI
            type(self).guiInstance.addThingSignal.emit(thing.name, thing.getHostname(), list(thing.services.values()))
        else:
            thing = self.allThings[json_data["Thing ID"]]

        if not (json_data["Name"] in self.allServices):
            temp = Service(json_data["Name"], json_data["Thing ID"])
            self.allServices[json_data["Name"]] = temp
            Globals.allServices[json_data["Name"]] = temp
            thing.services[json_data["Name"]] = temp

            # Add service to GUI
            type(self).guiInstance.addServicesSignal.emit(temp.name, temp.thing, [])

    # Parse Tweets of type 'Relationship'
    def parseRelationshipTweet(self, json_data):
        if not(json_data["Name"] in self.allRelationships):
            foundService1 = False
            foundService2 = False
            linked1 = True
            first_service = ""
            if 'unbounded' in json_data["FS name"]:
                first_service =  None 
                linked1 = False
                foundService1 = True
            elif json_data["FS name"] in self.allServices:
                foundService1 = True
                first_service =  self.allServices[json_data["FS name"]]

            second_service = ""
            linked2 = True
            if 'unbounded' in json_data["SS name"]:
                second_service = None 
                linked2 = False
                foundService2 = True
            elif json_data["SS name"] in self.allServices:
                second_service =  self.allServices[json_data["SS name"]]
                foundService2 = True
            # Used to fix an issue when a service is found first int the relationship instead of the Service tweet, causing a relationship with a missing service object
            if foundService1 and foundService2:
                relationship = Relationship(first_service, second_service, json_data["Name"], json_data["Type"], linked1, linked2)
                if 'unbounded' not in json_data["FS name"] and 'unbounded' not in json_data["SS name"]:
                    self.allRelationships[json_data["Name"]] = relationship
                    Globals.allRelationships[json_data["Name"]] = relationship

                    # Add relationship to GUI:
                    type(self).guiInstance.addRelationshipSignal.emit(relationship.name, relationship.service1.name, relationship.service2.name, relationship.type)
                    (first_service.relationships).append(second_service)
                    (second_service.relationships).append(first_service)
                else:
                    if json_data["Name"] not in Globals.allUnboundedRelationships:
                        Globals.allUnboundedRelationships[json_data["Name"]] = relationship
                        self.allUnboundedRelationships[json_data["Name"]] = relationship
                        service1Name = "Unbounded" if not first_service else relationship.service1.name # prevents the emit from acessing a 'None' Type
                        service2Name = "Unbounded" if not second_service else relationship.service2.name
                        # Add unbounded relationship to GUI:
                        type(self).guiInstance.addUnboundedRelationshipSignal.emit(relationship.name, service1Name, service2Name, relationship.type)



        
        

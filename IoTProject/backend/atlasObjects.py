import socket 
import struct 
import sys
import json
import random
import threading
#from terminalColorText import bcolors
from backend.globals import Globals
#from globals import Globals 
class Service:
    # allThings = {}
    def __init__(self, name, thing):
        self.name = name
        self.thing = thing
        self.active = False # service starts off as inactive
        self.relationships = []

    def __str__(self):
        return f"Service Name: {self.name}, Thing Name: {self.thing}"
        
    def invoke(self):
        pi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect host,port
        hostname = Globals.allThings[self.thing].getHostname()
        port = Globals.allThings[self.thing].getPort()

        pi.connect((hostname, 6668))
        print(f"Executing Service: {self.name}")

        active = True # service turn to be active
        # create send tweet
        call = "{ \"Tweet Type\" : \"Service Call\",\"Thing ID\" : \"" + self.thing + "\",\"Space ID\" : \"RaspberriesVSS\",\"Service Name\" :\"" + self.name +"\",\"Service Inputs\" : \"()\" }"

        # send request
        pi.sendall(call.encode())

        # wait and print for response from PI
        resp = pi.recv(1024)
        active = False
        decoded = resp.decode()
        resAsJSON = json.loads(decoded)

        # close PI socket
        pi.close()
        return str(resAsJSON["Service Result"])
    
class Thing:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.services = {}
    def __str__(self):
        return f"Thing ID: {self.name}, Thing IP: {self.ip[0]}"
    def getHostname(self):
        return self.ip[0]
    def getPort(self):
        return self.ip[1]

class Relationship:
    def __init__(self, service1, service2, name, type, linked1, linked2):
        self.service1 = service1
        self.service2 = service2
        self.linkedService1 = linked1 # False if (isinstance(service1, Unbounded) and service1.linked == False) else True
        self.linkedService2 = linked2 # False if (isinstance(service2, Unbounded) and service2.linked == False) else True
        self.invokable = self.linkedService1 and self.linkedService2
        self.type = type
        self.name = name
    
    def __str__(self):
        return f"Name: {self.name}, Service 1: [{self.service1}], Service 2: [{self.service2}], Type: {self.type}, Invokable: {self.invokable}"
    

    def invoke_Control(self):
        print("invoking control relationship") # if service1 then service2
        self.service1.invoke()
        #check if service 1 finished properly, if not break
        return self.service2.invoke()


    def invoke_Drive(self):    
        print("invoking Drive relationship") # use service1 to do service2
        return self.service1.invoke()
        #check if service 1 finished properly, if not break
        # self.service2.invoke()

    def invoke_Support(self):
        print("invoking support relationship") # before service1 check service2
        #check if service 2 already invoked, if not invoke
        if self.service2.active == False:
            return self.service2.invoke()
        # check if service 2 finished properly, if not break
        return self.service1.invoke()

    def invoke_Extend(self):
        print("invoking extend relationship") # do service1 while doing service2 
        # can only occur if on different things
        if self.service1.thing == self.service2.thing:
            print("cannot run both services because they belong to the same thing")
            return
        results = []
        # invoke the two services in different threads
        x = threading.Thread(target=self.invoke_thread, args=(self.service1, results, 0,))
        y = threading.Thread(target=self.invoke_thread, args=(self.service2, results, 1,))
        x.start()
        y.start()
        x.join()
        y.join()
        return f"Service 1 results: {results[0]}, Service 2 results: {results[1]}"

    def invoke_thread(self, service, results, index):
        results[index] = service.invoke()

    def invoke_Contest(self): # Randomize
        print("invoking contest relationship") # X---prefer service1 over doing service2---X
        # select one relationship over another based on certain criteria - RANDOM
        services = [self.service1, self.service2]
        return random.choice(services).invoke()


    def invoke_Interfere(self):
        print("invoking interfere relationship")# do not do service1 if doing service2
        if self.service2.active == False:
            return self.service1.invoke() 
        return "No output"
        

    def invoke(self):
        if not self.linkedService1 and self.linkedService2:
            print("Relationship cannot be invoked due to both services being unbounded")
        elif not self.linkedService1:
            print("Relationship cannot be invoked due to unbounded service 1")
        elif not self.linkedService2:
            print("Relationship cannot be invoked due to unbounded service 2")
        else:
            if self.type == 'control':
                return self.invoke_Control()
            elif self.type == 'drive': 
                return self.invoke_Drive()   
            elif self.type == 'support':
                return self.invoke_Support()
            elif self.type == 'extend':
                return self.invoke_Extend()
            elif self.type == 'contest':
                return self.invoke_Contest()
            elif self.type == 'interfere':  
                return self.invoke_Interfere()      

        
    def linkService1(self, service1):
        if not self.linkedService1:
            self.linkedService1 = True
            self.service1 = service1 # Assign Service object to previous None 
            # self.service1.service = service1.name
            # self.service1.linked = True
            if self.linkedService1 and self.linkedService2:
                self.invokable = True
                Globals.allRelationships[self.name] = self # Add self to all relationships
        else:
            print('Service 1 is already linked!')
    
    def linkService2(self, service2):
        if not self.linkedService2:
            self.linkedService2 = True
            self.service2 = service2 
            # self.service2.service = service2.name
            # self.service2.linked = True
            if self.linkedService1 and self.linkedService2:
                Globals.allRelationships[self.name] = self
                self.invokable = True
        else:
            print('Service 2 is already linked!')


    def bind(self,service):
        if not self.linkedService1:
            print("unbounded service 1")
            self.service1 = service
        elif not self.linkedService2:
            print("unbounded service 2")
            self.service2 = service

        (self.service1.relationships).append(self.service2)
        (self.service2.relationships).append(self.service1)

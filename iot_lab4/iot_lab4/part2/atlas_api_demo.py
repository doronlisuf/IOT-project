import socket
import json

def call_service(service_name):
    # Set up the socket connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print(host,":", port)
    
    s.connect((host,port))
    # invoke corresponding service
    if service_name == 'led':
        call1 = b'{"Tweet Type" : "Service call", "Thing ID" : "RaspberriesThing","Space ID" : "RaspberriesVSS","Service Name" : "led","Service Inputs" : "()" }'
    if service_name == 'button':
        call1 = b'{"Tweet Type" : "Service call", "Thing ID" : "RaspberriesThing","Space ID" : "RaspberriesVSS","Service Name" : "button","Service Inputs" : "()" }'
    if service_name == 'buzzer':
        call1 = b'{"Tweet Type" : "Service call", "Thing ID" : "RaspberriesThing","Space ID" : "RaspberriesVSS","Service Name" : "buzzer","Service Inputs" : "()" }'
    if service_name == 'distance':
        call1 = b'{"Tweet Type" : "Service call", "Thing ID" : "RaspberriesThing","Space ID" : "RaspberriesVSS","Service Name" : "distance","Service Inputs" : "()" }'

    s.sendall(call1)

    # wait for response from the pi 
    data = s.recv(1024)
    
    # decode the recieved data
    data_decode = data.decode()
    
    # convert the recieved data to json object
    json_data = json.loads(data_decode)
    
    # close the connection
    s.close()
    
    # output the recieved data
    print('Data recieved from',service_name,"service:", json_data["Service Result"])
    print('Service complete.\n')

# set host to Atlas multicast ip
host = "192.168.1.8"

# configure the port
port = 6668

print('\nWelcome to the Atlas demo!\n\nAvailable services:\n\tled\n\tdistance\n\tbuzzer\n\tbutton\ntype "exit" to quit program\n')

while(1):
    # get selection
    print('Enter your selection')
    service_name = input()
    print('\nYou chose:',service_name)
    
    # complete action based on selection
    if service_name == 'exit':
        print('Demo is complete. Exitting Demo.')
        break
    elif service_name != 'led' and service_name != 'distance' and service_name != 'buzzer' and service_name != 'button': 
        print(service_name, 'is not currently available')
    else:
        call_service(service_name)
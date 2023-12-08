from socket import *
import requests

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)

serverAddress = ('192.168.204.54', serverPort)

serverSocket.bind(serverAddress)
print("The server is ready")

# API-endepunkt til at tjekke koden
api_url_user = 'https://vendingmachinepihat.azurewebsites.net/api/users'
api_url_accounting = 'https://vendingmachinepihat.azurewebsites.net/api/accountings'
    

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    received_password = message.decode()
    print({'password': received_password}) 

    response = requests.get(api_url_user + '/' + received_password + '?password=' + received_password)

    if response.status_code == 200:
        serverSocket.sendto("OK".encode(), clientAddress)
        user_id = response.json()['id']
        todo = {"userId": user_id , "type": "M&M", "amount": 10}
        responsePost = requests.post(api_url_accounting, json=todo)
        if responsePost.status_code == 201:
           print (responsePost.json())
           serverSocket.sendto("OK CREATED".encode(), clientAddress)   
        else:
           print(f"Fejl ved at sende data til API. Statuskode: {responsePost.status_code}")
           print(responsePost.text)  # Udskriv fejltekst fra serveren
           serverSocket.sendto("FEJL VED POST".encode(), clientAddress)    
    elif response.status_code == 500:
          serverSocket.sendto("FEJL".encode(), clientAddress)
          serverSocket.sendto("PRØV IGEN".encode(), clientAddress)          


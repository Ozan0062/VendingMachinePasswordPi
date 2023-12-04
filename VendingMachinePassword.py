import pyodbc
from pynput.keyboard import Key, Listener
from socket import *
import requests

api_url = 'https://vendingmachinepihat.azurewebsites.net/api/accountings'

# Funktion til at hente alle koder fra SQL Server-databasen
def get_all_passwords_from_database():
    server = 'mssql4.unoeuro.com'
    database = 'ozanhs_dk_db_vending_machine'
    username = 'ozanhs_dk'
    password = 'GcB6m5g4awRnbE29tyzp'
    driver = 'ODBC Driver 17 for SQL Server'  # Brug den korrekte driver

    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};'

    connection = None
    cursor = None

    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Eksempel: Hent alle koder fra en tabel (tilpas dette til din database)
        cursor.execute("SELECT Password FROM [User]")
        rows = cursor.fetchall()

        return [row.Password for row in rows]

    except pyodbc.Error as e:
        print(f"Databasefejl: {e}")
        print(f"SQL State: {e.sqlstate}")  # Tilføj denne linje for mere detaljeret SQL State information
        return None  # Returner None i tilfælde af fejl

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_id_by_password(password):
    server = 'mssql4.unoeuro.com'
    database = 'ozanhs_dk_db_vending_machine'
    username = 'ozanhs_dk'
    password_db = 'GcB6m5g4awRnbE29tyzp'
    driver = 'ODBC Driver 17 for SQL Server'  # Brug den korrekte driver

    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password_db};'

    connection = None
    cursor = None

    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Søg efter brugerens ID baseret på adgangskoden i databasen
        cursor.execute("SELECT Id FROM [User] WHERE Password = ?", password)
        row = cursor.fetchone()

        if row:
            user_id = row[0]  # Brug det korrekte indeks for bruger-ID
            return user_id
        else:
            return None

    except pyodbc.Error as e:
        print(f"Databasefejl: {e}")
        print(f"SQL State: {e.sqlstate}")  # Tilføj denne linje for mere detaljeret SQL State information
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

   

# Eksempel på brug
all_passwords = get_all_passwords_from_database()
if all_passwords is not None:
    print("Hentede passwords fra databasen:")
    for password in all_passwords:
        print(password)
else:
    print("Fejl ved hentning af koder fra databasen.")

# Start authentication process
def main():
    global all_passwords

    # Hent alle koder fra SQL Server-databasen
    all_passwords = get_all_passwords_from_database()

    if all_passwords is not None:
        print("Indtast dit password ved at bruge piltasterne (op, ned, venstre, højre) som input.")
    else:
        print("Fejl ved hentning af koder fra databasen.")

    with Listener(on_release=on_key_release) as listener:
        listener.join()

# Resten af din kode forbliver uændret
# ...

# Definer det forventede kodeord
expected_password = "UUUUUUUU"

entered_chars = 0
user_password = ""

def on_key_release(key):
    global entered_chars, user_password, expected_password
    if key == Key.right:
        user_password += "R"
        entered_chars += 1
        print("Right key clicked")
    elif key == Key.left:
        user_password += "L"
        entered_chars += 1
        print("Left key clicked")
    elif key == Key.up:
        user_password += "U"
        entered_chars += 1
        print("Up key clicked")
    elif key == Key.down:
        user_password += "D"
        entered_chars += 1
        print("Down key clicked")
    elif key == Key.enter:
        print("Middle key clicked")
        user_password += "M"
        entered_chars += 1
    if entered_chars == len(expected_password):
        authenticate_user()

def authenticate_user():
    global user_password

    # Få brugerens indtastede adgangskode
    entered_password = user_password

    # Få brugerens ID ved at kalde get_id_by_password
    user_id = get_id_by_password(entered_password)

    if user_id is not None:
        print(f"Adgang godkendt! Bruger-ID for det indtastede password er: {user_id}")

        # Opret data til API-anmodning
        todo = {"userId": user_id, "type": "M&M", "amount": 10}

        try:
            # Send data til API
            response = requests.post(api_url, json=todo)
            response.raise_for_status()  # Kaster en HTTPError, hvis responsstatus er en fejlkode (4xx eller 5xx)

            # Tjek svar fra API
            if response.status_code == 201:
                print(f"Data sendt til API med succes. API-svar: {response.json()}")
            else:
                print(f"Fejl ved at sende data til API. Statuskode: {response.status_code}")
                print(response.text)  # Udskriv fejltekst fra serveren

        except requests.exceptions.RequestException as e:
            print(f"Anmodning fejlede: {e}")

    else:
        print("Adgang nægtet! Det indtastede password er forkert.")

    # Nulstil variabler
    user_password = ""
    global entered_chars
    entered_chars = 0

# Kør hovedfunktionen
if __name__ == "__main__":
    main()


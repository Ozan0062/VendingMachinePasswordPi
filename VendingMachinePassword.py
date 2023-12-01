import pyodbc
from pynput.keyboard import Key, Listener

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
    # while entered_chars < len(expected_password):
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
    # else: 
    #     print("Invalid password")    

def authenticate_user():
    global user_password, all_passwords

    if user_password in all_passwords:
        print("Adgang godkendt! Det indtastede password er korrekt.")
        print(f"Det indtastede password er: {user_password}")
    else:
        print("Adgang nægtet! Det indtastede password er forkert.")

    # Nulstil variabler
    user_password = ""
    global entered_chars
    entered_chars = 0
    # password.lenght = 8

# Kør hovedfunktionen
if __name__ == "__main__":
    main()

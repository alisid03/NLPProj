import os
from dotenv import load_dotenv
from openai import OpenAI
import mysql.connector 
import json
import sqlite3
import vosk
import pyaudio
import json

load_dotenv()

# Setup speech to text model
model = vosk.Model(lang="en-us")
rec = vosk.KaldiRecognizer(model, 16000)

# Set up API keys (Replace with actual keys)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
cache = []

def speech_to_text():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8192)


    print("Listening for speech. Say 'Done' to stop.")
    text = ""
    # Start streaming and recognize speech
    while True:
        data = stream.read(4096)#read in chunks of 4096 bytes
        if rec.AcceptWaveform(data):#accept waveform of input voice
            # Parse the JSON result and get the recognized text
            result = json.loads(rec.Result())
            recognized_text = result['text']
            
            # Write recognized text to the file
            print("You: " + recognized_text)
            
            # Check for the termination keyword
            if "done" in recognized_text.lower():
                print("Done keyword detected. Stopping...")
                print("Chatbot: Is this good, or would you like to try again?")
                answer = input("You (y/n): ")
                if answer == "y" :
                    break
            else:
                text = recognized_text

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate the PyAudio object
    p.terminate()
    return text

def chat_with_gpt(user_input):
    """Interacts with ChatGPT to process user queries."""
    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[{"role": "user", "content": user_input}])
    return response.choices[0].message.content

def extract_flight_details(user_input):
    """Uses ChatGPT to extract origin, destination, and date from user input."""
    prompt = f"""
    Extract the departure city, destination city, and travel date range from the following query:
    Query: "{user_input}"
    Provide the response in a format like this, using the nearest airport to that city:
    {{"origin": "NYC", "destination": "LAX", "date_start": "2024-03-10", "date_end: "NA"}}
    """
    response = chat_with_gpt(prompt)
    try:
        jsonResponse = json.loads(response)
        return jsonResponse
    except Exception as e:
        return None

def get_flights(origin, destination, start_date=None, end_date=None):
    conn = sqlite3.connect("CS6320.db")
    cursor = conn.cursor()

    query = "SELECT * FROM flights WHERE origin = ? AND destination = ?"
    params = [origin, destination]

    if start_date != "NA" and end_date != "NA" :
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    elif start_date != "NA" :
        query += " AND date >= ?"
        params.append(start_date)
    elif end_date != "NA" :
        query += " AND date <= ?"
        params.append(end_date)

    cursor.execute(query, params)
    results = cursor.fetchall()
    cache.append(results)
    conn.close()
    return results

def flight_chatbot(user_input):
    """Main chatbot function that handles user queries."""
    flight_details = extract_flight_details(user_input)
    print(flight_details)
    if flight_details:
        return get_flights(flight_details["origin"], flight_details["destination"], flight_details["date_start"], flight_details["date_end"])
    else:
        #return chat_with_gpt(user_input)  # Fallback to ChatGPT for general queries
        return "invalid"


def save_booking(name, address, flight):
    conn = sqlite3.connect("CS6320.db")
    cursor = conn.cursor()

    if flight:
        flight_id = flight[0]

        # Insert booking into the bookings table
        cursor.execute("""
        INSERT INTO bookings (name, address, flight_id) VALUES (?, ?, ?)
        """, (name, address, flight_id))

        conn.commit()
        print("Booking inserted successfully.")
    else:
        print("No matching flight found.")

    conn.close()

def view_booking():
    conn = sqlite3.connect("CS6320.db")
    cursor = conn.cursor()
    print(f"Chatbot: Please enter your name")
    user_query_name = input("You: ")
    print(f"Chatbot: Please enter your address")
    user_query_address = input("You: ")
    cursor.execute("""
    SELECT * FROM bookings WHERE name=? AND address=?
                   """, [user_query_name, user_query_address])
    results = cursor.fetchall()
    return results    

def book_flight():
    print(f"Chatbot: here are your options, if you want to book a flight type in the number")
    options = cache[0]
    i = 0
    for flight in options:
        print(f"{i} : {flight}")
        i += 1
    user_query = input("You: ")
    print(f"Chatbot: Please enter your name")
    user_query_name = input("You: ")
    print(f"Chatbot: Please enter your address")
    user_query_address = input("You: ")
    #TODO SQL Statement to insert into bookings
    save_booking(user_query_name, user_query_address, options[int(user_query)])
    print(f"Booked flight for {user_query_name} {user_query_address} for the booking {options[int(user_query)]}")

def detect_intent(user_input):
    prompt = f"""
    You are an intent classifier for a flight booking chatbot. Categorize the user's input into one of the following intents:
    - search_flight
    - view_bookings
    - book_flight
    - speech
    - exit

    With the output with just the intent

    Input: "{user_input}"
    """
    intent = chat_with_gpt(prompt).strip().lower()
    print(intent)
    return intent

# Example usage
if __name__ == "__main__":
    print(f"Chatbot: Welcome to the airflight booking chatbot. Please enter where you would like to travel from and to and we will find all the best deals for you.\n\nIf you would like to see your current bookings type 'view bookings'")
    while True:
        user_query = input("You: ")
        intent = detect_intent(user_query)

        if intent == "view_bookings":
            flights = view_booking()
            for flight in flights:
                print(flight)
            continue
        if intent == "book_flight":
            book_flight()
            break
        if intent == "exit":
            print("Chatbot: Goodbye!")
            break
        if intent == "speech":
            user_query = speech_to_text()
        response = flight_chatbot(user_query)
        print(f"Chatbot: {response}\nIf you like any of these flights, type book")



def create_and_populate_flights_table():
    conn = sqlite3.connect("CS6320.db")  # SQLite database file
    cursor = conn.cursor()

    """
    # Create flights tabe
    cursor.execute(
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        date TEXT NOT NULL,
        pricing REAL NOT NULL,
        class TEXT NOT NULL,
        company TEXT NOT NULL
    ))
    """

    # Create bookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_number INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        flight_id INTEGER NOT NULL,
        FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

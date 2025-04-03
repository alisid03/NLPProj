from openai import OpenAI
import mysql.connector 
import json

# Set up API keys (Replace with actual keys)
OPENAI_API_KEY = ""
client = OpenAI(api_key=OPENAI_API_KEY)
cache = []

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
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database=""
    )
    cursor = conn.cursor()

    query = """
    SELECT * FROM flights 
    WHERE origin = %s AND destination = %s
    """
    params = [origin, destination]

    if start_date != "NA" and end_date != "NA":
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    elif start_date != "NA":
        query += " AND date >= %s"
        params.append(start_date)
    elif end_date != "NA":
        query += " AND date <= %s"
        params.append(end_date)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    cache.append(results)
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
    print(f"Booked flight for {user_query_name} {user_query_address} for the booking {options[int(user_query)]}")

# Example usage
if __name__ == "__main__":
    while True:
        user_query = input("You: ")
        if user_query.lower() in ["book"] and len(cache) > 0:
            print(len(cache))
            book_flight()
            break
        if user_query.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye!")
            break
        response = flight_chatbot(user_query)
        print(f"Chatbot: {response}\nIf you like any of these flights, type book")
        print(cache)

import sqlite3
import random
import spacy
import dateparser
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

nlp = spacy.load("en_core_web_sm")
conn = sqlite3.connect("CS6320.db")
cursor = conn.cursor()

intents = {
    "search": [
        "search flights", "get me a flight", "I want to fly",
        "show me available flights", "find flights", "I need to book a flight",
        "what flights are there from New York to LA", "find me something from Atlanta"
    ],
    "book": [
        "book a ticket", "I want to book", "reserve this seat",
        "book flight ID 2", "I want to confirm my flight"
    ],
    "view": [
        "show my bookings", "view my reservations", "what flights did I book",
        "my tickets", "show my confirmed bookings", "view booking"
    ],
    "smalltalk": [
        "hi", "hello", "how are you", "good morning", "hey there",
        "what's up", "yo", "hello assistant"
    ],
    "exit": [
        "bye", "exit", "quit", "leave", "peace out", "see you later", "I'm done", "close the chat"
    ]
}

examples, labels = [], []
for label, phrases in intents.items():
    examples.extend(phrases)
    labels.extend([label] * len(phrases))

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(examples)
classifier = LogisticRegression()
classifier.fit(X, labels)

def get_intent(text):
    return classifier.predict(vectorizer.transform([text]))[0]

valid_cities = {
    "new york": "NYC", "los angeles": "LAX", "chicago": "CHI",
    "atlanta": "ATL", "dallas": "DFW", "houston": "HOU"
}

def normalize_city_name(input_text):
    city_lower = input_text.lower().strip()
    match = difflib.get_close_matches(city_lower, valid_cities.keys(), n=1, cutoff=0.8)
    if match:
        return valid_cities[match[0]], match[0].title()
    return None, None

def extract_entities(text):
    text_lower = text.lower()
    origin, destination = None, None
    mentioned = []

    for city in valid_cities:
        if city in text_lower:
            mentioned.append((city, valid_cities[city]))

    for city, code in mentioned:
        if f"from {city}" in text_lower:
            origin = code
        if f"to {city}" in text_lower:
            destination = code

    if not origin and not destination:
        if len(mentioned) == 1:
            destination = mentioned[0][1]
        elif len(mentioned) >= 2:
            origin = mentioned[0][1]
            destination = mentioned[1][1]

    for _, code in mentioned:
        if not origin and code != destination:
            origin = code
        elif not destination and code != origin:
            destination = code

    doc = nlp(text)
    airline = next((ent.text for ent in doc.ents if ent.label_ == "ORG"), None)
    date_entity = next((ent.text for ent in doc.ents if ent.label_ == "DATE"), None)
    parsed_date = dateparser.parse(date_entity) if date_entity else None

    return origin, destination, airline, parsed_date

def search_flights(origin, destination, airline=None, seat_class=None, date=None):
    if not origin or not destination:
        return []

    query = "SELECT * FROM flights WHERE origin = ? AND destination = ?"
    params = [origin, destination]
    if airline:
        query += " AND LOWER(company) LIKE ?"
        params.append(f"%{airline.lower()}%")
    if seat_class:
        query += " AND LOWER(class) LIKE ?"
        params.append(f"%{seat_class.lower()}%")
    if date:
        query += " AND strftime('%m', date) = ? AND strftime('%d', date) = ?"
        params.extend([f"{date.month:02d}", f"{date.day:02d}"])

    cursor.execute(query, params)
    return cursor.fetchall()

def book_flight(name, address, flight_id):
    cursor.execute("INSERT INTO bookings (name, address, flight_id) VALUES (?, ?, ?)", (name, address, flight_id))
    conn.commit()
    return cursor.lastrowid

origin_prompts = [
    "Where are you flying from? (e.g., New York, Atlanta)",
    "Departure city? (e.g., Dallas, Houston)",
    "Please enter your origin city (e.g., New York)",
    "From which city will you depart?"
]
destination_prompts = [
    "Where are you flying to? (e.g., Los Angeles, Chicago)",
    "Destination city? (e.g., Atlanta, Dallas)",
    "Please enter your destination city (e.g., Los Angeles)",
    "To which city are you heading?"
]
date_prompts = [
    "When would you like to fly? (e.g., March 10 or March 10, 2024)",
    "Preferred flight date? (optional)",
    "What date do you plan to travel?",
    "Enter travel date (e.g., April 2nd)"
]

smalltalk_responses = [
    "Hey there! Ready to book your next adventure?",
    "Hi! How can I assist your travel plans today?",
    "Hello! Looking for flights or something else?",
    "Hey! Need help with booking or checking flights?"
]

exit_responses = [
    "Goodbye! Safe travels. ✈️",
    "Catch you later! Hope to see you again soon.",
    "Take care and bon voyage!",
    "Thanks for using the flight bot. 👋"
]

no_flights_responses = [
    "Hmm, I couldn't find any flights with that info. Try changing the date or airline?",
    "No flights matched your search. Maybe try different cities or class?",
    "Oops! Looks like no flights are available. Try adjusting your preferences.",
    "Sorry, nothing came up. Want to search again with fewer filters?"
]

def chatbot():
    print("\n🛫 Welcome to the Flight Booking Chatbot! 🛬")
    print("You can search, book, or view bookings. Type 'exit' to quit.")

    context = {"origin": None, "destination": None, "airline": None, "class": None, "date": None}

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue

        intent = get_intent(user_input)
        origin, destination, airline, parsed_date = extract_entities(user_input)
        context["origin"] = context["origin"] or origin
        context["destination"] = context["destination"] or destination
        context["airline"] = context["airline"] or airline
        context["date"] = context["date"] or parsed_date

        if intent == "exit":
            print("Chatbot:", random.choice(exit_responses))
            break

        elif intent == "smalltalk":
            print("Chatbot:", random.choice(smalltalk_responses))
            continue

        elif intent == "book":
            print("Chatbot:", random.choice([
    "To book a flight, please search for available flights first.",
    "You’ll need to search for flights before booking one. Try typing 'search flights'.",
    "Booking a flight? Let's search for flights first so you can see what's available.",
    "Search first, book after! Try saying 'search flights' to get started."
]))
            continue

        elif intent == "view":
            name = input("Chatbot: Enter your name to view bookings: ")
            cursor.execute("""
                SELECT b.booking_number, f.origin, f.destination, f.date, f.pricing, f.class, f.company
                FROM bookings b JOIN flights f ON b.flight_id = f.id
                WHERE LOWER(b.name) = ?
            """, (name.lower(),))
            bookings = cursor.fetchall()
            if bookings:
                for b in bookings:
                    print(f"📋 Booking #{b[0]}: {b[1]} → {b[2]} on {b[3]} | ${b[4]} | {b[5]} | {b[6]}")
            else:
                print("Chatbot: No bookings found.")
            continue

        elif intent == "search":
            while not context["origin"]:
                origin_input = input("Chatbot: " + random.choice(origin_prompts) + " ")
                code, _ = normalize_city_name(origin_input)
                if code:
                    context["origin"] = code
                else:
                    print("Chatbot: Please enter a valid city name (e.g., New York, Houston).")

            while not context["destination"]:
                dest_input = input("Chatbot: " + random.choice(destination_prompts) + " ")
                code, _ = normalize_city_name(dest_input)
                if code:
                    context["destination"] = code
                else:
                    print("Chatbot: Please enter a valid city name (e.g., Los Angeles, Chicago).")

            if not context["date"]:
                date_input = input("Chatbot: " + random.choice(date_prompts) + " ")
                if date_input.strip():
                    parsed = dateparser.parse(date_input)
                    if parsed:
                        context["date"] = parsed
                    else:
                        print("Chatbot: Couldn't parse that date. Searching without it.")

            if not context["airline"]:
                airline_input = input("Chatbot: Preferred airline? (optional): ")
                context["airline"] = airline_input if airline_input else None

            seat_class = input("Chatbot: Preferred class? (e.g., Economy, Business — optional): ")
            context["class"] = seat_class if seat_class else None

            results = search_flights(
                context["origin"], context["destination"],
                context["airline"], context["class"], context["date"]
            )

            if results:
                print("\nChatbot: ✈️ Flights Found:")
                print("-" * 80)
                for f in results:
                    print(f"🆔 {f[0]} | {f[1]} → {f[2]} | {f[3]} | ${f[4]:.2f} | {f[5]} | {f[6]}")
                print("-" * 80)

                book_now = input("Chatbot: Would you like to book one of these flights? (yes/no): ").strip().lower()
                if book_now in ["yes", "y"]:
                    flight_ids = [str(f[0]) for f in results]
                    while True:
                        chosen = input("Chatbot: Enter the flight ID to book: ")
                        if chosen in flight_ids:
                            name = input("Chatbot: Your full name: ")
                            address = input("Chatbot: Your address: ")
                            booking_id = book_flight(name, address, int(chosen))
                            print(f"Chatbot: Booking confirmed! Your booking number is {booking_id}.")
                            break
                        else:
                            print("Chatbot: Invalid ID. Please select one of the shown flight IDs.")
                else:
                    print("Chatbot: No problem! Let me know if you'd like to search again or view your bookings.")
            else:
                print("Chatbot:", random.choice(no_flights_responses))

            context = {"origin": None, "destination": None, "airline": None, "class": None, "date": None}

        else:
            print("Chatbot: Sorry, I didn’t understand that. You can say things like 'search flights', 'view bookings', or 'check flights'.")

chatbot()
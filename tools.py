from functions import get_ticket_price, get_available_seats, book_ticket, get_user_bookings, create_account, get_flights_exact, get_flights_from_surrounding_city

def get_all_tools():
    return [
        {"type": "function", "function": {
            "name": "get_flights_exact",
            "description": "Find flights given an exact departure city and destination city",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure_city": {"type": "string"},
                    "destination_city": {"type": "string"}
                },
                "required": ["departure_city", "destination_city"]
            }
        }},
        {"type": "function", "function": {
            "name": "get_flights_from_surrounding_city",
            "description": "Find flights from surrounding cities near the departure city to a destination city",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure_city": {"type": "string"},
                    "destination_city": {"type": "string"}
                },
                "required": ["departure_city", "destination_city"]
            }
        }},
        {"type": "function", "function": {
            "name": "get_ticket_price",
            "description": "Get ticket price to a destination city",
            "parameters": {
                "type": "object",
                "properties": {"destination_city": {"type": "string"}},
                "required": ["destination_city"]
            }}},
        {"type": "function", "function": {
            "name": "get_available_seats",
            "description": "Get available seats for a destination city",
            "parameters": {
                "type": "object",
                "properties": {"destination_city": {"type": "string"}},
                "required": ["destination_city"]
            }}},
        {"type": "function", "function": {
            "name": "book_ticket",
            "description": "Book ticket for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_name": {"type": "string"},
                    "destination_city": {"type": "string"}
                },
                "required": ["user_name", "destination_city"]
            }}},
        {"type": "function", "function": {
            "name": "get_user_bookings",
            "description": "Retrieve bookings for a user",
            "parameters": {
                "type": "object",
                "properties": {"user_name": {"type": "string"}},
                "required": ["user_name"]
            }}},
        {"type": "function", "function": {
            "name": "create_account",
            "description": "Create a user account",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"}
                },
                "required": ["name", "email", "phone"]
            }}}
    ]

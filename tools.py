from functions import (
    get_ticket_price, get_available_seats, book_ticket, get_user_bookings,
    create_account, get_flights_exact, get_flights_from_surrounding_city,
    get_flights_by_date, cancel_booking, get_airport_code, get_nearby_airports,
    get_flight_status, get_flight_by_airline
)

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
                    "flight_number": {"type": "string"}
                },
                "required": ["user_name", "flight_id"]
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
            }}},
        {"type": "function", "function": {
            "name": "get_flights_by_date",
            "description": "Get flights between two cities on a specific date",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure_city": {"type": "string"},
                    "destination_city": {"type": "string"},
                    "date": {"type": "string", "format": "date"}
                },
                "required": ["departure_city", "destination_city", "date"]
            }}},
        {"type": "function", "function": {
            "name": "cancel_booking",
            "description": "Cancel a user's booking by booking ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "integer"}
                },
                "required": ["booking_id"]
            }}},
        {"type": "function", "function": {
            "name": "get_airport_code",
            "description": "Get the airport code for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }}},
        {"type": "function", "function": {
            "name": "get_nearby_airports",
            "description": "Get nearby airports for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }}},
        {"type": "function", "function": {
            "name": "get_flight_status",
            "description": "Check the status of a flight",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_number": {"type": "string"}
                },
                "required": ["flight_number"]
            }}},
        {"type": "function", "function": {
            "name": "get_flight_by_airline",
            "description": "Get all flights by airline name",
            "parameters": {
                "type": "object",
                "properties": {
                    "airline_name": {"type": "string"}
                },
                "required": ["airline_name"]
            }}}
    ]
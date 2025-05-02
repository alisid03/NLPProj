from functions import (
    get_ticket_price, get_available_seats, book_ticket, get_user_bookings,
    create_account, get_flights_exact, get_flights_from_surrounding_city,
    get_flights_by_date, cancel_booking, get_airport_code, get_nearby_airports,
    get_flight_status, get_flight_by_airline
)
import json

def handle_tool_call(tool_call):
    func_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if func_name == "get_ticket_price":
        result = get_ticket_price(arguments["destination_city"])
        content = {"destination_city": arguments["destination_city"], "price": result}

    elif func_name == "get_available_seats":
        result = get_available_seats(arguments["destination_city"])
        content = {"destination_city": arguments["destination_city"], "available_seats": result}

    elif func_name == "book_ticket":
        result = book_ticket(arguments["user_name"], arguments["flight_number"])
        content = {"result": result}

    elif func_name == "get_user_bookings":
        result = get_user_bookings(arguments["user_name"])
        content = {"bookings": result}

    elif func_name == "create_account":
        result = create_account(arguments["name"], arguments["email"], arguments["phone"])
        content = {"result": result}

    elif func_name == "get_flights_exact":
        result = get_flights_exact(arguments["departure_city"], arguments["destination_city"])
        content = {"flights": result}

    elif func_name == "get_flights_from_surrounding_city":
        result = get_flights_from_surrounding_city(arguments["departure_city"], arguments["destination_city"])
        content = {"flights": result}

    elif func_name == "get_flights_by_date":
        result = get_flights_by_date(arguments["departure_city"], arguments["destination_city"], arguments["date"])
        content = {"flights": result}

    elif func_name == "cancel_booking":
        result = cancel_booking(arguments["booking_id"])
        content = {"result": result}

    elif func_name == "get_airport_code":
        result = get_airport_code(arguments["city"])
        content = {"airport_code": result}

    elif func_name == "get_nearby_airports":
        result = get_nearby_airports(arguments["city"])
        content = {"nearby_airports": result}

    elif func_name == "get_flight_status":
        result = get_flight_status(arguments["flight_number"])
        content = {"flight_status": result}

    elif func_name == "get_flight_by_airline":
        result = get_flight_by_airline(arguments["airline_name"])
        content = {"flights": result}

    else:
        content = {"error": "Unknown tool"}

    return {
        "role": "tool",
        "content": json.dumps(content),
        "tool_call_id": tool_call.id
    }
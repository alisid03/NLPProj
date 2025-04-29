import json
from functions import *

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
        result = book_ticket(arguments["user_name"], arguments["destination_city"])
        content = {"result": result}

    elif func_name == "get_user_bookings":
        result = get_user_bookings(arguments["user_name"])
        content = {"bookings": result}

    elif func_name == "create_account":
        result = create_account(arguments["name"], arguments["email"], arguments["phone"])
        content = {"result": result}

    else:
        content = {"error": "Unknown tool"}

    return {
        "role": "tool",
        "content": json.dumps(content),
        "tool_call_id": tool_call.id
    }
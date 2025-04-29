from db import cursor, conn
from resendEmail import sendEmail
from airport import city_to_airport, get_nearest_airports

def get_flights_exact(departure_city, destination_city):
    departure_city_code = city_to_airport.get(departure_city)
    cursor.execute("SELECT * FROM flights WHERE departure_airport = %s AND lower(destination_city) = %s", [departure_city_code, destination_city.lower(),])
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    flights = []

    for tuple_row in rows:
        row = dict(zip(columns,tuple_row))
        flight = {
            "flight_id": row["flight_id"],
            "airline": row["airline"],
            "flight_number": row["flight_number"],
            "departure_airport": row["departure_airport"],
            "arrival_airport": row["arrival_airport"],
            "departure_time": row["departure_time"].strftime("%B %d, %Y at %H:%M"),
            "arrival_time": row["arrival_time"].strftime("%B %d, %Y at %H:%M"),
            "ticket_price": f"${row['ticket_price']:.2f}",
            "available_seats": row["available_seats"],
            "destination_city": row["destination_city"].title()
        }
        flights.append(flight)

    return flights

def get_flights_from_surrounding_city(departure_city, destination_city):
    print("Searching in surrounding cities")
    all_flights = []
    nearest_airports = get_nearest_airports(departure_city)
    for airport in nearest_airports:
        city = airport["city"]
        flights = get_flights_exact(city, destination_city)
        all_flights.append(flights)

    return all_flights

def get_ticket_price(destination_city):
    cursor.execute("SELECT ticket_price FROM flights WHERE lower(destination_city) = %s", (destination_city.lower(),))
    result = cursor.fetchone()
    return f"${result[0]}" if result else "Unknown"

def get_available_seats(destination_city):
    cursor.execute("SELECT available_seats FROM flights WHERE lower(destination_city) = %s", (destination_city.lower(),))
    result = cursor.fetchone()
    return result[0] if result else "Unknown"

def book_ticket(user_name, destination_city):
    cursor.execute("SELECT flight_id, airline, flight_number, departure_airport, arrival_airport, departure_time, status, available_seats FROM flights WHERE lower(destination_city) = %s AND available_seats > 0 LIMIT 1", (destination_city.lower(),))
    result = cursor.fetchone()
    if not result:
        return f"No seats available to {destination_city}"

    flight_id, _, _, _, _, _, _, _ = result
    cursor.execute("SELECT user_id, email FROM users WHERE lower(name) = %s", (user_name.lower(),))
    user_result = cursor.fetchone()
    if not user_result:
        return f"User '{user_name}' not found."

    user_id, user_email = user_result
    cursor.execute("INSERT INTO bookings (user_id, flight_id, status) VALUES (%s, %s, %s) RETURNING booking_id", (user_id, flight_id, 'Confirmed'))
    booking_id = cursor.fetchone()[0]
    cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE flight_id = %s", (flight_id,))
    conn.commit()
    sendEmail(user_email, result)
    return f"Booking confirmed for {user_name} to {destination_city}. Booking ID: {booking_id}"

def get_user_bookings(user_name):
    cursor.execute("""
        SELECT u.name, f.airline, f.flight_number, f.departure_airport, f.arrival_airport, f.departure_time, b.status
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN flights f ON b.flight_id = f.flight_id
        WHERE lower(u.name) = %s
    """, (user_name.lower(),))
    results = cursor.fetchall()
    if not results:
        return "No bookings found."
    return [{
        "user": row[0], "airline": row[1], "flight_number": row[2],
        "from": row[3], "to": row[4], "departure": row[5].isoformat(), "status": row[6]
    } for row in results]

def create_account(name, email, phone):
    try:
        cursor.execute("INSERT INTO users (name, email, phone, created_at) VALUES (%s, %s, %s, NOW()) RETURNING user_id", (name, email, phone))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return f"Account created successfully for {name} (User ID: {user_id})"
    except:
        conn.rollback()
        return "An account with this email already exists."

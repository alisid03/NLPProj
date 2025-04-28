from db import cursor, conn

def get_ticket_price(destination_city):
    cursor.execute("SELECT ticket_price FROM flights WHERE lower(destination_city) = %s", (destination_city.lower(),))
    result = cursor.fetchone()
    return f"${result[0]}" if result else "Unknown"

def get_available_seats(destination_city):
    cursor.execute("SELECT available_seats FROM flights WHERE lower(destination_city) = %s", (destination_city.lower(),))
    result = cursor.fetchone()
    return result[0] if result else "Unknown"

def book_ticket(user_name, destination_city):
    cursor.execute("SELECT flight_id, available_seats FROM flights WHERE lower(destination_city) = %s AND available_seats > 0 LIMIT 1", (destination_city.lower(),))
    result = cursor.fetchone()
    if not result:
        return f"No seats available to {destination_city}"

    flight_id, _ = result
    cursor.execute("SELECT user_id FROM users WHERE lower(name) = %s", (user_name.lower(),))
    user_result = cursor.fetchone()
    if not user_result:
        return f"User '{user_name}' not found."

    user_id = user_result[0]
    cursor.execute("INSERT INTO bookings (user_id, flight_id, status) VALUES (%s, %s, %s) RETURNING booking_id", (user_id, flight_id, 'Confirmed'))
    booking_id = cursor.fetchone()[0]
    cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE flight_id = %s", (flight_id,))
    conn.commit()
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

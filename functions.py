from db import cursor, conn
from resendEmail import sendEmail
from airport import city_to_airport, get_nearest_airports
from fpdf import FPDF
from datetime import datetime
import os

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

def book_ticket(user_name, flight_number):
    cursor.execute("SELECT flight_id, airline, flight_number, departure_airport, arrival_airport, departure_time, status, available_seats, ticket_price FROM flights WHERE flight_number = %s AND available_seats > 0 LIMIT 1", (flight_number,))
    result = cursor.fetchone()
    if not result:
        return f"No seats available"

    flight_id, airline, flight_number, departure_airport, arrival_airport, departure_time, status, available_seats, ticket_price = result
    cursor.execute("SELECT user_id, email FROM users WHERE lower(name) = %s", (user_name.lower(),))
    user_result = cursor.fetchone()
    if not user_result:
        return f"User '{user_name}' not found."

    user_id, user_email = user_result
    cursor.execute("INSERT INTO bookings (user_id, flight_id, status) VALUES (%s, %s, %s) RETURNING booking_id", (user_id, flight_id, 'Confirmed'))
    booking_id = cursor.fetchone()[0]
    cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE flight_id = %s", (flight_id,))
    conn.commit()
    # sendEmail(user_email, result)

    # Generate receipt PDF
    receipt_data = {
        "booking_id": booking_id,
        "full_name": user_name,
        "flight_id": flight_id,
        "origin": departure_airport,
        "destination": arrival_airport,
        "flight_date": departure_time,
        "airline": airline,
        "price": ticket_price,
        "booking_date": str(datetime.now().date())
    }

    receipt_path = f"booking_receipt_{booking_id}.pdf"
    generate_booking_receipt(receipt_data, receipt_path)

    return f"Booking confirmed for {user_name} to {arrival_airport}. \nBooking ID: {booking_id}", os.path.abspath(receipt_path)

def generate_booking_receipt(booking_data, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title("Flight Booking Receipt")

    pdf.cell(200, 10, txt="Flight Booking Receipt", ln=True, align='C')
    pdf.ln(10)

    for key, value in booking_data.items():
        pdf.cell(200, 10, txt=f"{key.replace('_', ' ').title()}: {value}", ln=True)

    pdf.output(output_path)

def get_user_bookings(user_name):
    cursor.execute("""
        SELECT u.name, f.airline, f.flight_number, f.departure_airport, f.arrival_airport, f.departure_time, b.status, b.booking_id
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN flights f ON b.flight_id = f.flight_id
        WHERE lower(u.name) = %s
    """, (user_name.lower(),))
    results = cursor.fetchall()
    if not results:
        return "No bookings found."
    return [{
        "user": row[0], "booking_id": row[7], "airline": row[1], "flight_number": row[2],
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

def get_flights_by_date(departure_city, destination_city, date):
    departure_code = city_to_airport.get(departure_city)
    if not departure_code:
        return f"Unknown departure city: {departure_city}"

    cursor.execute("""
        SELECT * FROM flights
        WHERE departure_airport = %s 
          AND lower(destination_city) = %s 
          AND DATE(departure_time) = %s
    """, (departure_code, destination_city.lower(), date))

    rows = cursor.fetchall()
    if not rows:
        return f"No flights found on {date} from {departure_city} to {destination_city}"

    columns = [desc[0] for desc in cursor.description]
    return [
        {
            "flight_id": row_dict["flight_id"],
            "airline": row_dict["airline"],
            "flight_number": row_dict["flight_number"],
            "departure_time": row_dict["departure_time"].strftime("%B %d, %Y at %H:%M"),
            "arrival_time": row_dict["arrival_time"].strftime("%B %d, %Y at %H:%M"),
            "ticket_price": f"${row_dict['ticket_price']:.2f}"
        }
        for row in rows
        for row_dict in [dict(zip(columns, row))]
    ]

def cancel_booking(booking_id):
    cursor.execute("SELECT status FROM bookings WHERE booking_id = %s", (booking_id,))
    result = cursor.fetchone()
    if not result:
        return f"Booking ID {booking_id} not found."

    if result[0] == "Cancelled":
        return f"Booking {booking_id} is already cancelled."

    cursor.execute("UPDATE bookings SET status = %s WHERE booking_id = %s", ('Cancelled', booking_id))
    conn.commit()
    return f"Booking {booking_id} has been cancelled successfully."

def get_airport_code(city):
    code = city_to_airport.get(city)
    return code if code else f"No airport code found for {city}"

def get_nearby_airports(city):
    airports = get_nearest_airports(city)
    if not airports:
        return f"No nearby airports found for {city}"
    return [{"city": a["city"], "airport_code": a["airport_code"]} for a in airports]

def get_flight_status(flight_number):
    cursor.execute("SELECT flight_number, status FROM flights WHERE flight_number = %s", (flight_number,))
    result = cursor.fetchone()
    if not result:
        return f"No status found for flight {flight_number}"
    return {"flight_number": result[0], "status": result[1]}

def get_flight_by_airline(airline_name):
    cursor.execute("SELECT * FROM flights WHERE lower(airline) = %s", (airline_name.lower(),))
    rows = cursor.fetchall()
    if not rows:
        return f"No flights found for airline {airline_name}"

    columns = [desc[0] for desc in cursor.description]
    return [
        {
            "flight_number": row_dict["flight_number"],
            "departure_airport": row_dict["departure_airport"],
            "arrival_airport": row_dict["arrival_airport"],
            "departure_time": row_dict["departure_time"].strftime("%B %d, %Y at %H:%M"),
            "arrival_time": row_dict["arrival_time"].strftime("%B %d, %Y at %H:%M"),
            "ticket_price": f"${row_dict['ticket_price']:.2f}"
        }
        for row in rows
        for row_dict in [dict(zip(columns, row))]
    ]
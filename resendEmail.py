import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

def sendEmail(email, booking):
    # Can only send to Ali's email
    _, airline, flight_number, departure_airport, arrival_airport, departure_time, status, _ = booking

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #333;">✈️ Your Flight Booking Details</h2>
        <p><strong>Airline:</strong> {airline}</p>
        <p><strong>Flight Number:</strong> {flight_number}</p>
        <p><strong>From:</strong> {departure_airport}</p>
        <p><strong>To:</strong> {arrival_airport}</p>
        <p><strong>Departure:</strong> {departure_time.strftime('%B %d, %Y, at %H:%M')}</p>
        <p><strong>Status:</strong> {status}</p>
        <br>
        <p>Thank you for choosing <strong>FlightAI</strong>! ✈️</p>
    </body>
    </html>
    """

    params = resend.Emails.SendParams(
        {
            "from": "FlightAI <flightAI@resend.dev>",
            "to": [email],
            "subject": "Flight Booking Confirmation",
            "html": html_content
        }
    )

    email = resend.Emails.send(params)

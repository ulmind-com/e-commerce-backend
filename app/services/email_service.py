import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_invoice_email(user_email: str, order: dict):
    """
    Sends an invoice email. If SMTP credentials are not found in the environment,
    it simulates the sending by printing the email to the console.
    """
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    # Generate HTML invoice
    items_html = ""
    for item in order.get("items", []):
        items_html += f"<tr><td>{item.get('title')}</td><td>{item.get('quantity')}</td><td>₹{item.get('price_at_purchase')}</td></tr>"

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Invoice for Order #{order.get('_id')}</h2>
        <p>Thank you for shopping at OneBasket!</p>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
          <thead>
            <tr>
              <th>Item</th>
              <th>Quantity</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {items_html}
          </tbody>
        </table>
        <h3 style="text-align: right;">Total Paid: ₹{order.get('total_amount')}</h3>
      </body>
    </html>
    """

    if not smtp_user or not smtp_password:
        print(f"\n{'='*50}\n[MOCK EMAIL] Sending invoice to {user_email}\n{'='*50}")
        print(html_content)
        print(f"{'='*50}\n")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"OneBasket Invoice - Order #{order.get('_id')}"
    msg["From"] = smtp_user
    msg["To"] = user_email

    part2 = MIMEText(html_content, "html")
    msg.attach(part2)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, user_email, msg.as_string())
        server.quit()
        print(f"Successfully sent invoice email to {user_email}")
    except Exception as e:
        print(f"Failed to send email to {user_email}: {e}")

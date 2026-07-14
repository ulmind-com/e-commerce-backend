import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

def send_invoice_email(user_email: str, order: dict):
    """
    Sends an Ultra Pro Premium GST invoice email. If SMTP credentials are not found in the environment,
    it simulates the sending by printing the email to the console and saving it to an HTML file for the user to view.
    """
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    # Generate Items Rows
    items_html = ""
    subtotal = 0
    for item in order.get("items", []):
        price = item.get('price_at_purchase', 0)
        qty = item.get('quantity', 1)
        total = price * qty
        subtotal += total
        items_html += f"""
        <tr>
            <td style="padding: 16px; border-bottom: 1px solid #e2e8f0; color: #1e293b; font-size: 14px; font-weight: 500;">
                {item.get('title')}
            </td>
            <td style="padding: 16px; border-bottom: 1px solid #e2e8f0; color: #64748b; font-size: 14px; text-align: center;">
                {qty}
            </td>
            <td style="padding: 16px; border-bottom: 1px solid #e2e8f0; color: #64748b; font-size: 14px; text-align: right;">
                ₹{price}
            </td>
            <td style="padding: 16px; border-bottom: 1px solid #e2e8f0; color: #0f766e; font-size: 14px; font-weight: bold; text-align: right;">
                ₹{total}
            </td>
        </tr>
        """

    gst_details = order.get("gst_details")
    order_id = str(order.get('_id'))[:8].upper()
    order_date = datetime.utcnow().strftime("%d %B, %Y")

    billed_to_html = f"""
    <p style="margin: 0 0 5px 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Billed To</p>
    <p style="margin: 0 0 4px 0; color: #1e293b; font-size: 16px; font-weight: bold;">{user_email}</p>
    """
    if gst_details:
        billed_to_html += f"""
        <div style="margin-top: 10px; background-color: #f1f5f9; padding: 12px; border-radius: 8px; border-left: 4px solid #0f766e;">
            <p style="margin: 0 0 4px 0; color: #0f766e; font-size: 12px; font-weight: bold; text-transform: uppercase;">GST Details Provided</p>
            <p style="margin: 0 0 2px 0; color: #334155; font-size: 14px;"><strong>Company:</strong> {gst_details.get('companyName')}</p>
            <p style="margin: 0; color: #334155; font-size: 14px;"><strong>GSTIN:</strong> <span style="font-family: monospace; font-size: 13px;">{gst_details.get('gstin')}</span></p>
        </div>
        """

    total_amount = order.get("total_amount", 0)
    packaging_fee = 9
    grand_total = total_amount + packaging_fee

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>OneBasket Tax Invoice</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <!-- Main Container -->
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                        
                        <!-- Header / Banner -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 40px;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td>
                                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">
                                                <span style="color: #38bdf8;">One</span>Basket
                                            </h1>
                                            <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 14px;">Delivery in 10 minutes</p>
                                        </td>
                                        <td align="right">
                                            <div style="background-color: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2);">
                                                <span style="color: #ffffff; font-size: 12px; font-weight: bold; letter-spacing: 1.5px;">TAX INVOICE</span>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Order Info & Billing -->
                        <tr>
                            <td style="padding: 40px;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td width="50%" valign="top">
                                            {billed_to_html}
                                        </td>
                                        <td width="50%" valign="top" align="right">
                                            <p style="margin: 0 0 5px 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Order Summary</p>
                                            <p style="margin: 0 0 4px 0; color: #1e293b; font-size: 14px;"><strong>Order ID:</strong> #{order_id}</p>
                                            <p style="margin: 0 0 4px 0; color: #1e293b; font-size: 14px;"><strong>Date:</strong> {order_date}</p>
                                            <p style="margin: 0; color: #1e293b; font-size: 14px;"><strong>Payment Mode:</strong> {order.get('payment_mode')}</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Items Table -->
                        <tr>
                            <td style="padding: 0 40px;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-collapse: collapse;">
                                    <thead>
                                        <tr>
                                            <th align="left" style="padding: 12px 16px; background-color: #f8fafc; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; border-radius: 8px 0 0 8px;">Item Description</th>
                                            <th align="center" style="padding: 12px 16px; background-color: #f8fafc; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Qty</th>
                                            <th align="right" style="padding: 12px 16px; background-color: #f8fafc; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold;">Price</th>
                                            <th align="right" style="padding: 12px 16px; background-color: #f8fafc; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; border-radius: 0 8px 8px 0;">Total</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {items_html}
                                    </tbody>
                                </table>
                            </td>
                        </tr>

                        <!-- Totals Section -->
                        <tr>
                            <td style="padding: 40px;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td width="50%" valign="top">
                                            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 16px; border-radius: 8px; margin-top: 10px;">
                                                <p style="margin: 0; color: #166534; font-size: 13px; line-height: 1.5;">
                                                    <strong style="display: block; margin-bottom: 4px; font-size: 14px;">Thank you for your business!</strong>
                                                    Your order has been processed securely. If you have any questions, reply to this email.
                                                </p>
                                            </div>
                                        </td>
                                        <td width="50%" valign="top">
                                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-left: 20px;">
                                                <tr>
                                                    <td align="right" style="padding: 8px 0; color: #64748b; font-size: 14px;">Subtotal:</td>
                                                    <td align="right" style="padding: 8px 0; color: #1e293b; font-size: 14px; font-weight: 500;">₹{subtotal}</td>
                                                </tr>
                                                <tr>
                                                    <td align="right" style="padding: 8px 0; color: #64748b; font-size: 14px;">Packaging Fee:</td>
                                                    <td align="right" style="padding: 8px 0; color: #1e293b; font-size: 14px; font-weight: 500;">₹{packaging_fee}</td>
                                                </tr>
                                                {f'''<tr>
                                                    <td align="right" style="padding: 8px 0; color: #64748b; font-size: 14px;">COD Fee:</td>
                                                    <td align="right" style="padding: 8px 0; color: #1e293b; font-size: 14px; font-weight: 500;">₹{order.get("cod_surcharge", 0)}</td>
                                                </tr>''' if order.get("payment_mode") == "COD" and order.get("cod_surcharge", 0) > 0 else ''}
                                                <tr>
                                                    <td colspan="2" style="padding-top: 16px;">
                                                        <div style="height: 1px; background-color: #e2e8f0; width: 100%;"></div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td align="right" style="padding: 16px 0 0 0; color: #0f172a; font-size: 16px; font-weight: bold;">Grand Total:</td>
                                                    <td align="right" style="padding: 16px 0 0 0; color: #0f766e; font-size: 24px; font-weight: 900;">₹{grand_total}</td>
                                                </tr>
                                                <tr>
                                                    <td colspan="2" align="right" style="padding-top: 8px;">
                                                        <span style="background-color: #f1f5f9; color: #64748b; font-size: 10px; padding: 4px 8px; border-radius: 4px; font-weight: bold; letter-spacing: 0.5px;">INCLUDES GST (WHERE APPLICABLE)</span>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8fafc; padding: 30px 40px; border-top: 1px solid #e2e8f0; text-align: center;">
                                <p style="margin: 0 0 8px 0; color: #64748b; font-size: 12px; font-weight: bold;">OneBasket E-Commerce Ltd.</p>
                                <p style="margin: 0; color: #94a3b8; font-size: 12px;">This is a computer generated invoice and does not require a physical signature.</p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    if not smtp_user or not smtp_password:
        print(f"\n{'='*50}\n[MOCK EMAIL] Sending Ultra Premium Invoice to {user_email}\n{'='*50}")
        # Save to file so the user can actually see it in browser
        try:
            with open(f"invoice_{order_id}.html", "w") as f:
                f.write(html_content)
            print(f"Saved invoice HTML to invoice_{order_id}.html for preview.")
        except Exception as e:
            print(e)
        print(f"{'='*50}\n")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your OneBasket Tax Invoice - #{order_id}"
    msg["From"] = f"OneBasket <{smtp_user}>"
    msg["To"] = user_email

    part2 = MIMEText(html_content, "html")
    msg.attach(part2)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, user_email, msg.as_string())
        server.quit()
        print(f"Successfully sent Ultra Premium GST invoice email to {user_email}")
    except Exception as e:
        print(f"Failed to send email to {user_email}: {e}")

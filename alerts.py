from twilio.rest import Client
from database import log_alert
import config

def send_whatsapp_alert(bin_name, location, fill_level, hours_to_overflow=None):
    """
    Sends real WhatsApp message to truck driver
    via Twilio API
    """
    try:
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)

        if hours_to_overflow:
            message_body = (
                f"🚨 *WASTE ALERT — SmartWaste AI*\n\n"
                f"📍 *Location:* {location}\n"
                f"🗑️ *Bin:* {bin_name}\n"
                f"📊 *Fill Level:* {fill_level}%\n"
                f"⏰ *Overflow in:* {hours_to_overflow} hours\n\n"
                f"⚡ Immediate collection required!"
            )
        else:
            message_body = (
                f"⚠️ *WASTE ALERT — SmartWaste AI*\n\n"
                f"📍 *Location:* {location}\n"
                f"🗑️ *Bin:* {bin_name}\n"
                f"📊 *Fill Level:* {fill_level}%\n\n"
                f"📅 Schedule collection today."
            )

        message = client.messages.create(
            body=message_body,
            from_=f"whatsapp:{config.TWILIO_WHATSAPP_FROM}",
            to=f"whatsapp:{config.DRIVER_PHONE_NUMBER}"
        )

        return {
            "success": True,
            "message_sid": message.sid,
            "message": f"Alert sent to driver for {bin_name}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def check_and_alert(bins):
    """
    Automatically checks all bins and sends
    alerts for any above 80% fill level
    """
    alerts_sent = []

    for bin in bins:
        bin_id = bin[0]
        name = bin[1]
        location = bin[2]
        fill_level = bin[5]

        if fill_level >= 80:
            result = send_whatsapp_alert(
                bin_name=name,
                location=location,
                fill_level=fill_level
            )

            log_alert(bin_id, f"Auto alert sent — fill level {fill_level}%")
            alerts_sent.append({
                "bin": name,
                "fill_level": fill_level,
                "alert_result": result
            })

    return alerts_sent
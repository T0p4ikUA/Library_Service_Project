import os
import requests
from borrowings.models import Borrowing
from datetime import date

def send_telegram_message(message: str) -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print(f"DEBUG TOKEN: {bot_token}, CHAT_ID: {chat_id}")

    if not bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send telegram message: {e}")


def check_overdue_borrowings():
    today = date.today()

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
    ).select_related("book", "user")

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"<b>OVERDUE BORROWING!</b>\n\n"
                f"<b>User:</b> {borrowing.user.email}\n"
                f"<b>Book:</b> {borrowing.book.title}\n"
                f"<b>Borrow date:</b> {borrowing.borrow_date}\n"
                f"<b>Expected return date:</b> {borrowing.expected_return_date}"
            )
            send_telegram_message(message)
    else:
        send_telegram_message("No borrowings overdue today!")

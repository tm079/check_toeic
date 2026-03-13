import requests
from datetime import datetime, date
import os

# ========== CẤU HÌNH ==========
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Khoảng ngày muốn theo dõi
DATE_FROM = date(2026, 4, 15)
DATE_TO = date(2026, 4, 30)

# API IIG
API_URL = (
    "https://online.iigvietnam.com/ExamCalendarEnglish/GetList"
    "?exam=32f6ac8b-df8f-43f3-bf53-035fe126436e"
    "&area=32c5bd30-3547-4242-b6f2-55d91edca07a"
    "&headerQuarterId="
    "&status=true"
    f"&dateTest={date.today().strftime('%Y-%m-%d')},{DATE_TO.strftime('%Y-%m-%d')}"
    "&lang=vi"
    "&pageIndex=1"
    "&pageSize=100"
)
# ================================


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    print("✅ Đã gửi Telegram!")


def check_exam():
    print(f"🔍 Đang kiểm tra lịch thi lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

    resp = requests.get(API_URL, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    exams = data.get("data", [])
    matched = []

    for exam in exams:
        date_str = exam.get("dateTest", "")
        exam_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()

        if DATE_FROM <= exam_date <= DATE_TO:
            matched.append(exam)

    if matched:
        lines = [f"🎯 <b>Có {len(matched)} lịch thi TOEIC trong khoảng {DATE_FROM.strftime('%d/%m')} - {DATE_TO.strftime('%d/%m/%Y')}!</b>\n"]
        for e in matched:
            exam_date = datetime.fromisoformat(e["dateTest"].replace("Z", "+00:00"))
            lines.append(
                f"📅 <b>{exam_date.strftime('%d/%m/%Y')}</b> | ⏰ {e['timeTest']}\n"
                f"📍 {e['headQuarter']}\n"
                f"🏢 {e['headQuarterAddress']}\n"
                f"📝 {e['examName']}\n"
                f"📋 Kết quả: {e['resultDate']}\n"
            )
        lines.append("👉 Đăng ký ngay: https://online.iigvietnam.com/")
        send_telegram("\n".join(lines))
    else:
        print(f"ℹ️ Không có lịch thi nào trong khoảng {DATE_FROM} - {DATE_TO}.")


if __name__ == "__main__":
    check_exam()

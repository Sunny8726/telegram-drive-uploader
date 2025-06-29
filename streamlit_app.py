import streamlit as st
import requests
import datetime
import gspread
from google.oauth2.service_account import Credentials

# ================= CONFIG =================
BOT_TOKEN = "8058471433:AAE68N4V0tqTryeu3yjKohRPchoYYen-AU0"
CHANNEL_ID = "-1002835921912"
SHEET_ID = "1knLaq6Jr2rWaWggBoyqZlKtX6CrttK3mFkVyTdi33Zg"

# Load Google Sheet credentials
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CREDS = Credentials.from_service_account_file("creds.json", scopes=SCOPE)
gc = gspread.authorize(CREDS)
sheet = gc.open_by_key(SHEET_ID).sheet1

# =============== Streamlit UI ===============
st.set_page_config(page_title="SunnyDrive - Upload", layout="centered")
st.title("📤 Upload to SunnyDrive")
st.markdown("---")

with st.form("upload_form"):
    file = st.file_uploader("📁 Select a file")
    folder = st.text_input("📂 Folder Name")
    caption = st.text_area("📝 Add Caption")
    submit = st.form_submit_button("🚀 Upload")

if submit:
    if not file or not folder:
        st.warning("Please select a file and enter a folder name.")
    else:
        with st.spinner("Uploading to Telegram & saving to Sheet..."):
            file_bytes = file.read()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_caption = f"{caption}\n\n📁 Folder: {folder}\n🕒 {timestamp}"

            tg_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            resp = requests.post(tg_api, data={
                "chat_id": CHANNEL_ID,
                "caption": full_caption
            }, files={"document": (file.name, file_bytes)})

            if resp.status_code == 200:
                msg_id = resp.json()["result"]["message_id"]
                link = f"https://t.me/c/{CHANNEL_ID[4:]}/{msg_id}" if CHANNEL_ID.startswith("-100") else f"https://t.me/{CHANNEL_ID}/{msg_id}"
                sheet.append_row([file.name, folder, caption, timestamp, link])
                st.success("✅ File uploaded!")
                st.markdown(f"[🔗 Open in Telegram]({link})")
            else:
                st.error("❌ Failed to upload to Telegram. Check bot/channel permissions.")

import os
import time
import requests
import smtplib
import winsound
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# === .env Dosyasını Yükle ===
load_dotenv()

# === Kullanıcı Bilgileri ===
USERNAME = os.getenv("USERNAME", "30472669726")
PASSWORD = os.getenv("PASSWORD", "Stfa.1023")

LOGIN_URL = "https://online.spor.istanbul/uyegiris"
REZERVASYON_URL = "https://online.spor.istanbul/uyespor"

# === Telegram Bilgileri ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "8285688755:AAEZgB1cd2WtnJuioK3KmFeLLbr22x_s-X0")
CHAT_ID = os.getenv("CHAT_ID", "1169909946")

def send_telegram(message):
    """Telegram mesajı gönder"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=data)
        print("📩 Telegram mesajı gönderildi:", message)
    except Exception as e:
        print("⚠️ Telegram mesajı gönderilemedi:", e)

# === E-Posta Ayarları ===
EMAIL_USER = os.getenv("EMAIL_USER", "emrahkapucu@gmail.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "nljd ebew nbax nzsc")
EMAIL_TO = os.getenv("EMAIL_TO", "emrahkapucu@gmail.com")

def send_email(subject, message):
    """Kalan kontenjan olduğunda e-posta gönder"""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("📧 E-posta gönderildi.")
    except Exception as e:
        print("⚠️ E-posta gönderilemedi:", e)

# === Tarayıcı Ayarları ===
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    # 1️⃣ Giriş
    driver.get(LOGIN_URL)
    time.sleep(3)

    username_box = driver.find_element(By.ID, "txtTCPasaport")
    password_box = driver.find_element(By.ID, "txtSifre")

    username_box.send_keys(USERNAME)
    password_box.send_keys(PASSWORD)
    password_box.send_keys(Keys.ENTER)

    print("🔐 Giriş yapılıyor...")
    time.sleep(5)

    # 2️⃣ Rezervasyon sayfasına git
    driver.get(REZERVASYON_URL)
    print("🎾 Rezervasyon sayfası açıldı.")
    time.sleep(5)

    # 3️⃣ “Seans Seç” butonuna tıkla
    try:
        seans_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "pageContent_rptListe_lbtnSeansSecim_0"))
        )
        driver.execute_script("arguments[0].click();", seans_button)
        print("✅ 'Seans Seç (Rezervasyon Yap)' butonuna tıklandı.")
    except Exception as e:
        print("⚠️ 'Seans Seç' butonu tıklanamadı:", e)

    # Telegram’a sistemin başladığını bildir
    send_telegram("✅ Rezervasyon botu çalışmaya başladı...")

    sayac = 0
    while True:
        sayac += 1
        print(f"🔍 {sayac}. kontrol yapılıyor...")
        seanslar = driver.find_elements(By.CSS_SELECTOR, "div.well")
        uygun_bulundu = False
        mesaj = ""

        for seans in seanslar:
            try:
                kort = seans.find_element(By.TAG_NAME, "label").text.strip()
                saat = seans.find_element(By.XPATH, ".//span[contains(@id,'lblSeansSaat')]").text.strip()
                kalan_text = seans.find_element(By.XPATH, ".//span[@title='Kalan Kontenjan']").text.strip()
                kalan = int(kalan_text)

                if kalan > 0:
                    uygun_bulundu = True
                    mesaj += f"🎾 {kort} | {saat} | Kalan: {kalan}\n"
                    print(f"✅ Müsait seans bulundu: {kort} - {saat} ({kalan})")
            except:
                continue

        if uygun_bulundu:
            # 🔔 Sesli ve Telegram + Mail uyarısı
            for _ in range(3):
                winsound.Beep(1500, 700)

            send_telegram(f"🎾 Boş seans bulundu!\n\n{mesaj}")
            send_email("🎾 Spor.İstanbul Boş Seans Uyarısı", mesaj)
        else:
            print("⏳ Boş seans yok. 2 dakika sonra tekrar kontrol edilecek...")

        # Her 2 saatte bir sistemin aktif olduğunu bildir
        if sayac % 120 == 0:
            send_telegram("🤖 Sistem halen çalışıyor...")

        # Sayfayı yenile
        time.sleep(120)
        driver.refresh()
        time.sleep(5)

finally:
    driver.quit()

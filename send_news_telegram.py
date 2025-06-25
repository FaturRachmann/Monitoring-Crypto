import os
import json
import time

from backend.news_feed import fetch_news
from ai.summarize import summarize
from telegram.send_telegram import send_to_telegram

CACHE_FILE = "sent_news.json"

# Load cache berita yang sudah dikirim
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        sent_links = set(json.load(f))
else:
    sent_links = set()

def save_sent_links():
    with open(CACHE_FILE, "w") as f:
        json.dump(list(sent_links), f)

def run():
    print("🚀 Menjalankan News Bot...")
    all_news = fetch_news()
    print(f"🔎 Jumlah berita ditemukan: {len(all_news)}")

    new_news = [news for news in all_news if news['link'] not in sent_links]
    print(f"🆕 Berita baru: {len(new_news)}")

    for i, news in enumerate(new_news):
        print(f"📌 Memproses berita baru #{i+1}: {news['title']}")
        raw = f"{news['title']}\n\n{news['summary']}"
        summary = summarize(raw)
        print("🧠 Ringkasan AI:", summary)

        message = f"📰 *{news['title']}*\n{news['link']}\n\n📌 *Ringkasan:*\n{summary}"
        success = send_to_telegram(message)

        if success:
            print(f"✅ Terkirim: {news['title']}")
            sent_links.add(news['link'])  # Tambah ke cache
            save_sent_links()  # Simpan cache setiap kali ada berita baru terkirim
        else:
            print(f"❌ Gagal kirim: {news['title']}")

if __name__ == "__main__":
    while True:
        run()
        print("💤 Menunggu 10 menit...\n")
        time.sleep(600)  # 10 menit
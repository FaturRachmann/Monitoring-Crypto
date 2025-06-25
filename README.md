# Monitoring-Crypto
📰 Bloomberg Crypto Lokal Bloomberg Crypto Lokal adalah dashboard real-time yang menampilkan informasi pasar kripto terupdate, termasuk:

Harga aset crypto populer

Transaksi besar dari wallet whale

Posisi long/short bernilai besar (≥ $10K)

Berita penting dari berbagai sumber kripto

Ringkasan AI otomatis menggunakan LLM

Mengirim Berita Otomatis ke Telegram

🚀 Fitur Utama Fitur Keterangan 📈 Harga Crypto Harga BTC, ETH, SOL dengan perubahan % 🐋 Whale Transactions Transaksi besar di blockchain dengan dampak & hash 📍 Posisi Long/Short Posisi leverage besar dengan margin, PnL, dan liquidation 📰 Crypto News Berita terbaru dari CoinTelegraph, Bitcoin.com, CryptoSlate 🧠 Ringkasan AI Auto-summarize berita pakai LLM (bisa pakai Groq API atau open-source) 💬 Telegram Bot (opsional) Kirim ringkasan otomatis ke Telegram (bisa ditambahkan)

🛠️ Cara Menjalankan

Clone Repositori bash Salin Edit git clone https://github.com/namakamu/bloomberg-local.git cd bloomberg-local
Install Dependensi bash Salin Edit pip install -r requirements.txt
Jalankan Dashboard bash Salin Edit streamlit run dashboard/app.py
Buka di Browser text Salin Edit http://localhost:8501
📦 Dependensi Utama streamlit

pandas

requests

streamlit-autorefresh

📌 Catatan Ringkasan berita menggunakan model LLM, bisa disesuaikan dengan Groq API, Ollama, atau local model.

Posisi long/short real menggunakan Binance Futures API.

Data whale transaction bersifat simulatif. Bisa diintegrasi dengan Arkham, Dexscreener, atau Etherscan jika diperlukan.

🤝 Kontribusi Proyek ini open-source. Kamu bisa bantu dengan:

Menambahkan sumber data baru (misalnya CoinGecko, Arkham, Coinglass)

Integrasi AI lokal tanpa Groq

Menambahkan grafik Streamlit atau notifikasi Telegram

# Gunakan image Python resmi
FROM python:3.10-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Salin file requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file & folder ke dalam container
COPY . .

# Ekspose port default Streamlit
EXPOSE 8501

# Jalankan streamlit saat container dijalankan
CMD ["streamlit", "run", "run.py", "--server.port=8501", "--server.address=0.0.0.0"]

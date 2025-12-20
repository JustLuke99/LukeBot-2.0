# Použijeme lehkou verzi Pythonu 3.11
FROM python:3.13

# Nastavení pracovního adresáře v kontejneru
WORKDIR /app

# Nastavení proměnných prostředí
# PYTHONDONTWRITEBYTECODE: Zabrání Pythonu v psaní .pyc souborů
# PYTHONUNBUFFERED: Zajistí, že se logy vypisují ihned do konzole
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalace systémových závislostí
# ffmpeg - pro ffmpeg-python
# build-essential, gcc - pro kompilaci některých python knihoven
# chromium, chromium-driver - pro Selenium
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Zkopírujeme requirements a nainstalujeme závislosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Zkopírujeme zbytek projektu do kontejneru
COPY . .

# Příkaz, který se spustí při startu kontejneru
CMD ["sh", "-c", "python manage.py migrate && python main.py"]
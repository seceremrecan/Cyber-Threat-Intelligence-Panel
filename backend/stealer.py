import json
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import pytz

# PostgreSQL bağlantı bilgileri
DB_USER = "postgres"
DB_PASSWORD = "258258258"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "cti_panel"

# SQLAlchemy bağlantısı
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# JSON dosya yolu
JSON_FILE_PATH = r"C:\Users\secer\OneDrive\Masaüstü\parsed_redline_output.json"

# Türkiye saat dilimini ayarla
turkey_tz = pytz.timezone("Europe/Istanbul")
current_time = datetime.now(turkey_tz)

# JSON dosyasını oku
with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Veriyi DataFrame'e dönüştür
df = pd.DataFrame(raw_data)
df["date_published"] = current_time
df["created_at"] = current_time
df["updated_at"] = None  # İlk yüklemede boş bırak

# Veritabanındaki mevcut verileri kontrol et
try:
    existing = pd.read_sql("SELECT username, url FROM stealer", engine)

    # Zaten kayıtlı olmayanları filtrele
    new_data = df[~df.set_index(["username", "url"]).index.isin(existing.set_index(["username", "url"]).index)]

    # Yeni kayıtları veritabanına ekle
    if not new_data.empty:
        new_data.to_sql("stealer", engine, if_exists="append", index=False)
        print(f"✅ {len(new_data)} yeni stealer kaydı eklendi.")
    else:
        print("🔄 Yeni stealer verisi bulunamadı.")
except Exception as e:
    print(f"❌ Veritabanı işlem hatası: {e}")

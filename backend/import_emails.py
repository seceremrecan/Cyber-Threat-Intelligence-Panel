import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import pytz  # Zaman dilimi desteği için

# PostgreSQL bağlantı bilgileri
DB_USER = 'postgres'
DB_PASSWORD = '258258258'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'cti_panel'

# SQLAlchemy bağlantı dizisi
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# CSV dosyasının yolu
CSV_FILE_PATH = r"C:\Users\secer\OneDrive\Masaüstü\(2023-11-12)totalstay.com.csv"

# SQLAlchemy engine oluştur
engine = create_engine(DATABASE_URL)

# CSV'yi oku
df = pd.read_csv(CSV_FILE_PATH, header=None)  # `header=None` sütun adlarını göz ardı eder
df = df[[0]].rename(columns={0: 'email'})  # İlk sütunu 'email' olarak yeniden adlandır

# Türkiye saat dilimini ayarla
turkey_tz = pytz.timezone('Europe/Istanbul')
current_time_turkey = datetime.now(turkey_tz)

# Ek sütunları ekleyerek DataFrame'i hazırla
df['data_breach_id'] = 2  # Tüm mailler için data_breach_id olarak 1 ata
df['created_at'] = current_time_turkey  # Türkiye saatine göre oluşturulma zamanı
df['updated_at'] = None  # Güncelleme zamanı boş bırakılabilir

# Veritabanına ekleme işlemi
try:
    # Veritabanındaki mevcut verileri çek
    existing_emails = pd.read_sql('SELECT email FROM emails', engine)

    # Yeni verilerle mevcut veriler arasındaki farkı bulun
    new_emails = df[~df['email'].isin(existing_emails['email'])]

    # Yeni verileri ekle
    if not new_emails.empty:
        new_emails.to_sql(
            'emails',  # Tablo adı
            engine,
            if_exists='append',  # Mevcut tabloya ekle
            index=False  # DataFrame'deki index sütununu ekleme
        )
        print(f"{len(new_emails)} yeni e-posta adresi eklendi.")
    else:
        print("Eklemek için yeni e-posta adresi bulunamadı.")

except Exception as e:
    print(f"Bir hata oluştu: {e}")

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import pytz

# PostgreSQL bağlantı bilgileri
DB_USER = 'postgres'
DB_PASSWORD = '258258258'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'cti_panel'

# SQLAlchemy bağlantı dizisi
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy engine oluştur
engine = create_engine(DATABASE_URL)

# Türkiye saat dilimini ayarla
turkey_tz = pytz.timezone('Europe/Istanbul')
current_time_turkey = datetime.now(turkey_tz)

# Yeni data_breach verisini DataFrame olarak oluştur
new_data = pd.DataFrame([{
    'company_name': 'totalstay',
    'type': 'email exposure',
    'date_published': datetime(2023, 11, 12),
    'description': '',  # Şimdilik boş
    'records_affected': 208,
    'created_at': current_time_turkey,
    'updated_at': None  # Henüz güncellenmediği için boş
}])

try:
    # DataFrame'i veritabanına ekle
    new_data.to_sql(
        'data_breach',  # Tablo adı
        engine,
        if_exists='append',  # Mevcut tabloya ekle
        index=False  # DataFrame'deki index sütununu ekleme
    )
    print("Yeni kayıt başarıyla eklendi.")

except Exception as e:
    print(f"Bir hata oluştu: {e}")

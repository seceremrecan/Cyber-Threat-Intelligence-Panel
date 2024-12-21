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
CSV_FILE_PATH = r"C:\Users\secer\OneDrive\Masaüstü\filtered_urls.csv"

# SQLAlchemy engine oluştur
engine = create_engine(DATABASE_URL)

# CSV'yi oku
df = pd.read_csv(CSV_FILE_PATH, header=None)  # `header=None` sütun adlarını göz ardı eder
df = df[[0]].rename(columns={0: 'address'})  # İlk sütunu 'address' olarak yeniden adlandır

# Türkiye saat dilimini ayarla
turkey_tz = pytz.timezone('Europe/Istanbul')
current_time_turkey = datetime.now(turkey_tz)

# Ek sütunları ekleyerek DataFrame'i hazırla
df['address_type'] = 'Domain'  # Adres tipini "Domain" olarak ayarla
df['created_time'] = current_time_turkey  # Türkiye saatine göre zamanı atayın
df['updated_time'] = None  # Güncelleme zamanı boş bırakılabilir
df['source'] = 'Phistank'  # Kaynak sütununa "USOM" yaz
df['malicious'] = 'Phishing'  # Kötücül davranışı "Phishing" olarak ayarla
df['is_valid'] = True  # Geçerli adres olarak işaretle

# Veritabanına ekleme veya güncelleme işlemi
try:
    # Veritabanındaki mevcut verileri çek
    existing_data = pd.read_sql('SELECT address FROM all_iocs', engine)

    # Yeni verilerle mevcut veriler arasındaki farkı bulun
    new_data = df[~df['address'].isin(existing_data['address'])]

    # Yeni verileri ekle
    if not new_data.empty:
        new_data.to_sql(
            'all_iocs',  # Tablo adı
            engine,
            if_exists='append',  # Mevcut tabloya ekle
            index=False  # DataFrame'deki index sütununu ekleme
        )
        print(f"{len(new_data)} yeni kayıt eklendi.")
    else:
        print("Eklemek için yeni veri bulunamadı.")

    # Mevcut verilerden güncellenmesi gerekenleri işle
    updated_data = df[df['address'].isin(existing_data['address'])]
    if not updated_data.empty:
        with engine.connect() as conn:
            for _, row in updated_data.iterrows():
                conn.execute(f"""
                    UPDATE all_iocs
                    SET updated_time = '{current_time_turkey}',
                        source = '{row['source']}',
                        malicious = '{row['malicious']}',
                        is_valid = {row['is_valid']}
                    WHERE address = '{row['address']}'
                """)
        print(f"{len(updated_data)} kayıt güncellendi.")

except Exception as e:
    print(f"Bir hata oluştu: {e}")

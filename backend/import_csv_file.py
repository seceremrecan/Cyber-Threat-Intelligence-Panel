import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import pytz  # Zaman dilimi desteği için eklenen kütüphane

# PostgreSQL bağlantı bilgileri
DB_USER = 'postgres'
DB_PASSWORD = '258258258'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'cti_panel'

# SQLAlchemy bağlantı dizisi
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# CSV dosyasının yolu
CSV_FILE_PATH = r"C:\Users\secer\OneDrive\Masaüstü\MaliciousIpAddress.csv"  

# SQLAlchemy engine oluştur
engine = create_engine(DATABASE_URL)

# CSV'yi oku, sütun adlarını yok say
df = pd.read_csv(CSV_FILE_PATH, header=None)  # `header=None` sütun adlarını göz ardı eder

# A sütununu al (ilk sütun olduğu için `df[0]`)
df = df[[0]].rename(columns={0: 'ip_address'})  # İlk sütunu 'ip_address' olarak yeniden adlandır

# Türkiye saat dilimini ayarlayın
turkey_tz = pytz.timezone('Europe/Istanbul')
current_time_turkey = datetime.now(turkey_tz)

# Ek sütunları ekleyerek DataFrame'i hazırlayın
df['created_time'] = current_time_turkey  # Türkiye saatine göre zamanı atayın
df['updated_time'] = None  # İsterseniz updated_time'ı boş bırakabilirsiniz
df['source'] = 'USOM'  # Kaynağı USOM olarak atayın
df['category'] = 'Phishing'  # Kategori olarak Phishing atayın
df['is_valid'] = True  # Varsayılan olarak geçerli kabul edin

# Veritabanına ekleme veya güncelleme işlemi
try:
    # Veritabanındaki mevcut verileri çek
    existing_data = pd.read_sql('SELECT ip_address FROM ip_ioc', engine)
    
    # Yeni verilerle mevcut veriler arasındaki farkı bulun
    new_data = df[~df['ip_address'].isin(existing_data['ip_address'])]
    
    # Yeni verileri ekle
    if not new_data.empty:
        new_data[['ip_address', 'created_time', 'updated_time', 'source', 'category', 'is_valid']].to_sql(
            'ip_ioc',  # Tablo adı
            engine,
            if_exists='append',  # Mevcut tabloya ekle
            index=False  # DataFrame'deki index sütununu ekleme
        )
        print(f"{len(new_data)} yeni kayıt eklendi.")
    else:
        print("Eklemek için yeni veri bulunamadı.")
    
    # Mevcut verilerden güncellenmesi gerekenleri işle
    updated_data = df[df['ip_address'].isin(existing_data['ip_address'])]
    if not updated_data.empty:
        with engine.connect() as conn:
            for _, row in updated_data.iterrows():
                conn.execute(f"""
                    UPDATE ip_ioc
                    SET updated_time = '{current_time_turkey}',
                        source = '{row['source']}',
                        category = '{row['category']}',
                        is_valid = {row['is_valid']}
                    WHERE ip_address = '{row['ip_address']}'
                """)
        print(f"{len(updated_data)} kayıt güncellendi.")

except Exception as e:
    print(f"Bir hata oluştu: {e}")

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False,  # Ortam değişkeni öneki gerekmez
    settings_files=[".env"],  # .env dosyasını oku
)

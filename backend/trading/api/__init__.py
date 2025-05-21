import os
from django.conf import settings

csv_data_path = os.path.join(settings.BASE_DIR, "csv_data")
config_path = os.path.join(settings.BASE_DIR, "config")

os.makedirs(csv_data_path, exist_ok=True)
os.makedirs(config_path, exist_ok=True)

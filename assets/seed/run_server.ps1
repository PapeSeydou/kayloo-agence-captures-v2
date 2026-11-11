$ErrorActionPreference = 'Stop'
$root = 'C:/Users/log/OneDrive/Bureau/SEPRO/kayloo_siteweb'
$db = ($root + '/.agents/capture-v2/capture.db') -replace '\\', '/'
$env:DATABASE_URL = 'sqlite+aiosqlite:///' + $db
$env:S3_ACCESS_KEY = ''
$env:S3_SECRET_KEY = ''
$env:S3_BUCKET = ''
$env:S3_ENDPOINT = ''
$env:EMAIL_ENABLED = 'false'
$env:ENVIRONMENT = 'dev'
$env:TESTING = 'true'
$env:ENABLE_STARTUP_SEED = 'false'
$env:UPLOAD_DIR = $root + '/app/static/uploads'
$env:APP_URL = 'http://kayloo.local:8000'
$env:KAYLOO_DOMAIN = 'kayloo.local:8000'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location ($root + '/app')
& ($root + '/.venv/Scripts/python.exe') -m uvicorn main:app --host 127.0.0.1 --port 8000 --log-level warning
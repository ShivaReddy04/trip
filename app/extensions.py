from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

csrf = CSRFProtect()
cors = CORS()

# ⭐ NEW — Database extensions
db = SQLAlchemy()
migrate = Migrate()

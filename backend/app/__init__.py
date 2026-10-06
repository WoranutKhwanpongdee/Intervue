import os

# Ensure pure python collections for compatibility across all environments
os.environ.setdefault("DISABLE_SQLALCHEMY_CEXT", "1")

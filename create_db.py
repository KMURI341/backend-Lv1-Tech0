# create_db.py
from database import Base, engine
import models  # ← ここが重要！モデルをロードしておく

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done!")

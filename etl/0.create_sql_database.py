import sqlalchemy as sa
import pandas as pd

e = sa.create_engine("sqlite:///raw_data.sqlite")
pd.read_csv("data/raw/applications.csv").to_sql("raw_data", e)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

user = os.environ["CONSOLIDADA_USER"]
host = os.environ["CONSOLIDADA_IP"]
port = os.environ["CONSOLIDADA_PORT"]
database = os.environ["CONSOLIDADA_DB"]
password = os.environ["CONSOLIDADA_PASS"]


class ConsolidadaConnection:
    @staticmethod
    def get_session():
        engine = create_engine(
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )
        consolidada_session = sessionmaker(bind=engine)
        return consolidada_session()

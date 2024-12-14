from sqlalchemy import create_engine, select, Select, Engine
import os


class DBConnector:
    def __init__(self, db_name: str = "temp"):
        if db_name == "temp":
            self.engine = self.__init_temp()
            self.test_connection(self.engine)

    def __init_temp(self):
        temp_user = os.environ["TEMP_USER"]
        temp_pass = os.environ["TEMP_PASS"]
        temp_db = os.environ["TEMP_DB"]
        temp_ip = os.environ["TEMP_IP"]
        temp_port = os.environ["TEMP_PORT"]
        engine = create_engine(
            f"postgresql+psycopg2://{temp_user}:{temp_pass}@{temp_ip}:{temp_port}/{temp_db}"
        )
        return engine

    def test_connection(self, engine: Engine) -> None:
        try:
            engine.connect()
            print("Conexión exitosa!")
        except Exception as e:
            print("Error de conexión: ", str(e))

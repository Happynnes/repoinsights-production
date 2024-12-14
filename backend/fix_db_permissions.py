from metabase.views.connector.create_role_and_policy import create_user_with_policy
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-name", required=True, help="User to be created in the database.")
    parser.add_argument("-password", required=True, help="Password for the new database user.")
    args = parser.parse_args()

    CONSOLIDADA_DATABASE = os.environ["CONSOLIDADA_DB"]
    CONSOLIDADA_USER = os.environ["CONSOLIDADA_USER"]
    CONSOLIDADA_IP = os.environ["CONSOLIDADA_IP"]
    CONSOLIDADA_PASSWORD = os.environ["CONSOLIDADA_PASS"]
    CONSOLIDADA_PORT = os.environ["CONSOLIDADA_PORT"]
    

    create_user_with_policy(
        dbname=CONSOLIDADA_DATABASE,
        dbuser=CONSOLIDADA_USER,
        dbhost=CONSOLIDADA_IP,
        dbpassword=CONSOLIDADA_PASSWORD,
        dbport=CONSOLIDADA_PORT,
        username=args.name,
        password=args.password,
    )

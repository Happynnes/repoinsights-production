from services.extract_service.config import GHToken
from loguru import logger
from pprint import pprint


def main():
    tokens = GHToken().get_public_tokens(only_token=False)
    for token, calls, time in tokens:
        logger.info(f"{token[-10:]}: {calls} {time}")


if __name__ == "__main__":
    main()

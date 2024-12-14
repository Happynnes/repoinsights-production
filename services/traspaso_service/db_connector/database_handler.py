from .connector import DBConnector
from .models import (
    User,
    Project,
    Commit,
    CommitParent,
    Issue,
    IssueComment,
    PullRequest,
    PullRequestComment,
    Watcher,
    ProjectMember,
)
from typing import List, Union, Dict, Any, Optional, Type
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger


class CreateError(Exception):
    pass


class DatabaseHandler:
    def __init__(self, connector: DBConnector):
        self.connector = connector
        self.session_maker_consolidada = sessionmaker(bind=connector.consolidada_engine)
        self.session_consolidada = self.session_maker_consolidada()

        self.session_maker_temp = sessionmaker(bind=connector.temp_engine)
        self.session_temp = self.session_maker_temp()

    def get_or_create(
        self,
        model: Type[
            Union[
                User,
                Project,
                Commit,
                CommitParent,
                Issue,
                IssueComment,
                PullRequest,
                PullRequestComment,
                Watcher,
            ]
        ],
        session: Session,
        create: Optional[bool] = True,
        many: Optional[bool] = False,
        **kwargs,
    ):
        query = session.query(model).filter_by(**kwargs)
        exist_instance = query.all() if many else query.first()

        if exist_instance:
            logger.debug("Instance already exists")
            return exist_instance
        elif create:
            try:
                logger.debug("Creating new instance")
                instance = model(**kwargs)
                session.add(instance)
                session.commit()
                return instance
            except Exception as e:
                logger.exception(f"Error creating: {e}", traceback=True)
                raise CreateError(e)
        else:
            logger.debug("Instance does not exist and not created")
            return None

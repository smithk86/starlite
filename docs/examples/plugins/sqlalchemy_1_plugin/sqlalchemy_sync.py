from typing import Optional

from sqlalchemy import Column, Float, Integer, String, select
from sqlalchemy.orm import Mapped, Session, declarative_base

from litestar import Litestar, get, post
from litestar.contrib.sqlalchemy_1.config import SQLAlchemyConfig
from litestar.contrib.sqlalchemy_1.plugin import SQLAlchemyPlugin
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND

Base = declarative_base()

sqlalchemy_config = SQLAlchemyConfig(connection_string="sqlite+pysqlite:///test.sqlite", use_async_engine=False)
sqlalchemy_plugin = SQLAlchemyPlugin(config=sqlalchemy_config)


class Company(Base):  # pyright: ignore
    __tablename__ = "company"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String)
    worth: Mapped[float] = Column(Float)


def on_startup() -> None:
    """Initialize the database."""
    Base.metadata.create_all(sqlalchemy_config.engine)  # type: ignore


@post(path="/companies")
def create_company(data: Company, db_session: Session) -> Company:
    """Create a new company and return it."""
    db_session.add(data)
    db_session.commit()
    return data


@get(path="/companies/{company_id:int}")
def get_company(company_id: str, db_session: Session) -> Company:
    """Get a company by its ID and return it.

    If a company with that ID does not exist, return a 404 response
    """
    company: Optional[Company] = db_session.scalars(select(Company).where(Company.id == company_id)).one_or_none()
    if not company:
        raise HTTPException(detail=f"Company with ID {company_id} not found", status_code=HTTP_404_NOT_FOUND)
    return company


app = Litestar(
    route_handlers=[create_company, get_company],
    on_startup=[on_startup],
    plugins=[sqlalchemy_plugin],
)

from sqlalchemy import String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.tasks import Task

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column (primary_key= True)
    
    title: Mapped[str] = mapped_column (
        String(255),
        nullable= False
    )
    
    description: Mapped[str | None] = mapped_column (
        Text,
        nullable= True
    )
    
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project"
    )
    
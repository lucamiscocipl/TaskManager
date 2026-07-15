from sqlalchemy import String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.projects import Project
from app.models.user import User

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key= True)
    
    title: Mapped[str] = mapped_column (
        
        String(255),
        nullable= False
    )
    
    description: Mapped[str | None] = mapped_column (
        Text,
        nullable= False
    )
    
    status: Mapped[str] = mapped_column (
        String(50),
        default= "Not Assigned",
        nullable= False
    )
    
    project_id: Mapped[int] = mapped_column (
        ForeignKey("projects.id"),
        nullable= False
    )
    
    user_id: Mapped[int] = mapped_column (
        ForeignKey = ("users.id"),
        nullable= False
    )
    
    project: Mapped["Project"] = relationship(
        back_populates="tasks"
    )
    
    assigned_user: Mapped["User | None"] = relationship(
        back_populates="tasks"
    )
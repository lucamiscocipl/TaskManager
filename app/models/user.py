from typing import TYPE_CHECKING

from sqlalchemy import String 
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.projects import Project
    from app.models.tasks import Task

class User (Base):
    __tablename__ = "users"
    
    id: Mapped [int] = mapped_column(primary_key= True )
    
    username: Mapped [str] = mapped_column(
        
        String(25),
        unique= True,
        nullable= False
    )
    
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="assigned_user"
    )

    hashed_password: Mapped[str] = mapped_column(
        String (255),
        nullable= False
    )
    
    owned_projects: Mapped [list["Project"]] = relationship (
        back_populates= "owner",
        foreign_keys="Project.owner_id"
    )

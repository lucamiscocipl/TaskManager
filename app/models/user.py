from sqlalchemy import String 
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
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
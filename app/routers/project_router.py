from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.projects import ProjectCreate, ProjectResponse
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.create_project(
        project_data=project_data,
        db=db,
        current_user=current_user,
    )


@router.get("", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return project_service.get_projects(db=db)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return project_service.get_project(project_id=project_id, db=db)

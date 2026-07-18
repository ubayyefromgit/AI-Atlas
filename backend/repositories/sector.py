from typing import Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from models.sector import Sector
from schemas.sector import SectorBase

class SectorRepository(BaseRepository[Sector, SectorBase, SectorBase]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Sector]:
        return db.query(Sector).filter(Sector.name == name, Sector.is_deleted == False).first()

sector_repo = SectorRepository(Sector)

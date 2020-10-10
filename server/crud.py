from sqlalchemy.orm import Session

import models
import schemas

def get_entity(db: Session, word: str):
    return db.query(models.NamedEntity).filter(models.NamedEntity.word == word).first()

#def get_users(db: Session, skip: int = 0, limit: int = 100):
#    return db.query(models.User).offset(skip).limit(limit).all()


def create_entity(db: Session, entity: schemas.NamedEntity):
    db_entity = models.NamedEntity(word=entity.word.lower(), score=entity.score, entity=entity.entity)
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


import argparse
import uvicorn
import os
from enum import Enum
from typing import Dict, List, Tuple

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import crud
import models
from schemas import *
from database import SessionLocal, engine

# from schemas import Tweet, NEROut, EntityTypeEnum, FakeNewsOut, NamedEntity

#from bert_fake_news.inference import BertFakeNews
#from bert_ner.inference import BertNER
#from bert_sexism_detection.inference import BertSexism

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
registered_entities = {}
#ner = BertNER("./bert_ner/model_save", gpu=False)
#fake_news = BertFakeNews("./bert_fake_news/model_save")
#sexism = BertSexism("./bert_sexism_detection/model_save")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.post("/ents")
def ent_recognition(tweet: Tweet, db: Session = Depends(get_db)):
    """Performs entity recognition with spacy & manually registered entities

    Args:
        tweet (Tweet): Tweet object that represents the text of a tweet
    Returns:
        response (NEROut): NEROut object that represents the list of found entities
    """
    text = tweet.text

    entities = ner.predict(text)
    for item in entities:
        word = item["word"]
        db_entity = crud.get_entity(db, word=word.lower())
        if db_entity:
            item["entity"] = db_entity.entity
            item["score"] = db_entity.score
        else:
            item["entity"] = item["entity"].replace("-", "_")

    response = NEROut(entities=entities)
    return response


@app.post("/create_entity", status_code=status.HTTP_201_CREATED)
def create_entity(entity: NamedEntity, db: Session = Depends(get_db)):
    """Manually register a known entity

    Args:
        entity (Entity): Entity object with label and text

    Returns:
        Response outlaying the success of registration
    """
    word = entity.word
    entity_type = entity.entity.replace(
        "-", "_"
    )  # make sure to replace hyphen with underscore
    if entity_type.lower() not in [x.name.lower() for x in EntityTypeEnum]:
        raise HTTPException(
            status_code=422, detail=f"{entity_type} is not a valid entity type"
        )
    else:
        db_entity = crud.get_entity(db, word=word.lower())
        if db_entity:
            raise HTTPException(status_code=400, detail=f"{word} is already registered")
        else:
            new_entity = NamedEntity(
                word=word, score=1.0, entity=entity.entity, index=-1
            )
            crud.create_entity(db, new_entity)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED, content="Successfully registered"
            )


@app.post("/fake_news_detection")
def fake_news_inference(tweet: Tweet):
    if type(tweet) != str:
        text = tweet.text
    else:
        text = tweet
    output = fake_news.predict(text)
    response = FakeNewsOut(is_fake=bool(output))

    return response


@app.post("/sexism_detection")
def fake_news_inference(tweet: Tweet):
    if type(tweet) != str:
        text = tweet.text
    else:
        text = tweet
    output = sexism.predict(text)
    response = SexismDetectionOut(is_fake=bool(output))

    return response

def main():
    parser = argparse.ArgumentParser(description="Run the server")
    parser.add_argument("--port", type=int, help="Port for server", default=7575)
    parser.add_argument("--dev", help="Run in development mode", action="store_false")
    args = parser.parse_args()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.dev,
    )

if __name__ == "__main__":
    main()

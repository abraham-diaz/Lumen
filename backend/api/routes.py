import os
from fastapi import APIRouter
from pydantic import BaseModel

from backend.query.rag import query
from backend.ingestion.projects import add_project
from backend.ingestion.indexer import index_file
router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class IndexRequest(BaseModel):
    project_name: str
    file_path: str

@router.post("/query")
def query_endpoint(request: QueryRequest):
    answer = query(request.query)
    return {"answer": answer}


@router.post("/index")
def index_endpoint(request: IndexRequest):
    project_id = add_project(request.project_name, request.file_path)
    files_indexed = 0
    for root, dirs, files in os.walk(request.file_path):
        for filename in files:
            if filename.endswith(".py"):
                file_path = os.path.join(root, filename)
                index_file(project_id, file_path)
                files_indexed += 1
    return {"project_id": project_id, "files_indexed": files_indexed}
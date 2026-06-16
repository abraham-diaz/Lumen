import os
import shutil
import stat

from fastapi import APIRouter
from pydantic import BaseModel

from backend.query.rag import query
from backend.ingestion.projects import add_project
from backend.ingestion.indexer import index_file
from backend.ingestion.git_clone import clone_repo

router = APIRouter()


def _force_remove(func, path, exc):
    # En Windows, git marca los objetos de .git como solo lectura;
    # quitamos ese atributo antes de reintentar borrar.
    os.chmod(path, stat.S_IWRITE)
    func(path)

class QueryRequest(BaseModel):
    query: str

class IndexRequest(BaseModel):
    project_name: str
    git_url: str

@router.post("/query")
def query_endpoint(request: QueryRequest):
    answer = query(request.query)
    return {"answer": answer}


@router.post("/index")
def index_endpoint(request: IndexRequest):
    temp_dir = clone_repo(request.git_url)
    files_indexed = 0
    try:
        project_id = add_project(request.project_name, request.git_url)
        for root, dirs, files in os.walk(temp_dir):
            for filename in files:
                if filename.endswith(".py"):
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, temp_dir)
                    index_file(project_id, file_path, relative_path)
                    files_indexed += 1
    finally:
        shutil.rmtree(temp_dir, onexc=_force_remove)
    return {"project_id": project_id, "files_indexed": files_indexed}
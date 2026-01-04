from pydantic import BaseModel
from typing import Optional

class RepoUrl(BaseModel):
    url: str
    language_topic: str
    files_extension: str
    options: Optional[dict] = None

class RepoUrlList(BaseModel):
    url_list: list[str]
    language_topic: str
    files_extension: str
    options: Optional[dict] = None

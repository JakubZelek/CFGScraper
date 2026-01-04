from fastapi import APIRouter, Depends
from url_app.api.dependencies import get_event_service
from common.services.process_url import ProcessUrlService
from common.schemas.url_app import RepoUrl, RepoUrlList

router = APIRouter()

@router.post("/scrap")
async def scrap_single_repo(repo_input: RepoUrl, service: ProcessUrlService = Depends(get_event_service)):
    status = await service.scrap_single_repo(repo_input)
    return status


@router.post("/scrap_multiple")
async def scrap_multiple_repos(repo_input: RepoUrlList, service: ProcessUrlService = Depends(get_event_service)):
    status = await service.scrap_multiple_repos(repo_input)
    return status

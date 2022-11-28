import os
import json
import requests
from requests import Response
from django.http import JsonResponse, HttpRequest
from .models import Project
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt

GITHUB_API_REPOSITORY_ENDPOINT = "https://api.github.com/user/repos"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/json",
}

# Create your views here.
@csrf_exempt
def index(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        projects = list(Project.objects.values())
        return JsonResponse(projects, safe=False)

    if request.method == "POST":
        body = json.loads(request.body)

        github_response = requests.post(
            GITHUB_API_REPOSITORY_ENDPOINT,
            headers=GITHUB_HEADERS,
            data=json.dumps(
                {
                    "name": body.get("name", "No-name-provided"),
                    "description": body.get("description", "No-description-provided"),
                    "private": False,
                }
            ),
        ).json()

        project = Project(
            name=body.get("name", "No-name-provided"),
            link=github_response.get("url"),
        )
        project.save()
        return JsonResponse(model_to_dict(project))


@csrf_exempt
def detail(request: HttpRequest, project_id: int) -> JsonResponse:
    if request.method == "GET":
        project = Project.objects.get(id=project_id)
        return JsonResponse(model_to_dict(project))

    if request.method == "DELETE":
        Project.objects.filter(id=project_id).delete()
        return JsonResponse({})

    if request.method == "POST":
        project = Project.objects.get(id=project_id)
        return JsonResponse(model_to_dict(project))

import os
import json
import requests
from requests import Response
from django.http import JsonResponse, HttpRequest
from .models import Project
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt

GITHUB_DOT_COM = "https://github.com"
GITHUB_API_URI = "https://api.github.com"
GITHUB_API_CREATE_REPO_ENDPOINT = f"{GITHUB_API_URI}/user/repos"
GITHUB_API_DELETE_REPO_ENDPOINT = f"{GITHUB_API_URI}/repos"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/json",
}

EC2_INSTANCE = "ec2-3-15-235-218.us-east-2.compute.amazonaws.com"

# Create your views here.
@csrf_exempt
def index(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        projects = list(Project.objects.values())
        return JsonResponse(projects, safe=False)

    if request.method == "POST":
        body = json.loads(request.body)

        github_response = requests.post(
            GITHUB_API_CREATE_REPO_ENDPOINT,
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
            link=github_response.get("html_url"),
        )
        project.save()
        return JsonResponse(model_to_dict(project))


@csrf_exempt
def detail(request: HttpRequest, project_id: int) -> JsonResponse:
    if request.method == "GET":
        project = Project.objects.get(id=project_id)
        return JsonResponse(model_to_dict(project) | {"ssh": EC2_INSTANCE})

    if request.method == "DELETE":
        project = Project.objects.get(id=project_id)

        user_slash_repo = project.link.split(GITHUB_DOT_COM)[-1]

        requests.delete(
            f"{GITHUB_API_DELETE_REPO_ENDPOINT}{user_slash_repo}",
            headers=GITHUB_HEADERS,
        )

        Project.objects.filter(id=project_id).delete()

        return JsonResponse({})

    if request.method == "POST":
        project = Project.objects.get(id=project_id)
        return JsonResponse(model_to_dict(project))

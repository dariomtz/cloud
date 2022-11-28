from django.http import JsonResponse, HttpRequest
from .models import Project
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def index(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        projects = list(Project.objects.values())
        return JsonResponse(projects, safe=False)

    if request.method == "POST":
        project = Project(
            name=request.POST.name, link="https://github.com/dariomtz/cloud"
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

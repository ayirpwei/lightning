from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import Http404

from loadgenomes.models import VarAnnotation

def index(request):
    trusted_annotation_list = VarAnnotation.objects.filter(source="library_generation")
    non_trusted_annotation_list = TileVarAnnotation.objects.filter(source="person")
    context = {
        'trusted_list': trusted_annotation_list,
        'uncertain_list': non_trusted_annotation_list,
        }
    return render(request, 'loadgenomes/index.html', context)

def detail(request, annotation_id):
    annotation = get_object_or_404(TileVarAnnotation, pk=annotation_id)
    return render(request, 'loadgenomes/detail.html', {'annotation' : annotation})

def review(request, annotation_id):
    annotation = get_object_or_404(TileVarAnnotation, pk=annotation_id)
    return render(request, 'loadgenomes/review.html', {'annotation' : annotation})

def annotate(request, tile_id):
    return HttpResponse("You are annotating tile %s" % tile_id)

def upload(request):
    return HttpResponse("You are uploading a new genome")

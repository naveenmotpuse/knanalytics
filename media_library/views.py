from django.http import HttpResponse
from django.shortcuts import render
from .models import MediaLibrary
from .models import MediaAsignments
from django.core.paginator import Paginator
import json

assigned_media_id = 0
reassigned_media_id = 0
isAdmin = True

def index(request):
    media_library_list = MediaLibrary.objects.all
    context = {"media_library_list": media_library_list}
    return HttpResponse(render(request, 'medialibrary/index.html', context))


def getAssignedMediaView(request):
    view_row_length = 3
    assigned_record_id = 1
    related_media_list = []
    assignment_id = "assignment_1"
    global assigned_media_id
    global reassigned_media_id
    original_record = None

    if request.method == "POST" and request.is_ajax():
        assigned_media_record = list(MediaLibrary.objects.filter(record_id=reassigned_media_id))
        original_media_record = list(MediaLibrary.objects.filter(record_id=assigned_media_id))
        if len(original_media_record) > 0:
            original_record = {"recommendation": original_media_record[0].recommendation.split(";"),
                               "record_id": original_media_record[0].record_id,
                               "record_title": original_media_record[0].record_title}
    else:
        assigned_record_id = request.GET.get('recordId', None)
        assignment_id = request.GET.get('assignmentId', None)
        custom_target = request.GET.get('customTarget', None)

        assigned_media_id = int(assigned_record_id)
        reassigned_media_id = 0
        assigned_media_record = list(MediaLibrary.objects.filter(record_id=assigned_record_id))

    if len(assigned_media_record) > 0:
        assigned_record = {"recommendation": assigned_media_record[0].recommendation.split(";"),
                           "record_id": assigned_media_record[0].record_id,
                           "record_title": assigned_media_record[0].record_title}

        assigned_recommendation_list = assigned_media_record[0].recommendation.split(";")
        media_library_list = MediaLibrary.objects.all()
        placeholder_listset = []
        placeholder_list = []

        for recommendation in assigned_recommendation_list:
            for media in media_library_list:
                existInRecord = False
                media_recommendation_list = media.recommendation.split(";")
                for mediameta in media_recommendation_list:
                    if set(recommendation).issubset(mediameta) and recommendation != "":
                        existInRecord = True
                if existInRecord and not media in placeholder_list and media != assigned_media_record[0]:
                    placeholder_list.append(media)
                    placeholder_listset.append(media)
                    if len(placeholder_listset) == view_row_length:
                        related_item = tuple(placeholder_listset)
                        related_media_list.append(related_item)
                        placeholder_listset = []
        if len(placeholder_listset) > 0:
            related_item = tuple(placeholder_listset)
            related_media_list.append(related_item)

    recommendation_list = getAllMediaRecommendations()

    all_media_list = getAllMediaListPage(1)
    all_media_pages_list = []
    for x in range(all_media_list.num_pages):
        all_media_pages_list.append(all_media_list.page((x+1)))

    media_length = 0
    if reassigned_media_id == 0:
        media_length = len(MediaLibrary.objects.all()) - 1
    else:
        media_length = len(MediaLibrary.objects.all()) - 2
    all_media_pages = {"allMedia": all_media_pages_list, "totalPages": all_media_list.num_pages,
                       "totalMedia": media_length}

    if reassigned_media_id == 0:
        original_record = assigned_record

        context = {"related_media_list": related_media_list, "assignment_id": assignment_id,
                   "custom_target": custom_target, "assigned_record": assigned_record,
                   "original_record": original_record,
                   "all_media_pages": all_media_pages,
                   "recommendation_list": recommendation_list, "assigned_media_id": assigned_media_id,
                   "reassigned_media_id": reassigned_media_id, "isAdmin": isAdmin}
    else:
        context = {"related_media_list": related_media_list, "assigned_record": assigned_record,
                   "original_record": original_record, "all_media_pages": all_media_pages,
                   "recommendation_list": recommendation_list, "assigned_media_id": assigned_media_id,
                   "reassigned_media_id": reassigned_media_id, "isAdmin": isAdmin}

    return HttpResponse(render(request, 'medialibrary/assignedMediaView.html', context))


def getAllMediaRecommendations():
    recommendations_list = []

    media_library_list = MediaLibrary.objects.all()

    for media in media_library_list:
        media_recommendations = media.recommendation.split(";")
        for recommendation in media_recommendations:
            if not recommendation in recommendations_list and recommendation != "":
                recommendations_list.append(recommendation)

    return recommendations_list


def getAllMediaListPage(pageId):
    view_row_length = 3
    placeholder_list = []
    placeholder_listset = []
    all_media_list = []

    global assigned_media_id
    global reassigned_media_id

    all_media = MediaLibrary.objects.all()
    for media in all_media:
        if media.record_id != assigned_media_id and media.record_id != reassigned_media_id and not media in placeholder_list:
            placeholder_list.append(media)
            placeholder_listset.append(media)
            if len(placeholder_listset) == view_row_length:
                media_triplet = tuple(placeholder_listset)
                all_media_list.append(media_triplet)
                placeholder_listset = []
    if len(placeholder_listset) > 0:
        media_triplet = tuple(placeholder_listset)
        all_media_list.append(media_triplet)

    paginator = Paginator(all_media_list, 2)
    return paginator


def getSearchMediaView(request):
    search_content = ""
    searchresults = ""
    if request.method == "POST" and request.is_ajax():
        search_content = request.POST.get('searchContent', "")
        show_partial_view = request.POST.get('showPartialView', None)

    if reassigned_media_id == 0:
        assigned_media_record = list(MediaLibrary.objects.filter(record_id=assigned_media_id))
    else:
        assigned_media_record = list(MediaLibrary.objects.filter(record_id=reassigned_media_id))

    view_row_length = 3
    media_library_list = MediaLibrary.objects.all()
    related_media_list = []
    placeholder_listset = []
    placeholder_list = []
    for media in media_library_list:
        existInRecord = False
        media_metadata = media.metadata
        media_title = media.record_title
        if search_content.lower() in media_metadata.lower() or search_content.lower() in media_title.lower() \
                and assigned_media_record[0] != media:
            if media_metadata != "" and media_title != "":
                existInRecord = True
        if existInRecord and not media in placeholder_list:
            placeholder_list.append(media)
            placeholder_listset.append(media)
            if len(placeholder_listset) == view_row_length:
                related_item = tuple(placeholder_listset)
                related_media_list.append(related_item)
                placeholder_listset = []
    if len(placeholder_listset) > 0:
        related_item = tuple(placeholder_listset)
        related_media_list.append(related_item)

    search_media = Paginator(related_media_list, 2)
    search_media_list = []
    for x in range(search_media.num_pages):
        search_media_list.append(search_media.page((x + 1)))

    all_media_list = getAllMediaListPage(1)
    all_media_pages_list = []
    for x in range(all_media_list.num_pages):
        all_media_pages_list.append(all_media_list.page((x + 1)))

    if show_partial_view == "show":
        all_media_pages = {"allMedia": search_media_list, "totalPages": search_media.num_pages,
                           "totalMedia": len(placeholder_list)}
    else:
        media_length = 0
        if reassigned_media_id == 0:
            media_length = len(MediaLibrary.objects.all()) - 1
        else:
            media_length = len(MediaLibrary.objects.all()) - 2
        all_media_pages = {"allMedia": all_media_pages_list, "totalPages": all_media_list.num_pages,
                           "totalMedia": media_length}

    context = {"all_media_pages": all_media_pages, "isSearch": "isSearch", "isAdmin": isAdmin}
    return HttpResponse(render(request, 'medialibrary/assignedMediaView.html', context))


def getFilterMediaView(request):
    view_row_length = 3
    assigned_record_id = 1
    show_partial_view = ""
    related_media_list = []
    assignment_id = "assignment_1"
    page_id = 1

    if request.method == "POST" and request.is_ajax():
        filter_content = request.POST.get('filterContent', None)
        show_partial_view = request.POST.get('showPartialView', None)

    if reassigned_media_id == 0:
        assigned_media_record = list(MediaLibrary.objects.filter(record_id=assigned_media_id))
    else:
        assigned_media_record = list(MediaLibrary.objects.filter(record_id=reassigned_media_id))

    media_library_list = MediaLibrary.objects.all()
    placeholder_listset = []
    placeholder_list = []

    if not filter_content is None:
        for media in media_library_list:
            existInRecord = False
            media_recommendation_list = media.recommendation.split(";")
            for mediameta in media_recommendation_list:
                if set(mediameta).issubset(filter_content) and mediameta != "":
                    existInRecord = True
            if existInRecord and not media in placeholder_list and media != assigned_media_record[0]:
                placeholder_list.append(media)
                placeholder_listset.append(media)
                if len(placeholder_listset) == view_row_length:
                    related_item = tuple(placeholder_listset)
                    related_media_list.append(related_item)
                    placeholder_listset = []
        if len(placeholder_listset) > 0:
            related_item = tuple(placeholder_listset)
            related_media_list.append(related_item)

        filter_media = Paginator(related_media_list, 2)
        filter_media_list = []
        for x in range(filter_media.num_pages):
            filter_media_list.append(filter_media.page((x + 1)))

    all_media_list = getAllMediaListPage(1)
    all_media_pages_list = []
    for x in range(all_media_list.num_pages):
        all_media_pages_list.append(all_media_list.page((x + 1)))

    if show_partial_view == "show":
        all_media_pages = {"allMedia": filter_media_list, "totalPages": filter_media.num_pages,
                           "totalMedia": len(placeholder_list)}
    else:
        media_length = 0
        if reassigned_media_id == 0:
            media_length = len(MediaLibrary.objects.all()) - 1
        else:
            media_length = len(MediaLibrary.objects.all()) - 2
        all_media_pages = {"allMedia": all_media_pages_list, "totalPages": all_media_list.num_pages,
                           "totalMedia": media_length}

    context = {"all_media_pages": all_media_pages, "isSearch": "isSearch", "isAdmin": isAdmin}
    return HttpResponse(render(request, 'medialibrary/assignedMediaView.html', context))


def getSaveAssignmentView(request):
    view_row_length = 3
    assigned_record_id = 1

    related_media_list = []

    if request.method == "POST" and request.is_ajax():
        global reassigned_media_id
        reassigned_media_id = int(request.POST.get('recordId', None))
        assignment_id = request.POST.get('assignmentId', None)
        custom_target = request.POST.get('customTarget', None)

    existingAssignment = list(MediaAsignments.objects.filter(assignment_id=assignment_id))
    if len(existingAssignment) > 0:
        MediaAsignments.objects.filter(assignment_id=assignment_id).update(media_record_id=reassigned_media_id)
    else:
        media_assignments = MediaAsignments(assignment_id=assignment_id, media_record_id=reassigned_media_id,
                                            custom_target=custom_target)
        media_assignments.save()

    return HttpResponse(getAssignedMediaView(request))


def getEditMediaView(request):
    if request.method == "POST" and request.is_ajax():
        global reassigned_media_id
        edit_media_id = int(request.POST.get('recordId', None))

    context = {"edit_media_id": edit_media_id}
    return HttpResponse(render(request, 'medialibrary/add_edit_assignment_view.html', context))


def getRequestedMediaJson(request):
    recordId = 1
    if request.method == "POST" and request.is_ajax():
        recordId = request.POST.get('record_Id')

    media_library_record = MediaLibrary.objects.filter(record_id=recordId)
    recordMCQ = ""
    videoInfo = ""
    for media in media_library_record:
        recordMCQ = media.media_mcq
        videoInfo = media.video_info

    if recordMCQ != "":
        recordMCQ = json.loads(recordMCQ)
        recordMCQ["LandingPageContent"] = videoInfo
        recordMCQ = json.dumps(recordMCQ)
        return HttpResponse(recordMCQ)
    else:
        return HttpResponse("No Records")


def setRequestedMediaJson(request):
    recordId = 1
    if request.method == "POST" and request.is_ajax():
        recordId = request.POST.get('record_Id')
        jsonData = request.GET.get('data', None)

    MediaLibrary.objects.filter(record_id=recordId).update(media_mcq=jsonData)
    return HttpResponse("Success")
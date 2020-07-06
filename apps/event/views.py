from django.shortcuts import render


def view_all_events(request):
    return render(request, 'all_events.html')


def view_event(request, id):
    pass


def edit_event(request, id):
    pass


def create_event(request):
    pass

from django.shortcuts import render


def view_artcc_map(request):
    return render(request, 'artcc_map.html', {'page_title': 'ARTCC Map'})


def view_scenery(request):
    return render(request, 'scenery.html', {'page_title': 'Scenery'})

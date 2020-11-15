from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.static import serve

from apps.administration import views as administration
from apps.api import views as api
from apps.event import views as event
from apps.feedback import views as feedback
from apps.pilots import views as pilots
from apps.resource import views as resource
from apps.training import views as training
from apps.uls import views as uls
from apps.user import views as user
from apps.views import views as views
from apps.visit import views as visit

urlpatterns = [
    # Administration
    path('admin/', administration.view_admin_panel, name='admin'),
    path('admin/log/', administration.view_action_log, name='log'),
    path('admin/transfers/', administration.view_transfers, name='transfer_requests'),
    path('admin/announcement/', administration.view_announcement, name='announcement'),
    path('admin/broadcast/', administration.view_broadcast, name='broadcast'),

    # API
    path('statistics/', api.view_statistics, name='statistics'),
    path('api/vatis/', api.update_atis, name='update_atis'),
    path('api/vatis/<str:icao>/', api.get_atis, name='get_atis'),
    path('api/tmi/', api.tmu_notice, name='tmu_notice')

    # Event
    path('events/', event.view_all_events, name='events'),
    path('events/archived/', event.view_archived_events, name='archived_events'),
    path('events/new/', event.add_event, name='new_event'),
    path('events/score/', event.view_event_score, name='event_score'),
    path('events/score/<int:cid>/', event.view_event_score, name='event_score_cid'),
    path('events/<int:event_id>/', event.view_event, name='event'),
    path('events/<int:event_id>/edit/', event.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', event.delete_event, name='delete_event'),
    path('events/<int:event_id>/add/', event.add_position, name='add_position'),
    path('events/position/<int:position_id>/request/', event.request_position, name='request_position'),
    path('events/position/<int:request_id>/unrequest/', event.unrequest_position, name='unrequest_position'),
    path('events/position/<int:request_id>/assign/', event.assign_position, name='assign_position'),
    path('events/position/<int:position_id>/assign/<int:cid>/', event.manual_assign, name='manual_assign_position'),
    path('events/position/<int:position_id>/unassign/', event.unassign_position, name='unassign_position'),
    path('events/position/<int:position_id>/delete/', event.delete_position, name='delete_position'),
    path('events/presets/', event.view_presets, name='presets'),
    path('events/presets/new/', event.add_preset, name='new_preset'),
    path('events/presets/edit/<int:preset_id>/', event.edit_preset, name='edit_preset'),
    path('events/presets/delete/<int:preset_id>/', event.delete_preset, name='delete_preset'),

    # Feedback
    path('feedback/', feedback.view_all_feedback, name='feedback'),
    path('feedback/new/', feedback.add_feedback, name='new_feedback'),
    path('feedback/approval/', feedback.view_feedback_approval, name='feedback_approval'),
    path('feedback/<int:feedback_id>/approve/', feedback.approve_feedback, name='accept_feedback'),
    path('feedback/<int:feedback_id>/reject/', feedback.reject_feedback, name='reject_feedback'),

    # Pilots
    path('map/', pilots.view_artcc_map, name='map'),
    path('scenery/', pilots.view_scenery, name='scenery'),
    path('scenery/new/', pilots.add_scenery, name='new_scenery'),
    path('scenery/<int:scenery_id>/edit/', pilots.edit_scenery, name='edit_scenery'),
    path('scenery/<int:scenery_id>/delete/', pilots.delete_scenery, name='delete_scenery'),

    # Resource
    path('resources/', resource.view_resources, name='resources'),
    path('resources/new/', resource.add_resource, name='new_resource'),
    path('resources/<int:resource_id>/edit/', resource.edit_resource, name='edit_resource'),
    path('resources/<int:resource_id>/delete/', resource.delete_resource, name='delete_resource'),

    # Training
    path('training/', training.view_training_center, name='training'),
    path('training/schedule/', training.request_training, name='request_training'),
    path('training/requests/', training.view_training_requests, name='training_requests'),
    path('training/requests/<int:request_id>/accept/', training.accept_training_request, name='accept_training'),
    path('training/requests/<int:request_id>/reject/', training.reject_training_request, name='reject_training'),
    path('training/requests/<int:request_id>/cancel/', training.cancel_training_request, name='cancel_training'),
    path('training/session/<int:session_id>/', training.view_session, name='view_session'),
    path('training/session/<int:session_id>/edit/', training.edit_session, name='edit_session'),
    path('training/session/<int:session_id>/file/', training.file_session, name='file_session'),
    path('training/mentors/', training.view_mentor_history, name='mentor_history'),
    path('training/scheduled/', training.view_scheduled_sessions, name='scheduled_sessions'),
    path('training/student/<int:cid>/', training.view_student_profile, name='student_profile'),

    # ULS (Auth)
    path('login/', uls.login, name='login'),
    path('logout/', uls.logout, name='logout'),

    # User
    path('staff/', user.view_staff, name='staff'),
    path('roster/', user.view_roster, name='roster'),
    path('roster/<int:cid>/', user.view_profile, name='view_user'),
    path('roster/<int:cid>/edit/', user.edit_user, name='edit_user'),
    path('roster/<int:cid>/editbio/', user.edit_bio, name='edit_bio'),
    path('roster/<int:cid>/editavatar/', user.edit_avatar, name='edit_avatar'),
    path('roster/<int:cid>/status/', user.update_status, name='edit_status'),
    path('roster/<int:cid>/addcomment/', user.add_comment, name='add_comment'),
    path('roster/<int:cid>/removecomment/', user.remove_comment, name='remove_comment'),
    path('roster/tidy/', user.view_inactive_users, name='roster_tidy'),
    path('roster/remove/', user.remove_users, name='remove_user'),

    # Views
    path('', views.view_homepage, name='home'),
    path('privacy/', views.view_privacy_policy, name='privacy'),
    path('calendar/', views.view_calendar, name='calendar'),

    # Visit
    path('visit/', visit.submit_visiting_request, name='visit'),
    path('visit/requests/', visit.view_visiting_requests, name='visit_requests'),
    path('visit/<int:visit_id>/accept/', visit.accept_visiting_request, name='accept_visit'),
    path('visit/<int:visit_id>/reject/', visit.reject_visiting_request, name='reject_visit'),

    path('django/', admin.site.urls),
]

# Allows access of media files such as documents and user profiles
urlpatterns += static(settings.MEDIA_URL, view=xframe_options_sameorigin(serve), document_root=settings.MEDIA_ROOT)

handler404 = 'apps.views.views.error_404'
handler500 = 'apps.views.views.error_500'
handler403 = 'apps.views.views.error_403'
handler400 = 'apps.views.views.error_400'

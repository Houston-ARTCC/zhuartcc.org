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
    path('admin/', administration.view_admin_panel),                    # View Admin Panel (STAFF)
    path('admin/log/', administration.view_action_log),                 # View Action Log (STAFF)
    path('admin/transfers/', administration.view_transfers),            # View VATUSA Transfer Requests (STAFF)
    path('admin/announcement/', administration.view_announcement),      # View Announcement Page (STAFF)
    path('admin/broadcast/', administration.view_broadcast),            # View Broadcast Page (STAFF)
    path('admin/broadcast/send/', administration.send_broadcast),       # Send Broadcast Email (POST / STAFF)

    # API
    path('stats/', api.view_statistics),                                # View Statistics

    # Event
    path('events/', event.view_all_events),                             # View Upcoming Events
    path('events/new/', event.add_event),                               # Add Event (POST / STAFF)
    path('events/archived/', event.view_archived_events),               # View Archived Events
    path('events/<int:id>/', event.view_event),                         # View Event
    path('events/<int:id>/edit/', event.edit_event),                    # Edit Event (STAFF)
    path('events/<int:id>/delete/', event.delete_event),                # Delete Event (POST / STAFF)
    path('events/request/<int:id>/', event.request_position),           # Request Position (POST / MEMBER)
    path('events/unrequest/<int:id>/', event.unrequest_position),       # Unrequest Postiion (POST / MEMBER)
    path('events/assign/<int:id>/', event.assign_position),             # Assign Positions (POST / STAFF)
    path('events/unassign/<int:id>/', event.unassign_position),         # Unassign Position Request (POST / STAFF)
    path('events/delete/<int:id>/', event.delete_position),             # Delete Position (POST / STAFF)
    path('events/new/<int:id>/', event.add_position),                   # Add Position (POST / STAFF)
    path('events/presets/', event.view_presets),                        # View Position Presets (STAFF)
    path('events/presets/new/', event.add_preset),                      # Add Position Preset (POST / STAFF)
    path('events/presets/edit/<int:id>/', event.edit_preset),           # Edit Position Preset (POST / STAFF)
    path('events/presets/delete/<int:id>/', event.delete_preset),       # Delete Position Preset (POST / STAFF)

    # Feedback
    path('feedback/', feedback.view_all_feedback),                      # View All Feedback
    path('feedback/new/', feedback.add_feedback),                       # Add New Feedback

    # Pilots
    path('map/', pilots.view_artcc_map),                                # View ARTCC Map
    path('scenery/', pilots.view_scenery),                              # View Scenery
    path('scenery/new/', pilots.add_scenery),                           # Add Scenery (POST / STAFF)
    path('scenery/edit/', pilots.edit_scenery),                         # Edit Scenery (POST / STAFF)
    path('scenery/delete/', pilots.delete_scenery),                     # Delete Scenery (POST / STAFF)

    # Resource
    path('resources/', resource.view_resources),                        # View Resources
    path('resources/new/', resource.add_resource),                      # Add Resource (POST / STAFF)
    path('resources/edit/', resource.edit_resource),                    # Edit Resource (POST / STAFF)
    path('resources/delete/', resource.delete_resource),                # Delete Resource (POST / STAFF)

    # Training
    path('training/', training.view_training_center),                   # View Training Center
    path('training/session/<int:id>/', training.view_session),          # View Training Session

    # ULS (Auth)
    path('login/', uls.login),                                          # Login via VATUSA ULS
    path('logout/', uls.logout),                                        # Logout + Delete Session Data

    # User
    path('staff/', user.view_staff),                                    # View Staff
    path('roster/', user.view_roster),                                  # View Roster
    path('roster/<int:cid>/', user.view_profile),                       # View User Profile
    path('roster/<int:cid>/edit/', user.edit_user),                     # Edit User (STAFF)
    path('roster/update/status/', user.update_status),                  # Change User Status (POST / STAFF)
    path('roster/tidy/', user.view_inactive_users),                     # Roster Tody (STAFF)
    path('roster/remove/', user.remove_users),                          # Remove Users (POST / STAFF)
    path('roster/<int:cid>/addcomment/', user.add_comment),             # Add Staff Comment (POST / STAFF)
    path('roster/<int:cid>/removecomment/', user.remove_comment),       # Remove Staff Comment (POST / STAFF)

    # Views
    path('', views.view_homepage),                                      # View Homepage
    path('privacy/', views.view_privacy_policy),                        # View Privacy Policy

    # Visit
    path('visit/', visit.submit_visiting_request),                      # Submit Visiting Request (LOGGED IN)
    path('admin/visits/', visit.view_visiting_requests),                # View All Visiting Requests (STAFF)
    path('admin/visits/accept/', visit.accept_visiting_request),        # Accept Visiting Request (POST / STAFF)
    path('admin/visits/reject/', visit.reject_visiting_request),        # Reject Visiting Request (POST / STAFF)

    path('django/', admin.site.urls),                                   # django Admin Panel
]

# Allows access of media files such as documents and user profiles
urlpatterns += static(settings.MEDIA_URL, view=xframe_options_sameorigin(serve), document_root=settings.MEDIA_ROOT)

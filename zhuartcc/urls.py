from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from apps.resource import views as resource
from apps.training import views as training
from apps.uls import views as uls
from apps.user import views as user
from apps.views import views as views
from apps.visit import views as visit

urlpatterns = [
    # Static Pages
    path('', views.view_homepage),                                     # View Homepage
    path('privacy/', views.view_privacy_policy),                       # View Privacy Policy

    # Authentication
    path('login/', uls.login),                                         # Login via VATUSA ULS
    path('logout/', uls.logout),                                       # Logout + Delete Session Data

    # User Management
    path('staff/', user.view_staff),                                   # View Staff
    path('roster/', user.view_roster),                                 # View Roster
    path('roster/<int:cid>/', user.view_user_profile),                 # View User Profile
    path('roster/<int:cid>/edit/', user.edit_user),                    # Edit User
    path('visit/', visit.submit_visiting_request),                     # Submit Visiting Request

    # Resource Management
    path('resources/', resource.view_resources),                       # View Resources
    path('resources/add/', resource.add_resource),                     # Add Resource (POST)
    path('resources/edit/', resource.edit_resource),                   # Edit Resource (POST)
    path('resources/delete/', resource.delete_resource),               # Delete Resource (POST)

    # Training Management
    path('training/', training.view_training_center),                  # View Training Center Home
    path('training/schedule/', training.schedule),                     # View Session Details
    path('training/history/<int:cid>/', training.view_history),        # View Session Details

    # Admin Panel
    path('admin/', views.view_admin_panel),                            # View Main Admin Panel
    path('admin/visit/', visit.view_visiting_requests),                # View Visiting Requests
    path('admin/visit/accept/', visit.accept_visiting_request),        # Accept Visiting Request (POST)
    path('admin/visit/reject/', visit.reject_visiting_request),        # Reject Visiting Request (POST)

    path('django/', admin.site.urls),                                  # django Admin Panel
    # Resource
    path('resources/', resource.view_resources),                        # View Resources
    path('resources/add/', resource.add_resource),                      # Add Resource (POST)
    path('resources/edit/', resource.edit_resource),                    # Edit Resource (POST)
    path('resources/delete/', resource.delete_resource),                # Delete Resource (POST)

    # Training
    path('training/', training.view_training_center),                   # View Training Center Home
    path('training/schedule/', training.schedule),                      # View Session Details
    path('training/history/<int:cid>/', training.view_history),         # View Session Details

    # ULS (Auth)
    path('login/', uls.login),                                          # Login via VATUSA ULS
    path('logout/', uls.logout),                                        # Logout + Delete Session Data

    # User
    path('staff/', user.view_staff),                                    # View Staff
    path('roster/', user.view_roster),                                  # View Roster
    path('roster/<int:cid>/', user.view_user_profile),                  # View User Profile
    path('roster/<int:cid>/edit/', user.edit_user),                     # Edit User
    path('visit/', visit.submit_visiting_request),                      # Submit Visiting Request

    # Views
    path('', views.view_homepage),                                      # View Homepage
    path('privacy/', views.view_privacy_policy),                        # View Privacy Policy

    path('django/', admin.site.urls),                                   # django Admin Panel
]

# Allows access of media files such as documents and user profiles
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views


urlpatterns = [
    path('', views.AdListView.as_view(), name='ad_list'),

    path('ads/new/', views.AdCreateView.as_view(), name='ad_create'),
    path('ads/<int:pk>/edit/', views.AdEditView.as_view(), name='ad_edit'),
    path('ads/<int:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),

    path('register', views.RegisterView.as_view(), name='register'),

    path('proposals/', views.ProposalListView.as_view(), name='proposal_list'),

    path('proposals/<int:ad_id>/new/', views.ProposalCreateView.as_view(), name='proposal_create'),
    path('proposals/<int:pk>/accept/', views.proposal_accept, name='proposal_accept'),
    path('proposals/<int:pk>/reject/', views.proposal_reject, name='proposal_reject'),



]

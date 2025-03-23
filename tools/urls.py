from django.urls import path
from tools import views

urlpatterns = [
    path("",views.ToolsViewClass.as_view(),name="home"),
    path("type/<str:slug>/",views.Category,name="cat"),
    path("new-tool/",views.FetchUrlData,name="new-tool"),
    path("manual-newtool/",views.addToolManual,name="add-tool-manual"),
    path("tags/",views.Tags,name="new-tool"),
    path("search/",views.SearchTool.as_view(),name="search"),
    path('api/search/', views.search_suggestions, name='search_tools'),
]

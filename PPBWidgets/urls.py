from django.urls import path
from . import views

'''
For configuring URL
views is a Python module
e.g path('search/',views.search) can match www.xxx.com/search
'''
urlpatterns = [
    path('', views.index, name="index"),
    path('search/', views.search, name="search"),
    path('search_result/<str:gene_id>',
         views.search_result, name="search_result"),
    path("blast", views.blast, name="blast"),
    path("blastResult/<str:token>", views.blast_result, name="blast_result"),
    path("geneStructure/", views.geneStructure),
    path("download/",views.download,name="download"),
    path("search_species/<str:species>",views.search_species,name='search_species'),
    path("jbrowse/",views.jbrowse_index,name='jbrowse_index'),
    path("jbrowse/<str:species>",views.jbrowse_species,name='jbrowse_species'),
    path("jbrowse/<str:species>/<str:file>",views.jbrowse_static_file,name="jbrowse_static_file"),
]

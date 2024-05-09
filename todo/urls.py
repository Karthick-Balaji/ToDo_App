from django.urls import path
from todo import views

urlpatterns = [
    path("", views.home, name="home"),
    path("addTask", views.addTask, name="home"),
    path("getAllTasks", views.getAllTasks, name="home"),
    path("editTask", views.editTask, name="home"),
    path("completeTask", views.completeTask, name="home"),
    path("cancelTask", views.cancelTask, name="home"),
    path("login", views.login, name="login")
]
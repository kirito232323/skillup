from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login.php', views.login_view, name='login'),
    path('logout.php', views.logout_view, name='logout'),
    path('session.php', views.session_view, name='session'),
    path('api/get_dashboard_stats.php', views.get_dashboard_stats, name='get_dashboard_stats'),
    path('api/get_recommendations.php', views.get_recommendations, name='get_recommendations'),
    path('api/get_skill_gaps.php', views.get_skill_gaps, name='get_skill_gaps'),
    path('api/get_trainees.php', views.get_trainees, name='get_trainees'),
    path('api/get_user_skills.php', views.get_user_skills, name='get_user_skills'),
    path('api/create_user.php', views.create_user, name='create_user'),
    path('api/get_users.php', views.get_users, name='get_users'),
    path('api/reset_user_password.php', views.reset_user_password, name='reset_user_password'),
    path('api/get_training_modules.php', views.get_training_modules, name='get_training_modules'),
    path('api/add_training_module.php', views.add_training_module, name='add_training_module'),
    path('api/update_training_module_status.php', views.update_training_module_status, name='update_training_module_status'),
    path('api/delete_training_module.php', views.delete_training_module, name='delete_training_module'),
    path('api/create_evaluation_form.php', views.create_evaluation_form, name='create_evaluation_form'),
    path('api/get_evaluation_forms.php', views.get_evaluation_forms, name='get_evaluation_forms'),
    path('api/submit_evaluation.php', views.submit_evaluation, name='submit_evaluation'),
]

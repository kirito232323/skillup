import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from .models import (
    EmployeeSkill,
    EvaluationAnswer,
    EvaluationForm,
    EvaluationQuestion,
    EvaluationSubmission,
    JobRole,
    Recommendation,
    Skill,
    SkillGapLog,
    SkillUpUser,
    TrainingModule,
)


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()

    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.account_role,
                'job_role': user.job_role.role_name if user.job_role else '',
            }
        })

    return JsonResponse({'success': False, 'message': 'Invalid credentials'})


def logout_view(request):
    logout(request)
    return redirect('/')


def session_view(request):
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True, 'user_id': request.user.id})
    return JsonResponse({'authenticated': False})


def get_dashboard_stats(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)

    try:
        user = SkillUpUser.objects.get(pk=user_id)
    except SkillUpUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    skills_count = EmployeeSkill.objects.filter(user=user).count()
    recommendations_count = Recommendation.objects.filter(user=user).count()
    gaps_count = SkillGapLog.objects.filter(user=user, gap_score__gt=0).count()

    return JsonResponse({
        'skills': skills_count,
        'recommendations': recommendations_count,
        'gaps': gaps_count,
    })


def get_recommendations(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)

    try:
        user = SkillUpUser.objects.get(pk=user_id)
    except SkillUpUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    records = Recommendation.objects.filter(user=user).select_related('module')
    data = []
    for rec in records:
        data.append({
            'recommendation_id': rec.id,
            'status': rec.status,
            'title': rec.module.title,
            'description': rec.module.description,
            'duration_hours': str(rec.module.duration_hours) if rec.module.duration_hours is not None else '',
        })

    return JsonResponse(data, safe=False)


def get_skill_gaps(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)

    try:
        user = SkillUpUser.objects.get(pk=user_id)
    except SkillUpUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    records = SkillGapLog.objects.filter(user=user).select_related('skill')
    gaps = [
        {
            'skill_name': rec.skill.skill_name,
            'gap_score': rec.gap_score,
            'analysis_date': rec.analysis_date.isoformat(),
        }
        for rec in records
    ]

    return JsonResponse(gaps, safe=False)


def get_trainees(request):
    trainees = SkillUpUser.objects.filter(account_role='trainee').select_related('job_role').order_by('first_name')
    data = [
        {
            'id': trainee.id,
            'first_name': trainee.first_name,
            'last_name': trainee.last_name,
            'email': trainee.email,
            'job_role': trainee.job_role.role_name if trainee.job_role else '',
            'account_role': trainee.account_role,
        }
        for trainee in trainees
    ]

    return JsonResponse({'success': True, 'count': len(data), 'trainees': data})


def get_user_skills(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)

    try:
        user = SkillUpUser.objects.get(pk=user_id)
    except SkillUpUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    records = EmployeeSkill.objects.filter(user=user).select_related('skill')
    skills = [
        {
            'skill_name': rec.skill.skill_name,
            'current_proficiency_level': rec.current_proficiency_level,
        }
        for rec in records
    ]

    return JsonResponse(skills, safe=False)


def _parse_request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return {}
    return request.POST.dict()


@csrf_exempt
def create_user(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    data = _parse_request_data(request)
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', '').strip().lower()
    job_title = data.get('job_title', '').strip() or 'General'
    track = data.get('track', '').strip()
    password = data.get('password', '').strip()

    if not first_name or not last_name or not email or not role or not password:
        return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

    if SkillUpUser.objects.filter(email=email).exists():
        return JsonResponse({'success': False, 'message': 'User already exists'}, status=409)

    job_role, _ = JobRole.objects.get_or_create(role_name=job_title)
    user = SkillUpUser.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        account_role=role,
        job_role=job_role,
        track=track,
        is_staff=(role == 'admin')
    )

    return JsonResponse({'success': True, 'user_id': user.id})


def get_users(request):
    users = SkillUpUser.objects.select_related('job_role').order_by('first_name')
    data = [
        {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.account_role,
            'job_title': user.job_role.role_name if user.job_role else '',
            'track': user.track,
        }
        for user in users
    ]
    return JsonResponse({'success': True, 'users': data})


@csrf_exempt
def reset_user_password(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    data = _parse_request_data(request)
    email = data.get('email', '').strip()
    new_password = data.get('password', '').strip()

    if not email or not new_password:
        return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

    try:
        user = SkillUpUser.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return JsonResponse({'success': True})
    except SkillUpUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)


@csrf_exempt
def get_training_modules(request):
    modules = TrainingModule.objects.all().order_by('title')
    data = [
        {
            'id': module.id,
            'title': module.title,
            'track': module.track,
            'domain': module.target_skill.category if module.target_skill else '',
            'summary': module.description,
            'hours': float(module.duration_hours) if module.duration_hours else 0,
            'provider': module.provider,
            'status': module.status,
        }
        for module in modules
    ]
    return JsonResponse({'success': True, 'modules': data})


@csrf_exempt
def add_training_module(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    data = _parse_request_data(request)
    title = data.get('title', '').strip()
    track = data.get('track', '').strip() or 'All Tracks'
    domain = data.get('domain', '').strip() or 'General'
    hours = data.get('hours')
    summary = data.get('summary', '').strip()
    provider = data.get('provider', 'SkillUp Learning Registry').strip()

    if not title or not summary:
        return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

    skill, _ = Skill.objects.get_or_create(skill_name=domain, defaults={'category': 'Technical', 'description': domain})
    module = TrainingModule.objects.create(
        title=title,
        track=track,
        target_skill=skill,
        duration_hours=hours or 0,
        description=summary,
        provider=provider,
        status='Active'
    )

    return JsonResponse({'success': True, 'module_id': module.id})


@csrf_exempt
def update_training_module_status(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    data = _parse_request_data(request)
    module_id = data.get('id')
    status = data.get('status')

    if not module_id or status not in ['Active', 'Inactive']:
        return JsonResponse({'success': False, 'message': 'Invalid parameters'}, status=400)

    try:
        module = TrainingModule.objects.get(pk=module_id)
        module.status = status
        module.save()
        return JsonResponse({'success': True})
    except TrainingModule.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Module not found'}, status=404)


@csrf_exempt
def delete_training_module(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    data = _parse_request_data(request)
    module_id = data.get('id')

    if not module_id:
        return JsonResponse({'success': False, 'message': 'Invalid parameters'}, status=400)

    try:
        module = TrainingModule.objects.get(pk=module_id)
        module.delete()
        return JsonResponse({'success': True})
    except TrainingModule.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Module not found'}, status=404)


@csrf_exempt
def create_evaluation_form(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    data = _parse_request_data(request)
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    target_course = data.get('targetCourse', '').strip() or 'All Tracks'
    questions = data.get('questions', [])
    created_by_id = data.get('created_by')

    if not title or not questions:
        return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

    user = None
    if created_by_id:
        try:
            user = SkillUpUser.objects.get(pk=created_by_id)
        except SkillUpUser.DoesNotExist:
            pass

    form = EvaluationForm.objects.create(
        title=title,
        description=description,
        target_course=target_course,
        created_by=user,
    )

    for question in questions:
        q_type = question.get('type')
        q_text = question.get('text', '').strip()
        if not q_type or not q_text:
            continue
        metadata = {}
        if q_type == 'mc':
            metadata = {
                'options': question.get('options', []),
                'correct_answer': question.get('correctAns', '')
            }
            q_type = 'multiple_choice'
        elif q_type == 'paragraph':
            q_type = 'short_answer'
        elif q_type == 'scale':
            q_type = 'rating_scale'
        EvaluationQuestion.objects.create(
            form=form,
            question_text=q_text,
            question_type=q_type,
            metadata=metadata,
        )

    return JsonResponse({'success': True, 'form_id': form.id})


def get_evaluation_forms(request):
    forms = EvaluationForm.objects.order_by('-created_at')
    data = []

    for form in forms:
        questions = []
        for q in form.evaluationquestion_set.all():
            question = {
                'id': q.id,
                'text': q.question_text,
                'type': 'scale' if q.question_type == 'rating_scale' else 'paragraph' if q.question_type == 'short_answer' else 'mc',
                'metadata': q.metadata or {},
                'options': q.metadata.get('options', []) if q.metadata else [],
            }
            if q.question_type == 'multiple_choice':
                question['options'] = q.metadata.get('options', []) if q.metadata else []
                question['correctAns'] = q.metadata.get('correct_answer', '') if q.metadata else ''
            questions.append(question)

        submissions = []
        for submission in form.evaluationsubmission_set.all():
            answers = []
            for answer in submission.evaluationanswer_set.all():
                answers.append({
                    'questionText': answer.question.question_text,
                    'type': answer.question.question_type,
                    'userAnswer': answer.answer_text,
                })
            submissions.append({
                'userEmail': submission.user.email,
                'userName': submission.user.full_name,
                'submittedAt': submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                'isGraded': False,
                'assignedTotalScore': 'Awaiting Verification',
                'answers': answers,
            })

        data.append({
            'id': form.id,
            'title': form.title,
            'description': form.description,
            'targetCourse': form.target_course,
            'questions': questions,
            'submittedResponsesLogs': submissions,
        })

    return JsonResponse({'success': True, 'forms': data})


@csrf_exempt
def submit_evaluation(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    data = _parse_request_data(request)
    form_id = data.get('form_id')
    user_id = data.get('user_id')
    answers = data.get('answers', [])

    if not form_id or not user_id or not answers:
        return JsonResponse({'success': False, 'message': 'Missing required fields'}, status=400)

    try:
        form = EvaluationForm.objects.get(pk=form_id)
        user = SkillUpUser.objects.get(pk=user_id)
    except (EvaluationForm.DoesNotExist, SkillUpUser.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Form or user not found'}, status=404)

    submission = EvaluationSubmission.objects.create(form=form, user=user)
    for answer_data in answers:
        question_id = answer_data.get('question_id')
        text = answer_data.get('answer', '')
        if not question_id:
            continue
        try:
            question = EvaluationQuestion.objects.get(pk=question_id, form=form)
            EvaluationAnswer.objects.create(submission=submission, question=question, answer_text=text)
        except EvaluationQuestion.DoesNotExist:
            continue

    return JsonResponse({'success': True, 'submission_id': submission.id})

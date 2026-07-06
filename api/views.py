from django.http import HttpResponse, HttpRequest, JsonResponse

from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm
from .models import Hobby, CustomUser, FriendRelationships
from django.core.paginator import Paginator


def main_spa(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return render(request, 'api/spa/index.html', {})
    else:
        return redirect('login')

@ensure_csrf_cookie
@login_required
@require_http_methods(['GET'])
def set_csrf_token(request):
    """
    We set the CSRF cookie on the frontend.
    """
    return JsonResponse({'message': 'CSRF cookie set'})

@login_required
@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out'})


@login_required
@require_http_methods(['GET'])
def user(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {'username': request.user.username, 'email': request.user.email, 'name': request.user.name}
        )
    return JsonResponse(
        {'message': 'Not logged in'}, status=401
    )


def login_view(request:HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
            
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'auth/login.html')


def signup_view(request:HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CreateUserForm()
    return render(request, 'auth/signup.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def hobbies_list(request) -> JsonResponse:
    if request.method == 'GET':
        hobbies = Hobby.objects.all()
        return JsonResponse({
            'hobbies': [hobby.as_dict() for hobby in hobbies]
        })
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        hobby = Hobby.objects.create(
            hobby_name=data['hobby_name'],
        )
        return JsonResponse(hobby.as_dict())


@login_required
@require_http_methods(['GET'])
def similar_users(request) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Get age filter parameters from query string
    min_age = request.GET.get('min_age')
    max_age = request.GET.get('max_age')
    
    # Get current user's hobbies
    current_user_hobbies = set(request.user.hobbies.values_list('id', flat=True))
    
    # Get all users except current user
    users = CustomUser.objects.exclude(id=request.user.id)
    
    # Apply age filtering if parameters are provided
    from datetime import date
    current_year = date.today().year
    
    if min_age:
        try:
            min_birth_year = current_year - int(min_age)
            users = users.filter(date_of_birth__year__lte=min_birth_year)
        except ValueError:
            pass
            
    if max_age:
        try:
            max_birth_year = current_year - int(max_age)
            users = users.filter(date_of_birth__year__gte=max_birth_year)
        except ValueError:
            pass
    
    # Calculate shared hobbies for each user
    users_with_similarity = []
    for user in users:
        user_hobbies = set(user.hobbies.values_list('id', flat=True))
        shared_hobbies = len(current_user_hobbies & user_hobbies)
        
        user_dict = user.as_dict()
        user_dict['shared_hobbies_count'] = shared_hobbies
        users_with_similarity.append(user_dict)

    # Sort users by shared hobbies count (descending)
    users_with_similarity.sort(key=lambda x: -x['shared_hobbies_count'])

    paginator = Paginator(users_with_similarity, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    users_with_similarity_page = list(page_obj.object_list)
    total_pages = paginator.num_pages
    
    return JsonResponse({
        'similar_users': users_with_similarity_page,
        'total_pages': total_pages,
    })

@login_required
@require_http_methods(['GET', 'PUT'])
def user_info(request) -> JsonResponse:
    if request.method == 'GET':
        user = request.user
        return JsonResponse({
            'username': user.username,
            'password': user.password,
            'email': user.email,
            'name': user.name,
            'date_of_birth': user.date_of_birth,
            'hobbies': [hobby.as_dict() for hobby in user.hobbies.all()],
            'friends': [friend.id for friend in user.friends.all()]
        })
    
    elif request.method == 'PUT':
        data = json.loads(request.body)
        user = request.user
        user.name = data['name']
        user.email = data['email']
        user.username = data['username']
        if (user.password != data['password']):
            user.set_password(data['password'])
        user.date_of_birth = data['date_of_birth']
        user.hobbies.clear()
        hobby_ids = [hobby['id'] if isinstance(hobby, dict) else hobby for hobby in data['hobbies']]
        for hobby_id in hobby_ids:
            hobby = Hobby.objects.get(id=hobby_id)
            user.hobbies.add(hobby)
        user.save()
        return JsonResponse(user.as_dict())
    
    
@login_required
@require_http_methods(['GET', 'POST'])
def friend_relationships(request):
    if request.method == 'GET':
        relationships = FriendRelationships.objects.filter(
            sender=request.user
        ) | FriendRelationships.objects.filter(
            receiver=request.user
        )
        
        return JsonResponse({
            'relationships': [{
                'id': rel.id,
                'sender': {
                    'id': rel.sender.id,
                    'name': rel.sender.name
                },
                'receiver': {
                    'id': rel.receiver.id,
                    'name': rel.receiver.name
                },
                'status': rel.status,
                'created_at': rel.created_at
            } for rel in relationships],
            'current_user_id': request.user.id
        })
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        receiver_id = data.get('receiver_id')
        
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
            
            existing_relationship = FriendRelationships.objects.filter(
                sender=request.user, 
                receiver=receiver,
                status__in=['pending', 'accepted']
            ).first() or FriendRelationships.objects.filter(
                sender=receiver, 
                receiver=request.user,
                status__in=['pending', 'accepted']
            ).first()
            
            if existing_relationship:
                return JsonResponse(
                    {'error': 'Active relationship already exists'}, 
                    status=400
                )
            
            relationship, created = FriendRelationships.objects.update_or_create(
                sender=request.user,
                receiver=receiver,
                defaults={'status': 'pending'}
            )
            
            return JsonResponse({
                'id': relationship.id,
                'sender': {
                    'id': relationship.sender.id,
                    'name': relationship.sender.name
                },
                'receiver': {
                    'id': relationship.receiver.id,
                    'name': relationship.receiver.name
                },
                'status': relationship.status,
                'created_at': relationship.created_at
            })
            
        except CustomUser.DoesNotExist:
            return JsonResponse(
                {'error': 'Receiver not found'}, 
                status=404
            )

@login_required
@require_http_methods(['PUT'])
def update_friend_relationship(request, relationship_id):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        if status not in ['accepted', 'rejected']:
            return JsonResponse(
                {'error': 'Invalid status'}, 
                status=400
            )
            
        relationship = FriendRelationships.objects.get(id=relationship_id)
        
        # Verify the current user is the receiver
        if relationship.receiver.id != request.user.id:
            return JsonResponse(
                {'error': 'Not authorized to update this relationship'}, 
                status=403
            )
            
        relationship.status = status
        relationship.save()
        
        return JsonResponse({
            'id': relationship.id,
            'sender': {
                'id': relationship.sender.id,
                'name': relationship.sender.name
            },
            'receiver': {
                'id': relationship.receiver.id,
                'name': relationship.receiver.name
            },
            'status': relationship.status,
            'created_at': relationship.created_at
        })
        
    except FriendRelationships.DoesNotExist:
        return JsonResponse(
            {'error': 'Relationship not found'}, 
            status=404
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid JSON'}, 
            status=400
        )
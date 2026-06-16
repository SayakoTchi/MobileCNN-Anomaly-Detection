from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import Post

# Create your views here.
def connect(request):
    return render(request, 'blog/connect.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # DB에 유저 저장
            login(request, user) # 가입 즉시 자동 로그인 처리
            return redirect('dashboard')
    else:
        form = UserCreationForm()
        
    return render(request, 'blog/signup.html', {'form' : form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # 유저 인증 및 세션 로그인
            user = form.get_user()
            login(request, user)
            return redirect('dashboard') # 로그인 성공 시 대시보드로 이동
    else:
        form = AuthenticationForm()
    
    return render(request, 'blog/login.html', {'form': form})


@login_required
def dashboard_view(request):
    # 로그인 후 진입하는 메인 대시보드
    return render(request, 'blog/index.html')

@login_required
def anomaly_view(request):
    return render(request, 'blog/Anomaly.html')

@login_required
def history_view(request):
    return render(request, 'blog//History.html')

@login_required
def settings_view(request):
    return render(request, 'blog/settings.html')


def index(request):
    posts = Post.objects.all()

    return render(
        request,
        'blog/index.html',
        {
            'posts' : posts,
        }
    )
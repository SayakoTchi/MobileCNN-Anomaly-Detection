from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.pk}{self.pk}]"
    
# 1. AI 이상징후/배회 탐지 로그 모델
class AnomalyLog(models.Model):
    LEVEL_CHOICES = [
        (1, '1단계 (최고위험)'),
        (2, '2단계 (주요경보)'),
        (3, '3단계 (일반주의)'),
    ]
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    confidence = models.FloatField()  # 예: 0.964 (96.4%)
    message = models.TextField()      # YOLOv8 분석 요약 문구
    video_file = models.CharField(max_length=255, blank=True, null=True) # 비디오 파일 경로/이름
    is_permanent = models.BooleanField(default=False) # 영구 저장 여부

# 2. 시스템 예외/오류 로그 모델 (History용)
class SystemExceptionLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField()     # Error Level (1~5)
    file_name = models.CharField(max_length=100) # 예: inference_engine.py
    line_number = models.IntegerField()
    message = models.TextField()
    code_snippet = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False) # 해결 여부

from rest_framework import serializers
from django.contrib.auth.models import User
from coderr_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    location = serializers.CharField(default='', allow_blank=True)
    tel = serializers.CharField(default='', allow_blank=True)
    description = serializers.CharField(default='', allow_blank=True)
    working_hours = serializers.CharField(default='', allow_blank=True)

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',            
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]
        read_only_fields = ['user', 'type', 'created_at']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
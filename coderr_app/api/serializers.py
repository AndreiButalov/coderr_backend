from rest_framework import serializers
from django.contrib.auth.models import User
from coderr_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    
    # Default = '', allow_blank=True sorgt dafür, dass Response nie null ist
    first_name = serializers.CharField(default='', allow_blank=True, required=False)
    last_name = serializers.CharField(default='', allow_blank=True, required=False)
    location = serializers.CharField(default='', allow_blank=True, required=False)
    tel = serializers.CharField(default='', allow_blank=True, required=False)
    description = serializers.CharField(default='', allow_blank=True, required=False)
    working_hours = serializers.CharField(default='', allow_blank=True, required=False)

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
        user_data = validated_data.pop('user', {})

        user = instance.user
        email = user_data.get('email')
        if email is not None:
            user.email = email
            user.save()

        for attr, value in validated_data.items():
            if value is None:
                value = ''
            setattr(instance, attr, value)
        instance.save()

        return instance
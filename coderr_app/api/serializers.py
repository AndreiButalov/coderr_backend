from rest_framework import serializers
from django.contrib.auth.models import User
from coderr_app.models import Profile, OfferDetail, Offer, Order, Review
from rest_framework.reverse import reverse


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)    
    first_name = serializers.CharField(default='', allow_blank=True, required=False)
    last_name = serializers.CharField(default='', allow_blank=True, required=False)
    file = serializers.ImageField(required=False, allow_null=True)
    location = serializers.CharField(default='', allow_blank=True, required=False)
    tel = serializers.CharField(default='', allow_blank=True, required=False)
    description = serializers.CharField(default='', allow_blank=True, required=False)
    working_hours = serializers.CharField(default='', allow_blank=True, required=False)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel',
            'description', 'working_hours', 'type', 'email', 'created_at'
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
    


class ProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(default='', allow_blank=True, required=False)
    last_name = serializers.CharField(default='', allow_blank=True, required=False)
    location = serializers.CharField(default='', allow_blank=True, required=False)
    tel = serializers.CharField(default='', allow_blank=True, required=False)
    description = serializers.CharField(default='', allow_blank=True, required=False)
    working_hours = serializers.CharField(default='', allow_blank=True, required=False)

    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'location', 'tel', 'description', 'working_hours', 'email'
            ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data and 'email' in user_data:
            instance.user.email = user_data['email']
            instance.user.save()

        for attr, value in validated_data.items():
            if value is None:
                value = ''
            setattr(instance, attr, value)
        instance.save()
        return instance


class BusinessProfileSerializer(ProfileSerializer, serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel',
            'description', 'working_hours', 'type'
            ]
        
    read_only_fields = ['user', 'type']


class CustomerProfileSerializer(ProfileSerializer, serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'type']
        
    read_only_fields = ['user', 'type']



class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']



class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        return reverse('offer-detail', args=[obj.id], request=request)


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_min_price(self, obj):
        details = obj.details.all()
        if details.exists():
            return min([d.price for d in details])
        return 0

    def get_min_delivery_time(self, obj):
        details = obj.details.all()
        if details.exists():
            return min([d.delivery_time_in_days for d in details])
        return 0

    def get_user_details(self, obj):
        user = obj.user
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username
        }


class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate(self, attrs):
        details = attrs.get('details', [])

        if len(details) != 3:
            raise serializers.ValidationError(
                "Ein Offer muss genau 3 Details enthalten."
            )

        offer_types = [d.get('offer_type') for d in details]
        required_types = {'basic', 'standard', 'premium'}

        if set(offer_types) != required_types:
            raise serializers.ValidationError(
                "Es müssen genau die offer_types 'basic', 'standard' und 'premium' enthalten sein."
            )

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        details_data = validated_data.pop('details')

        offer = Offer.objects.create(
            user=request.user,
            **validated_data
        )

        for detail in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail
            )

        return offer

    


class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')

                if not offer_type:
                    raise serializers.ValidationError({"details": "offer_type muss angegeben werden."})

                try:
                    detail_instance = instance.details.get(offer_type=offer_type)
                except OfferDetail.DoesNotExist:
                    raise serializers.ValidationError({"details": f"Detail mit offer_type '{offer_type}' existiert nicht."})

                detail_data.pop('offer_type', None)

                for attr, value in detail_data.items():
                    setattr(detail_instance, attr, value)

                detail_instance.save()

        return instance

class OfferDetailViewSerializer(OfferSerializer, serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at',
            'updated_at', 'details', 'min_price', 'min_delivery_time',
        ]


class OfferPatchSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']



class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at',
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 
                  'delivery_time_in_days', 'price', 'features', 'offer_type', 
                  'status', 'created_at', 'updated_at']

        read_only_fields = fields

    @classmethod
    def create_from_offer_detail(cls, offer_detail, customer_user):
        return cls.Meta.model.objects.create(
            customer_user=customer_user,
            business_user=offer_detail.offer.user,
            offer=offer_detail.offer,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress'
        )
    

class OrderCreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 
                  'delivery_time_in_days', 'price', 'features', 'offer_type', 
                  'status', 'created_at']

        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        try:
            offer_detail = OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError("OfferDetail existiert nicht.")
        return value



class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        allowed_statuses = ['in_progress', 'completed', 'cancelled']
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Ungültiger Status. Erlaubt: {allowed_statuses}")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]



class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['business_user', 'rating', 'description']

    def validate(self, attrs):
        user = self.context['request'].user
        business = attrs['business_user']

        if not hasattr(user, 'profile') or user.profile.type != 'customer':
            raise serializers.ValidationError("Nur Kunden dürfen bewerten.")

        if not hasattr(business, 'profile') or business.profile.type != 'business':
            raise serializers.ValidationError("Kein gültiger Geschäftsbenutzer.")

        if Review.objects.filter(business_user=business, reviewer=user).exists():
            raise serializers.ValidationError("Bereits bewertet.")

        return attrs

    def create(self, validated_data):
        return Review.objects.create(
            reviewer=self.context['request'].user,
            **validated_data
        )
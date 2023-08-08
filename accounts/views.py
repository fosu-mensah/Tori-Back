from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter, KakaoProvider
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_username

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import PasswordChangeView
from dj_rest_auth.serializers import PasswordResetConfirmSerializer
from dj_rest_auth.views import sensitive_post_parameters_m
from dj_rest_auth.app_settings import api_settings

from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


from .serializers import SMSSendSerializer, SMSAuthConfirmSerializer
from .models import SMSAuthentication
from .permissions import IsUserInfoMatched


class CustomPasswordResetView(generics.GenericAPIView):
    """
    Calls Django Auth SetPasswordForm save method.

    Accepts the following POST parameters: new_password1, new_password2
    Returns the success/fail message.
    """
    serializer_class = api_settings.PASSWORD_CHANGE_SERIALIZER
    permission_classes = (IsUserInfoMatched,)
    throttle_scope = 'dj_rest_auth'

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('New password has been saved.')})

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_signup_form_initial_data(self, sociallogin):
        user = sociallogin.user
        initial = {
            "username": user_username(user) or "",
        }
        return initial

class SMSAuthSendView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SMSSendSerializer
    
    def post(self, request):
        data = request.data
        
        serializer = SMSSendSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        sms_auth = SMSAuthentication.objects.filter(phone_number=serializer.validated_data['phone_number'])
        
        if sms_auth:
            sms_auth.delete()
        SMSAuthentication.objects.create(phone_number=serializer.validated_data['phone_number'], is_authenticated = False)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class SMSAuthConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SMSAuthConfirmSerializer
    def post(self, request):
        data = request.data
        serializer = SMSAuthConfirmSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        auth_number = serializer.validated_data['auth_number']
        
        result = SMSAuthentication.check_auth_number(phone_number, auth_number)
        
        SMSAuthentication.objects.filter(phone_number=phone_number).update(is_authenticated=result)
        return Response({'success': result, 'data': serializer.data}, status=status.HTTP_200_OK)

class FindUserNameView(APIView):
    pass
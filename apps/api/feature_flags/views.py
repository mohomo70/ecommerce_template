from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import FeatureFlag


@api_view(['GET'])
@permission_classes([AllowAny])
def get_feature_flags(request):
    """Get all feature flags for frontend."""
    flags = FeatureFlag.objects.all()
    flags_dict = {flag.name: flag.is_enabled for flag in flags}
    return Response(flags_dict)
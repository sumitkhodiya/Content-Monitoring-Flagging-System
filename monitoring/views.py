"""
API views for the content monitoring system.

Endpoints:
- POST /keywords/          - Create a new keyword
- POST /scan/             - Trigger a scan
- GET /flags/             - List flags
- PATCH /flags/{id}/      - Update flag status
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Avg
from django.views.generic import TemplateView

from monitoring.models import Keyword, Flag
from monitoring.serializers import (
    KeywordSerializer, 
    FlagSerializer, 
    FlagUpdateSerializer,
    ScanRequestSerializer
)
from monitoring.services import ScanService


class KeywordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing keywords.
    
    Endpoints:
    - GET /keywords/           - List all keywords
    - POST /keywords/          - Create new keyword
    - GET /keywords/{id}/      - Retrieve specific keyword
    - PUT /keywords/{id}/      - Update keyword
    - DELETE /keywords/{id}/   - Delete keyword
    """
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    
    def get_queryset(self):
        """Get all keywords, optionally filtered by name."""
        queryset = Keyword.objects.all()
        
        # Support filtering by name substring
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset


class ScanAPIView(APIView):
    """
    API endpoint to trigger a content scan.
    
    POST /api/scan/
    {
        "source": "mock" | "newsapi"
    }
    """
    
    def post(self, request):
        """
        Trigger a scan against the specified source.
        
        Returns scan statistics including:
        - content_items_processed
        - flags_created
        - flags_updated
        - flags_suppressed
        """
        serializer = ScanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        source = serializer.validated_data['source']
        
        try:
            stats = ScanService.run_scan(source)
            return Response(
                {
                    'success': True,
                    'message': f'Scan completed for source: {source}',
                    'stats': stats
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class FlagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing flags.
    
    Endpoints:
    - GET /flags/                    - List all flags
    - POST /flags/                   - Create flag (shouldn't be used directly, created by scan)
    - GET /flags/{id}/               - Retrieve specific flag
    - PATCH /flags/{id}/             - Update flag status
    """
    queryset = Flag.objects.select_related('keyword', 'content_item')
    serializer_class = FlagSerializer
    
    def get_queryset(self):
        """
        Get flags with optional filters.
        
        Query parameters:
        - status: Filter by status (pending, relevant, irrelevant)
        - keyword_id: Filter by keyword
        - min_score: Filter by minimum score
        - ordering: Order by field (default: -score)
        """
        queryset = Flag.objects.select_related('keyword', 'content_item')
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by keyword
        keyword_id = self.request.query_params.get('keyword_id')
        if keyword_id:
            queryset = queryset.filter(keyword_id=keyword_id)
        
        # Filter by minimum score
        min_score = self.request.query_params.get('min_score')
        if min_score:
            try:
                queryset = queryset.filter(score__gte=int(min_score))
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_serializer_class(self):
        """Use FlagUpdateSerializer for updates, FlagSerializer for reads."""
        if self.request.method in ['PATCH', 'PUT']:
            return FlagUpdateSerializer
        return FlagSerializer
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH request to update flag status."""
        flag = self.get_object()
        serializer = self.get_serializer(flag, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return updated flag with full serializer
        return Response(
            FlagSerializer(flag).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending flags (convenience endpoint)."""
        flags = self.get_queryset().filter(status='pending')
        serializer = FlagSerializer(flags, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about flags."""
        total = Flag.objects.count()
        by_status = {}
        for status_choice in ['pending', 'relevant', 'irrelevant']:
            count = Flag.objects.filter(status=status_choice).count()
            by_status[status_choice] = count
        
        return Response({
            'total_flags': total,
            'by_status': by_status,
        })


class DashboardView(TemplateView):
    """
    Serves the frontend dashboard.
    
    GET /
    """
    template_name = 'index.html'

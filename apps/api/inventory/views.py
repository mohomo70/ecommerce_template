from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import StockAdjustment, LowStockAlert, InventoryReport, StockMovement
from .serializers import (
    StockAdjustmentSerializer, LowStockAlertSerializer, InventoryReportSerializer,
    StockMovementSerializer, StockLevelSerializer, InventoryValuationSerializer
)
from catalog.models import ProductVariant


class StockAdjustmentListView(generics.ListCreateAPIView):
    """List and create stock adjustments."""
    
    serializer_class = StockAdjustmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StockAdjustment.objects.select_related('variant', 'user').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StockAdjustmentDetailView(generics.RetrieveAPIView):
    """Get stock adjustment details."""
    
    serializer_class = StockAdjustmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StockAdjustment.objects.select_related('variant', 'user')


class LowStockAlertListView(generics.ListAPIView):
    """List low stock alerts."""
    
    serializer_class = LowStockAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        status_filter = self.request.query_params.get('status', 'active')
        return LowStockAlert.objects.filter(
            status=status_filter
        ).select_related('variant', 'acknowledged_by').order_by('-created_at')


class LowStockAlertDetailView(generics.RetrieveUpdateAPIView):
    """Get and update low stock alert."""
    
    serializer_class = LowStockAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LowStockAlert.objects.select_related('variant', 'acknowledged_by')


class InventoryReportListView(generics.ListAPIView):
    """List inventory reports."""
    
    serializer_class = InventoryReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return InventoryReport.objects.select_related('generated_by').order_by('-generated_at')


class StockMovementListView(generics.ListAPIView):
    """List stock movements."""
    
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = StockMovement.objects.select_related('variant').order_by('-created_at')
        
        # Filter by variant if provided
        variant_id = self.request.query_params.get('variant_id')
        if variant_id:
            queryset = queryset.filter(variant_id=variant_id)
        
        # Filter by movement type if provided
        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_levels(request):
    """Get current stock levels for all variants."""
    variants = ProductVariant.objects.filter(track_inventory=True).select_related('product')
    
    stock_levels = []
    for variant in variants:
        # Check if variant has low stock alert
        low_stock_alert = LowStockAlert.objects.filter(
            variant=variant, status='active'
        ).first()
        
        # Determine status
        if variant.stock_quantity <= 0:
            status = 'out_of_stock'
        elif low_stock_alert:
            status = 'low_stock'
        else:
            status = 'in_stock'
        
        # Get last movement
        last_movement = StockMovement.objects.filter(
            variant=variant
        ).order_by('-created_at').first()
        
        stock_levels.append({
            'variant_id': variant.id,
            'sku': variant.sku,
            'product_name': variant.product.name,
            'current_stock': variant.stock_quantity,
            'threshold': low_stock_alert.threshold if low_stock_alert else 10,
            'status': status,
            'last_movement': last_movement.created_at if last_movement else None,
        })
    
    serializer = StockLevelSerializer(stock_levels, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_valuation(request):
    """Get inventory valuation report."""
    variants = ProductVariant.objects.filter(
        track_inventory=True,
        stock_quantity__gt=0
    ).select_related('product')
    
    valuation_data = []
    total_value = 0
    
    for variant in variants:
        # Use cost_price if available, otherwise use price * 0.6 as estimated cost
        unit_cost = variant.cost_price or (variant.price * 0.6)
        total_value += variant.stock_quantity * unit_cost
        
        valuation_data.append({
            'variant_id': variant.id,
            'sku': variant.sku,
            'product_name': variant.product.name,
            'quantity': variant.stock_quantity,
            'unit_cost': unit_cost,
            'total_value': variant.stock_quantity * unit_cost,
        })
    
    serializer = InventoryValuationSerializer(valuation_data, many=True)
    return Response({
        'items': serializer.data,
        'total_value': total_value,
        'total_items': len(valuation_data),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stock_adjustment(request):
    """Create a stock adjustment."""
    serializer = StockAdjustmentSerializer(data=request.data)
    if serializer.is_valid():
        # Get variant
        variant = get_object_or_404(ProductVariant, id=serializer.validated_data['variant_id'])
        
        # Check if adjustment would result in negative stock
        new_quantity = variant.stock_quantity + serializer.validated_data['quantity']
        if new_quantity < 0:
            return Response(
                {'error': 'Adjustment would result in negative stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create adjustment
        adjustment = serializer.save(user=request.user)
        
        # Create stock movement record
        StockMovement.objects.create(
            variant=variant,
            movement_type='adjustment',
            quantity=serializer.validated_data['quantity'],
            reference=serializer.validated_data.get('reference', ''),
            notes=serializer.validated_data.get('reason', ''),
        )
        
        # Check for low stock alert
        check_low_stock_alert(variant)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_low_stock_alert(request, alert_id):
    """Acknowledge a low stock alert."""
    alert = get_object_or_404(LowStockAlert, id=alert_id)
    alert.acknowledge(request.user)
    
    serializer = LowStockAlertSerializer(alert)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_inventory_report(request):
    """Generate an inventory report."""
    report_type = request.data.get('report_type')
    title = request.data.get('title', f'{report_type.title()} Report')
    
    if report_type == 'stock_levels':
        data = get_stock_levels_data()
    elif report_type == 'movement':
        data = get_stock_movement_data()
    elif report_type == 'valuation':
        data = get_inventory_valuation_data()
    elif report_type == 'low_stock':
        data = get_low_stock_data()
    else:
        return Response(
            {'error': 'Invalid report type'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    report = InventoryReport.objects.create(
        report_type=report_type,
        title=title,
        data=data,
        generated_by=request.user,
    )
    
    serializer = InventoryReportSerializer(report)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def check_low_stock_alert(variant, threshold=10):
    """Check if variant needs a low stock alert."""
    if variant.stock_quantity <= threshold:
        # Check if there's already an active alert
        existing_alert = LowStockAlert.objects.filter(
            variant=variant,
            status='active'
        ).first()
        
        if not existing_alert:
            LowStockAlert.objects.create(
                variant=variant,
                threshold=threshold,
                current_stock=variant.stock_quantity,
            )


def get_stock_levels_data():
    """Get stock levels data for report."""
    variants = ProductVariant.objects.filter(track_inventory=True)
    return [
        {
            'sku': variant.sku,
            'product_name': variant.product.name,
            'current_stock': variant.stock_quantity,
            'status': 'low' if variant.stock_quantity <= 10 else 'normal',
        }
        for variant in variants
    ]


def get_stock_movement_data():
    """Get stock movement data for report."""
    movements = StockMovement.objects.select_related('variant').order_by('-created_at')[:100]
    return [
        {
            'sku': movement.variant.sku,
            'product_name': movement.variant.product.name,
            'movement_type': movement.movement_type,
            'quantity': movement.quantity,
            'reference': movement.reference,
            'created_at': movement.created_at.isoformat(),
        }
        for movement in movements
    ]


def get_inventory_valuation_data():
    """Get inventory valuation data for report."""
    variants = ProductVariant.objects.filter(track_inventory=True, stock_quantity__gt=0)
    total_value = 0
    
    data = []
    for variant in variants:
        unit_cost = variant.cost_price or (variant.price * 0.6)
        total_value += variant.stock_quantity * unit_cost
        
        data.append({
            'sku': variant.sku,
            'product_name': variant.product.name,
            'quantity': variant.stock_quantity,
            'unit_cost': float(unit_cost),
            'total_value': float(variant.stock_quantity * unit_cost),
        })
    
    return {
        'items': data,
        'total_value': float(total_value),
        'total_items': len(data),
    }


def get_low_stock_data():
    """Get low stock data for report."""
    alerts = LowStockAlert.objects.filter(status='active').select_related('variant')
    return [
        {
            'sku': alert.variant.sku,
            'product_name': alert.variant.product.name,
            'current_stock': alert.current_stock,
            'threshold': alert.threshold,
            'created_at': alert.created_at.isoformat(),
        }
        for alert in alerts
    ]
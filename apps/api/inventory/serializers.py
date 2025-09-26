from rest_framework import serializers
from .models import StockAdjustment, LowStockAlert, InventoryReport, StockMovement
from catalog.serializers import ProductVariantSerializer


class StockAdjustmentSerializer(serializers.ModelSerializer):
    """Serializer for StockAdjustment model."""
    
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = StockAdjustment
        fields = [
            'id', 'variant', 'variant_id', 'adjustment_type', 'quantity',
            'reason', 'reference', 'user', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_quantity(self, value):
        """Validate quantity based on adjustment type."""
        adjustment_type = self.initial_data.get('adjustment_type')
        if adjustment_type in ['out', 'damage', 'theft'] and value > 0:
            raise serializers.ValidationError(
                'Quantity must be negative for stock out adjustments'
            )
        elif adjustment_type in ['in', 'return'] and value < 0:
            raise serializers.ValidationError(
                'Quantity must be positive for stock in adjustments'
            )
        return value


class LowStockAlertSerializer(serializers.ModelSerializer):
    """Serializer for LowStockAlert model."""
    
    variant = ProductVariantSerializer(read_only=True)
    acknowledged_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = LowStockAlert
        fields = [
            'id', 'variant', 'threshold', 'current_stock', 'status',
            'acknowledged_by', 'acknowledged_at', 'created_at'
        ]
        read_only_fields = ['id', 'acknowledged_by', 'acknowledged_at', 'created_at']


class InventoryReportSerializer(serializers.ModelSerializer):
    """Serializer for InventoryReport model."""
    
    generated_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = InventoryReport
        fields = [
            'id', 'report_type', 'title', 'description', 'data',
            'generated_by', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_by', 'generated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for StockMovement model."""
    
    variant = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'variant', 'movement_type', 'quantity',
            'reference', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StockLevelSerializer(serializers.Serializer):
    """Serializer for stock level data."""
    
    variant_id = serializers.IntegerField()
    sku = serializers.CharField()
    product_name = serializers.CharField()
    current_stock = serializers.IntegerField()
    threshold = serializers.IntegerField()
    status = serializers.CharField()
    last_movement = serializers.DateTimeField()


class InventoryValuationSerializer(serializers.Serializer):
    """Serializer for inventory valuation data."""
    
    variant_id = serializers.IntegerField()
    sku = serializers.CharField()
    product_name = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_value = serializers.DecimalField(max_digits=10, decimal_places=2)

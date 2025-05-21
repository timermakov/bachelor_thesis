from rest_framework import serializers

from ..models import Position, Target


class TargetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    position = serializers.PrimaryKeyRelatedField(required=False, queryset=Position.objects.all())

    class Meta:
        model = Target
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True)

    class Meta:
        model = Position
        fields = ('id', 'base_asset', 'quote_asset', 'entry_point', 'stop_loss', 'quantity', 'targets')

    def create(self, validated_data):
        targets_data = validated_data.pop('targets')
        position = Position.objects.create(**validated_data)
        for target in targets_data:
            Target.objects.create(position=position, **target)
        return position

    def update(self, instance, validated_data):
        targets_data = validated_data.pop('targets')
        position = super(PositionSerializer, self).update(instance, validated_data)

        target_ids = [target.get('id') for target in targets_data if target.get('id', None)]
        Target.objects.filter(position_id=position.id).exclude(id__in=target_ids).delete()

        for target in targets_data:
            target_id = target.pop('id', None)
            target['position'] = position
            Target.objects.update_or_create(id=target_id, defaults=target)

        return position

from rest_framework import serializers

from ..models.queue import Queue

class QueueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Queue
        fields = [
            'id',
            'guid',
            'document',
            'parser',
            'queue_class',
            'input_result',
            'parsed_result',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """ Create a queue. """
        queue = Queue.objects.create(**validated_data)

        return queue

    def update(self, instance, validated_data):
        """ Update queue. """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


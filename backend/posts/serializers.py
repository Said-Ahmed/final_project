from rest_framework import serializers

from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'category', 'content', 'image', 'created_at', 'updated_at')
        read_only_fields = ['created_at', 'updated_at', 'author']

    def to_representation(self, instance):
        request = self.context.get('request')

        base_url = request.build_absolute_uri('/')[:-1].strip("/")

        representation = super().to_representation(instance)
        representation['created_at'] = instance.created_at.strftime('%d.%m.%Y, %H:%M')
        representation['updated_at'] = instance.updated_at.strftime('%d.%m.%Y, %H:%M')
        if instance.image and hasattr(instance.image, 'url'):
            representation['image'] = base_url + instance.image.url
        else:
            representation['image'] = 'null'

        if instance.category:
            representation['category'] = {
                'id': instance.category.id,
                'name': instance.category.name
            }
        else:
            representation['category'] = 'null'

        return {'posts': representation}


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def to_representation(self, instance):
        request = self.context.get('request')
        base_url = request.build_absolute_uri('/')[:-1].strip("/")

        representation = super().to_representation(instance)
        representation['created_at'] = instance.created_at.strftime('%d.%m.%Y, %H:%M')
        representation['updated_at'] = instance.updated_at.strftime('%d.%m.%Y, %H:%M')
        if instance.author.profile.photo and hasattr(instance.author.profile.photo, 'url'):
            representation['author_photo'] = base_url + instance.author.profile.photo.url
        else:
            representation['author_photo'] = 'null'

        return {
            'comment': representation
        }

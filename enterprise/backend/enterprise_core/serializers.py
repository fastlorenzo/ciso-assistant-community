from django.conf import settings
from rest_framework import serializers
from core.serializers import (
    BaseModelSerializer,
    UserWriteSerializer as CommunityUserWriteSerializer,
)
from core.serializer_fields import FieldsRelatedField
from iam.models import Folder, User

from .models import ClientSettings
from auditlog.models import LogEntry

import structlog

logger = structlog.get_logger(__name__)


class FolderWriteSerializer(BaseModelSerializer):
    class Meta:
        model = Folder
        exclude = [
            "builtin",
            "content_type",
        ]

    def validate_parent_folder(self, parent_folder):
        """
        Check that the folders graph will not contain cycles
        """
        if not self.instance:
            return parent_folder
        if parent_folder:
            if (
                parent_folder == self.instance
                or parent_folder in self.instance.get_sub_folders()
            ):
                raise serializers.ValidationError(
                    "errorFolderGraphMustNotContainCycles"
                )
        return parent_folder


class EditorPermissionMixin:
    @staticmethod
    def check_editor_permissions(instance, group):
        editor_prefixes = {"add_", "change_", "delete_"}
        editors = User.get_editors()
        seats = settings.LICENSE_SEATS

        perms = group.permissions
        if any(perm.startswith(prefix) for prefix in editor_prefixes for perm in perms):
            logger.info("Adding editor permissions to user", user=instance, group=group)
            if instance not in editors and len(editors) >= seats:
                logger.error(
                    "License seats exceeded, cannot add editor user groups to user",
                    user=instance,
                    seats=seats,
                )
                raise serializers.ValidationError(
                    {"user_groups": "errorLicenseSeatsExceeded"}
                )


class UserWriteSerializer(CommunityUserWriteSerializer, EditorPermissionMixin):
    def _update_user_groups(self, instance, validated_data):
        if validated_data.get("user_groups"):
            logger.info(
                "Updating user groups",
                user=instance,
                groups=validated_data["user_groups"],
            )
            for group in validated_data["user_groups"]:
                self.check_editor_permissions(instance, group)

    def update(self, instance: User, validated_data):
        self._update_user_groups(instance, validated_data)
        return super().update(instance, validated_data)

    def partial_update(self, instance, validated_data):
        self._update_user_groups(instance, validated_data)
        return super().partial_update(instance, validated_data)


class ClientSettingsWriteSerializer(BaseModelSerializer):
    class Meta:
        model = ClientSettings
        exclude = ["is_published", "folder"]


class ClientSettingsReadSerializer(BaseModelSerializer):
    logo_hash = serializers.CharField()
    favicon_hash = serializers.CharField()
    logo = serializers.SerializerMethodField()
    favicon = serializers.SerializerMethodField()
    logo_mime_type = serializers.CharField()
    favicon_mime_type = serializers.CharField()

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.name.split("/")[-1]
        return None

    def get_favicon(self, obj):
        if obj.favicon:
            return obj.favicon.name.split("/")[-1]
        return None

    class Meta:
        model = ClientSettings
        exclude = ["is_published", "folder"]


class LogEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for the LogEntry model.
    """

    actor = FieldsRelatedField()
    action = serializers.CharField(source="get_action_display")
    content_type = serializers.SerializerMethodField(method_name="get_content_type")

    def get_content_type(self, obj):
        return obj.content_type.name

    class Meta:
        model = LogEntry
        fields = "__all__"
        read_only_fields = ["id", "timestamp", "actor", "action", "changes_text"]

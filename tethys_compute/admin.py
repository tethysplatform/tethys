from django.contrib import admin
from django.forms import Textarea
from django.db import models
from tethys_compute.models import Cluster, SettingsCategory, Setting
# Register your models here.


class SettingInline(admin.TabularInline):
    fields = ('name', 'content', 'date_modified')
    readonly_fields = ('name', 'date_modified')
    model = Setting
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 65})},
    }

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

@admin.register(SettingsCategory)
class SettingCategoryAdmin(admin.ModelAdmin):
    fields = ('name',)
    readonly_fields = ('name',)
    inlines = [SettingInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):

    list_display = ['name', 'size', 'status', 'cloud_provider']
    list_display_links = ('name', 'size')

    def get_form(self, request, obj=None, **kwargs):
        self.fieldsets = [
            ['General', {'fields': []}],
            ['Advanced Options', {
                # 'classes':('collapse',),
                'fields': ['_cloud_provider',
                           ('_master_image_id',
                           '_master_instance_type'),
                           ('_node_image_id',
                           '_node_instance_type')]
            }],
        ]
        fields = self.fieldsets[0][1]['fields']
        advanced_options = self.fieldsets[1][1]['fields']
        if obj is None:
            self.readonly_fields = ['_cloud_provider']
            fields[:] = ['_name', '_size']
        else:
            self.readonly_fields = ['_name', '_cloud_provider', '_status', '_master_instance_type', '_master_image_id']
            fields[:] = ['_name', '_size', '_status']
            advanced_options.pop(1)
        return super(ClusterAdmin, self).get_form(request, obj, **kwargs)



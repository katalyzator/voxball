from django.contrib.admin.models import LogEntry, DELETION
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import escape
from itertools import chain
from models import MainUser, ResetPasswordRequest, Country, City, \
    Activation, ResetEmailRequest, BlackList, AppVersion


@admin.register(MainUser)
class MainUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'full_name', 'showable_votem')

    fieldsets = (
        ('Main Fields', {'fields': (
            'username',
            'password',
            'email',
            'phone',
            'category_ids',
            'showable_votem',
            # 'push'
        )}),
        ('Password', {'fields': ('password',)}),  # we can change password in admin-site
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_moderator',)}),
    )

    search_fields = ['username', 'email', 'phone']
    list_filter = ('is_admin', 'is_moderator', 'is_active')


@admin.register(ResetPasswordRequest)
class ResetPasswordRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ['id', 'name', 'code']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    search_fields = ['id', 'name']


@admin.register(Activation)
class ActivationAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'key')


@admin.register(ResetEmailRequest)
class ResetEmailRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'new_email', 'key', 'user')


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    readonly_fields = list(set(chain.from_iterable(
        (field.name, field.attname) if hasattr(field, 'attname') else (field.name,)
        for field in LogEntry._meta.get_fields()
        # For complete backwards compatibility, you may want to exclude
        # GenericForeignKey from the results.
        if not (field.many_to_one and field.related_model is None)
    )))

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return link

    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'

    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')


@admin.register(BlackList)
class BlackListAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_bounced', 'is_complained')


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    pass

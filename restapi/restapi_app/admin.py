from django.contrib import admin
from .models import UserPost, Images,User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

class UserModelAdmin(BaseUserAdmin):
  # The fields to be used in displaying the User model.
  # These override the definitions on the base UserModelAdmin
  # that reference specific fields on auth.User.
  list_display = ('id', 'email', 'is_admin','username')
  list_filter = ('is_admin',)
  fieldsets = (
      ('User Credentials', {'fields': ('email', 'password','username')}),
      ('Permissions', {'fields': ('is_admin',)}),
  )
  # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
  # overrides get_fieldsets to use this attribute when creating a user.
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('email','password1', 'password2'),
      }),
  )
  search_fields = ('email',)
  ordering = ('email', 'id')
  filter_horizontal = ()


admin.site.register(User, UserModelAdmin)
admin.site.register(UserPost)
admin.site.register(Images)
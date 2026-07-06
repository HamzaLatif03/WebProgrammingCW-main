from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, Hobby, UserHobby, FriendRelationships

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
   list_display = ('username', 'name', 'email', 'date_of_birth','get_hobbies', 'get_friend_count')
   list_filter = ('date_of_birth', 'hobbies')
   search_fields = ('username', 'name', 'email')
   filter_horizontal = ('friends',)
   ordering = ('username', 'name')
   
   def get_hobbies(self, obj):
        return ", ".join([hobby.hobby_name for hobby in obj.hobbies.all()])
   get_hobbies.short_description = 'Hobbies'

   def get_friend_count(self, obj):
        return obj.friends.count()
   get_friend_count.short_description = 'Friends'

@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin):
   list_display = ('hobby_name', )
   search_fields = ('hobby_name',)

@admin.register(UserHobby)
class UserHobbyAdmin(admin.ModelAdmin):
   list_display = ('user', 'hobby')
   list_filter = ('hobby',)
   search_fields = ('user__name', 'hobby__hobby_name')

@admin.register(FriendRelationships)
class FriendRelationshipsAdmin(admin.ModelAdmin):
   list_display = ('sender', 'receiver', 'status', 'created_at')
   list_filter = ('status', 'created_at')
   search_fields = ('sender__name', 'receiver__name')
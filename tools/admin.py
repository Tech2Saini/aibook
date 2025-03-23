from django.contrib import admin
from tools.models import AiTool,Bookmark

# Register your models here.
admin.site.register(Bookmark)

class AiToolManager(admin.ModelAdmin):
    list_display= [ "title","paid","shares","created_at","url",]


admin.site.register(AiTool,AiToolManager)

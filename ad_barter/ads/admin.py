from django.contrib import admin
from .models import Ad, ExchangeProposal

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'category', 'condition', 'created_at')
    search_fields = ('title', 'description', 'category')
    list_filter = ('condition', 'category')

@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad_sender', 'ad_receiver', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('comment',)


from django.contrib.auth.decorators import login_required
from django.dispatch import receiver

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm


class AdListView(View):
    def get(self, request):
        ads = Ad.objects.all().order_by('-created_at')
        query = request.GET.get('q')
        condition = request.GET.get('condition')
        category = request.GET.get('category')
        other = request.GET.get('other')


        if query:
            ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if condition:
            ads = ads.filter(condition=condition)
        if category:
            ads = ads.filter(category=category)
        if other:
            ads = ads.filter(other=other)



        page_number = request.GET.get('page')
        paginator = Paginator(ads, per_page=5)
        page_obj = paginator.get_page(page_number)

        return render(request, template_name='ad_list.html', context={
            'ads': page_obj,
            'query': query,
            'condition': condition,
            'category': category,
            'other': other
        })


class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, template_name = 'register.html', context={'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ad_list')

        return render(request, template_name='register.html', context={'form': form})


class AdCreateView(CreateView, LoginRequiredMixin):

    model = Ad
    form_class = AdForm
    template_name = 'ad_form.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = context['form']
        return context


class AdEditView(UpdateView, UserPassesTestMixin, LoginRequiredMixin):

    model = Ad
    form_class = AdForm
    template_name = 'ad_form.html'

    success_url = reverse_lazy('ad_list')


    def test_func(self):
        ad = self.get_object()
        return ad.user == self.request.user


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = context['form']
        return context



class AdDeleteView(DeleteView, UserPassesTestMixin, LoginRequiredMixin):
    model = Ad
    template_name = 'ad_confirm_delete.html'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        ad = self.get_object()
        return ad.user == self.request.user


class ProposalCreateView(LoginRequiredMixin, View):
    def get(self, request, ad_id):
        ad_receiver = get_object_or_404(Ad, pk=ad_id)
        if ad_receiver.user == request.user:
            return render(request, template_name = 'error.html')

        form = ExchangeProposalForm()
        form.fields['ad_sender'].queryset = Ad.objects.filter(user=request.user)

        return render(request, template_name = 'proposal_form.html', context={
            'ad_receiver': ad_receiver,
            'form': form
        })

    def post(self, request, ad_id):
        ad_receiver = get_object_or_404(Ad, pk=ad_id)
        if ad_receiver.user == request.user:
            return render(request, template_name='error.html')

        form = ExchangeProposalForm(request.POST)

        form.fields['ad_sender'].queryset = Ad.objects.filter(user=request.user)

        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.save()
            return redirect('proposal_list')

        return render(request, template_name='proposal_form.html', context={
            'ad_receiver': ad_receiver,
            'form': form
        })



class ProposalListView(TemplateView, LoginRequiredMixin):
    template_name = 'proposal_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sent'] = ExchangeProposal.objects.filter(ad_sender__user=self.request.user)
        context['received'] = ExchangeProposal.objects.filter(ad_receiver__user=self.request.user)
        return context


@login_required
def proposal_accept(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk)

    if proposal.ad_receiver.user != request.user:
        return redirect('proposal_list')

    proposal.status = 'accepted'
    proposal.save()
    return redirect('proposal_list')


class ProposalActionView(LoginRequiredMixin, View):
    def post(self, request, pk, action):
        proposal = get_object_or_404(ExchangeProposal, pk=pk)
        if proposal.ad_receiver.user != request.user:
            return redirect('proposal_list')
        if action == 'accept':
            proposal.status = 'accepted'
        elif action == 'reject':
            proposal.status = 'rejected'
        proposal.save()
        return redirect('proposal_list')



@login_required
def proposal_reject(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk)

    if proposal.ad_receiver.user != request.user:
        return redirect('proposal_list')
    proposal.status = 'rejected'
    proposal.save()
    return redirect('proposal_list')


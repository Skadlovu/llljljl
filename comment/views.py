from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CommentForm  # Assuming you have a CommentForm in your forms.py
from .models import Comment,Like, Dislike
from django.urls import reverse

class Requirements(View):
    form_class = CommentForm
    template_name = 'ktu/comment.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class
        comment = Comment.objects.all()

        context = {}
        context['page_obj'] = comment
        context['form'] = form

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            comment_form = form.save(commit=False)
            comment_form.user = request.user
            comment_form.save()
            messages.success(request, "Your comment successfully added")
            return HttpResponseRedirect(reverse('comment'))

        context = {}
        context['form'] = form

        return render(request, self.template_name, context)

class UpdateCommentVote(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        comment_id = self.kwargs.get('comment_id', None)
        opinion = self.kwargs.get('opinion', None)
        comment = get_object_or_404(Comment, id=comment_id)

        try:
            comment.dis_likes
        except Comment.dis_likes.RelatedObjectDoesNotExist as identifier:
            Dislike.objects.create(comment=comment)
        try:
            comment.likes
        except Comment.likes.RelatedObjectDoesNotExist as identifier:
            Like.objects.create(comment=comment)

        if opinion.lower() == 'like':
            if request.user in comment.likes.users.all():
                comment.likes.users.remove(request.user)
            else:
                comment.likes.users.add(request.user)
                comment.dis_likes.users.remove(request.user)

        elif opinion.lower() == 'dis_like':
            if request.user in comment.dis_likes.users.all():
                comment.dis_likes.users.remove(request.user)
            else:
                comment.dis_likes.users.remove(request.user)
                comment.likes.users.add(request.user)

        else:
            return HttpResponseRedirect(reverse('comment'))
        return HttpResponseRedirect(reverse('comment'))

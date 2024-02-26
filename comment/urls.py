from.views import Requirements,UpdateCommentVote
from django.urls import path

app_namespace='comment'


urlpatterns=[
    path('comments', Requirements.as_view(), name='requirements'),
    path('requirement/<int:comment_id>/<str:opition>', UpdateCommentVote.as_view(), name='requirement_comment_vote'),
]
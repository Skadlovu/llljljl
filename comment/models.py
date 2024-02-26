from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from events.models import Event


class Comment(models.Model):
    user=models.ForeignKey(User,related_name='comments', on_delete=models.CASCADE )
    comment=models.TextField(validators=[MinLengthValidator(150)])
    created_at=models.DateTimeField()
    updated_at=models.DateTimeField()

    def get_total_likes(self):
        return self.likes.users.count()
    
    
    def get_total_dis_likes(self):
        return self.dis_likes.users.count()


    def __str__(self):
        return str(self.comment)[:30]
    

class Like(models.Model):
    comment=models.OneToOneField(Comment,related_name='likes', on_delete=models.CASCADE)
    users=models.ManyToManyField(User, related_name='requirements_comments_likes')
    created_at=models.DateTimeField()
    updated_at=models.DateTimeField()

    def __str__(self):
        return str(self.comment.comment)[:10]
    
class Dislike(models.Model):
    comment=models.OneToOneField(Comment,related_name='dis_likes', on_delete=models.CASCADE)
    users=models.ManyToManyField(User, related_name='requirements_comments_dis_likes')
    created_at=models.DateTimeField()
    updated_at=models.DateTimeField()

    def __str__(self):
        return str(self.comment.comment)[:10]

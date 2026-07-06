from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import Dict, Any
from datetime import date, datetime
    
class Hobby(models.Model):
    """Hobby model."""
    hobby_name: str = models.CharField(max_length=100, unique=True)
    
    def __str__(self) -> str:
        return self.hobby_name

    def as_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'hobby_name': self.hobby_name,
        }
     
class CustomUser(AbstractUser):
    
    # Custom user model from learnouts
    name: str = models.CharField(max_length=100, blank=True)
    email: str = models.EmailField('Email address', unique=True)
    date_of_birth: date = models.DateField('Date of birth', null=True, blank=True)
    hobbies = models.ManyToManyField(Hobby, through="UserHobby")
    friends = models.ManyToManyField("CustomUser", blank=True)
    
    def __str__(self) -> str:
        return self.name
    
    def as_dict(self) -> Dict[str, Any]:
        return{
            'id':self.id,
            'name':self.name,
            'username':self.username,
            'password':self.password,
            'email':self.email,
            'date_of_birth':self.date_of_birth,
            'hobbies': [hobby.as_dict() for hobby in self.hobbies.all()],
            'friends': [friend.id for friend in self.friends.all()]
        }
    
    
#through model
class UserHobby(models.Model):
    
    hobby: Hobby = models.ForeignKey(Hobby, on_delete=models.CASCADE)
    user: CustomUser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    
    def __str__(self) -> str:
        return f"{self.hobby} for {self.user}"
    
    
    def as_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'hobby': {
                "id": self.hobby.id,
                "name": self.hobby.hobby_name,
            },
            'user': {
                "id": self.user.id,
                "name": self.user.name,
            }
        }
        
class FriendRelationships(models.Model):  
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    
    sender: CustomUser = models.ForeignKey(CustomUser, related_name='sender', on_delete=models.CASCADE)
    receiver: CustomUser = models.ForeignKey(CustomUser, related_name='receiver', on_delete=models.CASCADE) 
    status: str = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str :
        return f"{self.sender} to {self.receiver}"
    
    def as_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'sender': {
                "id": self.sender.id,
                "name": self.sender.name,
            },
            'receiver': {
                "id": self.receiver.id,
                "name": self.receiver.name,
            },
            'status': self.status,
            'created_at': self.created_at
        }
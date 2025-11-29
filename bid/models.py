from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your models here.
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    phone_number = models.CharField(max_length=15)
    bid_type = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.user.username} of amount {self.amount}"
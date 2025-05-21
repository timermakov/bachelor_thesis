from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model


class BaseDateModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Position(BaseDateModel):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='positions')

    base_asset = models.CharField(max_length=16)
    quote_asset = models.CharField(max_length=16)

    entry_point = models.FloatField(validators=[MinValueValidator(0)])
    stop_loss = models.FloatField(validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.base_asset}/{self.quote_asset}'


class Target(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='targets')
    value = models.FloatField(validators=[MinValueValidator(0)])

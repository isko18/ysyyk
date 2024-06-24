from django.db import models

class UserBusiness(models.Model):
    user_id = models.CharField(max_length=100, verbose_name='user id')
    referrer_id = models.CharField(max_length=100, verbose_name='Айди реферальк')
    username = models.CharField(max_length=100, verbose_name='username')
    
    def __str__(self) -> str:
        return f'{self.username}' 

    class Meta:
        verbose_name_plural = 'Бизнес пользователи'

class UserCklient(models.Model):
    user_id = models.CharField(max_length=100, verbose_name='user id')
    referrer_id = models.CharField(max_length=100, verbose_name='Айди Реферальки')
    username = models.CharField(max_length=100, verbose_name='username')

    class Meta:
        verbose_name_plural = 'Пользователи клиента'

class Business(models.Model):
    user = models.ForeignKey(UserBusiness, on_delete=models.CASCADE, verbose_name='Пользователь')
    region = models.CharField(max_length=155, verbose_name='Район')
    pansionat = models.CharField(max_length=155, verbose_name='Название пансионата')
    type_accommodation = models.CharField(max_length=155, verbose_name='Тип размещения')
    facilities = models.CharField(max_length=155, verbose_name='Удобства')
    quantities = models.CharField(max_length=155, verbose_name='Количества')
    price = models.CharField(max_length=155, verbose_name='Цена')
    phone_number = models.CharField(max_length=155, verbose_name='Номер телефона')
    photos = models.TextField(verbose_name='Фотографии')
    is_active = models.BooleanField(default=False, verbose_name='Активный')
    referrer_id = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self) -> str:
        return self.region
    
    class Meta:
        verbose_name_plural = 'Отели Бизнесов'


class Cklient(models.Model):
    user = models.ForeignKey(UserCklient, on_delete=models.CASCADE, verbose_name='Пользователи')
    region = models.CharField(max_length=155,verbose_name='Район')
    date = models.CharField(max_length=155,verbose_name='Дата Заезда')
    comment = models.TextField(verbose_name='Комментраия')

    class Meta:
        verbose_name_plural = 'Бронирование Клиента'
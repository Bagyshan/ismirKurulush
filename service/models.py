from django.db import models

# Create your models here.





class Service(models.Model):
    icon = models.ImageField(upload_to='service_icons/', verbose_name="Иконка услуги", blank=True, null=True)
    name = models.CharField(max_length=200, unique=True, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание услуги", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена услуги")
    unit_of_measurement = models.CharField(max_length=50, verbose_name="Единица измерения", blank=True)
    term = models.CharField(max_length=100, verbose_name="Срок выполнения", blank=True)
    # possibilities = models.ForeignKey(
    #     Possibilities, 
    #     on_delete=models.SET_NULL,
    #     related_name='services', 
    #     null=True,
    #     blank=True, 
    #     verbose_name="Возможности услуги"
    # )
    # advantages = models.ForeignKey(
    #     Advantages, 
    #     on_delete=models.SET_NULL,
    #     related_name='services', 
    #     null=True,
    #     blank=True, 
    #     verbose_name="Преимущества услуги"
    # )
    # work_process = models.ForeignKey(
    #     WorkProcess, 
    #     on_delete=models.SET_NULL,
    #     related_name='services', 
    #     null=True,
    #     blank=True, 
    #     verbose_name="Этапы работы"
    # )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["name"]

    def __str__(self):
        return self.name
    


class Possibilities(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='possibilities', null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name="Название возможности")

    class Meta:
        verbose_name = "Возможность"
        verbose_name_plural = "Возможности"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Advantages(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='advantages', null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name="Название преимущества")

    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
        ordering = ["name"]

    def __str__(self):
        return self.name
    


class WorkProcess(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='work_process', null=True, blank=True)
    step_number = models.PositiveIntegerField(verbose_name="Номер шага")
    description = models.TextField(verbose_name="Описание шага")

    class Meta:
        verbose_name = "Этап работы"
        verbose_name_plural = "Этапы работы"
        ordering = ["step_number"]

    def __str__(self):
        return f"Шаг {self.step_number}"

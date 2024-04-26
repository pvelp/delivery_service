from django.db import models


class IikoAPIKey(models.Model):
    key = models.TextField(verbose_name='API Ключ компании')

    class Meta:
        verbose_name = 'Ключ компании'
        verbose_name_plural = 'Ключи компании из iikoWeb'


class ExternalMenu(models.Model):
    menu_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Внешнее меню iikoWeb'
        verbose_name_plural = 'Внешние меню iikoWeb'


class Organization(models.Model):
    organization_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Организация из iikoWeb'
        verbose_name_plural = 'Организации из iikoWeb'


class FetchMenu(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='ID организации')
    menu = models.ForeignKey(ExternalMenu, on_delete=models.CASCADE, verbose_name='ID Меню')

    class Meta:
        verbose_name = 'Сохранить меню'
        verbose_name_plural = 'Сохранить меню'

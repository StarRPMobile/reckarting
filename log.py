import datetime
from typing import Optional


import Settings as Sett
from Settings import FontType as ft


def error(text: Optional[str]):
    """Функция выводит в Output сообщение об ошибке

    :param text: Текст сообщения
    :type text: Optional[str]

    :return: Выводит в Output ошибку
    """
    print(ft.Bold+ft.Underline+ft.RedBG+ft.White+text+'\n'+ft.Normal)
def ok(text: Optional[str]):
    """Функция выводит в Output сообщение об успехе

    :param text: Текст сообщения
    :type text: Optional[str]

    :return: Выводит в Output успех
    """
    print(ft.Bold+ft.GreenBG+ft.White+str(datetime.datetime.now().time())+' | '+text+ft.Normal)
def warn(text: Optional[str]):
    """Функция выводит в Output предупреждение

    :param text: Текст сообщения
    :type text: Optional[str]

    :return: Выводит в Output предупреждение
    """
    print(ft.Bold+ft.YellowBG+ft.White+text+ft.Normal)
def line(text=''):
    """Функция выводит в Output разделительную линию

    :param text: Текст после линии(в т.ч. Знак перевода строки)
    :type text: Optional[str]

    :return: Выводит в Output разделительную линию
    """
    print(Sett.razdelitel.rjust(Sett.widthline,Sett.razdelitel)+text)
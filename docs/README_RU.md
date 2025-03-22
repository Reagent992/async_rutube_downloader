[![release](https://img.shields.io/github/release/Reagent992/async_rutube_downloader.svg)](https://github.com/Reagent992/async_rutube_downloader/releases/latest)
[![tests](https://github.com/Reagent992/async_rutube_downloader/actions/workflows/tests.yml/badge.svg)](https://github.com/Reagent992/async_rutube_downloader/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Reagent992/async_rutube_downloader/badge.svg?branch=main)](https://coveralls.io/github/Reagent992/async_rutube_downloader?branch=main)
[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Reagent992/async_rutube_downloader/total?label=release%20downloads)](https://github.com/Reagent992/async_rutube_downloader/releases/latest)

[English](README.md) / Russian

# Что это?

Небольшой проект с одной основной функцией - скачивание видео с RuTube.

## Как пользоваться?
### Графический пользовательский интерфейс
-  [Скачать исполняемый файл в разделе релизы(Releases)](https://github.com/Reagent992/async_rutube_downloader/releases/latest)

![screen_cast](screen_cast.gif)

### [Установка исходного кода проекта](./dev.md)


# О проекте
Этот проект был создан в учебных целях и был вдохновлен аналогичной синхронной библиотекой и книгой по асинхронному программированию.

## Технические особенности
- Графический пользовательский интерфейс(GUI) на TKinter.
- Интерфейс командной строки с использованием `argparse`(Из стандартной библиотеки)
- Честный прогресс бар, он отображает реальный прогресс загрузки.
- UI и загрузка работают в разных потоках.
- Перевод UI.
- Асинхронная версия позволяет использовать полную скорость интернет-соединения.

# Используемые библиотеки:

| title                                                           | description                               |
| --------------------------------------------------------------- | ----------------------------------------- |
| [m3u8](https://github.com/globocom/m3u8/)                       | Используется для парсинга плейлистов      |
| [aiohttp](https://github.com/aio-libs/aiohttp)                  | асинхронный http клиент                   |
| [aiofiles](https://github.com/Tinche/aiofiles)                  | асинхронная работа с файлами              |
| [PyInstaller](https://github.com/pyinstaller/pyinstaller)       | Создание исполняемого файла               |
| [slugify ](https://github.com/un33k/python-slugify)             | Преобразование названия видео в имя файла |
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Better TKinter UI                         |

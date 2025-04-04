��    !      $  /   ,      �  �   �  �  �  l   �     �       /        M     V     h     {     �  [   �               &  P   <     �     �     �  5   �       +   (  N   T  S   �     �     		  0   	  "   H	     k	     �	  )   �	     �	  |  �	  �  W  �  �  �   �  $   �  (   �  ^        a  #   t  !   �  #   �  3   �  �        �  /   �  /     �   <  0   �     �  #     T   9  ,   �  X   �  z     �   �          .  ]   J  W   �        "      ;   C                                     
                                                                  	                                           !                  
This CLI utility allows you to download videos from Rutube.
 - You can download a single video or multiple videos by providing a file with URLs.
 - By default, videos from a file will be downloaded in the best available quality.
 
Usage examples:
 - Download single video:
      [async_rutube_downloader] 365ae8f40a2ffd2a5901ace4db799de7
      [async_rutube_downloader] https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/
      [async_rutube_downloader] https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/ -q
 - Download multiple videos:
      [async_rutube_downloader] -f ~/path/to/file1.txt
      [async_rutube_downloader] -f ~/path/to/file2.txt -d ,
 A network issue occurred while downloading a video segment. Please check your internet connection and retry. Available qualities: Cancelling download... Delimiter between URLs in the file(default: \n) Download Download Complete Download cancelled Download directory: {} Enter RuTube URL or Video ID Failed to fetch video data. The URL might be incorrect, or there may be a connection issue. Get Video Info Invalid URL Invalid URL Error: {} Invalid file. The file contains errors or does not meet validation requirements. Multiple videos download No folder selected No such file or directory: {} Output directory (default: current working directory) Path to the file with URLs Please enter a video URL before proceeding. Report: Downloaded {} videos, Invalid urls {}, it takes {} minutes, {} seconds Resource not found (404) The URL may be incorrect, or the API might be unavailable. Rutube Downloader Select Folder Select quality. (Enter the corresponding number) Select video quality interactively URL or ID of the Rutube video [{}] download started [{}] downloaded in {} minutes, {} seconds [{}] saved to {} Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2025-03-01 02:57+0300
Last-Translator: Automatically generated
Language-Team: none
Language: ru
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
 
Эта утилита командной строки позволяет загружать видео с Rutube.
 - Вы можете загрузить одно видео или несколько видео, указав файл с URL.
 - По умолчанию видео из файла будут загружаться в наилучшем доступном качестве.
 
Примеры использования:
 - Загрузить одно видео:
      [async_rutube_downloader] 365ae8f40a2ffd2a5901ace4db799de7
      [async_rutube_downloader] https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/
      [async_rutube_downloader] https://rutube.ru/video/365ae8f40a2ffd2a5901ace4db799de7/ -q
 - Загрузить несколько видео:
      [async_rutube_downloader] -f ~/path/to/file1.txt
      [async_rutube_downloader] -f ~/path/to/file2.txt -d ,
 Произошла ошибка сети при скачивании сегмента видео. Пожалуйста, проверьте ваше интернет-соединение и попробуйте снова. Доступные качества: Загрузка отменяется... Разделитель между ссылками в файле (по умолчанию: \n) Загрузить Загрузка завершена Загрузка отменена Каталог загрузки: {} Введите URL или ID видео на RuTube Не удалось получить данные о видео. URL может быть неправильным, или возникла проблема с соединением. Проверить Ошибка недопустимого URL: {} Ошибка недопустимого URL: {} Недопустимый файл. Файл содержит ошибки или не соответствует требованиям. Загрузить несколько видео Папка не выбрана Каталог загрузки: {} Каталог вывода (по умолчанию: текущий каталог) Путь до файла с ссылками Пожалуйста, введите URL видео перед продолжением. Отчет: Загружено {} видео, Недопустимых URL {}, заняло {} минут, {} секунд Ресурс не найден (404) Возможно, указан неверный URL-адрес или API недоступен. Загрузчик RuTube Выберите папку Выберите качество. (Введите соответствующий номер) Выберите качество видео в интерактивном режиме URL или ID Rutube видео [{}] загрузка начата [{}] загружено за {} минут, {} секунд [{}] сохранено в {} 
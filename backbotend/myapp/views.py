# myapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from .read_file import read_file  # Импорт функции для чтения файла//


class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Сохраняем файл с использованием стандартного хранилища
        file_name = default_storage.save(file.name, ContentFile(file.read()))
        file_url = default_storage.url(file_name)
        
        # Полный путь к файлу для функции read_file
        file_path = os.path.join(default_storage.location, file_name)
        
        # Чтение содержимого файла
        file_content = read_file(file_path)
        # print("File content:", file_content)

        # Вопрос и анализ текста
        question = "Ваш вопрос здесь"  # Подставьте вопрос
        #answer = analText(question, file_content)  # Анализируем текст
        
        # Возвращаем результат, включая URL и содержимое файла
        return Response({
            "file_url": default_storage.url(file_name),
            "file_content": file_content,
            #"answer": answer
        }, status=status.HTTP_201_CREATED)

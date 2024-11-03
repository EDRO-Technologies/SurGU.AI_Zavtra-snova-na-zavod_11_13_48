# считывание PDF
import PyPDF2
# анализ структуры ПДФ, извлечение текста
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# извлечение текста из таблиц в PDF
import pdfplumber
# извлечение изображений из PDF
from PIL import Image
from pdf2image import convert_from_path
# извлечение текстов из изображений 
import pytesseract 
import os



# Извлечение текста
def text_extraction(element):
    # Извлекаем текст из вложенного текстового элемента
    # line_text = [element.replace('\t', '\n') if element is not None and '\n' in element else element.get_text()]
    line_text = element.get_text()
    # Удаляем разрыв строки из текста с переносом
    
        
    return (line_text)

# Выделение изображений из PDF
def crop_image(element, pageObj):
    # Получаем координаты для вырезания изображения из PDF
    [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
    # Обрезаем страницу по координатам (left, bottom, right, top)
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # Сохраняем обрезанную страницу в новый PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # Сохраняем обрезанный PDF в новый файл
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)

# преобразования PDF в изображение
def convert_to_images(input_file,):
    images = convert_from_path(input_file, poppler_path="./poppler-24.08.0/Library/bin")
    image = images[0]
    output_file = "PDF_image.png"
    image.save(output_file, "PNG")


# считывание текста из изображений
def image_to_text(image_path):
    # Считываем изображение
    img = Image.open(image_path)
    # Извлекаем текст из изображения
    img = img.convert('RGBA')
    pix = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pix[x, y][0] < 102 or pix[x, y][1] < 102 or pix[x, y][2] < 102:
                pix[x, y] = (0, 0, 0, 255)
            else:
                pix[x, y] = (255, 255, 255, 255)

    pytesseract.pytesseract.tesseract_cmd = './Tesseract-OCR/tesseract.exe'
    text = pytesseract.image_to_string(img, lang= 'rus+eng')
    return text

# Извлечение таблиц из страницы
def extract_table(pdf_path, page_num, table_num):
    # Открываем файл pdf
    pdf = pdfplumber.open(pdf_path)
    # Находим исследуемую страницу
    table_page = pdf.pages[page_num]
    # Извлекаем соответствующую таблицу
    table = table_page.extract_tables()[table_num]
    return table

# Преобразуем таблицу в соответствующий формат
def table_converter(table):
    table_string = ''
    # Итеративно обходим каждую строку в таблице
    for row_num in range(len(table)):
        row = table[row_num]
        # Удаляем разрыв строки из текста с переносом
        cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
        # Преобразуем таблицу в строку
        table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
    # Удаляем последний разрыв строки
    table_string = table_string[:-1]
    return table_string

def read_file(file_path):

    # Находим путь к PDF
    # pdf_path = 'Док.pdf'
    # pdf_path = 'Programma.pdf'
    #pdf_path = 'lr1.pdf'
    # pdf_path = 'Гильмуллина_Кристина_Владимировна.pdf'

    # создаём объект файла PDF
    pdfFileObj = open(file_path, 'rb')
    # создаём объект считывателя PDF
    pdfReaded = PyPDF2.PdfReader(pdfFileObj, strict=False)

    # Создаём словарь для извлечения текста из каждого изображения
    text_per_page = {}
    result = ""

    # Извлекаем страницы из PDF
    for pagenum, page in enumerate(extract_pages(file_path)):
        
        # Инициализируем переменные, необходимые для извлечения текста со страницы
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        text_from_images = []
        text_from_tables = []
        page_content = []
        
        # Инициализируем количество исследованных таблиц
        table_num = 0
        first_element= True
        table_extraction_flag= False
        # Открываем файл pdf
        pdf = pdfplumber.open(file_path)
        # Находим исследуемую страницу
        page_tables = pdf.pages[pagenum]
        # Находим количество таблиц на странице
        tables = page_tables.find_tables()

        # Находим все элементы
        page_elements = [(element.y1, element) for element in page._objs]
        # Сортируем все элементы по порядку нахождения на странице
        page_elements.sort(key=lambda a: a[0], reverse=True)

        # Находим элементы, составляющие страницу
        for i,component in enumerate(page_elements):
            # Извлекаем положение верхнего края элемента в PDF
            pos= component[0]
            # Извлекаем элемент структуры страницы
            element = component[1]
            
            # Проверяем, является ли элемент текстовым
            if (isinstance(element, LTTextContainer)):
                # Проверяем, находится ли текст в таблице
                if table_extraction_flag == False:
                    # Используем функцию извлечения текста
                    (line_text) = text_extraction(element)
                    # Добавляем текст каждой строки к тексту страницы

                    if not line_text.isspace():

                        page_text.append(line_text)
                        page_content.append(line_text)
                else:
                    # Пропускаем текст, находящийся в таблице
                    pass

            # Проверяем элементы на наличие изображений
            if isinstance(element, LTFigure):
                # Вырезаем изображение из PDF
                crop_image(element, pageObj)
                # Преобразуем обрезанный pdf в изображение
                convert_to_images('cropped_image.pdf')
                # Извлекаем текст из изображения
                image_text = image_to_text('PDF_image.png')
                text_from_images.append(image_text)
                page_content.append(image_text)
                # Добавляем условное обозначение в списки текста и формата
                page_text.append('image')

            # # Проверяем элементы на наличие таблиц
            # if isinstance(element, LTRect):
            #     print("Я ТАБЛИЦА!")
            #     # Если первый прямоугольный элемент
            #     # lower_side = 0
            #     # upper_side = 0
            #     if first_element == True and (table_num+1) <= len(tables):
            #         print("Я ТАБЛИЦА! номер ДВА")
            #         # Находим ограничивающий прямоугольник таблицы
            #         lower_side = page.bbox[3] - tables[table_num].bbox[3]
            #         upper_side = element.y1 
            #         print("lower = ", lower_side, "upper_side = ", upper_side)
            #         # Извлекаем информацию из таблицы
            #         table = extract_table(file_path, pagenum, table_num)
            #         # Преобразуем информацию таблицы в формат структурированной строки
            #         table_string = table_converter(table)
            #         # Добавляем строку таблицы в список
            #         text_from_tables.append(table_string)
            #         page_content.append(table_string)
            #         # Устанавливаем флаг True, чтобы избежать повторения содержимого
            #         table_extraction_flag = True
            #         # Преобразуем в другой элемент
            #         first_element = False
            #         # Добавляем условное обозначение в списки текста и формата
            #         page_text.append('table')
            #     else:
            #         lower_side = 0 
            #         upper_side = 0
            #     # Проверяем, извлекли ли мы уже таблицы из этой страницы
            #     if element.y0 >= lower_side and element.y1 <= upper_side:
            #         pass
            #     elif not isinstance(page_elements[i+1][1], LTRect):
            #         table_extraction_flag = False
            #         first_element = True
            #         table_num+=1

        # Создаём ключ для словаря
        dctkey = 'Page_'+str(pagenum)
        # Добавляем список списков как значение ключа страницы
        text_per_page[dctkey]= [page_text, text_from_images,text_from_tables, page_content]
        res = ''.join(text_per_page[f"Page_{str(pagenum)}"][3])
        # print(pagenum)
        result += res
    
    # Закрываем объект файла pdf
    pdfFileObj.close()

    # Удаляем созданные дополнительные файлы
    try:
        os.remove('cropped_image.pdf')
        os.remove('PDF_image.png')
    except Exception as e:
        print(e)

    # result = ''.join(text_per_page[f"Page_0"][3])
    # print(result)
    return result

# %%
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pdfminer.high_level as pdfm
from pypdf import PdfReader
import shutil
import os

CLEAR_DIR = True  # перезапись или дополнение директории с фотками

# размеры фоток
IMAGE_LENGTH_MIN = 500
IMAGE_LENGTH_MAX = 1000

IMAGE_WIDTH_MIN = 500
IMAGE_WIDTH_MAX = 1000

# раземер шрифта
FONT_SIZE_MIN = 20
FONT_SIZE_MAX = 60

NUMBER_OF_IMAGES = 15  # сколько фоток генерить
PERCENT_OF_START_END_BOOK_CUTTING = 0.1  # какой процент страниц пропустить в начале и в конце книги

# Отступ между строками в пикселях
STRING_WHITE_SPACE_PIXELS_MIN = 10
STRING_WHITE_SPACE_PIXELS_MAX = 15

# Отступ слева и справа от текста
BORD_WHITE_SPACE_PIXELS_MIN = 2
BORD_WHITE_SPACE_PIXELS_MAX = 10
# %%

fonts = ["/Library/Fonts/Arial.ttf", "/Library/Fonts/Times New Roman.ttf"]  # шрифты

text_path = "testTexts/kierkegaard_strach_i_trepet.pdf"

reader = PdfReader(text_path)
number_of_pages = len(reader.pages)  # число страниц

# выбираем все страницы, кроме установленного процента в начале и в конце
text = ""
for page_number in range(int(number_of_pages * PERCENT_OF_START_END_BOOK_CUTTING),
                         int(number_of_pages * (1 - PERCENT_OF_START_END_BOOK_CUTTING))):
    text += reader.pages[page_number].extract_text()

# если вдруг pypdf станет плохо видеть текст
# page_numbers=[i for i in range(int(number_of_pages * PERCENT_OF_START_END_BOOK_CUTTING), int(number_of_pages * (1 - PERCENT_OF_START_END_BOOK_CUTTING)))]
# text = pdfm.extract_text(text_path, page_numbers) 
# print(text)
# %%
# перезаписать или дополнить папку с фотками
dir_path = 'testImages'
if CLEAR_DIR:
    # если папка существует, то удаляем
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)
    ctr = 1
else:
    folder = Path(dir_path)
    if folder.is_dir():
        ctr = len(list(folder.iterdir()))
    else:
        ctr = 1
# %%
for i in range(NUMBER_OF_IMAGES):
    path = f"{dir_path}/{ctr}.jpg"

    # создаём белый лист рандомного размера
    img = Image.new('RGB', (
    random.randint(IMAGE_LENGTH_MIN, IMAGE_LENGTH_MAX), random.randint(IMAGE_WIDTH_MIN, IMAGE_WIDTH_MAX)),
                    (255, 255, 255))
    img.save(path)

    # создаём рандомный шрифт рандомного размера
    font_size = random.randint(FONT_SIZE_MIN, FONT_SIZE_MAX)
    font_path = random.choice(fonts)

    # находим высоту строки, задаём интервал между строками
    font = ImageFont.truetype(font_path, font_size)
    box = font.getbbox("A")  # (лево, верх, право, низ)
    white_space_between_strings = random.randint(STRING_WHITE_SPACE_PIXELS_MIN, STRING_WHITE_SPACE_PIXELS_MAX)
    txt_height = (box[3] - box[1]) + white_space_between_strings

    # задаём отступы справа и слева от текста
    bord_white_space = random.randint(BORD_WHITE_SPACE_PIXELS_MIN, BORD_WHITE_SPACE_PIXELS_MAX)

    # ищем случайную начальную позицию для текста, чтобы это было новое предложение
    curr_letter_index = random.randint(0, int(len(text) * 0.9))
    new_sentence_flg = False
    while True:
        if text[curr_letter_index] == '.':
            new_sentence_flg = True
        if new_sentence_flg and not (text[curr_letter_index] in " \n."):
            break
        curr_letter_index += 1

    # пишем текст в белом квадрате 
    curr_txt_height = 2
    # по строкам
    while curr_txt_height + txt_height < img.height - white_space_between_strings:
        curr_str = ""
        curr_txt_width = 0
        # пишем строку с отступами
        while curr_txt_width < img.width - bord_white_space * 2:
            if text[curr_letter_index] != '\n' and not (
                    text[curr_letter_index] == '‐' and text[curr_letter_index + 1] == '\n'):
                if text[curr_letter_index] == '‐':  # костыль, этот придурошный плохо понимает тире
                    curr_str += '-'
                else:
                    curr_str += text[curr_letter_index]
                box = font.getbbox(curr_str)
                curr_txt_width = (box[2] - box[0])  # считаем длину строки в пикселях
            curr_letter_index += 1
        # print(curr_txt_width, img.width) 
        # print(curr_str)
        # отрезаем лишнее
        box = font.getbbox(curr_str)
        curr_txt_width = (box[2] - box[0])
        while curr_txt_width > img.width - bord_white_space * 2:  # если получилось больше, то отрезаем
            curr_str = curr_str[:-1]
            curr_letter_index -= 1
            box = font.getbbox(curr_str)
            curr_txt_width = (box[2] - box[0])

        while text[
            curr_letter_index] not in '  ':  # Удаляем отрезанные слова (странный символ - что-то вроде пробела для него)
            # print(curr_str)
            curr_str = curr_str[:-1]
            curr_letter_index -= 1
        curr_letter_index += 1
        # print(curr_str)

        # отрисовываем (без этой проверки он иногда режет нижнюю строку)
        if curr_txt_height + txt_height < img.height - white_space_between_strings:
            idDraw = ImageDraw.Draw(img)
            box = font.getbbox(curr_str)
            idDraw.text((bord_white_space, curr_txt_height), curr_str, font=font, fill=(0, 0, 0, 255))

        curr_txt_height += txt_height

    img.save(path)
    img = Image.open(path)
    img.show()

    ctr += 1
# %%

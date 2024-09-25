import requests
from bs4 import BeautifulSoup as bs4
import csv

url = "https://prodoctorov.ru/krasnodar/vrach/109211-lobach/"

headers = {
    "User-Agent": "Mozilla/4.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = bs4(response.content, "html.parser")

def extract_doctor_info(soup):
    # ФИО врача
    fio = soup.find("h1").find("span", {"itemprop": "name"}).text.strip()

    # Специализация
    specialization_tag = soup.find("div", class_="b-doctor-intro__specs")
    specializations = [spec.text for spec in specialization_tag.find_all("a")]
    result = ", ".join(specializations)
    specialization = "•" if not result else result

    # Стаж работы
    stazh_tag = soup.find("div", class_="ui-text_subtitle-1")
    if stazh_tag:
        experience = stazh_tag.text.replace('Стаж', '').strip()
    else:
        experience = "•"

    # Звания
    target_div = soup.find("div", class_="text-left mr-2")

    if target_div:
        zvaniya_tags = target_div.find_all("span", class_="b-doctor-card__text-with-dot")
        
        # Объединяем тексты тегов в одну строку с разделителем ", "
        zvaniya = ', '.join([tag.text.strip() for tag in zvaniya_tags])
    else:
        zvaniya = "•"

    # Клиника
    clinic_tag = soup.find("div", class_="doctor-place")
    clinic = clinic_tag.text.strip() if clinic_tag else "•"

    # Общий рейтинг врача
    rating_tag = soup.find("div", class_="rating-value")
    rating = rating_tag.text.strip() if rating_tag else "•"

    # Количество отзывов
    reviews_count_tag = soup.find("a", href="#reviews")
    reviews_count = reviews_count_tag.text.strip() if reviews_count_tag else "•"

    # Образование и квалификация
    education_tag = soup.find("div", class_="doctor-education")
    education = education_tag.text.strip() if education_tag else "•"

    # Фото врача (если доступно)
    photo_tag = soup.find("div", class_="doctor-photo img-circle")
    photo_url = photo_tag.img['src'] if photo_tag and photo_tag.img else "•"

    return {
        "ФИО": fio,
        "Специализация": specialization,
        "Стаж работы": experience,
        "Полученные степени": zvaniya,
        "Клиника": clinic,
        "Рейтинг": rating,
        "Количество отзывов": reviews_count,
        "Образование": education,
        "Фото": photo_url
    }

doctor_info = extract_doctor_info(soup)

def save_to_csv(data, filename="doctors.csv"):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys(), delimiter=';')
        file_empty = file.tell() == 0
        if file_empty:
            writer.writeheader()
        writer.writerow(data)

save_to_csv(doctor_info)

print(f"Данные {doctor_info['ФИО']} сохранены.")

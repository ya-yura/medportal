import requests
from bs4 import BeautifulSoup
import csv

url = "https://prodoctorov.ru/krasnodar/vrach/109211-lobach/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

def extract_doctor_info(soup):
    # ФИО врача
    fio = soup.find("h1").text.strip()

    # Специализация
    specialization_tag = soup.find("div", class_="doctor-specialization")
    specialization = specialization_tag.text.strip() if specialization_tag else "Нет"

    # Стаж работы
    experience_tag = soup.find("div", class_="doctor-experience")
    experience = experience_tag.text.strip() if experience_tag else "Нет"

    # Клиника
    clinic_tag = soup.find("div", class_="doctor-place")
    clinic = clinic_tag.text.strip() if clinic_tag else "Нет"

    # Общий рейтинг врача
    rating_tag = soup.find("div", class_="rating-value")
    rating = rating_tag.text.strip() if rating_tag else "Нет"

    # Количество отзывов
    reviews_count_tag = soup.find("a", href="#reviews")
    reviews_count = reviews_count_tag.text.strip() if reviews_count_tag else "Нет"

    # Образование и квалификация
    education_tag = soup.find("div", class_="doctor-education")
    education = education_tag.text.strip() if education_tag else "Нет"

    # Фото врача (если доступно)
    photo_tag = soup.find("div", class_="doctor-photo img-circle")
    photo_url = photo_tag.img['src'] if photo_tag and photo_tag.img else "Нет"

    return {
        "ФИО": fio,
        "Специализация": specialization,
        "Стаж работы": experience,
        "Клиника": clinic,
        "Рейтинг": rating,
        "Количество отзывов": reviews_count,
        "Образование": education,
        "Фото": photo_url
    }

doctor_info = extract_doctor_info(soup)

def save_to_csv(data, filename="doctors.csv"):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        file_empty = file.tell() == 0
        if file_empty:
            writer.writeheader()
        writer.writerow(data)

save_to_csv(doctor_info)

print(f"Данные {doctor_info['ФИО']} сохранены.")

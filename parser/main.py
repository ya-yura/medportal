import csv, random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


url = "https://prodoctorov.ru/krasnodar/vrach/109211-lobach/"
keywords = ['стомат', 'клини', 'институт', 'космет', 'центр', 'больн', 'лаборат']

service = Service("O:\\Dev\\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get(url)
driver.implicitly_wait(random.randint(5, 15))  # Ждём, пока загрузится вся страница

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

def extract_doctor_info(soup):
    # ФИО врача
    fio = soup.find("h1").find("span", {"itemprop": "name"}).text.strip()

    # Специализация
    specialization_tag = soup.find("div", class_="b-doctor-intro__specs")
    specializations = [spec.text for spec in specialization_tag.find_all("a")]
    specialization = ", ".join(specializations)
    
    # Стаж работы
    stazh_tag = soup.find("div", class_="ui-text_subtitle-1")
    experience = stazh_tag.text.replace('Стаж', '').strip() if stazh_tag else "•"

    # Звания
    target_div = soup.find("div", class_="text-left mr-2")
    zvaniya_tags = target_div.find_all("span", class_="b-doctor-card__text-with-dot") if target_div else []
    zvaniya = ', '.join([tag.text.strip() for tag in zvaniya_tags])

    # Клиника
    filtered_clinic_texts = []
    clinic_links = soup.find_all('a', href=lambda href: href and '/lpu/' in href)
    for link in clinic_links:
        if any(keyword.lower() in link.get_text().lower() for keyword in keywords):
            clinic_name = link.get_text(strip=True)
            clinic_url = link['href']
            filtered_clinic_texts.append(f"{clinic_name} ({clinic_url})")

    clinic = filtered_clinic_texts

    # Общий рейтинг врача
    rating_element = soup.find(id="doctor-rating")
    rating_value = rating_element.find(class_="ui-text_h5").text
    rating = rating_value

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
        "отзывов": reviews_count,
        "Образование": education,
        "Фото": photo_url,
        "рейтинг": rating,
    }

doctor_info = extract_doctor_info(soup)

# Сохранение данных в CSV файл
def save_to_csv(data, filename="doctors.csv"):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys(), delimiter=';')
        file_empty = file.tell() == 0
        if file_empty:
            writer.writeheader()
        writer.writerow(data)

save_to_csv(doctor_info)

print(f"Данные {doctor_info['ФИО']} сохранены.")

driver.quit()
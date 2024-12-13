from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from webdriver_manager.chrome import ChromeDriverManager

# Selenium ayarları
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
service = Service(ChromeDriverManager().install())  # Chromedriver'ı otomatik indirir
driver = webdriver.Chrome(service=service, options=options)  # WebDriver ile tarayıcı başlatılır
# URL
url = "https://www.trendyol.com/oyuncu-dizustu-bilgisayari-x-c106084"
driver.get(url)

try:
    cookie_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Kabul Et')]")
    cookie_button.click()
    print("Çerez bildirimi kapatıldı.")
except Exception as e:
    print("Çerez bildirimi bulunamadı veya zaten kapatılmış:", str(e))

scroll_increment = 1000
b=0
while True:
    driver.execute_script(f"window.scrollBy(0, {scroll_increment});")  # 1000 oranında kaydır
    time.sleep(2)  # Yeni içeriklerin yüklenmesi için bekle
    b+=1
    # Yeni yüksekliği kontrol et
    new_height = driver.execute_script("return document.body.scrollHeight")
    print("Yeni yükseklik:", new_height)

    # Bazen kaysa bile yükseklik değişmediği için sabit bir sayı kullandım ve bunu sayaç ile döngüye aldım sayaç büyüdükçe veri
    # çekmeye devam ediyor.

    if b == 3:
        print("döngü tamamlandı , veri çekiildi.")
        break


# Sayfa kaydırma işlemi bitti, HTML'i al
html = driver.page_source
driver.quit()

# BeautifulSoup ile HTML'i işle
soup = BeautifulSoup(html, 'html.parser')

# Verileri toplama
products = []
for item in soup.find_all('div', class_='product-down'):
    marka = item.find('span', class_='prdct-desc-cntnr-ttl').text.strip() if item.find('span', class_='prdct-desc-cntnr-ttl') else "Marka Yok"
    model = item.find('span', class_='prdct-desc-cntnr-name').text.strip() if item.find('span', class_='prdct-desc-cntnr-name') else "Model Yok"
    açıklama = item.find('div', class_='product-desc-sub-text').text.strip() if item.find('div', class_='product-desc-sub-text') else "Açıklama Yok"
    price = item.find('div', class_='prc-box-dscntd').text.strip() if item.find('div', class_='prc-box-dscntd') else "Fiyat Yok"
    rating = item.find('span', class_='rating-score').text.strip() if item.find('span', class_='rating-score') else "N/A"
    reviews = item.find('span', class_='ratingCount').text.strip() if item.find('span', class_='ratingCount') else "0"
    products.append([marka,model,açıklama, price, rating, reviews])

# DataFrame oluştur ve CSV'ye yaz
df = pd.DataFrame(products, columns=['Ürün markası','Ürün modeli','Ürün açıklaması', 'Fiyat', 'Puan', 'Yorum Sayısı'])
df['Tarih'] = datetime.now().strftime("%Y-%m")
df.to_csv('urun_fiyatlari.csv', index=False, encoding='utf-8')
print("Veriler başarıyla kaydedildi.")


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os  # Para forzar el cierre de procesos

# Configuración de opciones para el navegador
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Ruta al ChromeDriver
driver_path = 'C:/Users/User/Desktop/chromedriver-win64/chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Configuración de espera implícita
driver.implicitly_wait(5)

# URL inicial
url = 'https://evokeclub.com.mx/yachts-search-results/?location_name=Riviera+Maya&location_id=20095&start=&end=&date=13%2F10%2F2024+12%3A00+am-14%2F10%2F2024+11%3A59+pm&price_range=0%3B29480&taxonomy%5Bactivity_types%5D='

driver.get(url)

# Espera explícita
wait = WebDriverWait(driver, 10)

# Lista para almacenar todos los títulos de los productos
todos_los_titulos = []

def hacer_scroll():
    """Función para hacer scroll en toda la página hasta el final"""
    ultima_altura = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Espera para cargar nuevos elementos
        nueva_altura = driver.execute_script("return document.body.scrollHeight")
        if nueva_altura == ultima_altura:
            break  # Salir del bucle si no hay más scroll disponible
        ultima_altura = nueva_altura

def extraer_titulos():
    """Función para extraer los títulos de los productos de la página actual"""
    hacer_scroll()  # Hacer scroll antes de extraer títulos para asegurar que todos se carguen
    productos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h4.service-title a')))
    productos_titulos = []  # Lista temporal para almacenar los títulos de una sola página
    for producto in productos:
        titulo = producto.text
        productos_titulos.append({'Título': titulo})  # Almacenar todos los títulos
        print(f"Título: {titulo}")
    return productos_titulos

# Extraer títulos de la primera página
todos_los_titulos.extend(extraer_titulos())

# Manejar la paginación
while True:
    try:
        # Intentar obtener el botón "Siguiente página"
        boton_siguiente = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.next.page-numbers')))
        
        # Desplazarse hacia el botón "Siguiente"
        driver.execute_script("arguments[0].scrollIntoView();", boton_siguiente)
        
        # Esperar hasta que el botón "Siguiente página" esté clicable
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.next.page-numbers')))
        
        # Hacer clic en el botón "Siguiente página"
        boton_siguiente.click()
        
        # Aumentar el tiempo de espera después de hacer clic en "Siguiente página"
        time.sleep(8)  # Dar suficiente tiempo de carga
        
        # Extraer títulos de la nueva página
        nuevos_titulos = extraer_titulos()
        
        # Verificar si se han encontrado nuevos títulos
        if not nuevos_titulos:
            print("No se encontraron nuevos productos.")
            break
        
        todos_los_titulos.extend(nuevos_titulos)

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        break

# Guardar los resultados en un archivo CSV
df = pd.DataFrame(todos_los_titulos)
df.to_csv('productos_titulos.csv', index=False, encoding='utf-8-sig')
print("Datos guardados en 'productos_titulos.csv'")

# Cerrar el navegador con un retraso y forzar el cierre si es necesario
time.sleep(2)  # Esperar un par de segundos antes de cerrar el navegador

try:
    driver.quit()
except Exception as e:
    print(f"Ocurrió un error al cerrar el navegador: {e}")

# Forzar el cierre de procesos de Chrome si queda algún proceso colgado
os.system("taskkill /f /im chromedriver.exe /T")

print("Procesos cerrados.")
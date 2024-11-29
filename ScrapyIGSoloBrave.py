# Pausas entre acciones del script
# Manejo y analisis de datos crea y guarda df de seguidores
# Selenium automatiza navegadores
# webdrives modulo de interaccion para selenium
# by localiza elementos web
# Service//Servicio del controlador de chrome
# Option//Configura las opciones del navegador
import time 
import pandas as pd 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def login_to_instagram(driver, username, password):
    """Inicia sesión en Instagram"""
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(3)
    driver.find_element(By.NAME, 'username').send_keys(username)
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)

def get_followers(username, target_user, driver):
    """Obtiene solo los seguidores de un perfil"""
    driver.get(f'https://www.instagram.com/{target_user}/')
    time.sleep(5)

    # Buscar el enlace de seguidores y hacer clic
    try:
        followers_link = driver.find_element(By.XPATH, "//a[contains(@href, '/followers/')]")
        followers_link.click()
        time.sleep(5)
    except Exception as e:
        print("No se encontró el enlace de seguidores:", e)
        return []

    # Desplazarse hacia abajo para cargar más seguidores
    scroll_box = driver.find_element(By.CSS_SELECTOR, "div.xyi19xy.x1rife3k")  # Contenedor de seguidores
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)

    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
        time.sleep(2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
        if new_height == last_height:
            break
        last_height = new_height

    # Extraer los nombres de los seguidores usando el selector de clase específico
    followers = driver.find_elements(By.CSS_SELECTOR, 'span._ap3a._aaco._aacw._aacx._aad7._aade')
    follower_data = [follower.text for follower in followers if follower.text != '']  # Solo nombres, ignorar vacíos

    return follower_data

def get_number_of_followers(driver, user):
    """Obtiene el número de seguidores de un perfil"""
    driver.get(f'https://www.instagram.com/{user}/')
    time.sleep(3)

    # Intentar encontrar el número de seguidores usando el nuevo selector
    try:
        # Usar un selector más amplio que podría funcionar con más elementos
        followers_count = driver.find_element(By.XPATH, "//span[contains(@class, 'x5n08af') and @title]")
        return followers_count.get_attribute('title')  # Obtén el número de seguidores
    except Exception as e:
        print(f"No se pudo obtener el número de seguidores de {user}: {e}")
        return "N/A"  # Si no se puede obtener el número, devolver N/A

def save_to_csv(data, target_user):
    """Guarda los seguidores en un archivo CSV"""
    filename = f"{target_user}_followers_with_count.csv"
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Datos guardados en {filename}")
    except PermissionError:
        print(f"Error: No se pudo guardar el archivo. Verifica si {filename} está abierto o si tienes permisos.")
    except Exception as e:
        print(f"Error inesperado al guardar el archivo: {e}")

def print_as_table(data):
    """Imprime los datos como tabla en la consola"""
    df = pd.DataFrame(data)
    print("\nTabla de seguidores:")
    print(df.to_string(index=False))  # No mostrar índice

if __name__ == "__main__":
    # Ingresar usuario de Instagram y objetivo
    username = input("Ingresa tu usuario de Instagram: ")
    password = input("Ingresa tu contraseña de Instagram: ")
    target_user = input("Ingresa el usuario objetivo: ")

    # Configuración del navegador
    options = Options()
    options.headless = False  # Cambiar a True si quieres usarlo sin ventana gráfica
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.85 Safari/537.36")
    
    # Configura el driver de Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Iniciar sesión una sola vez
    login_to_instagram(driver, username, password)

    # Obtener los seguidores
    followers = get_followers(username, target_user, driver)

    # Extraer el número de seguidores para cada uno
    followers_with_count = []
    for follower in followers:
        followers_count = get_number_of_followers(driver, follower)
        followers_with_count.append({"Username": follower, "N_Seguidores": followers_count})

    # Imprimir los resultados en la consola
    print_as_table(followers_with_count)

    # Guardar los resultados en un archivo CSV
    save_to_csv(followers_with_count, target_user)

    # Cerrar el navegador después de todo el proceso
    driver.quit()

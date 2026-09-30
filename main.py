from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from pypdf import PdfReader
import re
import os
import sys
import time


# Quando o programa vira executável (PyInstaller), "sys.frozen" passa a existir.
# Nesse caso, o .env deve ficar na MESMA pasta do .exe (e não dentro dele).
if getattr(sys, 'frozen', False):
    pasta_base = os.path.dirname(sys.executable)
else:
    pasta_base = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(pasta_base, '.env'))

PASTA_FILES = os.path.join(pasta_base, 'files')


def salvar_em_files(caminho_minuta, caminho_booking):
    """
    Limpa a pasta files/ e grava os dois arquivos com nome fixo:
        files/minuta_ex.pdf  e  files/booking.pdf
    Retorna os dois caminhos novos.
    """
    # 1. Lê o conteúdo dos dois arquivos para a memória ANTES de apagar qualquer coisa.
    #    Se o usuário escolheu um arquivo que já está em files/, ele não se perde no passo 2.
    with open(caminho_minuta, 'rb') as arquivo:  # 'rb' = ler em modo binário
        conteudo_minuta = arquivo.read()
    with open(caminho_booking, 'rb') as arquivo:
        conteudo_booking = arquivo.read()

    # 2. Cria a pasta se não existir e apaga os arquivos que estavam lá.
    os.makedirs(PASTA_FILES, exist_ok=True)
    for nome in os.listdir(PASTA_FILES):
        caminho = os.path.join(PASTA_FILES, nome)
        if os.path.isfile(caminho):  # apaga só arquivos, nunca subpastas
            os.remove(caminho)

    # 3. Grava os arquivos novos com nome fixo.
    destino_minuta = os.path.join(PASTA_FILES, 'minuta_ex.pdf')
    destino_booking = os.path.join(PASTA_FILES, 'booking.pdf')

    with open(destino_minuta, 'wb') as arquivo:  # 'wb' = gravar em modo binário
        arquivo.write(conteudo_minuta)
    with open(destino_booking, 'wb') as arquivo:
        arquivo.write(conteudo_booking)

    return destino_minuta, destino_booking


# ----------- IA | Slide Submit Button -----------
def submit(driver):

    button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'ui-draggable-handle'))
    )

    track = button.find_element(By.XPATH, '..')
    distance = track.size['width'] - button.size['width']

    ActionChains(driver, duration=0) \
        .click_and_hold(button) \
        .move_by_offset(1, 0) \
        .move_by_offset(distance + 5, 0) \
        .release() \
        .perform()
# ----------- END IA | Slide Submit Button END -----------


def realizar_agendamento(caminho_minuta, caminho_booking, data_hora_1, data_hora_2):
    """
    Executa o robô de agendamento.

    caminho_minuta / caminho_booking: caminho completo dos PDFs escolhidos na tela.
    data_hora_1 / data_hora_2: objetos datetime vindos da tela.
    """

    # file_minuta = PdfReader(caminho_minuta)
    # text_minuta = file_minuta.pages[0].extract_text()

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)

    try:
        driver.get('http://websag.windrose.com.br/arearestrita')

        field_email = driver.find_element(By.ID, 'login')
        field_email.send_keys(os.environ['WINDROSE_LOGIN'])

        field_password = driver.find_element(By.NAME, 'senha')
        field_password.send_keys(os.environ['WINDROSE_PASSWORD'])

        submit(driver)

        # TODO
        time.sleep(0.5)

        scheduling = driver.find_element(By.ID, 'agendamento')
        scheduling.click()

        # TODO
        time.sleep(0.3)

        cad = driver.find_element(By.CLASS_NAME, 'cadastro')
        cad.click()

        # TODO
        time.sleep(0.2)

        select_type = driver.find_element(By.ID, 'tipo')
        select_type.click()

        option_type = driver.find_element(By.XPATH, "//option[@value=1]")
        option_type.click()

        # TODO
        time.sleep(0.1)

        select_company = driver.find_element(By.ID, 'empresa')
        select_company.click()

        time.sleep(0.1)

        option_company = driver.find_element(By.XPATH, '//option[@value=4]')
        option_company.click()

        # TODO: enviar os arquivos. Em um <input type="file">, basta usar
        # send_keys com o caminho do arquivo, por exemplo:
        # driver.find_element(By.ID, 'id_do_campo').send_keys(caminho_minuta)

        # TODO: preencher as datas. Converta o datetime para o texto que o site espera:
        # data_hora_1.strftime('%d/%m/%Y %H:%M')

        time.sleep(10)
    finally:
        # "finally" roda sempre, mesmo se der erro: garante que o Chrome fecha.
        driver.quit()


# Este bloco só roda quando você executa "python main.py" direto.
# Quando o app.py faz "from main import realizar_agendamento", ele NÃO roda.
# Útil para testar o robô sem abrir a tela.
if __name__ == '__main__':
    from datetime import datetime
    realizar_agendamento(
        os.path.join(pasta_base, 'files', 'minuta_ex.pdf'),
        os.path.join(pasta_base, 'files', 'BOOKING.pdf'),
        datetime.now(),
        datetime.now(),
    )

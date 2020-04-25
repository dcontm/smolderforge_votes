import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import lxml
import time
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType

URL='https://www.smolderforge.com/site/'
PROXIES_HUB = 'https://www.sslproxies.org/'


class Storm:


	def get_proxy(self):

		# получаем таблицу с прокси адресами с 'https://www.sslproxies.org/'
		proxies_list=[]
		r = requests.get(PROXIES_HUB)
		soup = BeautifulSoup(r.text, 'lxml')
		proxy_table=soup.find(id='proxylisttable')

		for row in proxy_table.tbody.find_all('tr'):

			#выбираем из каждой строки таблицы столбцы с ip и портом
			#проверяем на доступность и доступные добавляем в список который вернет функция
			proxy = row.find_all('td')[0].string+':'+row.find_all('td')[1].string
			proxies = {'http': proxy}	# аргумент для запроса доступности
			response=requests.get(URL, proxies=proxies, timeout=3)

			if response.status_code == 200:
				proxies_list.append(proxy)

		print('Провера прокси завершена, подготовлено {} адресов'.format(len(proxies_list)))
		print(proxies_list)

		return proxies_list

	def acc_list(self, file="acc.txt"):

		#формируем пару логин пароль из текстового файла
		#каждая пара новая строка в формате login$password
		res=[]
		with open(file,"r") as file:
			acc=file.read().splitlines()
			for every in acc:
				lp=every.split("$")
				res.append(lp)

		return res


	def run(self, headless=True):

		acc=self.acc_list()	# получем список пар логин пароль
		proxies_list=self.get_proxy() # получаем список прокси

		for every in acc:
			# для каждого аккаунта формируем запрос с новым прокси
			proxy = proxies_list.pop()
			print(proxy)

			prox = Proxy()
			prox.proxy_type = ProxyType.MANUAL
			prox.http_proxy = proxy
			prox.ssl_proxy = proxy
			capabilities = webdriver.DesiredCapabilities.CHROME
			prox.add_to_capabilities(capabilities)

			if headless == True:
				# режим запуска вебдрайвера по умолчанию безголовый
				chrome_options = webdriver.ChromeOptions()
				chrome_options.add_argument("--headless")
				driver = webdriver.Chrome(executable_path='/home/dcontm/Рабочий стол/develop/storm/venv/chromedriver', desired_capabilities=capabilities,chrome_options=chrome_options)

			else:
				driver = webdriver.Chrome(executable_path='/home/dcontm/Рабочий стол/develop/storm/venv/chromedriver', desired_capabilities=capabilities)


			driver.get(URL+'vote')
			time.sleep(6)

			username = driver.find_element_by_id('login_userinput')
			password = driver.find_element_by_id('login_passinput')
			login = driver.find_element_by_id('login_submit_1')


			username.send_keys(every[0])
			password.send_keys(every[1])
			login.click() # аутентифицируемся
			print("Вход в систему выполнен.")
			time.sleep(3)

			votes = driver.find_elements_by_class_name('vote_link_button')

			for vote in votes:
				# поочередно сликаем на кнопку голосования
				vote.click()
				print("Голосование успешною.")
				time.sleep(3)

			driver.quit()
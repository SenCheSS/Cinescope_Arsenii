# Обращение по классу
#page.locator('.submit-button')     # Найдет все элементы с классом submit-button

# Обращение по id элемента
#page.locator('#search')    # Найдет элементы с (id)search

# Обращение по значению атрибута
#page.locator('[name="agreement"]')     # Найдет элемент с атрибутом name = "agreement" в данном случае чекбокс

# Поиск элемента с текстом ":has-text"
#page.locator('p:has-text("Загрузка завершена")')   # Данный локатор ищет на странице параграф <p>, что содержит текст "Загрузка завершена"

# Поиск элемента с текстом "text="
#page.locator('button', text='Отправить')   # Этот локатор найдет кнопку содержащая текст "Отправить"
# Важный момент: Содержит, а не совпадает. Регистр не важен.

# Поиск по тегу элемента
#page.locator("input")      # В данном случае вернет все 3 элемента <input>

# Вложенные элементы
#page.locator("#product-card span").text_content()      # В данном примере локатор найдет элемент <span> внутри элемента с id product-card
# Также можно использовать оператор >> или chaining (цепочку) методов locator()
#page.locator("#product-card >> .price")
#page.locator("#product-card").locator(".price")

# Поиск по нескольким селекторам
#page.locator("input#search.input_main")    #В данном случае будет найден именно 1 элемент, соответствующий *всем* правилам: - тег - `input`- id = `search`- class = `input_main`


#Playwright локаторы "get_by"

#Поиск элементов по роли "page.get_by_role()"
#<button>Sign in</button>
#page.get_by_role("button", name="Sign in").click() #Код найдет кнопку с нужной ролью и доступным именем "Sign in" и кликнет по ней.

# ПРИМЕР
#<h3>Sign up</h3>
#<label>
#  <input type="checkbox" /> Subscribe
#</label>
#<br/>
#<button>Submit</button>
#----
#expect(page.get_by_role("headiсng", name="Sign up"))
#page.get_by_role("checkbox", name="Subscribe")
#page.get_by_role("button", name=re.compile("submit", re.IGNORECASE)) #Регулярное выражение для name

# Поиск элементов по тексту "page.get_by_text()"
#находит элемент по тексту, который он содержит.

#ПРИМЕР
#<span>Welcome, John</span>
#page.get_by_text("Welcome") #Найдет элемент, содержащий "Welcome"
#page.get_by_text("John") #Найдет элемент, содержащий "John"
#в обоих вариантах мы найдем элемент <span>, с текстом "Welcome, John"

# Поиск элементов по метке "page.get_by_label()"
#ПРИМЕР
#<label for="password">Password</label>
#<input type="password" id="password" />
#page.get_by_label("Password")      #Этот код найдет поле ввода пароля, связанное с меткой "Password"

# Поиск элементов по placeholder "page.get_by_placeholder()"
# ищет элемент <input> у которого атрибут placeholder содержит указанный текст.
#ПРИМЕР
#<input type="email" placeholder="name@example.com" />
#page.get_by_placeholder("name@example.com").fill("playwright@microsoft.com")
# ищет точное совпадение с текстом в атрибуте placeholder. Регистр не важен
# Только для <input>

# Поиск элементов по alt тексту "page.get_by_alt_text()"
# ищет элемент <img> у которого атрибут alt содержит указанный текст.
#ПРИМЕР
#<img alt="playwright logo" src="/img/playwright-logo.svg" width="100" />
#page.get_by_alt_text("playwright logo").click()
# ищет точное совпадение с текстом в атрибуте alt. Регистр не важен
# Только для <img>

# Поиск элементов по title "(page.get_by_title())"
# Вы можете найти элемент с соответствующим атрибутом title, используя page.get_by_title()
#ПРИМЕР
#<span title='Issues count'>25 issues</span>
#page.get_by_title("Issues count")
# ищет точное совпадение с текстом в атрибуте title. Регистр не важен

# Поиск элементов по test id "(page.get_by_test_id())"
#  ищет элемент, у которого атрибут data-testid (по умолчанию) или другой настроенный атрибут содержит указанный test id
#ПРИМЕР
#<button data-testid="directions">Itinéraire</button>
#page.get_by_test_id("directions").click()
# Использовать только тогда когда не работают другие методы
# Когда договорился с разработчиками
# Избегайте использования test id для всех элементов подряд


"""--------------------"""

# Взаимодействие с элементами

# Клик по элементу (page.click())
#page.click('button#submit')                                #Клик по кнопке с id
#page.get_by_role('link', name='Подробнее').click()         #Клик по элементу с классом, с уже полученным локатором
#page.click('button#submit', force=True, timeout=5000)      #Дополнительные опции (макс. время ожидания клика 5 секунд).

# Заполнение текстового поля (page.fill())
#page.fill(selector, text, [options])
#page.fill('input[name="q"]', 'Playwright')     #Заполнение поля ввода с name
#page.fill('#message', 'Hello, Playwright!')    #Заполнение textarea

# Ввод текста (имитация пользователя) (page.type())
#page.type(selector, text, [options])
#page.type('input[name="q"]', 'Playwright')     #Имитация посимвольного ввода текста

# Выбор чекбокса (page.check())
#page.check(selector, [options])
#page.check('#agreement')       #Установка флажка в чекбоксе с id agreement.

# Выбор радиобаттона (page.check())
#page.check(selector, [options])
#page.check('#option1')        #Выбор радиобаттона с id option1.

# Выбор опции из выпадающего списка (page.select_option())
#page.select_option(selector, value)
#page.select_option('#country', 'ca')   #Выбор опции "Canada" из выпадающего списка с id country.

# Получение текста элемента (page.text_content())
#page.text_content(selector)
#message = page.text_content('#message')
#print(message)                            #Выведет "Hello, Playwright!".

# Получение значения атрибута (page.get_attribute())
#page.get_attribute(selector, attribute_name)
#href = page.get_attribute('#link', 'href')
#print(href)                                #Выведет "/about".

# Переход по ссылке (page.goto())
#page.goto(url, [options])
#page.goto('https://www.example.com')       #Открытие страницы https://www.example.com.


'''-----------------------------------------------------------------'''


# Ожидания и состояния

# Ожидание загрузки страницы "page.wait_for_load_state()"
#page.wait_for_load_state([state, [options]])

#page.wait_for_load_state('load')                           # Ожидает полной загрузки страницы (событие 'load')
#page.wait_for_load_state('domcontentloaded')               # Ожидает загрузки DOM (событие 'domcontentloaded')
#page.wait_for_load_state('networkidle2', timeout=10000)    # Ожидает, пока не будет более 2 сетевых запросов в течение 500 мс (networkidle2), но не более 10 секунд


# Проверка видимости элемента "page.is_visible()"
#page.is_visible(selector)

#<div id="message" style="display: none;">Hello!</div>
#is_visible = page.is_visible('#message')
#print(is_visible)  # Выведет False, так как элемент скрыт


# Проверка активности элемента "page.is_enabled()"
#page.is_enabled(selector)

#<button id="submit" disabled>Отправить</button>
#<button id="submit2">Отправить</button>

#is_enabled = page.is_enabled('#submit')     # Проверяем, доступна ли кнопка с id "submit"
#print(is_enabled)                           # Выведет False, так как кнопка disabled

#is_enabled2 = page.is_enabled('#submit2')   # Проверяем, доступна ли кнопка с id "submit2"
#print(is_enabled2)                          # Выведет True, так как кнопка активна


# Ожидание появления элемента на странице "page.wait_for_selector()"
#page.wait_for_selector(selector, [options])

#page.wait_for_selector('div.popup', state='visible', timeout=10000)
# Ожидает, пока элемент div.popup станет видимым, но не более 10 секунд
#page.wait_for_selector('div.popup', state='attached', timeout=10000)
# Ожидает, пока элемент div.popup будет добавлен в DOM, но не более 10 секунд


#Ожидание скрытия элемента "page.is_hidden()" и "page.wait_for_selector()"

#page.is_hidden(selector)
#<div class="loading" style="display: block;">Загрузка...</div>
#is_hidden = page.is_hidden('.loading')
# Проверяем, скрыт ли элемент с классом "loading"
#print(is_hidden)  # Выведет False, так как элемент виден

#page.wait_for_selector() с состоянием hidden или detached

#page.wait_for_selector('.loading', state='hidden', timeout=10000)
# Ожидает, пока элемент с классом "loading" станет невидимым, но не более 10 секунд
#page.wait_for_selector('.loading', state='detached', timeout=10000)
# Ожидает, пока элемент с классом "loading" будет удален из DOM, но не более 10 секунд


'''----------------------------------------------------------------------------'''


# expect (встроенные assert’ы) в playwright

#
import pygame
import pygame as pg
import sys
from time import sleep
import random


# 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 - токен Егора Атарщикова на гитхабе





# Инициализация Pygame
pygame.init()
pygame.font.init() # Инициализация модуля шрифтов

# --- Константы ---
SCREEN_WIDTH = 800 # Ширина основного игрового поля без областей счета
SCREEN_HEIGHT = 600 # Высота всего окна
BALL_SIZE = 20
PADDLE_WIDTH = 20 # Ширина вертикальных платформ
PADDLE_HEIGHT = 100 # Высота вертикальных платформ
PADDLE_MARGIN = 30 # Отступ платформ от края игрового поля

# Ширина области для счета с каждой стороны
SCORE_AREA_WIDTH = 100

# Общая ширина окна, включая области счета
SCREEN_WIDTH_EXTENDED = SCREEN_WIDTH + 2 * SCORE_AREA_WIDTH

WHITE = (255, 255, 255) # Белый цвет
BLACK = (0, 0, 0)     # Черный цвет
RED = (255, 0, 0)       # Красный цвет
BLUE = (0, 0, 255)      # Синий цвет
GREEN = (0, 255, 0)     # Зеленый цвет (для сообщения о победе)
GRAY = (150, 150, 150) # Серый цвет (для кнопок меню)

BALL_SPEED_X = 4
BALL_SPEED_Y = 4
PADDLE_SPEED = 9
AI_SPEED = 7

SCORE_TO_WIN = 10 # Сколько очков нужно для победы

# Состояния игры
STATE_MENU = 0
STATE_PVP = 1 # Player vs Player (1v1)
STATE_PVAI = 2 # Player vs AI (1vAI)
STATE_GAME_OVER = 4

# --- Классы для отрисовки ---
class Area():
    def __init__(self, x=0, y=0, width=10, height=10, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.fill_color = color

    def set_color(self, new_color):
        self.fill_color = new_color

    def fill(self, surface):
        # Рисуем прямоугольник только если fill_color задан (не None)
        if self.fill_color is not None:
            pygame.draw.rect(surface, self.fill_color, self.rect)

    def outline(self, surface, frame_color, thickness):
        pygame.draw.rect(surface, frame_color, self.rect, thickness)

    # Метод collidepoint принимает два отдельных аргумента x и y
    def collidepoint(self, x, y):
        return self.rect.collidepoint(x, y)

    def colliderect(self, rect):
        return self.rect.colliderect(rect)


class Picture(Area):
    def __init__(self, filename, x=0, y=0, width=10, height=10):
        # Задаем color=None, так как у Picture нет своего цвета заливки, только изображение
        super().__init__(x=x, y=y, width=width, height=height, color=None)
        self.original_image = None # Для хранения оригинального изображения
        try:
            self.original_image = pygame.image.load(filename)
            self.image = pygame.transform.scale(self.original_image, (width, height))
        except pygame.error as e:
            print(f"Не удалось загрузить изображение {filename}: {e}. Используется цветная заглушка.")
            self.image = pygame.Surface([width, height])
            self.image.fill(GRAY) # Цвет по умолчанию для заглушки
            self.rect = self.image.get_rect(topleft=(x, y)) # Обновим rect на основе размера заглушки


    def draw(self, surface):
        # Отрисовываем изображение. У Picture нет своей заливки перед draw.
        surface.blit(self.image, self.rect.topleft)

    # Метод для изменения размера изображения, если оно было успешно загружено
    def scale_image(self, new_width, new_height):
        self.rect.width = new_width
        self.rect.height = new_height
        if self.original_image: # Ма


            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        else: # Если изображение не загружено, просто создаем новую цветную заглушку
             self.image = pygame.Surface([new_width, new_height])
             self.image.fill(GRAY) # Цвет по умолчанию для заглушки
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))


class Label(Area):
    # color=None по умолчанию, чтобы метки не рисовали фоновый прямоугольник
    def __init__(self, x=0, y=0, width=10, height=10, color=None):
        super().__init__(x=x, y=y, width=width, height=height, color=color)
        self.font = None
        self.text_surface = None
        self.text_color = BLACK
        self._text = "" # Добавлено для хранения исходного текста

    def draw(self, surface):
        # self.fill(surface) # Удалена заливка фона, чтобы метки не рисовали прямоугольник
        if self.text_surface:
            # Отрисовываем текст по центру области Label
            text_rect = self.text_surface.get_rect(center=self.rect.center)
            surface.blit(self.text_surface, text_rect)

    # Обновлен метод set_text для хранения текста и использования str(text)
    def set_text(self, text, fsize=24, text_color=BLACK, font_name='Verdana.ttf'):
        self._text = text # Сохраняем исходный текст
        try:
            self.font = pygame.font.Font(font_name, fsize)
        except pygame.error:
            self.font = pygame.font.SysFont('Arial', fsize) # Используем системный шрифт
            print(f"Шрифт {font_name} не найден. Используется Arial.")
        self.text_color = text_color
        # Преобразуем текст в строку при рендеринге
        self.text_surface = self.font.render(str(self._text), True, self.text_color)


# --- Инициализация игрового окна ---
# Увеличена ширина экрана, чтобы освободить место для счета сбоку
# SCREEN_WIDTH_EXTENDED определена выше в константах
mw = pygame.display.set_mode((SCREEN_WIDTH_EXTENDED, SCREEN_HEIGHT))
pygame.display.set_caption("Ping Pong")
clock = pygame.time.Clock() # Переменная clock теперь определена в глобальной области


# --- Глобальные переменные игры (инициализируются в create_game_objects) ---
ball = None
paddle_left = None
paddle_right = None
paddle_top = None # Не используется в режимах 1v1/1vAI
paddle_bottom = None # Не используется в режимах 1v1/1vAI

ball_dx = 0 # Скорость мяча по X
ball_dy = 0 # Скорость мяча по Y

# Флаги движения игроков (читаются одновременно в handle_input)
move_left_up = False    # Игрок 1 (слева)
move_left_down = False
move_right_up = False   # Игрок 2 (справа)
move_right_down = False


# Флаги AI
is_right_ai = False # True, если правая платформа - бот
is_left_ai = False # По умолчанию False (левый игрок)


# Счет
score_left = 0 # Счет левого игрока
score_right = 0 # Счет правого игрока


# Метки для отображения счета сбоку
# Настроены так, чтобы отображаться слева и справа от основного игрового поля
score_label_left = Label() # Переменная score_label_left определена
score_label_right = Label() # Переменная score_label_right определена


# Переменные состояния игры
current_game_state = STATE_MENU

# Объекты меню
menu_title = None
menu_button_pvp = None
menu_button_pvai = None


# --- Функции игры ---

# Функция создания объектов меню
def create_menu_objects(): # Функция create_menu_objects определена
    global menu_title, menu_button_pvp, menu_button_pvai

    menu_title = Label(0, 100, SCREEN_WIDTH_EXTENDED, 80) # SCREEN_WIDTH_EXTENDED определена
    menu_title.set_text("Pygame Pong", fsize=60, text_color=BLACK)

    button_width = 400
    button_height = 60
    button_x = (SCREEN_WIDTH_EXTENDED - button_width) // 2

    menu_button_pvp = Label(button_x, 250, button_width, button_height, color=GRAY)
    menu_button_pvp.set_text("Игрок против Игрока (1v1)", fsize=24, text_color=BLACK)

    menu_button_pvai = Label(button_x, 330, button_width, button_height, color=GRAY)
    menu_button_pvai.set_text("Игрок против Бота (1vAI)", fsize=24, text_color=BLACK)


# Функция отрисовки меню
def draw_menu(surface): # Функция draw_menu определена
    surface.fill(WHITE) # Белый фон меню
    menu_title.draw(surface)
    menu_button_pvp.draw(surface)
    menu_button_pvai.draw(surface)


# Функция обработки клика в меню
def handle_menu_click(pos): # Функция handle_menu_click определена
    global current_game_state, score_left, score_right

    score_left = 0
    score_right = 0

    if menu_button_pvp.collidepoint(*pos):
        current_game_state = STATE_PVP
        create_game_objects()
    elif menu_button_pvai.collidepoint(*pos):
        current_game_state = STATE_PVAI
        create_game_objects()


# Функция создания игровых объектов
def create_game_objects(): # Функция create_game_objects определена
    global ball, paddle_left, paddle_right, paddle_top, paddle_bottom
    global is_left_ai, is_right_ai
    global score_left, score_right
    global score_label_left, score_label_right

    # Сбрасываем счет
    score_left = 0
    score_right = 0

    # Сбрасываем флаги AI
    is_left_ai = False
    is_right_ai = False

    # Определяем границы игрового поля (для размещения мяча и платформ)
    game_area_x_start = SCORE_AREA_WIDTH
    game_area_width = SCREEN_WIDTH_EXTENDED - 2 * SCORE_AREA_WIDTH

    # Создаем мяч. Координаты должны быть внутри *игрового поля*
    ball_start_x = game_area_x_start + (game_area_width - BALL_SIZE) // 2
    ball_start_y = (SCREEN_HEIGHT - BALL_SIZE) // 2 # Мяч центрируется по высоте всего окна

    ball = Picture('ball.png', ball_start_x, ball_start_y, BALL_SIZE, BALL_SIZE)
    reset_ball(0) # Функция reset_ball определена


    # Пересоздаем метки счета, чтобы они были типа Label() без фона по умолчанию
    score_label_left = Label()
    score_label_right = Label()
    # Эти метки не используются в этих режимах, но определены в глобальной области
    score_label_red = Label()
    score_label_blue = Label()


    # Создаем вертикальные платформы. Координаты должны быть относительно *игрового поля*
    paddle_left = Picture('youPlat.png', game_area_x_start + PADDLE_MARGIN, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_right = Picture('enPlat.png', SCREEN_WIDTH_EXTENDED - SCORE_AREA_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH, (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_top = None # Горизонтальные платформы не используются
    paddle_bottom = None # Горизонтальные платформы не используются


    # Настраиваем метки счета, чтобы они были сбоку от игрового поля
    score_label_left.rect = pygame.Rect(0, SCREEN_HEIGHT // 2 - 25, SCORE_AREA_WIDTH, 50) # Слева в середине, ширина = SCORE_AREA_WIDTH
    score_label_right.rect = pygame.Rect(SCREEN_WIDTH_EXTENDED - SCORE_AREA_WIDTH, SCREEN_HEIGHT // 2 - 25, SCORE_AREA_WIDTH, 50) # Справа в середине


    if current_game_state == STATE_PVAI:
         is_right_ai = True # Правая платформа - бот


# Функция сброса мяча
def reset_ball(scoring_side=0): # Функция reset_ball определена
    global ball_dx, ball_dy

    # Центр игрового поля, а не всего экрана
    game_area_x_start = SCORE_AREA_WIDTH
    game_area_width = SCREEN_WIDTH_EXTENDED - 2 * SCORE_AREA_WIDTH
    ball.rect.center = (game_area_x_start + game_area_width // 2, SCREEN_HEIGHT // 2)


    if scoring_side == 0:
        direction_x = random.choice([-1, 1])
        direction_y = random.choice([-1, 1])
    else:
        # Направление после гола в режимах 1v1/1vAI
        if scoring_side == 1: direction_x = 1 # Мимо левого -> летит вправо (к правому)
        elif scoring_side == 2: direction_x = -1 # Мимо правого -> летит влево (к левому)
        else: direction_x = random.choice([-1, 1]) # В 1v1/1vAI scoring_side всегда 1 или 2

        # В 1v1/1vAI мяч всегда отбивается от верхнего/нижнего края, направление по Y случайное после гола
        direction_y = random.choice([-1, 1])


    ball_dx = BALL_SPEED_X * direction_x
    ball_dy = BALL_SPEED_Y * direction_y

    sleep(0.5)


# Функция обработки ввода
def handle_input():
    global move_left_up, move_left_down, move_right_up, move_right_down

    keys = pygame.key.get_pressed()

    # Управление Игрока 1 (слева) - стрелки ВВЕРХ/ВНИЗ
    move_left_up = keys[pygame.K_UP]
    move_left_down = keys[pygame.K_DOWN]

    # Управление Игрока 2 (справа в 1v1) - W/S
    # Этот блок активен ТОЛЬКО если правая платформа не AI (т.е. в режиме 1v1)
    if not is_right_ai:
        move_right_up = keys[pygame.K_w]
        move_right_down = keys[pygame.K_s]
    else:
        move_right_up = False
        move_right_down = False


# Функция обновления движения платформ и AI
def update_movement():
    # Движение левой платформы (Игрок 1) - вертикальное
    if paddle_left:
        if not is_left_ai: # Если это игрок
             if move_left_up: paddle_left.rect.y -= PADDLE_SPEED
             if move_left_down: paddle_left.rect.y += PADDLE_SPEED
        # Ограничение движения по вертикали в пределах экрана
        paddle_left.rect.top = max(0, paddle_left.rect.top)
        paddle_left.rect.bottom = min(SCREEN_HEIGHT, paddle_left.rect.bottom)


    # Движение правой платформы (Игрок 2 в 1v1 / Бот в 1vAI) - вертикальное
    if paddle_right:
        if not is_right_ai: # Если это игрок (только в 1v1)
             if move_right_up: paddle_right.rect.y -= PADDLE_SPEED
             if move_right_down: paddle_right.rect.y += PADDLE_SPEED
        else: # Если это бот (1vAI)
            # AI движение по вертикали: следует за центром мяча
            if ball.rect.centery < paddle_right.rect.centery:
                paddle_right.rect.y -= AI_SPEED
            elif ball.rect.centery > paddle_right.rect.centery:
                paddle_right.rect.y += AI_SPEED
        # Ограничение движения по вертикали
        paddle_right.rect.top = max(0, paddle_right.rect.top)
        paddle_right.rect.bottom = min(SCREEN_HEIGHT, paddle_right.rect.bottom)


# --- Функция проверки столкновений ---
def check_collisions(): # Функция check_collisions определена
    global ball_dx, ball_dy

    # Столкновение с вертикальными платформами (слева и справа)
    # Проверяем столкновение ТОЛЬКО если мяч движется в сторону платформы
    # и убеждаемся, что мяч находится в пределах вертикальных границ платформы по Y
    if ball_dx < 0 and paddle_left and ball.rect.colliderect(paddle_left.rect):
        # Дополнительная проверка, чтобы мяч не "застревал" или не проходил насквозь при быстром движении
        if ball.rect.right > paddle_left.rect.left:
             ball_dx *= -1
             # ball_dy = (ball.rect.centery - paddle_left.rect.centery) / (PADDLE_HEIGHT / 2) * abs(ball_dx) * 0.5 # Отскок по Y

    elif ball_dx > 0 and paddle_right and ball.rect.colliderect(paddle_right.rect):
         if ball.rect.left < paddle_right.rect.right:
            ball_dx *= -1
            # ball_dy = (ball.rect.centery - paddle_right.rect.centery) / (PADDLE_HEIGHT / 2) * abs(ball_dx) * 0.5


    # Столкновение с верхним и нижним краями экрана (активно в обоих режимах)
    if ball.rect.top <= 0:
        ball_dy *= -1
    elif ball.rect.bottom >= SCREEN_HEIGHT:
        ball_dy *= -1


# --- Функция проверки счета ---
def check_scoring(): # Функция check_scoring определена
    global score_left, score_right, current_game_state

    scored = False
    scoring_side = 0 # 1-мимо левого, 2-мимо правого

    # Определяем границы игрового поля
    game_area_x_start = SCORE_AREA_WIDTH
    game_area_x_end = SCREEN_WIDTH_EXTENDED - SCORE_AREA_WIDTH

    # Проверка голов
    if ball.rect.left <= game_area_x_start: # Гол мимо левого (влетел в левую область счета)
        score_right += 1
        scored = True
        scoring_side = 2 # Мимо левого -> отправить в сторону правого
    elif ball.rect.right >= game_area_x_end: # Гол мимо правого (влетел в правую область счета)
        score_left += 1
        scored = True
        scoring_side = 1 # Мимо правого -> отправить в сторону левого

    if scored:
        # Проверка условия победы
        if score_left >= SCORE_TO_WIN or score_right >= SCORE_TO_WIN:
            current_game_state = STATE_GAME_OVER
        else:
            reset_ball(scoring_side) # Сброс мяча после гола


# --- Функция обновления игры ---
def update_game():
    global ball_dx, ball_dy

    # Обновление положения мяча
    ball.rect.x += ball_dx
    ball.rect.y += ball_dy

    # Обновление движения платформ (игроки и AI)
    update_movement()

    # Проверка столкновений мяча с платформами или краями
    check_collisions() # Функция check_collisions определена

    # Проверка забитых голов и обновление счета
    check_scoring() # Функция check_scoring определена


# --- Функция отрисовки игры ---
def draw_game(surface): # Функция draw_game определена
    surface.fill(WHITE) # Белый фон игры

    # Отрисовка игрового поля (опционально, можно нарисовать границы)
    # pygame.draw.line(surface, BLACK, (SCORE_AREA_WIDTH, 0), (SCORE_AREA_WIDTH, SCREEN_HEIGHT), 2)
    # pygame.draw.line(surface, BLACK, (SCREEN_WIDTH_EXTENDED - SCORE_AREA_WIDTH, 0), (SCREEN_WIDTH_EXTENDED - SCORE_AREA_WIDTH, SCREEN_HEIGHT), 2)


    # Отрисовка платформ (всегда вертикальные в этих режимах)
    if paddle_left:
        paddle_left.fill(surface) # Заливка цветом (если задан)
        paddle_left.draw(surface) # Отрисовка изображения

    if paddle_right:
        paddle_right.fill(surface)
        paddle_right.draw(surface)


    # Отрисовка мяча
    if ball:
        ball.draw(surface)

    # Отрисовка счета сбоку
    # Цвет текста черный, чтобы был виден на белом фоне
    score_label_left.set_text(f"{score_left}", text_color=BLACK) # Переменная score_label_left определена
    score_label_left.draw(surface) # Метка слева

    score_label_right.set_text(f"{score_right}", text_color=BLACK) # Переменная score_label_right определена
    score_label_right.draw(surface) # Метка справа


# Функция отрисовки экрана конца игры
def draw_game_over(surface): # Функция draw_game_over определена
    surface.fill(WHITE) # Белый фон конца игры

    final_score_text = ""
    winner_text = ""

    if current_game_state == STATE_PVP:
        final_score_text = f"Финальный счет: {score_left} - {score_right}"
        winner_text = f"Победил Игрок {'Слева' if score_left >= SCORE_TO_WIN else 'Справа'}!"
    elif current_game_state == STATE_PVAI:
        final_score_text = f"Финальный счет: {score_left} - {score_right}"
        winner_text = f"Победил {'Игрок' if score_left >= SCORE_TO_WIN else 'Бот'}!"


    # Метка финального счета
    final_score_label = Label(0, SCREEN_HEIGHT // 2 - 100, SCREEN_WIDTH_EXTENDED, 50) # SCREEN_WIDTH_EXTENDED определена
    final_score_label.set_text(final_score_text, fsize=40, text_color=BLACK) # Черный текст
    final_score_label.draw(surface)

    # Метка победителя
    winner_message = Label(0, SCREEN_HEIGHT // 2 - 50, SCREEN_WIDTH_EXTENDED, 100) # winner_message определена. Позиция скорректирована, чтобы не перекрывать счет.
    winner_message.set_text(winner_text, fsize=50, text_color=GREEN) # Зеленый текст
    winner_message.draw(surface)

    # Метка инструкции для возврата в меню
    restart_message = Label(0, SCREEN_HEIGHT // 2 + 100, SCREEN_WIDTH_EXTENDED, 50) # SCREEN_WIDTH_EXTENDED определена
    restart_message.set_text("Нажмите любую клавишу для возврата в меню", fsize=20, text_color=BLACK) # Черный текст
    restart_message.draw(surface)


# --- Главный игровой цикл ---
game_running = True
create_menu_objects() # Функция create_menu_objects определена

while game_running:
    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_game_state == STATE_MENU:
                handle_menu_click(event.pos) # Функция handle_menu_click определена

        if event.type == pygame.KEYDOWN:
            if current_game_state == STATE_GAME_OVER:
                 current_game_state = STATE_MENU
                 create_menu_objects() # Функция create_menu_objects определена

    # --- Обновление состояния игры (только в режимах игры)


    if current_game_state != STATE_MENU and current_game_state != STATE_GAME_OVER:
        handle_input() # Функция handle_input определена
        update_game() # Функция update_game определена

    # --- Отрисовка ---
    if current_game_state == STATE_MENU:
        draw_menu(mw) # Функция draw_menu определена. Переменная mw определена.
    elif current_game_state == STATE_PVP or current_game_state == STATE_PVAI:
        draw_game(mw) # Функция draw_game определена. Переменная mw определена.
    elif current_game_state == STATE_GAME_OVER:
        draw_game_over(mw) # Функция draw_game_over определена. Переменная mw определена.

    # --- Обновление экрана и контроль FPS ---
    pygame.display.update()
    clock.tick(60) # Переменная clock определена

# --- Завершение Pygame ---
pygame.quit()
sys.exit()

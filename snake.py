import pygame
import sys
import random
from pygame.math import Vector2

CELL_SIZE, NUMBER_OF_CELLS, OFFSET = 15, 25, 75
FONT_PATH = 'Monocraft.ttf'
SNAKE_INITIAL_INTERVAL = 125
COLORS = {'BLUE': (0, 14, 128), 'WHITE': (255, 255, 255), 'LIGHT_GRAY': (
    230, 230, 230), 'GREEN': (0, 255, 0), 'BLACK': (0, 0, 0)}


class GameState:
    DIFFICULTY_SELECT, RUNNING, STOPPED, WON = "DIFFICULTY_SELECT", "RUNNING", "STOPPED", "WON"


class Direction:
    UP, DOWN, LEFT, RIGHT = Vector2(
        0, -1), Vector2(0, 1), Vector2(-1, 0), Vector2(1, 0)


pygame.init()
font = pygame.font.Font(FONT_PATH, 35)
end_game_font = pygame.font.Font(FONT_PATH, 20)


class Food:
    def __init__(self, snake_body, obstacles):
        self.position = self.generate_random_pos(snake_body, obstacles)

    def draw(self):
        food_rect = pygame.Rect(OFFSET + self.position.x * CELL_SIZE, OFFSET + self.position.y * CELL_SIZE,
                                CELL_SIZE, CELL_SIZE)
        pygame.draw.circle(
            screen, COLORS['WHITE'], food_rect.center, CELL_SIZE // 2)

    def generate_random_cell(self):
        x = random.randint(0, NUMBER_OF_CELLS - 1)
        y = random.randint(0, NUMBER_OF_CELLS - 1)
        return Vector2(x, y)

    def generate_random_pos(self, snake_body, obstacles):
        position = self.generate_random_cell()
        while position in snake_body or position in obstacles:
            position = self.generate_random_cell()
        return position


class Snake:
    def __init__(self, obstacles):
        self.body = []
        self.generate_random_spawn_point(obstacles)
        self.direction = Direction.UP
        self.add_segment = False
        self.eat_sound = pygame.mixer.Sound("Sounds/eat.mp3")
        self.death_sound = pygame.mixer.Sound("Sounds/death.mp3")
        self.fireworks_sound = pygame.mixer.Sound("Sounds/fireworks.mp3")

    def generate_random_spawn_point(self, obstacles):
        while True:
            random_x = random.randint(0, NUMBER_OF_CELLS - 3)
            random_y = random.randint(0, NUMBER_OF_CELLS - 3)
            new_body = [Vector2(random_x, random_y + _) for _ in range(3)]

            if not any(pos in obstacles for pos in new_body):
                self.body = new_body
                break

    def draw(self):
        for i, segment in enumerate(self.body):
            brightness = 1.0 - i / len(self.body)
            color = pygame.Color(255, 255, 255)
            color.hsva = (0, 0, brightness * 100, 100)
            segment_rect = (
                OFFSET + segment[0] * CELL_SIZE, OFFSET + segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, segment_rect, 0, 4)

    def update(self):
        new_head = self.body[0] + self.direction
        self.body.insert(0, new_head)

        if self.add_segment:
            self.add_segment = False
        else:
            self.body = self.body[:-1]

    def reset(self, obstacles):
        self.body = []
        self.generate_random_spawn_point(obstacles)
        self.direction = Direction.UP


class Game:
    def __init__(self):
        self.obstacles = []
        self.snake = Snake(self.obstacles)
        self.food = Food(self.snake.body, self.obstacles)
        self.state = GameState.DIFFICULTY_SELECT
        self.difficulty = "HARD"
        self.score = 0
        self.best_score = self.load_best_score()

        if self.difficulty == "HARD":
            self.generate_obstacles()
            self.snake.generate_random_spawn_point(self.obstacles)

    def generate_obstacles(self):
        if self.difficulty == "HARD":
            num_obstacles = 144
            self.obstacles = []

            start_col = 1
            start_row = 1

            for i in range(num_obstacles):
                obstacle_pos = Vector2(start_col + (i % (NUMBER_OF_CELLS // 2)) * 2,
                                       start_row + (i // (NUMBER_OF_CELLS // 2)) * 2)
                self.obstacles.extend(
                    [obstacle_pos, obstacle_pos])

    def draw_obstacles(self):
        if self.difficulty == "HARD":
            for obstacle in self.obstacles:
                obstacle_rect = pygame.Rect(
                    OFFSET + obstacle.x * CELL_SIZE, OFFSET + obstacle.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, COLORS['BLACK'], obstacle_rect)

    def draw_difficulty_select(self):
        difficulty_surface = font.render(
            "Select Difficulty:", True, COLORS['WHITE'])
        easy_surface = font.render("Easy (Press E)", True, COLORS['WHITE'])
        hard_surface = font.render("Hard (Press H)", True, COLORS['WHITE'])

        difficulty_pos = (
            screen.get_width() // 2 - difficulty_surface.get_width() // 2,
            screen.get_height() // 2 - difficulty_surface.get_height() - 50
        )
        easy_pos = (
            screen.get_width() // 2 - easy_surface.get_width() // 2,
            screen.get_height() // 2
        )
        hard_pos = (
            screen.get_width() // 2 - hard_surface.get_width() // 2,
            screen.get_height() // 2 + easy_surface.get_height()
        )

        screen.blit(difficulty_surface, difficulty_pos)
        screen.blit(easy_surface, easy_pos)
        screen.blit(hard_surface, hard_pos)

    def update_difficulty_select(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.difficulty = "EASY"
                self.state = GameState.RUNNING
            elif event.key == pygame.K_h:
                self.difficulty = "HARD"
                self.state = GameState.RUNNING

    def load_best_score(self):
        try:
            with open(f"best_score_{self.difficulty.lower()}.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def save_best_score(self):
        with open(f"best_score_{self.difficulty.lower()}.txt", "w") as file:
            file.write(str(self.best_score))

    def draw_win_message(self):
        win_message_surface = end_game_font.render(
            "Thank you for the game, you won it!", True, COLORS['GREEN'])
        win_message_pos = (screen.get_width() // 2 - win_message_surface.get_width() // 2,
                           screen.get_height() // 2 - win_message_surface.get_height() - 50)
        screen.blit(win_message_surface, win_message_pos)

    def check_win_condition(self):
        win_condition = 0
        if self.difficulty == "EASY":
            win_condition = NUMBER_OF_CELLS * NUMBER_OF_CELLS
        else:
            win_condition = NUMBER_OF_CELLS * \
                NUMBER_OF_CELLS - len(self.obstacles)
        if len(self.snake.body) == win_condition:
            self.state = GameState.WON
            self.snake.fireworks_sound.play()

    def draw(self):
        self.food.draw()
        self.snake.draw()
        if self.state == GameState.WON:
            self.draw_win_message()

    def update(self):
        if self.state == GameState.RUNNING:
            self.snake.update()
            self.check_collision_with_food()
            self.check_collision_with_edges()
            self.check_collision_with_tail()
            self.check_win_condition()

    def check_collision_with_food(self):
        if self.snake.body[0] == self.food.position:
            self.food.position = self.food.generate_random_pos(
                self.snake.body, self.obstacles)
            self.snake.add_segment = True
            self.score += 1
            self.snake.eat_sound.play()

    def check_collision_with_edges(self):
        if self.snake.body[0].x == NUMBER_OF_CELLS or self.snake.body[0].x == -1:
            self.game_over()
        if self.snake.body[0].y == NUMBER_OF_CELLS or self.snake.body[0].y == -1:
            self.game_over()

    def check_collision_with_obstacles(self):
        if self.difficulty == "HARD" and self.snake.body[0] in self.obstacles:
            self.game_over()

    def game_over(self):
        self.snake.reset(self.obstacles)
        self.food.position = self.food.generate_random_pos(
            self.snake.body, self.obstacles)
        self.state = GameState.STOPPED
        self.snake.death_sound.play()

        if self.score > self.best_score:
            self.best_score = self.score
            self.snake.fireworks_sound.play()
            self.save_best_score()

        self.score = 0

        best_score_surface = end_game_font.render(
            f"Best Score for {self.difficulty}: {self.best_score}", True, COLORS['WHITE'])
        restart_surface = end_game_font.render(
            "Press SPACE to Restart", True, COLORS['WHITE'])
        leave_surface = end_game_font.render(
            "Press ESC to Leave", True, COLORS['WHITE'])

        best_score_pos = (screen.get_width() // 2 - best_score_surface.get_width() // 2,
                          screen.get_height() // 2 - best_score_surface.get_height())
        restart_pos = (screen.get_width() // 2 - restart_surface.get_width() // 2,
                       screen.get_height() // 2)
        leave_pos = (screen.get_width() // 2 - leave_surface.get_width() // 2,
                     screen.get_height() // 2 + restart_surface.get_height())

        screen.blit(best_score_surface, best_score_pos)
        screen.blit(restart_surface, restart_pos)
        screen.blit(leave_surface, leave_pos)
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def reset_game(self):
        self.snake.reset(self.obstacles)
        self.food.position = self.food.generate_random_pos(
            self.snake.body, self.obstacles)
        self.generate_obstacles()
        self.state = GameState.RUNNING
        self.score = 0

    def check_collision_with_tail(self):
        headless_body = self.snake.body[1:]
        if self.snake.body[0] in headless_body:
            self.game_over()


def handle_key_event(event, game):
    if game.state == GameState.STOPPED:
        if event.key == pygame.K_SPACE:
            game.state = GameState.RUNNING
    elif game.state == GameState.RUNNING:
        if event.key == pygame.K_SPACE:
            game.state = GameState.STOPPED
    elif game.state == GameState.WON:
        if event.key == pygame.K_SPACE:
            game.reset_game()
    elif game.state == GameState.DIFFICULTY_SELECT:
        game.update_difficulty_select(event)

    if event.key == pygame.K_UP and game.snake.direction != Direction.DOWN:
        game.snake.direction = Direction.UP
    elif event.key == pygame.K_DOWN and game.snake.direction != Direction.UP:
        game.snake.direction = Direction.DOWN
    elif event.key == pygame.K_LEFT and game.snake.direction != Direction.RIGHT:
        game.snake.direction = Direction.LEFT
    elif event.key == pygame.K_RIGHT and game.snake.direction != Direction.LEFT:
        game.snake.direction = Direction.RIGHT

    if event.key == pygame.K_e:
        game.difficulty = "EASY"
        game.state = GameState.RUNNING
    elif event.key == pygame.K_h:
        game.difficulty = "HARD"
        game.state = GameState.RUNNING

    if event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()


def draw_game_over_messages(game):
    if game.state == GameState.WON:
        lines = [
            "CLICK SPACE TO PLAY AGAIN",
            "OR",
            "ESC TO EXIT"
        ]
        for i, line in enumerate(lines):
            text_surface = end_game_font.render(line, True, COLORS['GREEN'])
            text_pos = (
                screen.get_width() // 2 - text_surface.get_width() // 2,
                screen.get_height() // 2 - text_surface.get_height() // 2 + i * 30
            )
            screen.blit(text_surface, text_pos)
    else:
        text_surface = font.render("PAUSED", True, COLORS['WHITE'])
        text_pos = (
            screen.get_width() // 2 - text_surface.get_width() // 2,
            screen.get_height() // 2 - text_surface.get_height() // 2
        )
        screen.blit(text_surface, text_pos)


screen = pygame.display.set_mode(
    (2 * OFFSET + CELL_SIZE * NUMBER_OF_CELLS, 2 * OFFSET + CELL_SIZE * NUMBER_OF_CELLS))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

game = Game()
pygame.time.set_timer(pygame.USEREVENT, SNAKE_INITIAL_INTERVAL)

while True:
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT and game.state == GameState.RUNNING:
            game.update()
            game.check_collision_with_obstacles()
        elif event.type == pygame.USEREVENT and game.state == GameState.DIFFICULTY_SELECT:
            game.update_difficulty_select(event)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            handle_key_event(event, game)

    screen.fill(COLORS['BLUE'])

    if game.state == GameState.DIFFICULTY_SELECT:
        game.draw_difficulty_select()
    else:
        pygame.draw.rect(screen, COLORS['WHITE'], (OFFSET - 5, OFFSET - 5,
                         CELL_SIZE * NUMBER_OF_CELLS + 10, CELL_SIZE * NUMBER_OF_CELLS + 10), 5)
        game.draw_obstacles()
        game.draw()

    title_surface = font.render("Snake", True, COLORS['WHITE'])
    score_surface = font.render(str(game.score), True, COLORS['WHITE'])
    screen.blit(score_surface, (OFFSET + CELL_SIZE * NUMBER_OF_CELLS, 20))

    if game.state in [GameState.STOPPED, GameState.WON]:
        draw_game_over_messages(game)

    pygame.display.update()
    clock.tick(60)

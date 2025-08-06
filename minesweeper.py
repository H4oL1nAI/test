import pygame
import random
import sys
from pygame.locals import *

# 确保中文显示正常
pygame.init()
pygame.font.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 16
GRID_HEIGHT = 16
MINES_COUNT = 40

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 初始化屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("扫雷游戏")

# 加载字体
try:
    font = pygame.font.Font("simhei.ttf", 24)
    small_font = pygame.font.Font("simhei.ttf", 18)
except:
    # 如果找不到中文字体，使用默认字体
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)

class MineSweeper:
    def __init__(self):
        self.reset_game()
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = 0
        self.elapsed_time = 0

    def reset_game(self):
        # 初始化游戏板
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.revealed = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.flagged = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.mines = set()
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = 0
        self.elapsed_time = 0

    def place_mines(self, first_x, first_y):
        # 确保第一次点击的位置不是地雷
        forbidden_area = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    forbidden_area.add((nx, ny))

        # 随机放置地雷
        while len(self.mines) < MINES_COUNT:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in forbidden_area and (x, y) not in self.mines:
                self.mines.add((x, y))
                self.grid[y][x] = -1  # -1 表示地雷

        # 计算每个格子周围的地雷数
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if (x, y) not in self.mines:
                    count = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and (nx, ny) in self.mines:
                                count += 1
                    self.grid[y][x] = count

    def reveal_cell(self, x, y):
        if self.revealed[y][x] or self.flagged[y][x] or self.game_over:
            return

        self.revealed[y][x] = True

        # 如果是地雷，游戏结束
        if (x, y) in self.mines:
            self.game_over = True
            return

        # 如果是空格子（周围没有地雷），递归揭示周围的格子
        if self.grid[y][x] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        self.reveal_cell(nx, ny)

        # 检查是否获胜
        self.check_win()

    def toggle_flag(self, x, y):
        if self.revealed[y][x] or self.game_over:
            return
        self.flagged[y][x] = not self.flagged[y][x]
        self.check_win()

    def check_win(self):
        # 检查是否所有非地雷格子都被揭示
        revealed_count = 0
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.revealed[y][x] and (x, y) not in self.mines:
                    revealed_count += 1
        if revealed_count == GRID_WIDTH * GRID_HEIGHT - MINES_COUNT:
            self.game_over = True
            self.game_won = True

    def draw_grid(self):
        # 计算网格偏移量，使网格居中
        grid_offset_x = (SCREEN_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
        grid_offset_y = (SCREEN_HEIGHT - GRID_HEIGHT * GRID_SIZE) // 2

        # 绘制网格
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    grid_offset_x + x * GRID_SIZE,
                    grid_offset_y + y * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE
                )

                if self.revealed[y][x]:
                    pygame.draw.rect(screen, LIGHT_GRAY, rect)
                    pygame.draw.rect(screen, GRAY, rect, 1)

                    if (x, y) in self.mines:
                        # 绘制地雷
                        pygame.draw.circle(screen, BLACK, rect.center, GRID_SIZE // 4)
                    elif self.grid[y][x] > 0:
                        # 绘制数字
                        color_map = [
                            None, BLUE, GREEN, RED, (128, 0, 128), (139, 0, 0), (64, 224, 208), BLACK, GRAY
                        ]
                        text = small_font.render(str(self.grid[y][x]), True, color_map[self.grid[y][x]])
                        text_rect = text.get_rect(center=rect.center)
                        screen.blit(text, text_rect)
                else:
                    if self.flagged[y][x]:
                        pygame.draw.rect(screen, YELLOW, rect)
                        pygame.draw.rect(screen, GRAY, rect, 1)
                        # 绘制旗帜
                        pygame.draw.polygon(
                            screen, RED,
                            [
                                (rect.left + GRID_SIZE // 4, rect.top + GRID_SIZE // 4),
                                (rect.right - GRID_SIZE // 4, rect.top + GRID_SIZE // 2),
                                (rect.left + GRID_SIZE // 4, rect.bottom - GRID_SIZE // 4)
                            ]
                        )
                        pygame.draw.line(screen, BLACK, (rect.left + GRID_SIZE // 4, rect.top + GRID_SIZE // 4),
                                        (rect.left + GRID_SIZE // 4, rect.bottom - GRID_SIZE // 4), 2)
                    else:
                        pygame.draw.rect(screen, GRAY, rect)
                        pygame.draw.rect(screen, DARK_GRAY, rect, 1)

        # 游戏结束后显示所有地雷
        if self.game_over and not self.game_won:
            for (x, y) in self.mines:
                if not self.flagged[y][x]:
                    rect = pygame.Rect(
                        grid_offset_x + x * GRID_SIZE,
                        grid_offset_y + y * GRID_SIZE,
                        GRID_SIZE,
                        GRID_SIZE
                    )
                    pygame.draw.rect(screen, RED, rect)
                    pygame.draw.rect(screen, GRAY, rect, 1)
                    pygame.draw.line(screen, BLACK, rect.topleft, rect.bottomright, 2)
                    pygame.draw.line(screen, BLACK, rect.topright, rect.bottomleft, 2)

        return grid_offset_x, grid_offset_y

    def draw_ui(self):
        # 绘制标题
        title = font.render("扫雷游戏", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        # 绘制剩余地雷数
        flags_left = MINES_COUNT - sum(row.count(True) for row in self.flagged)
        mines_text = font.render(f"剩余地雷: {flags_left}", True, BLACK)
        screen.blit(mines_text, (50, 20))

        # 绘制计时器
        if not self.game_over and not self.first_click:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = font.render(f"时间: {self.elapsed_time}", True, BLACK)
        screen.blit(time_text, (SCREEN_WIDTH - 150, 20))

        # 游戏结束消息
        if self.game_over:
            if self.game_won:
                msg = font.render("恭喜你，获胜了！", True, GREEN)
            else:
                msg = font.render("游戏结束，触雷了！", True, RED)
            msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(msg, msg_rect)

            # 重新开始按钮
            restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50)
            pygame.draw.rect(screen, BLUE, restart_button)
            pygame.draw.rect(screen, WHITE, restart_button, 2)
            restart_text = font.render("重新开始", True, WHITE)
            restart_text_rect = restart_text.get_rect(center=restart_button.center)
            screen.blit(restart_text, restart_text_rect)
            return restart_button

        return None

    def handle_events(self, grid_offset_x, grid_offset_y):
        restart_button = None
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                # 检查是否点击了重新开始按钮
                if self.game_over:
                    restart_button = self.draw_ui()
                    if restart_button and restart_button.collidepoint(x, y):
                        self.reset_game()
                        return
                else:
                    # 检查是否点击了网格
                    grid_x = (x - grid_offset_x) // GRID_SIZE
                    grid_y = (y - grid_offset_y) // GRID_SIZE
                    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                        if self.first_click:
                            # 第一次点击，放置地雷并开始计时
                            self.place_mines(grid_x, grid_y)
                            self.first_click = False
                            self.start_time = pygame.time.get_ticks()
                        if event.button == 1:  # 左键点击
                            self.reveal_cell(grid_x, grid_y)
                        elif event.button == 3:  # 右键点击
                            self.toggle_flag(grid_x, grid_y)

    def run(self):
        while True:
            screen.fill(WHITE)
            grid_offset_x, grid_offset_y = self.draw_grid()
            self.draw_ui()
            self.handle_events(grid_offset_x, grid_offset_y)
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = MineSweeper()
    game.run()
import random
import pygame
import os
import sys
from math import sin, cos, pi, log
from tkinter import *

# --- 基础配置 ---
CANVAS_WIDTH = 840
CANVAS_HEIGHT = 680
CANVAS_CENTER_X = CANVAS_WIDTH / 2
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2
IMAGE_ENLARGE = 11
HEART_COLOR = "pink"  # 统一粉色

# --- 告白设置 ---
INTRO_TEXT = "遇见你是我最美的意外\n\n(请按下回车键)"
LOVE_WORD = "我喜欢你"

# 渐变色池
PINK_FADE = [
    "#1a0d10", "#331a20", "#4d2630", "#663340", "#804050",
    "#994d60", "#b35970", "#cc6680", "#e67390", "#ff80a0", "#ffc0cb"
]


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    elif getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    target_path = os.path.join(base_path, relative_path)

    if not os.path.exists(target_path):
        try:
            files = os.listdir(base_path)
            for f in files:
                if f.lower() == relative_path.lower():
                    target_path = os.path.join(base_path, f)
                    break
        except:
            pass

    return target_path


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    x *= shrink_ratio
    y *= shrink_ratio
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y
    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())
    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    return 2 * (2 * sin(4 * p)) / (2 * pi)


class Heart:
    def __init__(self, generate_frame=20):
        self.points = set()
        self.edge_diffusion_points = set()
        self.center_diffusion_points = set()
        self.all_points = {}
        self.build(2000)
        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self.points.add((x, y))
        for _x, _y in list(self.points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self.edge_diffusion_points.add((x, y))
        point_list = list(self.points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self.center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.420)
        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)
        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))
        all_points = []
        heart_halo_point = set()
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio=11.6)
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                all_points.append((x, y, random.choice((1, 2, 2))))
        for x, y in self.points:
            x, y = self.calc_position(x, y, ratio)
            all_points.append((x, y, random.randint(1, 3)))
        for x, y in self.edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            all_points.append((x, y, random.randint(1, 2)))
        for x, y in self.center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            all_points.append((x, y, random.randint(1, 2)))
        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


class ConfessionApp:
    def __init__(self, root):
        self.root = root

        # 1. 初始化并加载音乐
        pygame.mixer.init()
        try:
            # 确保你的音乐文件名是 love.mp3
            pygame.mixer.music.load(resource_path("love.mp3"))
        except Exception as e:
            print(f"未能加载音乐文件: {e}")

        self.canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH, highlightthickness=0)
        self.canvas.pack()

        self.heart = Heart()
        self.state = "INTRO"
        self.frame = 0
        self.love_messages = []

        self.root.bind("<Return>", self.on_enter)
        self.show_intro()

    def show_intro(self):
        self.canvas.delete('all')
        self.canvas.create_text(
            CANVAS_CENTER_X, CANVAS_CENTER_Y,
            text=INTRO_TEXT,
            fill="white",
            font=("Microsoft YaHei", 20, "bold"),
            justify=CENTER
        )

    def on_enter(self, event):
        if self.state == "INTRO":
            # 尝试播放音乐，即使失败也不要让程序崩溃
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            except pygame.error:
                print("提示：音乐未加载成功，程序将静音运行")

            self.state = "HEART_ONLY"
            self.animate()
            self.root.after(1000, self.start_confession)

    def start_confession(self):
        self.state = "LOVE_FLOW"

    def animate(self):
        self.canvas.delete('all')
        self.heart.render(self.canvas, self.frame)

        if self.state == "LOVE_FLOW":
            # 每一帧生成 2 个，上限 350 个
            if len(self.love_messages) < 350:
                for _ in range(2):
                    mx = random.randint(50, CANVAS_WIDTH - 50)
                    my = random.randint(50, CANVAS_HEIGHT - 50)
                    m_size = random.randint(10, 20)
                    self.love_messages.append({'x': mx, 'y': my, 'color_idx': 0, 'size': m_size})

            for msg in self.love_messages:
                current_color = PINK_FADE[msg['color_idx']]
                self.canvas.create_text(
                    msg['x'], msg['y'],
                    text=LOVE_WORD,
                    fill=current_color,
                    font=("Microsoft YaHei", msg['size'], "bold")
                )
                if msg['color_idx'] < len(PINK_FADE) - 1:
                    msg['color_idx'] += 1

        self.frame += 1
        self.root.after(40, self.animate)


if __name__ == '__main__':
    root = Tk()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f'{CANVAS_WIDTH}x{CANVAS_HEIGHT}+{int((sw - CANVAS_WIDTH) / 2)}+{int((sh - CANVAS_HEIGHT) / 2)}')
    root.resizable(False, False)
    root.title("致我最在意的人")

    app = ConfessionApp(root)
    root.mainloop()

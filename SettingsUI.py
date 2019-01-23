from GraphicsManager import GraphicsManager


class SettingsUI(GraphicsManager):
    def __init__(self, width, height):
        super().__init__(width, height)

    def __draw_level_select_board(self):
        self.draw_rect(100, 50, self.WIDTH // 2 + 240, self.HEIGHT // 2 - 145, self.GREY)
        self.draw_text(self.FONT, 30, "Level", self.WHITE, self.WIDTH // 2 + 255, self.HEIGHT // 2 - 145)

    def __draw_level_label(self, dx, dy, label, color):
        self.draw_rect(50, 50, self.WIDTH // 2 + 240 + dx, self.HEIGHT // 2 - 140 + dy, self.GREY)
        self.draw_text(self.FONT, 30, label, color, self.WIDTH // 2 + 255 + dx, self.HEIGHT // 2 - 140 + dy)

    def __draw_track_button(self, dx, dy, label):
        self.draw_rect(150, 50, self.WIDTH // 2 - 275 + dx, self.HEIGHT // 2 - 148 + dy, self.GREY)
        self.draw_text(self.FONT, 30, label, self.WHITE, self.WIDTH // 2 - 255 + dx, self.HEIGHT // 2 - 145 + dy)

    def __draw_start_button(self):
        self.draw_rect(180, 80, self.WIDTH // 2 - 90, self.HEIGHT // 2 + 300, self.GREY)
        self.draw_text(self.FONT, 30, "Start", self.WHITE, self.WIDTH // 2 - 41, self.HEIGHT // 2 + 317)

    def __draw_logo(self):
        c = [(1, 4), (1, 5), (1, 6), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (7, 5), (7, 6)]
        h = [(1, 8), (1, 10), (2, 8), (2, 10), (3, 8), (3, 10), (4, 8), (4, 9), (4, 10), (5, 8), (5, 10), (6, 8),
             (6, 10), (7, 8), (7, 10)]
        o = [(1, 12), (1, 13), (1, 14), (1, 15), (2, 12), (2, 15), (3, 12), (3, 15), (4, 12), (4, 15), (5, 12), (5, 15),
             (6, 12), (6, 15), (7, 12), (7, 13), (7, 14), (7, 15)]
        o2 = [(1, 17), (1, 18), (1, 19), (1, 20), (2, 17), (2, 20), (3, 17), (3, 20), (4, 17), (4, 20), (5, 17),
              (5, 20), (6, 17), (6, 20), (7, 17), (7, 18), (7, 19), (7, 20)]
        s = [(1, 22), (1, 23), (1, 24), (2, 22), (2, 24), (3, 22), (4, 22), (4, 23), (4, 24), (5, 24), (6, 22), (6, 24),
             (7, 22), (7, 23), (7, 24)]
        e = [(1, 26), (1, 27), (1, 28), (2, 26), (3, 26), (4, 26), (4, 27), (4, 28), (5, 26), (6, 26), (7, 26),
             (7, 27), (7, 28)]

        logo = [(c, self.RED), (h, self.ORANGE), (o, self.YELLOW), (o2, self.GREEN), (s, self.CYAN), (e, self.PURPLE)]
        for letter in logo:
            for l in letter[0]:
                self.draw_rect(35, 35, 2 * (l[1] + 1) + 35 * l[1], 2 * (l[0] + 1) + 35 * l[0], letter[1])

    def draw_settings(self, level):
        self.screen.fill(self.BLACK)
        self.__draw_logo()
        self.__draw_level_select_board()
        for i in range(5):
            for j in range(2):
                dx = 0
                dy = 50*(i+1)
                if j == 1:
                    dx = 50
                if level == 2*i+j+1:
                    self.__draw_level_label(dx, dy, str(2*i+j), self.BLACK)
                    continue
                self.__draw_level_label(dx, dy, str(2 * i + j), self.WHITE)
        for i in range(3):
            self.__draw_track_button(0, (i+1)*70, "Track " + str(i+1))
        self.__draw_start_button()

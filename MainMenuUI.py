from GraphicsManager import GraphicsManager


class MainMenuUI(GraphicsManager):
    def __init__(self, width, height):
        super().__init__(width, height)

    def __draw_play_button(self):
        self.draw_rect(180, 80, self.WIDTH // 2 - 90, self.HEIGHT // 2 - 115, self.GREY)
        self.draw_text(self.FONT, 30, "Play", self.WHITE, self.WIDTH // 2 - 30, self.HEIGHT // 2 - 100)

    def __draw_quit_button(self):
        self.draw_rect(180, 80, self.WIDTH // 2 - 90, self.HEIGHT // 2 + 35, self.GREY)
        self.draw_text(self.FONT, 30, "Quit", self.WHITE, self.WIDTH // 2 - 30, self.HEIGHT // 2 + 50)

    def __draw_logo(self):
        t = [(1, 4), (1, 5), (1, 6), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5)]
        e = [(1, 8), (1, 9), (1, 10), (2, 8), (3, 8), (4, 8), (4, 9), (4, 10), (5, 8), (6, 8), (7, 8), (7, 9), (7, 10)]
        t2 = [(1, 12), (1, 13), (1, 14), (2, 13), (3, 13), (4, 13), (5, 13), (6, 13), (7, 13)]
        r = [(1, 16), (1, 17), (1, 18), (1, 19), (1, 20), (2, 16), (2, 20), (3, 16), (3, 19), (4, 16), (4, 17), (4, 18),
             (5, 16), (5, 19), (6, 16), (6, 20), (7, 16), (7, 21)]
        i = [(1, 23), (2, 23), (3, 23), (4, 23), (5, 23), (6, 23), (7, 23)]
        s = [(1, 25), (1, 26), (1, 27), (2, 25), (2, 27), (3, 25), (4, 25), (4, 26), (4, 27), (5, 27), (6, 25), (6, 27),
             (7, 25), (7, 26), (7, 27)]
        logo = [(t, self.RED), (e, self.ORANGE), (t2, self.YELLOW), (r, self.GREEN), (i, self.CYAN), (s, self.PURPLE)]
        for letter in logo:
            for l in letter[0]:
                self.draw_rect(35, 35, 2 * (l[1] + 1) + 35 * l[1], 2 * (l[0] + 1) + 35 * l[0], letter[1])

    def draw_main_menu(self):
        self.screen.fill(self.BLACK)
        self.__draw_play_button()
        self.__draw_quit_button()
        self.__draw_logo()

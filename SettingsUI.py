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

    def draw_settings(self, level):
        self.screen.fill(self.BLACK)
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

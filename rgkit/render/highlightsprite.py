from rgkit.render.robotsprite import compute_color
from rgkit.render.utils import rgb_to_hex, blend_colors


class HighlightSprite(object):
    def __init__(self, loc, target, render):
        self.location = loc
        self.target = target
        self.renderer = render
        self.settings = self.renderer._settings
        self.hlt_square = None
        self.target_square = None

    def get_bot_color(self, loc):
        display_turn = self.renderer.current_turn_int()
        display_state = self.renderer._game.get_state(display_turn)
        if display_state.is_robot(loc):
            robot = display_state.robots[loc]
            return compute_color(self.settings,
                                 robot.player_id, robot.hp)

    def get_mixed_color(self, color, loc):
        bot_color = self.get_bot_color(loc)
        if bot_color is not None:
            color = blend_colors(color, bot_color, 0.7)
        return rgb_to_hex(*color)

    def clear(self):
        self.renderer.remove_object(self.hlt_square)
        self.renderer.remove_object(self.target_square)
        self.hlt_square = None
        self.target_square = None

    def animate(self, delta=0):
        if self.settings.highlight_cursor_blink:
            if not delta < self.settings.highlight_cursor_blink_interval:
                self.clear()
                return

        if self.location is not None:
            if self.hlt_square is None:
                color = self.settings.highlight_color
                color = self.get_mixed_color(color, self.location)
                self.hlt_square = self.renderer.draw_grid_object(
                    self.location, fill=color, layer=3, width=0)
            if self.target is not None and self.target_square is None:
                color = self.settings.target_color
                color = self.get_mixed_color(color, self.target)
                self.target_square = self.renderer.draw_grid_object(
                    self.target, fill=color, layer=3, width=0)

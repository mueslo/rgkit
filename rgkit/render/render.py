import Tkinter
import math

from rgkit.render.robotsprite import RobotSprite
from rgkit.render.highlightsprite import HighlightSprite
from rgkit.render.utils import millis, rgb_to_hex


class Render(object):
    def __init__(self, game_inst, settings, animations, names=["Red", "Blue"]):
        self.size_changed = False
        self.init = True

        self.cell_border_width = 2
        self.info_frame_height = 80
        self.board_margin = 0

        self._settings = settings
        self._animations = animations
        self._blocksize = 25
        self._winsize = (self._blocksize * self._settings.board_size
                         + self.board_margin)
        self._game = game_inst
        self._paused = True
        self._names = names
        self._layers = {}

        self._master = Tkinter.Tk()
        self._master.configure(background="#333")
        self._master.title('Robot Game')

        width = self._winsize
        height = self._winsize

        self._board_frame = Tkinter.Frame(self._master, background="#555")
        self._info_frame = Tkinter.Frame(self._master, background="#333")
        self._control_frame = Tkinter.Frame(self._info_frame)

        self._board_frame.pack(
            side=Tkinter.TOP, fill=Tkinter.BOTH, expand=True)

        # Tkinter problem: 'pack' distributes space according to which widgets
        # have expand set to true, not to which directions they can actually
        # expand to.
        self._info_frame.pack(side=Tkinter.BOTTOM)

        self._control_frame.pack(side=Tkinter.RIGHT)

        # Tkinter problem: highlightthickness supposedly defaults to 0, but
        # doesn't.
        self._win = Tkinter.Canvas(
            self._board_frame, width=width, height=height,
            background="#555", highlightthickness=0)
        self._info = Tkinter.Canvas(
            self._info_frame, width=300, height=self.info_frame_height,
            background="#333", highlightthickness=0)

        self._win.pack()
        self._info.pack(side=Tkinter.LEFT)

        self._master.bind('<Configure>', self.on_resize)

        self._labelred = self._info.create_text(
            self._blocksize / 2, self._blocksize * 1 / 4,
            anchor='nw', font='TkFixedFont', fill='#ff1a1a')
        self._labelblue = self._info.create_text(
            self._blocksize / 2, self._blocksize * 7 / 8,
            anchor='nw', font='TkFixedFont', fill='#3455ff')
        self._label = self._info.create_text(
            self._blocksize / 2, self._blocksize * 3 / 2,
            anchor='nw', font='TkFixedFont', fill='white')
        self.create_controls(self._info, width, height)

        self._turn = 1.0
        self._sub_turn = 0.0

        self._highlighted = None
        self._highlighted_target = None

        # Animation stuff (also see #render heading in settings.py)
        self._sprites = []
        self._highlight_sprite = None
        self._t_frame_start = 0
        self._t_next_frame = 0
        self._t_cursor_start = 0
        self._slider_delay = 0
        self.update_frame_start_time()

        self.draw_background()
        self.update_info_frame()
        self.update_sprites_new_turn()
        self.paint()

        self.callback()

        self._master.mainloop()

    def on_resize(self, event):
        self.size_changed = True

    def remove_object(self, obj):
        if obj is not None:
            self._win.delete(obj)

    def turn_changed(self):
        if self._settings.clear_highlight_between_turns:
            self._highlighted = None
        if self._settings.clear_highlight_target_between_turns:
            self._highlighted_target = None
        self.update_sprites_new_turn()
        self.update_info_frame()

    def update_block_size(self):
        if self.size_changed:
            if self.init:
                self.init = False
                return

            self.size_changed = False
            self._win.delete("all")

            self._winsize = min(self._board_frame.winfo_width(),
                                self._board_frame.winfo_height())
            self._winsize = max(min(self._winsize,
                                    self._master.winfo_height() -
                                    self.info_frame_height),
                                250)

            self._blocksize = ((self._winsize - self.board_margin) /
                               self._settings.board_size)
            self._win.configure(width=self._winsize, height=self._winsize)

            self.draw_background()
            self.update_sprites_new_turn()
            self.paint()

    def step_turn(self, turns):
        self._turn = self.current_turn_int() + turns
        self._turn = min(max(self._turn, 1.0), self._settings.max_turns)
        self._sub_turn = 0.0
        self.update_frame_start_time()
        self.turn_changed()
        self.update_info_frame()
        self.paint()

    def toggle_pause(self):
        self._paused = not self._paused
        # Print "paused" if self._paused else "unpaused".
        self._toggle_button.config(
            text=u'\u25B6' if self._paused else u'\u25FC')
        now = millis()
        if self._paused:
            self._sub_turn = 0.0
        else:
            self.update_frame_start_time(now)

    def update_frame_start_time(self, tstart=None):
        tstart = tstart or millis()
        self._t_frame_start = tstart

        self._t_next_frame = tstart + self._slider_delay

    def create_controls(self, win, width, height):
        def step_turn(turns):
            if not self._paused:
                self.toggle_pause()
            self.step_turn(turns)

        def prev():
            step_turn(-1)

        def next():
            step_turn(+1)

        def restart():
            step_turn((-self._turn) + 1)

        def pause():
            self.toggle_pause()
            self.update_info_frame()

        def onclick(event):
            x = (event.x - self.board_margin / 2) / self._blocksize
            y = (event.y - self.board_margin / 2) / self._blocksize
            loc = (x, y)
            if (0 <= x < self._settings.board_size and
                    0 <= y < self._settings.board_size):
                if loc == self._highlighted:
                    self._highlighted = None
                else:
                    self._highlighted = loc
                action = self._game.get_actions_on_turn(
                    self.current_turn_int()).get(loc)
                if action is not None:
                    self._highlighted_target = action.get("target", None)
                else:
                    self._highlighted_target = None
                self.update_highlight_sprite(True)
                self.update_info_frame()
                self._t_cursor_start = millis()

        self._win.bind("<Button-1>", lambda e: onclick(e))
        self._master.bind('<Left>', lambda e: prev())
        self._master.bind('<Right>', lambda e: next())
        self._master.bind('<space>', lambda e: pause())

        self.show_arrows = Tkinter.BooleanVar()

        frame = self._control_frame

        arrows_box = Tkinter.Checkbutton(
            frame, text="Show Arrows", variable=self.show_arrows,
            command=self.paint)
        arrows_box.pack()

        self._toggle_button = Tkinter.Button(
            frame, text=u'\u25B6', command=pause)
        self._toggle_button.pack(side='left')

        prev_button = Tkinter.Button(frame, text='<', command=prev)
        prev_button.pack(side='left')

        next_button = Tkinter.Button(frame, text='>', command=next)
        next_button.pack(side='left')

        restart_button = Tkinter.Button(frame, text='<<', command=restart)
        restart_button.pack(side='left')

        self._time_slider = Tkinter.Scale(
            frame,
            from_=-self._settings.turn_interval / 2,
            to_=self._settings.turn_interval / 2,
            orient=Tkinter.HORIZONTAL,
            borderwidth=0,
            length=90)
        self._time_slider.pack(fill=Tkinter.X)
        self._time_slider.set(0)

    def draw_grid_object(self, loc, type="square", layer=0, **kargs):
        layer_id = 'layer %d' % layer
        self._layers[layer_id] = None
        tags = kargs.get("tags", [])
        tags.append(layer_id)
        kargs["tags"] = tags
        x, y = self.grid_to_xy(loc)
        rx, ry = self.square_bottom_corner((x, y))
        if type == "square" or self._settings.bot_shape == "square":
            item = self._win.create_rectangle(
                x, y, rx, ry,
                **kargs)
        elif type == "circle":
            item = self._win.create_oval(
                x, y, rx, ry,
                **kargs)
        return item

    def update_layers(self):
        for layer in self._layers:
            self._win.tag_raise(layer)

    def draw_text(self, loc, text, color=None):
        layer_id = 'layer %d' % 9
        self._layers[layer_id] = None
        x, y = self.grid_to_xy(loc)
        item = self._win.create_text(
            x + (self._blocksize - self.cell_border_width) / 2,
            y + (self._blocksize - self.cell_border_width) / 2,
            text=text, font='TkFixedFont', fill=color, tags=[layer_id])
        return item

    def draw_line(self, src, dst, offset=(0, 0), layer=0, **kargs):
        layer_id = 'layer %d' % layer
        self._layers[layer_id] = None
        tags = kargs.get("tags", [])
        tags.append(layer_id)
        kargs["tags"] = tags
        ox, oy = offset
        srcx, srcy = self.grid_to_xy(src)
        dstx, dsty = self.grid_to_xy(dst)

        item = self._win.create_line(
            srcx + ox, srcy + oy, dstx + ox, dsty + oy, **kargs)
        return item

    def update_info_frame(self):
        display_turn = self.current_turn_int()
        display_state = self._game.get_state(display_turn)
        max_turns = self._settings.max_turns
        red, blue = display_state.get_scores()
        info = ''
        currentAction = ''
        if self._highlighted is not None:
            if self._highlighted in self._settings.obstacles:
                info = 'Obstacle'
            elif display_state.is_robot(self._highlighted):
                robot = display_state.robots[self._highlighted]
                info = 'Bot %d ' % (robot.robot_id,)

        r_text = '%s: %d' % (self._names[0], red)
        g_text = '%s: %d' % (self._names[1], blue)
        white_text = [
            'Turn: %d/%d' % (display_turn, max_turns),
            'Highlighted: %s; %s' % (self._highlighted, info),
            currentAction
        ]
        self._info.itemconfig(self._label, text='\n'.join(white_text))
        self._info.itemconfig(self._labelred, text=r_text)
        self._info.itemconfig(self._labelblue, text=g_text)

    def current_turn_int(self):
        return min(int(math.floor(self._turn + self._sub_turn)),
                   self._settings.max_turns)

    def update_slider_value(self):
        v = -self._time_slider.get()
        if v > 0:
            v = v * 20
        self._slider_delay = self._settings.turn_interval + v

    def callback(self):
        self.update_slider_value()
        self.tick()
        self._win.after(int(1000.0 / self._settings.FPS), self.callback)

    def tick(self):
        now = millis()

        # check if frame-update
        if self._animations:
            if not self._paused:
                self._sub_turn = max(0.0,
                                     float((now - self._t_frame_start)) /
                                     float(self._slider_delay))
                if self._turn >= self._settings.max_turns:
                    self.toggle_pause()
                    self._turn = self._settings.max_turns
                self.update_info_frame()
                if self._sub_turn >= 1:
                    self._sub_turn -= 1
                    self._turn += 1
                    self.update_frame_start_time(self._t_next_frame)
                    self.turn_changed()
            subframe_t = ((now - self._t_cursor_start) %
                          self._settings.rate_cursor_blink)
            subframe_hlt = float(subframe_t) / self._settings.rate_cursor_blink
            self.paint(self._sub_turn, subframe_hlt)
        elif now > self._t_next_frame and not self._paused:
            self._turn += 1
            self.update_frame_start_time(self._t_next_frame)
            self.turn_changed()
            self.paint(0, 0)

        self.update_block_size()

    def get_bg_color(self, loc):
        if loc in self._settings.obstacles:
            return rgb_to_hex(*self._settings.obstacle_color)
        return rgb_to_hex(*self._settings.normal_color)

    def draw_background(self):
        # draw squares
        for y in range(self._settings.board_size):
            for x in range(self._settings.board_size):
                loc = (x, y)
                self.draw_grid_object(
                    loc, fill=self.get_bg_color(loc), layer=1, width=0)
        # draw text labels
        text_color = rgb_to_hex(*self._settings.text_color)
        for y in range(self._settings.board_size):
            self.draw_text((y, 0), str(y), color=text_color)
            self.draw_text((0, y), str(y), color=text_color)

    def update_sprites_new_turn(self):
        for sprite in self._sprites:
            sprite.clear()
        self._sprites = []

        self.update_highlight_sprite()
        turn_action = self.current_turn_int()
        bots_activity = self._game.get_actions_on_turn(turn_action)
        for bot_data in bots_activity.values():
            self._sprites.append(RobotSprite(bot_data, self))

    def update_highlight_sprite(self, repaint=False):
        if self._highlight_sprite is not None:
            self._highlight_sprite.clear()
        self._highlight_sprite = HighlightSprite(
            self._highlighted, self._highlighted_target, self)
        if repaint:
            self.paint_highlight_sprite()

    def paint_highlight_sprite(self, subframe_hlt=0):
        if self._highlight_sprite is not None:
            self._highlight_sprite.animate(subframe_hlt)
            self.update_layers()

    def paint(self, subframe=0, subframe_hlt=0):
        for sprite in self._sprites:
            sprite.animate(subframe)
        self.update_highlight_sprite()
        self.paint_highlight_sprite(subframe_hlt)
        self.update_layers()

    def grid_to_xy(self, loc):
        x, y = loc
        return (x * self._blocksize + self.board_margin / 2,
                y * self._blocksize + self.board_margin / 2)

    def square_bottom_corner(self, square_topleft):
        x, y = square_topleft
        return (x + self._blocksize - self.cell_border_width,
                y + self._blocksize - self.cell_border_width)

    def grid_bbox(self, loc):
        x, y = self.grid_to_xy(loc)
        return (int(x),
                int(y),
                int(x + self._blocksize - self.cell_border_width),
                int(y + self._blocksize - self.cell_border_width))

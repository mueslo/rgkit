#!/usr/bin/env python2


def is_valid_coord(coord, coord_range):
	return (coord[0] < coord_range[0] and 0 <= coord[0] and
			coord[1] < coord_range[1] and 0 <= coord[1])


def check_map_consistency(m):
	for cell in m.config.spawn:
		assert is_valid_coord(cell, m.config.board_size)
		assert cell not in m.config.obstacle

	for cell in m.config.obstacle:
		assert is_valid_coord(cell, m.config.board_size)

	assert len(m.config.spawn) >= (m.config.num_players *
		m.config.bots_per_spawn_and_player)

	assert max(m.config.spawn_turns) < m.config.turns

	assert min(m.config.spawn_turns) == 0


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Map(object):
	#TODO: time-dependent attributes for maps (e.g. spawn and obstacle)
	# for that have the ability to take both lists and functions as these
	# attributes

	config = AttrDict({
	"num_players": 2,
	"spawn": [(7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (5, 2), (6, 2),
	          (12, 2), (13, 2), (3, 3), (4, 3), (14, 3), (15, 3), (3, 4),
	          (15, 4), (2, 5), (16, 5), (2, 6), (16, 6), (1, 7), (17, 7),
	          (1, 8), (17, 8), (1, 9), (17, 9), (1, 10), (17, 10), (1, 11),
	          (17, 11), (2, 12), (16, 12), (2, 13), (16, 13), (3, 14),
	          (15, 14), (3, 15), (4, 15), (14, 15), (15, 15), (5, 16),
	          (6, 16), (12, 16), (13, 16), (7, 17), (8, 17), (9, 17),
	          (10, 17), (11, 17)],
	"obstacle": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),
				 (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0),
				 (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0),
				 (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
				 (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1),
				 (18, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (14, 2),
				 (15, 2), (16, 2), (17, 2), (18, 2), (0, 3), (1, 3),
				 (2, 3), (16, 3), (17, 3), (18, 3), (0, 4), (1, 4),
				 (2, 4), (16, 4), (17, 4), (18, 4), (0, 5), (1, 5),
				 (17, 5), (18, 5), (0, 6), (1, 6), (17, 6), (18, 6),
				 (0, 7), (18, 7), (0, 8), (18, 8), (0, 9), (18, 9),
				 (0, 10), (18, 10), (0, 11), (18, 11), (0, 12), (1, 12),
				 (17, 12), (18, 12), (0, 13), (1, 13), (17, 13), (18, 13),
				 (0, 14), (1, 14), (2, 14), (16, 14), (17, 14), (18, 14),
				 (0, 15), (1, 15), (2, 15), (16, 15), (17, 15), (18, 15),
				 (0, 16), (1, 16), (2, 16), (3, 16), (4, 16), (14, 16),
				 (15, 16), (16, 16), (17, 16), (18, 16), (0, 17), (1, 17),
				 (2, 17), (3, 17), (4, 17), (5, 17), (6, 17), (12, 17),
				 (13, 17), (14, 17), (15, 17), (16, 17), (17, 17),
				 (18, 17), (0, 18), (1, 18), (2, 18), (3, 18), (4, 18),
				 (5, 18), (6, 18), (7, 18), (8, 18), (9, 18), (10, 18),
				 (11, 18), (12, 18), (13, 18), (14, 18), (15, 18),
				 (16, 18), (17, 18), (18, 18)],
	"board_size": (19, 19),
	"turns": 100,
	"spawn_turns": [t for t in range(100) if t % 10 == 0],
	"bots_per_spawn_and_player": 5
	})

	def __init__(self, **config):
		self.config.update(config)
		check_map_consistency(self)
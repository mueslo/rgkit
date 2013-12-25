#!/usr/bin/env python2


import basemap


square_config = {"spawn": list(set(zip([0]*19+range(19)+[19-1]*19+range(19),
						               range(19)+[0]*19+range(19)+[19-1]*19))),
				 "obstacle": []}


available = {"default": basemap.Map(),
			 "square": basemap.Map(**square_config)}
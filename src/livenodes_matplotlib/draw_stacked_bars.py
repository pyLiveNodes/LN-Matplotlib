import numpy as np

from livenodes.viewer import View_MPL
from livenodes_core_nodes.ports import Ports_data, Ports_empty


class Draw_stacked_bars(View_MPL):
    """
    """

    ports_in = Ports_data()
    ports_out = Ports_empty()

    category = "Draw"
    description = ""

    example_init = {
        "name": "Draw stacked bars",
        "xlim": 100
    }

    def __init__(self,
                 xlim=100,
                 name="Draw stacked bars",
                 **kwargs):
        super().__init__(name=name, **kwargs)

        self.xlim = xlim

    def _settings(self):
        return {\
            "name": self.name,
            "xlim": self.xlim
           }

    def _init_draw(self, subfig):
        subfig.suptitle(self.name, fontsize=14)

        self.ax = subfig.subplots(1, 1)
        self.ax.set_ylim((.5, 1.5))
        self.ax.set_yticks([])
        self.ax.set_xlim(self.xlim)
        self.ax.invert_xaxis()

        # self.broken_bar = self.ax.barh(y=1, width=[self.xlim])

        # def calc_vert(xmin, xmax, ymax=1.5, ymin=0.5):
        #     xwidth = xmax-xmin
        #     return [(xmin, ymin), (xmin, ymax), (xmin + xwidth, ymax),
        #       (xmin + xwidth, ymin), (xmin, ymin)]

        def update(data):
            nonlocal self
            bar_widths = []
            # Determine length of each segment
            for index_list in data:
                prev = 0
                for index in index_list[1]:
                    bar_widths.append(index-prev)
                    prev = index
                # Last border until end
                bar_widths.append(index_list[0]-prev)
            print(bar_widths)

            self.ax.clear()
            self.ax.barh(y=1, width=bar_widths)

            return []

        return update

    # data should follow the (batch/file, time, channel) format
    def process(self, data,  **kwargs):       
        self._emit_draw(data=data)

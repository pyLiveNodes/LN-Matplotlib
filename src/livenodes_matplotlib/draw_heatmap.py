import numpy as np

from livenodes.viewer import View_MPL
from .ports import Ports_data, Ports_empty


class Draw_heatmap(View_MPL):
    """
    Draw all the first two received data channels as heat plot.
    
    Time is represented via alpha values. The most current point is opaque the furthest point away is at 10% alpha.

    Draws on a matplotlib canvas.
    """

    ports_in = Ports_data()
    ports_out = Ports_empty()

    category = "Draw"
    description = ""

    example_init = {
        "name": "Draw Heatmap",
        "zlim": 100
    }

    def __init__(self,
                 zlim=100,
                 name="Draw Heatmap",
                 **kwargs):
        super().__init__(name=name, **kwargs)

        self.zlim = zlim

    def _settings(self):
        return {\
            "name": self.name,
            "zlim": self.zlim
           }

    def _init_draw(self, subfig):
        subfig.suptitle(self.name, fontsize=14)

        self.ax = subfig.subplots(1, 1)
        
        # self.ax.spines['top'].set_visible(False)
        # self.ax.spines['right'].set_visible(False)

        # self.ax.set_xlabel(self.plot_names[0])
        # self.ax.set_ylabel(self.plot_names[1])


        def update(data):
            nonlocal self
            # Not sure why the changes part doesn't work, (not even with zorder)
            # -> could make stuff more efficient, but well...
            # changes = []

            # TODO: figure out how to use propper blitting here!
            # x1 = np.linspace(0, len(sig) / 1000, len(data))
            mesh = self.ax.pcolormesh(data, cmap="YlGnBu")

            return [mesh]

        return update

    # data should follow the (batch/file, time, channel) format
    def process(self, data,  **kwargs):       
        self._emit_draw(data=data)

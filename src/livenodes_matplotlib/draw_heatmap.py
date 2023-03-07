from livenodes.viewer import View_MPL
from livenodes_core_nodes.ports import Ports_data, Ports_empty

from typing import NamedTuple
from livenodes_core_nodes.ports import Port_Matrix_Number, Ports_data, Port_Data

class Ports_in(NamedTuple):
    data: Port_Matrix_Number = Port_Matrix_Number('Matrix')

class Draw_heatmap(View_MPL):
    """
    Draw all the first two received data channels as heat plot.
    
    Time is represented via alpha values. The most current point is opaque the furthest point away is at 10% alpha.

    Draws on a matplotlib canvas.
    """

    ports_in = Ports_in()
    ports_out = Ports_empty()

    category = "Draw"
    description = ""

    example_init = {
        "name": "Draw Heatmap",
        "zlim": 100,
        "disp_ticks": False
    }

    def __init__(self,
                 zlim=100,
                 name="Draw Heatmap",
                 disp_ticks=False,
                 **kwargs):
        super().__init__(name=name, **kwargs)

        self.zlim = zlim
        self.disp_ticks = disp_ticks

    def _settings(self):
        return {\
            "name": self.name,
            "zlim": self.zlim,
            "disp_ticks": self.disp_ticks,
           }

    def _init_draw(self, subfig):
        subfig.suptitle(self.name, fontsize=14)

        ax = subfig.subplots(1, 1)
        
        # ax.spines['top'].set_visible(False)
        # ax.spines['right'].set_visible(False)

        # ax.set_xlabel(self.plot_names[0])
        # ax.set_ylabel(self.plot_names[1])

        if not self.disp_ticks:
            ax.set_yticks([])
            ax.set_xticks([])

        mesh = None
        zlim = self.zlim

        def update(data):
            nonlocal zlim, mesh
            # Not sure why the changes part doesn't work, (not even with zorder)
            # -> could make stuff more efficient, but well...
            # changes = []

            if mesh == None:
                mesh = ax.pcolormesh(data, cmap="YlGnBu", vmax=zlim, vmin=0)
            else:
                # TODO: figure out how to use propper blitting here!
                mesh.set_array(data)

            return [mesh]

        return update

    # data should follow the (batch/file, time, channel) format
    def process(self, data,  **kwargs):  
        # mask = np.tri(data.shape[0], k=-1).T
        # self._emit_draw(data=np.ma.array(data, mask=mask))
        
        # only every draw the last batch
        # since no history is displayed we also don't need to keep it
        self._emit_draw(data=data)

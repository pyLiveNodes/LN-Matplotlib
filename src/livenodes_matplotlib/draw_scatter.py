import numpy as np

from livenodes.viewer import View_MPL
from livenodes_core_nodes.ports import Ports_data_channels, Ports_empty


class Draw_scatter(View_MPL):
    """
    Draw all the first two received data channels as scatter plot.

    Time is represented via alpha values. The most current point is opaque the furthest point away is at 10% alpha.

    Draws on a matplotlib canvas.
    """

    ports_in = Ports_data_channels()
    ports_out = Ports_empty()

    category = "Draw"
    description = ""

    example_init = {
        "name": "Draw Data Scatter",
        "n_scatter_points": 50,
        "ylim": (-1.1, 1.1)
    }

    # TODO: move the sample rate into a data_stream?
    def __init__(self,
                 n_scatter_points=50,
                 ylim=(-1.1, 1.1),
                 name="Draw Output Scatter",
                 **kwargs):
        super().__init__(name=name, **kwargs)

        self.n_scatter_points = n_scatter_points
        self.ylim = ylim

        # computation process
        # yData follows the structure (time, channel)
        self.data = np.zeros(n_scatter_points * 2).reshape(
            (n_scatter_points, 2))

        # render process
        self.channels = list(map(str, range(2)))

    def _settings(self):
        return {\
            "name": self.name,
            "n_scatter_points": self.n_scatter_points,
            "ylim": self.ylim
           }

    def _init_draw(self, subfig):
        subfig.suptitle(self.name, fontsize=14)

        self.ax = subfig.subplots(1, 1)
        self.ax.set_xlim(*self.ylim)
        self.ax.set_ylim(*self.ylim)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        # self.ax.set_xlabel(self.plot_names[0])
        # self.ax.set_ylabel(self.plot_names[1])

        alphas = np.linspace(0.2, 1, self.n_scatter_points)
        xData = self.data[:, 0]
        yData = self.data[:, 1]

        scatter = self.ax.scatter(xData, yData, alpha=alphas)

        # self.labels = [self.ax.text(0.005, 0.95, name, zorder=100, fontproperties=self.ax.xaxis.label.get_font_properties(), rotation='horizontal', va='top', ha='left', transform = ax.transAxes) for name, ax in zip(self.channels, axes)]

        def update(data, channels):
            nonlocal scatter
            # Not sure why the changes part doesn't work, (not even with zorder)
            # -> could make stuff more efficient, but well...
            # changes = []

            scatter.set_offsets(data[::-1])

            return [scatter]

        return update

    def _should_process(self, data=None, channels=None):
        return (data is not None) and \
            (self.channels is not None or channels is not None)

    # data should follow the (batch/file, time, channel) format
    def process(self, data, channels=None, **kwargs):
        if channels is not None:
            self.channels = channels

        # data format is (batch/file, time, channel)
        # first subselect the channels we want to use
        # then concatenate batches
        d = np.vstack(np.array(data)[:, :, :2])

        self.data = np.roll(self.data, -d.shape[0], axis=0)
        self.data[-d.shape[0]:] = d

        # TODO: consider if we really always want to send the channel names? -> seems an unecessary overhead (but cleaner code atm, maybe massage later...)
        self._emit_draw(data=self.data[-self.n_scatter_points:],
                        channels=self.channels)

import numpy as np

from livenodes.viewer import View_MPL

# The draw pattern works as follows:
# 1. init_draw is called externally by matplotlib or qt and provides access to the subfig.
#   -> use this to setup axes, paths etc
# 2. init_draw returns a update function which is also called externally and does not receive any inputs
#   -> this should only interface the update calls on matplotlib using data stored in the attributes of the class instance
# 3. receive_data is called by the pipeline and receives the data as well as potential meta information or other data channels
#   -> calculate the data you will render in the update fn from draw_init
#
# The main advantage of this is, that the pipeline and render loops are separated and one doesn't slow down the other
#
from livenodes_common_ports import Ports_ts_channels, Ports_empty


# class Draw_lines_mpl(View_MPL):
class Draw_lines(View_MPL):
    """
    Draw all received data channels as line plot over time.

    Furthest right is the current time, left is x second in the past.

    Draws on a matplotlib canvas.
    """

    ports_in = Ports_ts_channels()
    ports_out = Ports_empty()

    category = "Draw"
    description = ""

    example_init = {
        "name": "Draw Data Lines",
        "n_plots": 4,
        "xAxisLength": 5000,
        "sample_rate": 1000,
        "ylim": (-1.1, 1.1),
        "disp_yticks": False
    }

    # TODO: move the sample rate into a data_stream?
    def __init__(self,
                 n_plots=4,
                 xAxisLength=5000,
                 sample_rate=1000,
                 ylim=(-1.1, 1.1),
                 disp_yticks=False,
                 name="Draw Output Lines",
                 **kwargs):
        super().__init__(name=name, **kwargs)

        self.xAxisLength = xAxisLength
        self.sample_rate = sample_rate
        self.ylim = ylim
        self.disp_yticks = disp_yticks
        self.n_plots = n_plots

        # computation process
        # yData follows the structure (time, channel)
        self.yData = np.zeros(xAxisLength * n_plots).reshape(
            (xAxisLength, n_plots))

        # render process
        self.channels = ["" for _ in range(n_plots)]

    def _settings(self):
        return {\
            "name": self.name,
            "n_plots": self.n_plots, # TODO: consider if we could make this max_plots so that the data stream might also contain less than the specified amount of plots
            "xAxisLength": self.xAxisLength,
            "sample_rate": self.sample_rate,
            "ylim": self.ylim,
            "disp_yticks": self.disp_yticks,
           }

    def _init_draw(self, subfig):
        subfig.suptitle(self.name, fontsize=14)

        axes = subfig.subplots(self.n_plots, 1, sharex=True)
        if self.n_plots <= 1:
            axes = [axes]

        for name, ax in zip(self.channels, axes):
            ax.set_ylim(*self.ylim)
            ax.set_xlim(0, self.xAxisLength)
            if not self.disp_yticks:
                ax.set_yticks([])

            ticks = np.linspace(0, self.xAxisLength, 11).astype(int)
            ax.set_xticks(ticks)
            ax.set_xticklabels(-ticks / self.sample_rate)
            ax.invert_xaxis()
            # ax.xaxis.grid(False)

        axes[-1].set_xlabel("Time [sec]")
        xData = range(0, self.xAxisLength)
        self.lines = [
            axes[i].plot(xData,
                         np.zeros((self.xAxisLength)) - 1,
                         lw=2,
                         animated=True)[0] for i in range(self.n_plots)
        ]

        # self.labels = []
        self.labels = [
            ax.text(0.005,
                    0.95,
                    name,
                    zorder=100,
                    fontproperties=ax.xaxis.label.get_font_properties(),
                    rotation='horizontal',
                    va='top',
                    ha='left',
                    transform=ax.transAxes)
            for name, ax in zip(self.channels, axes)
        ]

        # self.labels = [ax.text(0, 0.5, name, fontproperties=ax.xaxis.label.get_font_properties(), rotation='vertical', va='center', ha='right', transform = ax.transAxes) for name, ax in zip(self.channels, axes)]

        def update(data, channels):
            nonlocal self
            # Not sure why the changes part doesn't work, (not even with zorder)
            # -> could make stuff more efficient, but well...
            # changes = []

            # as the x-axis is reversed
            # data = np.array(data)[::-1]

            if self.channels != channels:
                self.channels = channels

                for i, label in enumerate(self.labels):
                    label.set_text(self.channels[i])

            for i in range(self.n_plots):
                self.lines[i].set_ydata(data[i][::-1])

            return list(np.concatenate([self.lines, self.labels]))

        return update

    def _should_process(self, ts=None, channels=None):
        return ts is not None and \
            (self.channels is not None or channels is not None)

    # data should follow the (batch/file, time, channel) format
    def process(self, ts, channels=None, **kwargs):
        if channels is not None:
            self.channels = channels

        # ts format is (batch/file, time, channel)
        # first subselect the channels we want to use
        # then concatenate batches
        d = np.vstack(np.array(ts)[:, :, :self.n_plots])
        # d is now of shape (time, channel)
        # now only keep the last xAxisLength values
        d = d[-self.xAxisLength:,:]


        # self.info(np.array(data).shape, d.shape, self.yData.shape)

        self.yData = np.roll(self.yData, -d.shape[0], axis=0)
        self.yData[-d.shape[0]:] = d

        # TODO: consider if we really always want to send the channel names? -> seems an unecessary overhead (but cleaner code atm, maybe massage later...)
        # self.debug('emitting draw', self.yData.shape)
        self._emit_draw(data=list(self.yData.T),
                        channels=self.channels)

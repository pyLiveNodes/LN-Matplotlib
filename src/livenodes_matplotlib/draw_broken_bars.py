import numpy as np
from itertools import groupby
import seaborn as sns

from livenodes.viewer import View_MPL
from typing import NamedTuple
from .ports import Port_two_dim_any, Ports_empty, Port_List_Str

class Ports_in(NamedTuple):
    classes: Port_two_dim_any = Port_two_dim_any("classes")
    channels: Port_List_Str = Port_List_Str("Channel Names")


def convert_pos(pos, yrange):
    ymin, ywidth = yrange
    ymax = ymin + ywidth
    verts = [[(xmin, ymin), (xmin, ymax), (xmin + xwidth, ymax),
              (xmin + xwidth, ymin), (xmin, ymin)] for xmin, xwidth in pos]
    return verts


# there is likeley a more efficient and elegant way with reduce here.
def convert_list_pos(itms, x_max, yrange):
    start = max(0, x_max - len(itms))
    pos = []
    names = []
    for act, group in groupby(itms):
        n_itms = len(list(group))
        next_start = start + n_itms
        pos.append((start, next_start))
        # pos.append((start, next_start - 1))
        names.append(act)
        start = next_start
        # print('|', n_itms, act)
    # print(names[0], start, sum([y - x for x, y in pos]), len(itms), multiplier)
    return names, convert_pos(pos, yrange)


class Draw_broken_bars(View_MPL):
    """

    """

    ports_in = Ports_in()
    ports_out = Ports_empty()

    category = "Draw"
    description = ""

    example_init = {"name": "Classes", "xAxisLength": 50, "n_plots": 1}

    def __init__(self,
                 xAxisLength=50,
                 name="Classes",
                 n_plots=1,
                 **kwargs):
        super().__init__(name=name, **kwargs)

        # process side
        self.colors = None
        self.buffer = [[]] * n_plots 

        # render side
        self._bar_colors = []

        self.xAxisLength = xAxisLength
        self.n_plots = n_plots

        self.verts = [[]] * n_plots 
        self.names = [['']] * n_plots 
        self.channels = None

    def _settings(self):
        return {\
            "name": self.name,
            "xAxisLength": self.xAxisLength,
            "n_plots": self.n_plots
           }

    def _should_draw(self, **cur_state):
        # if not bool(cur_state):
        #     print('Draw infos', "recognition" in cur_state, "annotation" in cur_state, "colors" in cur_state, bool(cur_state))
        return bool(cur_state)

    def _init_draw(self, subfig):
        yrange = (0, 0.7)

        axes = subfig.subplots(self.n_plots, 1)
        if self.n_plots == 1:
            axes = [axes]
        subfig.suptitle(self.name, fontsize=14)

        bar_objs = []
        txt_fout_objs = []
        txt_fin_objs = []

        for ax, name in zip(axes, self.names):
            ax.set_ylim(0, 1)
            ax.set_xlim(0, self.xAxisLength)
            ax.set_xticks([])
            ax.set_yticks([])
            # ax.set_ylabel(name)

            # many thanks to: https://stackoverflow.com/questions/59587466/how-can-i-annotate-a-grouped-broken-barh-chart-python-matplotlib
            bar_objs.append(
                ax.broken_barh([(0, 0)], yrange=yrange, edgecolor='white'))
            # bar_objs.append(ax.broken_barh([(0, 0)], yrange=yrange))
            txt_fout_objs.append(
                ax.text(x=0,
                        y=0.9,
                        s="",
                        ha='left',
                        va='top',
                        color='black',
                        fontsize=12))  #backgroundcolor='grey',
            txt_fin_objs.append(
                ax.text(x=self.xAxisLength,
                        y=0.9,
                        s="",
                        ha='right',
                        va='top',
                        color='black',
                        fontsize=12))  #backgroundcolor='grey',

        # Add legend
        # handles = [ mpatches.Patch(color=val, label=key) for key, val in self.token_cols.items()]
        # legend = subfig.legend(handles=handles, loc='upper right')
        # legend.set_alpha(0) # TODO: for some reason the legend is transparent, no matter what i set here...
        # legend.set_zorder(100)

        def update(classes):
            nonlocal self, bar_objs, txt_fout_objs, txt_fin_objs

            # if colors is not None:
            #     self._bar_colors = colors

            for i, sequence in enumerate(classes):
                self.names[i], self.verts[i] = convert_list_pos(
                    sequence[-self.xAxisLength:], self.xAxisLength, (0, 0.7))
            
            #TODO: rework this to work properly with missing streams...
            # if len(self.verts) > 0 and len(self._bar_colors) > 0:
            # for bar_obj, tx_out, tx_in, verts, names, colors in zip(
            for bar_obj, tx_out, tx_in, verts, names in zip(
                    bar_objs, txt_fout_objs, txt_fin_objs, self.verts,
                    self.names): #, self._bar_colors):
                bar_obj.set_verts(verts)
                # print('-----')
                # for v in verts:
                #     print(v)
                # bar_obj.set_facecolor([colors[name] for name in names])
                tx_out.set_text(names[0])
                tx_in.set_text(names[-1])
            return bar_objs + txt_fout_objs + txt_fin_objs

        return update

    def _should_process(self,
                        classes=None,
                        channels=None):

        return (classes is not None) \
            and (not self._is_input_connected(self.ports_in.channels) or (self.channels is not None) or (channels is not None))

    def process(self,
                classes=None,
                channels=None,
                **kwargs):
        # if hmm_meta is not None:
        #     token_colors, atom_colors, state_colors = self._init_colors(
        #         hmm_meta.get('topology'))
        #     self.colors = [
        #         state_colors, atom_colors, token_colors, token_colors
        #     ]

        # if len(recognition) > 0:
        #     # for the annotaiton, we'll assume it is in the normal (batch/file, time, channel) format and that batch is not relevant here
        #     # similarly we expect recognition not to have taken batch into account (ah fu... there is still some trouble there, that is not a true assumption)
        #     # print(np.array(annotation).shape, len(recognition))
        #     if annotation is not None:
        #         annotation = np.array(annotation)[0, :, 0]
        #     self._emit_draw(recognition=recognition,
        #                     colors=self.colors,
        #                     annotation=annotation)
            # self._emit_draw(recognition=recognition, colors=self.colors, annotation=None)
        
        for i, sequence in enumerate(classes):
            self.buffer[i] = (self.buffer[i] + list(sequence))[-self.xAxisLength:]
                
        # print('--')
        # print(self.buffer)

        self._emit_draw(classes=self.buffer) # TODO: add mem or batch before or inside this...

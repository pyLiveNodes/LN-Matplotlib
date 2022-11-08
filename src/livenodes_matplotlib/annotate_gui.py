import multiprocessing as mp
from matplotlib.widgets import TextBox, Button

from livenodes.viewer import View_MPL

from typing import NamedTuple
from .ports import Ports_data, Port_Data, Port_Vector_of_Strings

class Ports_out(NamedTuple):
    data: Port_Data = Port_Data("Data")
    annot: Port_Vector_of_Strings = Port_Vector_of_Strings("Annotation")


# TODO: figure out how to resolve these name clashes
class Annotate_gui(View_MPL):
    ports_in = Ports_data()
    ports_out = Ports_out()

    category = "Annotation"
    description = ""

    example_init = {
        "name": "GUI Button Annotation",
        "fall_back_target": "Unknown",
    }

    def __init__(self,
                 fall_back_target="Unknown",
                 name="GUI Button Annotation",
                 **kwargs):
        super().__init__(name=name, **kwargs)

        self.fall_back_target = fall_back_target

        self.annot_target = fall_back_target
        self.current_target = fall_back_target
        self.recording = False

        self.target_q = mp.Queue()

    def _settings(self):
        """
        Get the Nodes setup settings.
        Primarily used for serialization from json files.
        """
        return { \
            "name": self.name,
            "fall_back_target": self.fall_back_target
        }

    def process(self, data, **kwargs):
        # IMPORTANT: we assume that the length of data is always short enough that we do not care about timing issues with the label
        while not self.target_q.empty():
            self.fall_back_target, self.current_target = self.target_q.get()

        return self.ret(data=data, annot=[self.current_target] * len(data))

    def __activity_toggle_rec(self, event):
        if self.recording:
            # Stop recording
            self.bnext.label.set_text('Start')
            self.target_q.put((self.fall_back_target, self.fall_back_target))
        else:
            # Start recording
            self.bnext.label.set_text('Stop')
            self.target_q.put((self.fall_back_target, self.annot_target))

        self.recording = not self.recording

    def __update_fallback(self, text):
        self.fall_back_target = text
        self.target_q.put((self.fall_back_target, self.annot_target))

    def __update_annot(self, text):
        self.annot_target = text

    def _init_draw(self, subfig):
        subfig.suptitle("Annotate", fontsize=14)

        axes = subfig.subplots(3, 1, sharex=True)

        self.target_default = TextBox(axes[0],
                                      'Fallback:',
                                      initial=self.fall_back_target)
        # self.target_default.label.set_fontsize(20)
        self.target_default.on_submit(self.__update_fallback)

        self.target_annotate = TextBox(axes[1],
                                       'Recognize:',
                                       initial=self.annot_target)
        # self.target_annotate.label.set_fontsize(20)
        self.target_annotate.on_submit(self.__update_annot)

        self.bnext = Button(axes[2], 'Start')
        self.bnext.label.set_fontsize(20)
        self.bnext.on_clicked(self.__activity_toggle_rec)

        def update(**kwargs):
            nonlocal axes
            return axes

        return update

    def _should_draw(self, **kwargs):
        return True

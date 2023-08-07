from fluidsynth import (
    Synth,
    c_int,
    c_uint,
    c_void_p,
    cfunc,
    fluid_player_play,
    new_fluid_player,
)

fluid_player_add_mem = cfunc(
    "fluid_player_add_mem",
    c_int,
    ("player", c_void_p, 1),
    ("buffer", c_void_p, 1),
    ("len", c_uint, 1),
)


class PatchedSynth(Synth):
    def play_from_mem(self, data):
        self.player = new_fluid_player(self.synth)
        fluid_player_add_mem(self.player, data, len(data))
        fluid_player_play(self.player)

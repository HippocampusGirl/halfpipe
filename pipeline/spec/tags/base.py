# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

"""

"""

from marshmallow import Schema, RAISE, post_load, post_dump, pre_load


entity_colors = {
    "subject": "ired",
    "session": "igreen",
    "run": "imagenta",
    "task": "icyan",
    "direction": "iyellow",
    "condition": "yellow",
    "atlas": "yellow",
    "seed": "yellow",
}


class Tags:
    def __init__(self, **kwargs):
        self.datatype = kwargs.get("datatype")
        self.suffix = kwargs.get("suffix")
        self.extension = kwargs.get("extension")
        #
        self.subject = kwargs.get("subject")
        self.session = kwargs.get("session")
        self.run = kwargs.get("run")
        self.task = kwargs.get("task")
        self.condition = kwargs.get("condition")
        #
        self.phase_encoding_direction = kwargs.get("phase_encoding_direction")
        self.effective_echo_spacing = kwargs.get("effective_echo_spacing")
        self.echo_time_1 = kwargs.get("echo_time_1")
        self.echo_time_2 = kwargs.get("echo_time_2")
        self.echo_time = kwargs.get("echo_time")
        self.repetition_time = kwargs.get("repetition_time")
        #
        self.smoothed = kwargs.get("smoothed")
        self.band_pass_filtered = kwargs.get("band_pass_filtered")
        self.confounds_removed = kwargs.get("confounds_removed")
        self.space = kwargs.get("space")
        self.desc = kwargs.get("desc")
        #
        self.atlas = kwargs.get("atlas")
        self.seed = kwargs.get("seed")
        self.map = kwargs.get("map")

    @property
    def direction(self):
        return self.phase_encoding_direction

    @direction.setter
    def direction(self, value):
        self.phase_encoding_direction = value

    def __hash__(self):
        return hash(
            (
                self.datatype,
                self.suffix,
                self.extension,
                #
                self.subject,
                self.session,
                self.run,
                self.task,
                self.condition,
                #
                self.phase_encoding_direction,
                self.effective_echo_spacing,
                self.echo_time_1,
                self.echo_time_2,
                self.echo_time,
                self.repetition_time,
                #
                self.smoothed,
                self.band_pass_filtered,
                self.confounds_removed,
                self.space,
                self.desc,
                #
                self.atlas,
                self.seed,
                self.map,
            )
        )


class BaseSchema(Schema):
    class Meta:
        unknown = RAISE

    @pre_load
    def canonicalize_pedir_tagname(self, in_data, **kwargs):
        if "direction" in in_data and "phase_encoding_direction" not in in_data:
            in_data["phase_encoding_direction"] = in_data["direction"]
            del in_data["direction"]
        return in_data

    @post_load
    def make_object(self, data, **kwargs):
        return Tags(**data)

    @post_dump(pass_many=False)
    def remove_none(self, data, many):
        return {key: value for key, value in data.items() if value is not None}

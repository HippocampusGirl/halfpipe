# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import numpy as np

from nipype.interfaces.base import (
    isdefined,
    traits,
    TraitedSpec,
    DynamicTraitedSpec
)
from nipype.interfaces.io import (
    add_traits,
    IOBase
)


class LogicalAndInputSpec(DynamicTraitedSpec):
    pass


class LogicalAndOutputSpec(TraitedSpec):
    out = traits.Bool(desc="output")


class LogicalAnd(IOBase):
    """

    """

    input_spec = LogicalAndInputSpec
    output_spec = LogicalAndOutputSpec

    def __init__(self, numinputs=0, **inputs):
        super(LogicalAnd, self).__init__(**inputs)
        self._numinputs = numinputs
        if numinputs >= 1:
            input_names = ["in%d" % (i + 1) for i in range(numinputs)]
            add_traits(self.inputs, input_names, trait_type=traits.Bool)
        else:
            input_names = []

    def _list_outputs(self):
        outputs = self._outputs().get()
        out = []

        if self._numinputs < 1:
            return outputs

        def getval(idx):
            return getattr(self.inputs, "in%d" % (idx + 1))

        values = [
            getval(idx) for idx in range(self._numinputs)
            if isdefined(getval(idx))
        ]

        out = False

        if len(values) > 0:
            out = np.all(values)

        outputs["out"] = out
        return outputs


class Filter(IOBase):
    """Basic interface class to merge inputs into lists

    """

    input_spec = DynamicTraitedSpec
    output_spec = DynamicTraitedSpec

    def __init__(self, numinputs=0, fieldnames=["value"], **inputs):
        super(Filter, self).__init__(**inputs)
        self._numinputs = numinputs
        self._fieldnames = fieldnames
        if numinputs >= 1:
            for fieldname in self._fieldnames:
                input_names = [
                    "{}{}".format(fieldname, (i + 1))
                    for i in range(numinputs)
                ]
                add_traits(self.inputs, input_names)
            isenabled_input_names = \
                ["is_enabled%d" % (i + 1) for i in range(numinputs)]
            add_traits(self.inputs, isenabled_input_names,
                       trait_type=traits.Bool)
        else:
            input_names = []

    def _add_output_traits(self, base):
        return add_traits(base, self._fieldnames)

    def _list_outputs(self):
        outputs = self._outputs().get()

        if self._numinputs < 1:
            return outputs

        def getisenabled(idx):
            return getattr(self.inputs, "is_enabled%d" % (idx + 1))

        def getval(fieldname, idx):
            return getattr(
                self.inputs,
                "{}{}".format(fieldname, (idx + 1))
            )

        for fieldname in self._fieldnames:
            outputs["fieldname"] = []

        for idx in range(self._numinputs):
            use = isdefined(getisenabled(idx)) and getisenabled(idx)
            for fieldname in self._fieldnames:  # all need to be defined
                use &= isdefined(getval(fieldname, idx))
            if use:
                for fieldname in self._fieldnames:
                    outputs[fieldname].append(getval(fieldname, idx))

        return outputs

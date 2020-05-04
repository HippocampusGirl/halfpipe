# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

"""

"""

import logging
from uuid import uuid4
import os
from os import path as op

from marshmallow import (
    fields,
    Schema,
    post_load,
    RAISE,
    validate,
    validates_schema,
    ValidationError,
)
import marshmallow.exceptions

from .file import FileSchema
from .analysis import AnalysisSchema

entity_aliases = {"direction": "phase_encoding_direction"}
compatible_versions = ["1.0"]


class Spec:
    version = "1.0"

    def __init__(self, **kwargs):
        self.uuid = kwargs.get("uuid", uuid4())
        self.version = kwargs.get("version", self.version)
        self.files = kwargs.get("files", [])
        self.variants = kwargs.get("variants", [])
        self.analyses = kwargs.get("analyses", [])

    def _has_datatype(self, datatype):
        res = False
        for file_obj in self.files:
            if file_obj.tags.datatype == datatype:
                res = True
        return res

    def has_anat(self):
        return self._has_datatype("anat")


class SpecSchema(Schema):
    uuid = fields.UUID(required=True)
    version = fields.Str(validate=validate.OneOf(compatible_versions))
    files = fields.List(fields.Nested(FileSchema), required=True)
    analyses = fields.List(fields.Nested(AnalysisSchema), required=True)

    @validates_schema
    def validate_analyses(self, data, **kwargs):
        if "analyses" not in data:
            return
        seen_names = set()
        for analysis in data["analyses"]:
            if analysis.name in seen_names:
                raise ValidationError("analysis name must be unique")

    @post_load
    def make_object(self, data, **kwargs):
        return Spec(**data)


def loadspec(workdir=None, uuidstr=None, specpath=None, logger=logging.getLogger("pipeline")):
    if specpath is None:
        assert workdir is not None
        if uuidstr is not None:
            specpath = op.join(workdir, f"spec.{uuidstr}.json")
        else:
            specpath = op.join(workdir, "spec.json")
    if not op.isfile(specpath):
        return

    logger.info(f"Loading spec file: {specpath}")
    with open(specpath, "r") as f:
        jsn = f.read()

    try:
        spec = SpecSchema().loads(jsn, many=False, unknown=RAISE)
        return spec
    except marshmallow.exceptions.ValidationError as e:
        logger.warning(f'Ignored validation error in "{specpath}": %s', e, stack_info=True)


def savespec(spec, workdir=None, specpath=None, logger=logging.getLogger("pipeline")):
    os.makedirs(workdir, exist_ok=True)
    if specpath is None:
        assert workdir is not None
        specpath = op.join(workdir, "spec.json")
    if op.isfile(specpath):
        spectomove = loadspec(specpath=specpath)
        if spectomove is None:
            logger.warn("Overwriting invalid spec file")
        else:
            uuidstr = str(spectomove.uuid)[:8]
            newspecpath = op.join(workdir, f"spec.{uuidstr}.json")
            logger.info(f'Moving previous spec file from "{specpath}" to "{newspecpath}"')
            if op.isfile(newspecpath):
                logger.warn("Found specpath uuidstr collision, overwriting")
            os.replace(specpath, newspecpath)
    jsn = SpecSchema().dumps(spec, many=False, indent=4)
    with open(specpath, "w") as f:
        f.write(jsn)

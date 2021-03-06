# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

from calamities import (
    TextView,
    SpacerView,
    FilePatternInputView,
    TextInputView,
    TextElement,
)
from calamities.pattern import tag_parse, get_entities_in_path

import logging

from .step import Step
from ..model import FileSchema, entities, entity_longnames as entity_display_aliases
from .utils import messagefun, forbidden_chars, entity_colors
from ..utils import splitext, inflect_engine as p


class FilePatternSummaryStep(Step):
    entity_display_aliases = entity_display_aliases

    filetype_str = "file"
    filedict = {}
    schema = FileSchema

    next_step_type = None

    def setup(self, ctx):
        self.is_first_run = True

        entities = self.schema().fields["tags"].nested().fields.keys()

        filepaths = ctx.database.get(**self.filedict)
        message = messagefun(ctx.database, self.filetype_str, filepaths, entities)

        self._append_view(TextView(message))
        self._append_view(SpacerView(1))

    def run(self, ctx):
        return self.is_first_run

    def next(self, ctx):
        if self.is_first_run:
            self.is_first_run = False
            return self.next_step_type(self.app)(ctx)
        else:
            return


class AskForMissingEntities(Step):
    def __init__(
        self,
        app,
        entity_display_aliases,
        ask_if_missing_entities,
        suggest_file_stem,
        next_step_type,
    ):
        super(AskForMissingEntities, self).__init__(app)

        self.entity_display_aliases = entity_display_aliases
        self.ask_if_missing_entities = ask_if_missing_entities
        self.suggest_file_stem = suggest_file_stem

        self.entity = None
        self.entity_str = None
        self.tagval = None

        self.next_step_type = next_step_type

    def setup(self, ctx):
        self.is_first_run = True

        entites_in_path = get_entities_in_path(ctx.spec.files[-1].path)

        tags = ctx.spec.files[-1].tags
        while len(self.ask_if_missing_entities) > 0:
            entity = self.ask_if_missing_entities.pop(0)

            if entity in entites_in_path:
                continue

            if tags.get(entity) is not None:
                continue

            self.entity = entity
            break

        if self.entity is not None:
            self.entity_str = self.entity
            if self.entity_str in self.entity_display_aliases:
                self.entity_str = self.entity_display_aliases[self.entity_str]

            self._append_view(TextView(f"No {self.entity_str} name was specified"))
            self._append_view(TextView(f"Specify the {self.entity_str} name"))

            suggestion = ""
            if self.suggest_file_stem:
                suggestion, _ = splitext(ctx.spec.files[-1].path)

            self.input_view = TextInputView(
                text=suggestion, isokfun=lambda text: forbidden_chars.search(text) is None
            )

            self._append_view(self.input_view)
            self._append_view(SpacerView(1))

    def run(self, ctx):
        if self.entity is None:
            return self.is_first_run
        else:
            self.tagval = self.input_view()
            if self.tagval is None:
                return False
            return True

    def next(self, ctx):
        if self.tagval is not None:
            ctx.spec.files[-1].tags[self.entity] = self.tagval

        if self.entity is not None or self.is_first_run:
            self.is_first_run = False

            if len(self.ask_if_missing_entities) > 0:
                return AskForMissingEntities(
                    self.app,
                    {**self.entity_display_aliases},
                    [*self.ask_if_missing_entities],
                    self.suggest_file_stem,
                    self.next_step_type,
                )(ctx)

            else:
                ctx.database.put(
                    ctx.spec.files[-1]
                )  # we've got all tags, so we can add the fileobj to the index

                return self.next_step_type(self.app)(ctx)

        return


class FilePatternStep(Step):
    suggest_file_stem = False
    entity_display_aliases = entity_display_aliases

    filetype_str = "file"
    filedict = {}
    schema = FileSchema

    ask_if_missing_entities = []
    required_in_path_entities = []

    next_step_type = None

    def _transform_extension(self, ext):
        return ext

    def setup(self, ctx):
        self.file_obj = None

        if hasattr(self, "header_str") and self.header_str is not None:
            self._append_view(TextView(self.header_str))
            self._append_view(SpacerView(1))

        self._append_view(TextView(f"Specify the path of the {self.filetype_str} files"))

        schema_entities = self.schema().fields["tags"].nested().fields.keys()
        schema_entities = [
            entity for entity in reversed(entities) if entity in schema_entities
        ]  # keep order

        # need original entities for this
        entity_colors_list = [entity_colors[entity] for entity in schema_entities]

        # convert to display
        schema_entities = [
            self.entity_display_aliases[entity] if entity in self.entity_display_aliases else entity
            for entity in schema_entities
        ]

        required_entities = [*self.ask_if_missing_entities, *self.required_in_path_entities]

        entity_instruction_strs = []
        optional_entity_strs = []
        for entity in schema_entities:
            if entity in required_entities:
                entity_instruction_strs.append(f"Put {{{entity}}} in place of the {entity} names")
            else:
                optional_entity_strs.append(f"{{{entity}}}")

        if len(optional_entity_strs) > 0:
            entity_instruction_strs.append(f"You can also use {p.join(optional_entity_strs)}")

        entity_instruction_views = [TextView("") for str in entity_instruction_strs]
        for view in entity_instruction_views:
            self._append_view(view)

        self.file_pattern_input_view = FilePatternInputView(
            schema_entities,
            entity_colors_list=entity_colors_list,
            required_entities=self.required_in_path_entities,
        )
        self._append_view(self.file_pattern_input_view)

        for str, view in zip(entity_instruction_strs, entity_instruction_views):
            view.text = self.file_pattern_input_view._tokenize(str, addBrackets=False)

        self._append_view(SpacerView(1))

    def run(self, ctx):
        while True:
            path = self.file_pattern_input_view()
            if path is None:
                return False

            # remove display aliases

            inv = {alias: entity for entity, alias in self.entity_display_aliases.items()}

            i = 0
            _path = ""
            for match in tag_parse.finditer(path):
                groupdict = match.groupdict()
                if groupdict.get("tag_name") in inv:
                    _path += path[i : match.start("tag_name")]
                    _path += inv[groupdict.get("tag_name")]
                    i = match.end("tag_name")

            _path += path[i:]
            path = _path

            # create file obj

            try:
                filedict = {**self.filedict, "path": path, "tags": {}}

                _, ext = splitext(path)
                filedict["extension"] = self._transform_extension(ext)

                self.fileobj = self.schema().load(filedict)
                return True

            except Exception as e:

                logging.getLogger("halfpipe.ui").exception("Exception: %s", e)

                error_color = self.app.layout.color.red
                self.file_pattern_input_view.show_message(TextElement(str(e), color=error_color))

                if ctx.debug:
                    raise

    def next(self, ctx):
        ctx.spec.files.append(self.fileobj)

        return AskForMissingEntities(
            self.app,
            {**self.entity_display_aliases},
            [*self.ask_if_missing_entities],
            self.suggest_file_stem,
            self.next_step_type,
        )(ctx)

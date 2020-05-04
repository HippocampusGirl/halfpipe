# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

from .base import (
    Spec,
    SpecSchema,
    entity_aliases,
    savespec,
    loadspec,
)
from .file import File, FileSchema
from .direction import PhaseEncodingDirection
from .analysis import (
    AnalysisSchema,
    Analysis,
    Variable,
    Contrast,
    Filter,
    FilterSchema,
    FixedEffectsHigherLevelAnalysisSchema,
    GLMHigherLevelAnalysisSchema,
    GroupFilterSchema,
)

from .tags import (
    Tags,
    entity_colors,
    tagnames,
    TagsSchema,
    AnatTagsSchema,
    FuncTagsSchema,
    BoldTagsSchema,
    PreprocessedBoldTagsSchema,
    EventsTagsSchema,
    study_entities,
    bold_entities,
    PEPOLARTagsSchema,
    PhaseDifferenceTagsSchema,
    Phase1TagsSchema,
    Phase2TagsSchema,
    Magnitude1TagsSchema,
    Magnitude2TagsSchema,
    FieldMapTagsSchema,
    FmapTagsSchema,
    SmoothedTagSchema,
    SmoothedTag,
    BandPassFilteredTagSchema,
    BandPassFilteredTag,
    ConfoundsRemovedTag,
    ConfoundsRemovedTagSchema,
    derivative_entities,
    AtlasTagsSchema,
    SeedTagsSchema,
    MapTag,
    MapTagsSchema,
    BIDSAnatTagsSchema,
    BIDSEventsTagsSchema,
    BIDSBoldTagsSchema,
    BIDSFmapTagsSchema,
)

from .qualitycheck import QualitycheckExcludeEntrySchema

__all__ = [
    Spec,
    SpecSchema,
    study_entities,
    bold_entities,
    entity_aliases,
    savespec,
    loadspec,
    File,
    FileSchema,
    Tags,
    entity_colors,
    tagnames,
    TagsSchema,
    AnatTagsSchema,
    FuncTagsSchema,
    BoldTagsSchema,
    PreprocessedBoldTagsSchema,
    EventsTagsSchema,
    PEPOLARTagsSchema,
    PhaseDifferenceTagsSchema,
    Phase1TagsSchema,
    Phase2TagsSchema,
    Magnitude1TagsSchema,
    Magnitude2TagsSchema,
    FieldMapTagsSchema,
    FmapTagsSchema,
    SmoothedTagSchema,
    SmoothedTag,
    BandPassFilteredTagSchema,
    BandPassFilteredTag,
    ConfoundsRemovedTag,
    ConfoundsRemovedTagSchema,
    derivative_entities,
    AtlasTagsSchema,
    SeedTagsSchema,
    MapTag,
    MapTagsSchema,
    BIDSAnatTagsSchema,
    BIDSEventsTagsSchema,
    BIDSBoldTagsSchema,
    BIDSFmapTagsSchema,
    PhaseEncodingDirection,
    AnalysisSchema,
    Analysis,
    Variable,
    Contrast,
    Filter,
    FilterSchema,
    FixedEffectsHigherLevelAnalysisSchema,
    GLMHigherLevelAnalysisSchema,
    GroupFilterSchema,
    QualitycheckExcludeEntrySchema,
]

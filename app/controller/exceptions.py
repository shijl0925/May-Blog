"""Custom exceptions."""


class FlaskError(Exception):
    """Basic exception for this application."""


class ExperimentTypeSearchParamsMissing(FlaskError):
    """Raised when search params for an experiment type are not defined."""


class SearchOptionNotCustomizeable(FlaskError):
    """Raised when an attempt to pass a value
    for a search option that is not meant to be customized."""

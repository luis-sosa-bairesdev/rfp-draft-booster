"""Custom exceptions for RFP Draft Booster."""


class RFPDraftBoosterException(Exception):
    """Base exception for RFP Draft Booster."""
    pass


class PDFProcessingError(RFPDraftBoosterException):
    """Raised when PDF processing fails."""
    pass


class InvalidRFPError(RFPDraftBoosterException):
    """Raised when RFP validation fails."""
    pass


class LLMException(RFPDraftBoosterException):
    """Raised when LLM operations fail."""
    pass


class RequirementExtractionError(LLMException):
    """Raised when requirement extraction fails."""
    pass


class RiskDetectionError(LLMException):
    """Raised when risk detection fails."""
    pass


class ServiceMatchError(RFPDraftBoosterException):
    """Raised when service matching fails."""
    pass


class DraftGenerationError(LLMException):
    """Raised when draft generation fails."""
    pass


class ExportError(RFPDraftBoosterException):
    """Raised when export to Google Docs fails."""
    pass


class ConfigurationError(RFPDraftBoosterException):
    """Raised when configuration is invalid."""
    pass


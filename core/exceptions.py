"""
Production-Grade Exception Handling for School ERP System
"""

class SchoolERPException(Exception):
    """Base exception for School ERP system"""
    pass

class StudentError(SchoolERPException):
    """Student-related errors"""
    pass

class AcademicError(SchoolERPException):
    """Academic operations errors"""
    pass

class FinancialError(SchoolERPException):
    """Financial operations errors"""
    pass

class AdmissionError(SchoolERPException):
    """Admission process errors"""
    pass

class AttendanceError(SchoolERPException):
    """Attendance tracking errors"""
    pass

class ExaminationError(SchoolERPException):
    """Examination system errors"""
    pass

class LibraryError(SchoolERPException):
    """Library management errors"""
    pass

class TransportError(SchoolERPException):
    """Transport management errors"""
    pass

class HostelError(SchoolERPException):
    """Hostel management errors"""
    pass

class HRError(SchoolERPException):
    """HR management errors"""
    pass

class InventoryError(SchoolERPException):
    """Inventory management errors"""
    pass

class AnalyticsError(SchoolERPException):
    """Analytics and reporting errors"""
    pass

# Specific error classes for common scenarios
class InsufficientPermissions(SchoolERPException):
    """User lacks required permissions"""
    pass

class DataValidationError(SchoolERPException):
    """Data validation failed"""
    pass

class ExternalServiceError(SchoolERPException):
    """External service integration failed"""
    pass

class DatabaseOperationError(SchoolERPException):
    """Database operation failed"""
    pass

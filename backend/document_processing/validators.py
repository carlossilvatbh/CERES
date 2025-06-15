"""
Enhanced file validation utilities for CERES document processing
"""
import magic
import hashlib
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import PyPDF2
import io

class DocumentValidator:
    """
    Comprehensive document validation class
    """
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'pdf': 10 * 1024 * 1024,  # 10MB
        'image': 5 * 1024 * 1024,  # 5MB
    }
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'application/pdf': 'pdf',
        'image/jpeg': 'image',
        'image/jpg': 'image',
        'image/png': 'image',
        'image/tiff': 'image',
        'image/bmp': 'image',
    }
    
    # Minimum image dimensions
    MIN_IMAGE_DIMENSIONS = (300, 300)  # 300x300 pixels
    
    @classmethod
    def validate_file_upload(cls, uploaded_file):
        """
        Comprehensive file validation
        
        Args:
            uploaded_file: Django UploadedFile object
            
        Raises:
            ValidationError: If file validation fails
            
        Returns:
            dict: Validation results and metadata
        """
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # 1. File size validation
            cls._validate_file_size(uploaded_file)
            
            # 2. MIME type validation
            file_type = cls._validate_mime_type(uploaded_file)
            
            # 3. File content validation
            cls._validate_file_content(uploaded_file, file_type)
            
            # 4. Security validation
            cls._validate_file_security(uploaded_file)
            
            # 5. Calculate file hash
            file_hash = cls._calculate_file_hash(uploaded_file)
            
            # Reset file pointer for further processing
            uploaded_file.seek(0)
            
            return {
                'valid': True,
                'file_type': file_type,
                'file_hash': file_hash,
                'file_size': uploaded_file.size,
                'mime_type': cls._get_mime_type(uploaded_file),
            }
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"File validation failed: {str(e)}")
    
    @classmethod
    def _validate_file_size(cls, uploaded_file):
        """Validate file size"""
        if uploaded_file.size > max(cls.MAX_FILE_SIZES.values()):
            raise ValidationError(
                f"File size ({uploaded_file.size} bytes) exceeds maximum allowed size "
                f"({max(cls.MAX_FILE_SIZES.values())} bytes)"
            )
    
    @classmethod
    def _validate_mime_type(cls, uploaded_file):
        """Validate MIME type using python-magic"""
        try:
            # Read first 1024 bytes for MIME detection
            file_start = uploaded_file.read(1024)
            uploaded_file.seek(0)
            
            # Detect MIME type
            mime_type = magic.from_buffer(file_start, mime=True)
            
            if mime_type not in cls.ALLOWED_MIME_TYPES:
                raise ValidationError(
                    f"File type '{mime_type}' is not allowed. "
                    f"Allowed types: {list(cls.ALLOWED_MIME_TYPES.keys())}"
                )
            
            return cls.ALLOWED_MIME_TYPES[mime_type]
            
        except Exception as e:
            raise ValidationError(f"MIME type validation failed: {str(e)}")
    
    @classmethod
    def _validate_file_content(cls, uploaded_file, file_type):
        """Validate file content based on type"""
        try:
            uploaded_file.seek(0)
            
            if file_type == 'pdf':
                cls._validate_pdf_content(uploaded_file)
            elif file_type == 'image':
                cls._validate_image_content(uploaded_file)
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Content validation failed: {str(e)}")
    
    @classmethod
    def _validate_pdf_content(cls, uploaded_file):
        """Validate PDF file content"""
        try:
            # Check if file size is appropriate for PDF
            if uploaded_file.size > cls.MAX_FILE_SIZES['pdf']:
                raise ValidationError(f"PDF file too large (max {cls.MAX_FILE_SIZES['pdf']} bytes)")
            
            # Try to read PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            
            # Check if PDF has pages
            if len(pdf_reader.pages) == 0:
                raise ValidationError("PDF file contains no pages")
            
            # Check if PDF is not corrupted
            try:
                # Try to read first page
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
            except Exception:
                raise ValidationError("PDF file appears to be corrupted")
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"PDF validation failed: {str(e)}")
    
    @classmethod
    def _validate_image_content(cls, uploaded_file):
        """Validate image file content"""
        try:
            # Check if file size is appropriate for image
            if uploaded_file.size > cls.MAX_FILE_SIZES['image']:
                raise ValidationError(f"Image file too large (max {cls.MAX_FILE_SIZES['image']} bytes)")
            
            # Try to open image
            image = Image.open(uploaded_file)
            
            # Verify image
            image.verify()
            
            # Reset file pointer and reopen for dimension check
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)
            
            # Check minimum dimensions
            width, height = image.size
            min_width, min_height = cls.MIN_IMAGE_DIMENSIONS
            
            if width < min_width or height < min_height:
                raise ValidationError(
                    f"Image dimensions ({width}x{height}) are too small. "
                    f"Minimum required: {min_width}x{min_height}"
                )
            
            # Check if image is not too large (memory protection)
            max_pixels = 50 * 1024 * 1024  # 50 megapixels
            if width * height > max_pixels:
                raise ValidationError("Image resolution is too high")
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Image validation failed: {str(e)}")
    
    @classmethod
    def _validate_file_security(cls, uploaded_file):
        """Security validation to prevent malicious files"""
        try:
            uploaded_file.seek(0)
            
            # Check for suspicious file signatures
            file_start = uploaded_file.read(1024)
            uploaded_file.seek(0)
            
            # Check for executable signatures
            executable_signatures = [
                b'MZ',  # Windows executable
                b'\x7fELF',  # Linux executable
                b'\xfe\xed\xfa',  # macOS executable
                b'<script',  # JavaScript
                b'<?php',  # PHP
            ]
            
            for signature in executable_signatures:
                if signature in file_start:
                    raise ValidationError("File contains suspicious content")
            
            # Check file name for suspicious extensions
            filename = uploaded_file.name.lower()
            suspicious_extensions = [
                '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
                '.js', '.vbs', '.jar', '.php', '.asp', '.jsp'
            ]
            
            for ext in suspicious_extensions:
                if filename.endswith(ext):
                    raise ValidationError(f"File extension '{ext}' is not allowed")
                    
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Security validation failed: {str(e)}")
    
    @classmethod
    def _calculate_file_hash(cls, uploaded_file):
        """Calculate SHA-256 hash of the file"""
        uploaded_file.seek(0)
        hash_sha256 = hashlib.sha256()
        
        for chunk in iter(lambda: uploaded_file.read(4096), b""):
            hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    @classmethod
    def _get_mime_type(cls, uploaded_file):
        """Get MIME type of the file"""
        uploaded_file.seek(0)
        file_start = uploaded_file.read(1024)
        uploaded_file.seek(0)
        return magic.from_buffer(file_start, mime=True)

def validate_document_upload(uploaded_file):
    """
    Main validation function for document uploads
    
    Usage:
        try:
            validation_result = validate_document_upload(uploaded_file)
            # Process valid file
        except ValidationError as e:
            # Handle validation error
            return Response({'error': str(e)}, status=400)
    """
    return DocumentValidator.validate_file_upload(uploaded_file)


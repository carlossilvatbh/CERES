"""
Document Processing Service
"""
import logging
import json
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from .models import CustomerDocument, DocumentProcessingTask
from .ocr_service import OCRService
from .forensic_service import ForensicAnalysisService

logger = logging.getLogger('ceres')

class DocumentProcessingService:
    """
    Service for coordinating document processing tasks
    """
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.forensic_service = ForensicAnalysisService()
    
    def start_document_processing(self, document: CustomerDocument):
        """
        Start complete document processing pipeline
        """
        logger.info(f"Starting document processing for {document.id}")
        
        # Update document status
        document.verification_status = 'processing'
        document.save()
        
        # Create processing tasks
        tasks = [
            self._create_task(document, 'ocr', {'priority': 'high'}),
            self._create_task(document, 'categorization', {'auto_detect': True}),
        ]
        
        # Start OCR processing
        self._process_ocr(document, tasks[0])
        
        return tasks
    
    def start_forensic_analysis(self, document: CustomerDocument):
        """
        Start forensic analysis for document authenticity
        """
        logger.info(f"Starting forensic analysis for {document.id}")
        
        task = self._create_task(document, 'forensic', {'deep_analysis': True})
        self._process_forensic_analysis(document, task)
        
        return task
    
    def validate_document(self, document: CustomerDocument):
        """
        Validate document data against customer information
        """
        logger.info(f"Validating document {document.id}")
        
        validation_errors = []
        validation_warnings = []
        
        # Get customer data
        customer = document.customer
        personal_data = getattr(customer, 'personal_data', None)
        
        if not personal_data:
            validation_errors.append("No personal data available for validation")
            return {
                'document_id': document.id,
                'is_valid': False,
                'validation_errors': validation_errors,
                'validation_warnings': validation_warnings
            }
        
        # Validate extracted data against personal data
        extracted_data = document.extracted_data
        
        if extracted_data:
            # Name validation
            if 'name' in extracted_data:
                extracted_name = extracted_data['name'].lower().strip()
                customer_name = personal_data.full_name.lower().strip()
                
                if extracted_name != customer_name:
                    # Check for partial matches
                    name_similarity = self._calculate_name_similarity(extracted_name, customer_name)
                    if name_similarity < 0.8:
                        validation_errors.append(
                            f"Name mismatch: Document '{extracted_data['name']}' vs Customer '{personal_data.full_name}'"
                        )
                    elif name_similarity < 0.95:
                        validation_warnings.append(
                            f"Possible name variation: Document '{extracted_data['name']}' vs Customer '{personal_data.full_name}'"
                        )
            
            # Date of birth validation
            if 'date_of_birth' in extracted_data and personal_data.date_of_birth:
                try:
                    extracted_dob = datetime.strptime(extracted_data['date_of_birth'], '%Y-%m-%d').date()
                    if extracted_dob != personal_data.date_of_birth:
                        validation_errors.append(
                            f"Date of birth mismatch: Document '{extracted_dob}' vs Customer '{personal_data.date_of_birth}'"
                        )
                except ValueError:
                    validation_warnings.append("Could not parse date of birth from document")
            
            # Nationality validation
            if 'nationality' in extracted_data and personal_data.nationality:
                if extracted_data['nationality'].lower() != personal_data.nationality.lower():
                    validation_warnings.append(
                        f"Nationality difference: Document '{extracted_data['nationality']}' vs Customer '{personal_data.nationality}'"
                    )
            
            # Document expiry validation
            if 'expiry_date' in extracted_data:
                try:
                    expiry_date = datetime.strptime(extracted_data['expiry_date'], '%Y-%m-%d').date()
                    if expiry_date < timezone.now().date():
                        validation_errors.append("Document has expired")
                    elif (expiry_date - timezone.now().date()).days < 90:
                        validation_warnings.append("Document expires within 90 days")
                except ValueError:
                    validation_warnings.append("Could not parse expiry date from document")
        
        # Update document validation status
        is_valid = len(validation_errors) == 0
        document.verification_details = {
            'validation_performed_at': timezone.now().isoformat(),
            'validation_errors': validation_errors,
            'validation_warnings': validation_warnings,
            'is_valid': is_valid
        }
        
        if is_valid:
            document.verification_status = 'verified'
        else:
            document.verification_status = 'rejected'
        
        document.save()
        
        # Create validation task record
        task = self._create_task(document, 'validation', {
            'validation_errors': validation_errors,
            'validation_warnings': validation_warnings
        })
        self._complete_task(task, {
            'is_valid': is_valid,
            'errors_count': len(validation_errors),
            'warnings_count': len(validation_warnings)
        })
        
        return {
            'document_id': document.id,
            'is_valid': is_valid,
            'validation_errors': validation_errors,
            'validation_warnings': validation_warnings
        }
    
    def _create_task(self, document: CustomerDocument, task_type: str, task_data: dict):
        """Create a new processing task"""
        return DocumentProcessingTask.objects.create(
            document=document,
            task_type=task_type,
            task_data=task_data
        )
    
    def _complete_task(self, task: DocumentProcessingTask, result_data: dict):
        """Mark task as completed with results"""
        task.status = 'completed'
        task.result_data = result_data
        task.completed_at = timezone.now()
        task.save()
    
    def _fail_task(self, task: DocumentProcessingTask, error_message: str):
        """Mark task as failed"""
        task.status = 'failed'
        task.error_message = error_message
        task.completed_at = timezone.now()
        task.save()
    
    def _process_ocr(self, document: CustomerDocument, task: DocumentProcessingTask):
        """Process OCR for document"""
        try:
            task.status = 'processing'
            task.started_at = timezone.now()
            task.save()
            
            # Perform OCR
            ocr_result = self.ocr_service.extract_text(document.file.path)
            
            # Update document with OCR results
            document.ocr_data = ocr_result.get('raw_text', {})
            document.extracted_data = ocr_result.get('structured_data', {})
            document.processed_at = timezone.now()
            document.save()
            
            # Complete task
            self._complete_task(task, {
                'confidence_score': ocr_result.get('confidence', 0),
                'processing_time': ocr_result.get('processing_time', 0),
                'text_blocks_found': len(ocr_result.get('raw_text', {}))
            })
            
            # Start validation after OCR
            self.validate_document(document)
            
        except Exception as e:
            logger.error(f"OCR processing failed for document {document.id}: {e}")
            self._fail_task(task, str(e))
            document.verification_status = 'requires_manual_review'
            document.save()
    
    def _process_forensic_analysis(self, document: CustomerDocument, task: DocumentProcessingTask):
        """Process forensic analysis for document"""
        try:
            task.status = 'processing'
            task.started_at = timezone.now()
            task.save()
            
            # Perform forensic analysis
            forensic_result = self.forensic_service.analyze_document(document.file.path)
            
            # Update document with forensic results
            document.forensic_analysis = forensic_result.get('analysis_details', {})
            document.authenticity_score = forensic_result.get('authenticity_score', 0)
            document.save()
            
            # Complete task
            self._complete_task(task, {
                'authenticity_score': forensic_result.get('authenticity_score', 0),
                'risk_indicators': forensic_result.get('risk_indicators', []),
                'analysis_time': forensic_result.get('analysis_time', 0)
            })
            
        except Exception as e:
            logger.error(f"Forensic analysis failed for document {document.id}: {e}")
            self._fail_task(task, str(e))
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, name1, name2).ratio()


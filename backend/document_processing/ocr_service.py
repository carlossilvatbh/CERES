"""
OCR Service for document text extraction
"""
import logging
import time
from typing import Dict, Any
import os

logger = logging.getLogger('ceres')

class OCRService:
    """
    Service for extracting text from documents using OCR
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png']
        
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from document file
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        start_time = time.time()
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Extract text based on file type
            if file_ext == '.pdf':
                result = self._extract_from_pdf(file_path)
            else:
                result = self._extract_from_image(file_path)
            
            processing_time = time.time() - start_time
            
            # Structure the result
            return {
                'raw_text': result.get('text', ''),
                'structured_data': self._structure_extracted_data(result.get('text', ''), file_ext),
                'confidence': result.get('confidence', 0),
                'processing_time': processing_time,
                'method': result.get('method', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {file_path}: {e}")
            return {
                'raw_text': '',
                'structured_data': {},
                'confidence': 0,
                'processing_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF file"""
        try:
            # Try using PyPDF2 first for text-based PDFs
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                if text.strip():
                    return {
                        'text': text,
                        'confidence': 0.95,
                        'method': 'pypdf2'
                    }
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed, falling back to OCR: {e}")
        
        # Fall back to OCR for scanned PDFs
        try:
            # Convert PDF to images and OCR each page
            from pdf2image import convert_from_path
            import pytesseract
            
            images = convert_from_path(file_path)
            full_text = ""
            total_confidence = 0
            
            for i, image in enumerate(images):
                # OCR the image
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                # Extract text and confidence
                page_text = " ".join([
                    word for word in ocr_data['text'] 
                    if word.strip()
                ])
                
                # Calculate average confidence for this page
                confidences = [
                    int(conf) for conf in ocr_data['conf'] 
                    if int(conf) > 0
                ]
                page_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                full_text += f"[Page {i+1}]\n{page_text}\n\n"
                total_confidence += page_confidence
            
            avg_confidence = total_confidence / len(images) if images else 0
            
            return {
                'text': full_text,
                'confidence': avg_confidence / 100,  # Convert to 0-1 scale
                'method': 'tesseract_pdf'
            }
            
        except Exception as e:
            logger.error(f"PDF OCR extraction failed: {e}")
            return {
                'text': '',
                'confidence': 0,
                'method': 'failed',
                'error': str(e)
            }
    
    def _extract_from_image(self, file_path: str) -> Dict[str, Any]:
        """Extract text from image file"""
        try:
            import pytesseract
            from PIL import Image
            
            # Open and preprocess image
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # OCR configuration for better accuracy
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?()[]{}"\'-/\\ '
            
            # Extract text with confidence data
            ocr_data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Combine text
            text = " ".join([
                word for word in ocr_data['text'] 
                if word.strip()
            ])
            
            # Calculate average confidence
            confidences = [
                int(conf) for conf in ocr_data['conf'] 
                if int(conf) > 0
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text,
                'confidence': avg_confidence / 100,  # Convert to 0-1 scale
                'method': 'tesseract_image'
            }
            
        except Exception as e:
            logger.error(f"Image OCR extraction failed: {e}")
            return {
                'text': '',
                'confidence': 0,
                'method': 'failed',
                'error': str(e)
            }
    
    def _structure_extracted_data(self, text: str, file_ext: str) -> Dict[str, Any]:
        """
        Structure extracted text into meaningful fields
        """
        if not text:
            return {}
        
        structured_data = {}
        text_lower = text.lower()
        
        # Extract common document fields using regex patterns
        import re
        
        # Name patterns
        name_patterns = [
            r'name[:\s]+([a-zA-Z\s]+)',
            r'full name[:\s]+([a-zA-Z\s]+)',
            r'given name[:\s]+([a-zA-Z\s]+)',
            r'surname[:\s]+([a-zA-Z\s]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                structured_data['name'] = match.group(1).strip().title()
                break
        
        # Date patterns
        date_patterns = [
            r'date of birth[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'dob[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'born[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                date_str = match.group(1)
                # Normalize date format
                try:
                    from datetime import datetime
                    # Try different date formats
                    for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            structured_data['date_of_birth'] = parsed_date.strftime('%Y-%m-%d')
                            break
                        except ValueError:
                            continue
                except:
                    pass
                break
        
        # Document number patterns
        doc_number_patterns = [
            r'passport no[:\s]+([A-Z0-9]+)',
            r'passport number[:\s]+([A-Z0-9]+)',
            r'document no[:\s]+([A-Z0-9]+)',
            r'id no[:\s]+([A-Z0-9]+)',
            r'number[:\s]+([A-Z0-9]+)'
        ]
        
        for pattern in doc_number_patterns:
            match = re.search(pattern, text_lower)
            if match:
                structured_data['document_number'] = match.group(1).strip().upper()
                break
        
        # Nationality patterns
        nationality_patterns = [
            r'nationality[:\s]+([a-zA-Z\s]+)',
            r'citizen of[:\s]+([a-zA-Z\s]+)',
            r'country[:\s]+([a-zA-Z\s]+)'
        ]
        
        for pattern in nationality_patterns:
            match = re.search(pattern, text_lower)
            if match:
                structured_data['nationality'] = match.group(1).strip().title()
                break
        
        # Expiry date patterns
        expiry_patterns = [
            r'expiry[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'expires[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'valid until[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        ]
        
        for pattern in expiry_patterns:
            match = re.search(pattern, text_lower)
            if match:
                date_str = match.group(1)
                try:
                    from datetime import datetime
                    for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            structured_data['expiry_date'] = parsed_date.strftime('%Y-%m-%d')
                            break
                        except ValueError:
                            continue
                except:
                    pass
                break
        
        # Gender patterns
        gender_patterns = [
            r'sex[:\s]+([MF])',
            r'gender[:\s]+([a-zA-Z]+)',
            r'\b(male|female)\b'
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text_lower)
            if match:
                gender = match.group(1).strip().lower()
                if gender in ['m', 'male']:
                    structured_data['gender'] = 'male'
                elif gender in ['f', 'female']:
                    structured_data['gender'] = 'female'
                break
        
        return structured_data


"""
Enhanced OCR Service with Advanced Image Preprocessing
Improved accuracy and error handling for document processing
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import io
import base64
from pathlib import Path
import json

logger = logging.getLogger('ceres.ocr')

@dataclass
class OCRResult:
    """OCR processing result"""
    text: str
    confidence: float
    language: str
    processing_time: float
    preprocessing_applied: List[str]
    word_confidences: List[Dict[str, Any]]
    bounding_boxes: List[Dict[str, Any]]
    errors: List[str]

class ImagePreprocessor:
    """
    Advanced image preprocessing for better OCR accuracy
    """
    
    @staticmethod
    def enhance_image_quality(image: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """
        Apply multiple enhancement techniques to improve OCR accuracy
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (enhanced_image, applied_techniques)
        """
        applied_techniques = []
        enhanced = image.copy()
        
        try:
            # Convert to grayscale if needed
            if len(enhanced.shape) == 3:
                enhanced = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
                applied_techniques.append('grayscale_conversion')
            
            # Noise reduction
            enhanced = cv2.medianBlur(enhanced, 3)
            applied_techniques.append('noise_reduction')
            
            # Contrast enhancement using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(enhanced)
            applied_techniques.append('contrast_enhancement')
            
            # Sharpening
            kernel = np.array([[-1, -1, -1],
                             [-1,  9, -1],
                             [-1, -1, -1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            applied_techniques.append('sharpening')
            
            # Morphological operations to clean up text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
            applied_techniques.append('morphological_cleanup')
            
            return enhanced, applied_techniques
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            return image, []
    
    @staticmethod
    def deskew_image(image: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Detect and correct image skew
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (deskewed_image, was_skewed)
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Hough line detection
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Calculate average angle
                angles = []
                for rho, theta in lines[:10]:  # Use first 10 lines
                    angle = theta * 180 / np.pi
                    if angle > 90:
                        angle = angle - 180
                    angles.append(angle)
                
                if angles:
                    avg_angle = np.mean(angles)
                    
                    # Only correct if skew is significant (> 0.5 degrees)
                    if abs(avg_angle) > 0.5:
                        # Rotate image
                        (h, w) = image.shape[:2]
                        center = (w // 2, h // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                        deskewed = cv2.warpAffine(image, rotation_matrix, (w, h),
                                                flags=cv2.INTER_CUBIC,
                                                borderMode=cv2.BORDER_REPLICATE)
                        return deskewed, True
            
            return image, False
            
        except Exception as e:
            logger.error(f"Deskewing failed: {e}")
            return image, False
    
    @staticmethod
    def remove_borders(image: np.ndarray) -> np.ndarray:
        """
        Remove borders and margins from document images
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Image with borders removed
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Threshold to binary
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find largest contour (should be the document)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Add small margin
                margin = 10
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(image.shape[1] - x, w + 2 * margin)
                h = min(image.shape[0] - y, h + 2 * margin)
                
                # Crop image
                return image[y:y+h, x:x+w]
            
            return image
            
        except Exception as e:
            logger.error(f"Border removal failed: {e}")
            return image
    
    @staticmethod
    def adaptive_threshold(image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for better text extraction
        
        Args:
            image: Input grayscale image
            
        Returns:
            Binary image with adaptive threshold
        """
        try:
            # Apply adaptive threshold
            adaptive_thresh = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return adaptive_thresh
            
        except Exception as e:
            logger.error(f"Adaptive thresholding failed: {e}")
            return image

class EnhancedOCRService:
    """
    Enhanced OCR service with advanced preprocessing and error handling
    """
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd or '/usr/bin/tesseract'
        self.preprocessor = ImagePreprocessor()
        
        # Configure Tesseract
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
    
    def process_document(self, image_data: bytes, language: str = 'eng+por', 
                        preprocessing: bool = True) -> OCRResult:
        """
        Process document with enhanced OCR
        
        Args:
            image_data: Image data as bytes
            language: Tesseract language codes (e.g., 'eng+por')
            preprocessing: Whether to apply image preprocessing
            
        Returns:
            OCRResult with extracted text and metadata
        """
        import time
        start_time = time.time()
        
        try:
            # Load image
            image = self._load_image_from_bytes(image_data)
            if image is None:
                return self._create_error_result("Failed to load image", start_time)
            
            # Apply preprocessing if enabled
            applied_techniques = []
            if preprocessing:
                image, applied_techniques = self._preprocess_image(image)
            
            # Perform OCR with multiple configurations
            ocr_results = self._perform_multi_config_ocr(image, language)
            
            # Select best result
            best_result = self._select_best_result(ocr_results)
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=best_result['text'],
                confidence=best_result['confidence'],
                language=language,
                processing_time=processing_time,
                preprocessing_applied=applied_techniques,
                word_confidences=best_result.get('word_confidences', []),
                bounding_boxes=best_result.get('bounding_boxes', []),
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return self._create_error_result(str(e), start_time)
    
    def _load_image_from_bytes(self, image_data: bytes) -> Optional[np.ndarray]:
        """Load image from bytes"""
        try:
            # Convert bytes to PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """Apply comprehensive image preprocessing"""
        applied_techniques = []
        
        try:
            # Remove borders
            image = self.preprocessor.remove_borders(image)
            applied_techniques.append('border_removal')
            
            # Deskew image
            image, was_skewed = self.preprocessor.deskew_image(image)
            if was_skewed:
                applied_techniques.append('deskewing')
            
            # Enhance image quality
            image, enhancement_techniques = self.preprocessor.enhance_image_quality(image)
            applied_techniques.extend(enhancement_techniques)
            
            return image, applied_techniques
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return image, applied_techniques
    
    def _perform_multi_config_ocr(self, image: np.ndarray, language: str) -> List[Dict[str, Any]]:
        """Perform OCR with multiple configurations"""
        results = []
        
        # Configuration 1: Default
        try:
            result = self._perform_ocr_with_config(image, language, '--psm 3')
            results.append(result)
        except Exception as e:
            logger.warning(f"OCR config 1 failed: {e}")
        
        # Configuration 2: Single text block
        try:
            result = self._perform_ocr_with_config(image, language, '--psm 6')
            results.append(result)
        except Exception as e:
            logger.warning(f"OCR config 2 failed: {e}")
        
        # Configuration 3: Single text line
        try:
            result = self._perform_ocr_with_config(image, language, '--psm 7')
            results.append(result)
        except Exception as e:
            logger.warning(f"OCR config 3 failed: {e}")
        
        # Configuration 4: With adaptive threshold
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            adaptive_image = self.preprocessor.adaptive_threshold(gray)
            result = self._perform_ocr_with_config(adaptive_image, language, '--psm 3')
            results.append(result)
        except Exception as e:
            logger.warning(f"OCR config 4 failed: {e}")
        
        return results
    
    def _perform_ocr_with_config(self, image: np.ndarray, language: str, config: str) -> Dict[str, Any]:
        """Perform OCR with specific configuration"""
        try:
            # Get text with confidence
            data = pytesseract.image_to_data(image, lang=language, config=config, output_type=pytesseract.Output.DICT)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language, config=config).strip()
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract word-level data
            word_confidences = []
            bounding_boxes = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:
                    word_confidences.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i])
                    })
                    
                    bounding_boxes.append({
                        'text': data['text'][i],
                        'x': int(data['left'][i]),
                        'y': int(data['top'][i]),
                        'width': int(data['width'][i]),
                        'height': int(data['height'][i])
                    })
            
            return {
                'text': text,
                'confidence': avg_confidence,
                'word_confidences': word_confidences,
                'bounding_boxes': bounding_boxes,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"OCR with config '{config}' failed: {e}")
            return {
                'text': '',
                'confidence': 0,
                'word_confidences': [],
                'bounding_boxes': [],
                'config': config,
                'error': str(e)
            }
    
    def _select_best_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select best OCR result based on confidence and text length"""
        if not results:
            return {
                'text': '',
                'confidence': 0,
                'word_confidences': [],
                'bounding_boxes': []
            }
        
        # Filter out results with errors
        valid_results = [r for r in results if 'error' not in r and r['text'].strip()]
        
        if not valid_results:
            # Return first result even if it has errors
            return results[0]
        
        # Score results based on confidence and text length
        scored_results = []
        for result in valid_results:
            text_length = len(result['text'].strip())
            confidence = result['confidence']
            
            # Score: weighted combination of confidence and text length
            score = (confidence * 0.7) + (min(text_length / 100, 1.0) * 30)
            
            scored_results.append((score, result))
        
        # Return result with highest score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return scored_results[0][1]
    
    def _create_error_result(self, error_message: str, start_time: float) -> OCRResult:
        """Create OCR result for error cases"""
        import time
        processing_time = time.time() - start_time
        
        return OCRResult(
            text='',
            confidence=0.0,
            language='',
            processing_time=processing_time,
            preprocessing_applied=[],
            word_confidences=[],
            bounding_boxes=[],
            errors=[error_message]
        )
    
    def extract_structured_data(self, ocr_result: OCRResult, document_type: str) -> Dict[str, Any]:
        """
        Extract structured data from OCR text based on document type
        
        Args:
            ocr_result: OCR processing result
            document_type: Type of document (passport, id_card, etc.)
            
        Returns:
            Structured data dictionary
        """
        try:
            if document_type == 'passport':
                return self._extract_passport_data(ocr_result.text)
            elif document_type == 'id_card':
                return self._extract_id_card_data(ocr_result.text)
            elif document_type == 'driver_license':
                return self._extract_driver_license_data(ocr_result.text)
            else:
                return self._extract_generic_data(ocr_result.text)
                
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            return {'error': str(e)}
    
    def _extract_passport_data(self, text: str) -> Dict[str, Any]:
        """Extract passport-specific data"""
        import re
        
        data = {}
        
        # Extract passport number (various formats)
        passport_patterns = [
            r'(?:Passport|PASSPORT|No\.?|Number)\s*:?\s*([A-Z0-9]{6,12})',
            r'([A-Z]{1,2}[0-9]{6,8})',
        ]
        
        for pattern in passport_patterns:
            match = re.search(pattern, text)
            if match:
                data['passport_number'] = match.group(1)
                break
        
        # Extract names
        name_patterns = [
            r'(?:Name|NOME|Given names?)\s*:?\s*([A-Z\s]+)',
            r'(?:Surname|SOBRENOME|Family name)\s*:?\s*([A-Z\s]+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                if 'name' not in data:
                    data['name'] = match.group(1).strip()
                else:
                    data['surname'] = match.group(1).strip()
        
        # Extract dates
        date_patterns = [
            r'(?:Date of birth|DOB|Nascimento)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            r'(?:Expiry|Validade|Valid until)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                if 'birth_date' not in data:
                    data['birth_date'] = match.group(1)
                else:
                    data['expiry_date'] = match.group(1)
        
        return data
    
    def _extract_id_card_data(self, text: str) -> Dict[str, Any]:
        """Extract ID card specific data"""
        # Similar implementation for ID cards
        return {'document_type': 'id_card', 'extracted_text': text}
    
    def _extract_driver_license_data(self, text: str) -> Dict[str, Any]:
        """Extract driver's license specific data"""
        # Similar implementation for driver's licenses
        return {'document_type': 'driver_license', 'extracted_text': text}
    
    def _extract_generic_data(self, text: str) -> Dict[str, Any]:
        """Extract generic data from any document"""
        import re
        
        data = {'document_type': 'generic'}
        
        # Extract potential dates
        date_pattern = r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}'
        dates = re.findall(date_pattern, text)
        if dates:
            data['dates'] = dates
        
        # Extract potential numbers (IDs, etc.)
        number_pattern = r'\b[A-Z0-9]{6,}\b'
        numbers = re.findall(number_pattern, text)
        if numbers:
            data['numbers'] = numbers
        
        # Extract potential names (capitalized words)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        names = re.findall(name_pattern, text)
        if names:
            data['potential_names'] = names
        
        return data


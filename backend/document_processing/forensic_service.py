"""
Forensic Analysis Service for document authenticity verification
"""
import logging
import time
from typing import Dict, Any
import os

logger = logging.getLogger('ceres')

class ForensicAnalysisService:
    """
    Service for analyzing document authenticity and detecting forgeries
    """
    
    def __init__(self):
        self.analysis_methods = [
            'metadata_analysis',
            'compression_analysis', 
            'pixel_analysis',
            'font_analysis',
            'structure_analysis'
        ]
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive forensic analysis on document
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing analysis results and authenticity score
        """
        start_time = time.time()
        
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            analysis_results = {}
            risk_indicators = []
            authenticity_scores = []
            
            # Perform different types of analysis
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png']:
                # Image-specific analysis
                analysis_results.update(self._analyze_image_metadata(file_path))
                analysis_results.update(self._analyze_image_compression(file_path))
                analysis_results.update(self._analyze_pixel_patterns(file_path))
                
            elif file_ext == '.pdf':
                # PDF-specific analysis
                analysis_results.update(self._analyze_pdf_metadata(file_path))
                analysis_results.update(self._analyze_pdf_structure(file_path))
            
            # Common analysis for all file types
            analysis_results.update(self._analyze_file_properties(file_path))
            
            # Calculate overall authenticity score
            authenticity_score = self._calculate_authenticity_score(analysis_results)
            
            # Identify risk indicators
            risk_indicators = self._identify_risk_indicators(analysis_results)
            
            analysis_time = time.time() - start_time
            
            return {
                'authenticity_score': authenticity_score,
                'analysis_details': analysis_results,
                'risk_indicators': risk_indicators,
                'analysis_time': analysis_time,
                'analysis_methods': self.analysis_methods
            }
            
        except Exception as e:
            logger.error(f"Forensic analysis failed for {file_path}: {e}")
            return {
                'authenticity_score': 0,
                'analysis_details': {'error': str(e)},
                'risk_indicators': ['Analysis failed'],
                'analysis_time': time.time() - start_time
            }
    
    def _analyze_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Analyze image metadata for signs of manipulation"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            image = Image.open(file_path)
            metadata = {}
            
            # Extract EXIF data
            exif_data = image.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    metadata[tag] = str(value)
            
            # Check for suspicious metadata patterns
            suspicious_indicators = []
            
            # Check for missing expected metadata
            expected_fields = ['DateTime', 'Software', 'Make', 'Model']
            missing_fields = [field for field in expected_fields if field not in metadata]
            
            if len(missing_fields) > 2:
                suspicious_indicators.append('Missing expected metadata fields')
            
            # Check for editing software indicators
            software_field = metadata.get('Software', '').lower()
            editing_software = ['photoshop', 'gimp', 'paint.net', 'canva', 'pixlr']
            
            if any(editor in software_field for editor in editing_software):
                suspicious_indicators.append('Image editing software detected')
            
            # Check for inconsistent timestamps
            if 'DateTime' in metadata and 'DateTimeOriginal' in metadata:
                if metadata['DateTime'] != metadata['DateTimeOriginal']:
                    suspicious_indicators.append('Inconsistent timestamp metadata')
            
            return {
                'metadata_analysis': {
                    'metadata_fields': len(metadata),
                    'suspicious_indicators': suspicious_indicators,
                    'metadata_score': max(0, 100 - len(suspicious_indicators) * 20),
                    'raw_metadata': metadata
                }
            }
            
        except Exception as e:
            logger.warning(f"Metadata analysis failed: {e}")
            return {
                'metadata_analysis': {
                    'error': str(e),
                    'metadata_score': 50  # Neutral score when analysis fails
                }
            }
    
    def _analyze_image_compression(self, file_path: str) -> Dict[str, Any]:
        """Analyze compression artifacts and quality"""
        try:
            from PIL import Image
            import numpy as np
            
            image = Image.open(file_path)
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Calculate compression quality indicators
            compression_indicators = []
            
            # Check for JPEG compression artifacts
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                # Look for blocking artifacts (8x8 DCT blocks)
                if len(img_array.shape) >= 2:
                    # Simple blocking artifact detection
                    height, width = img_array.shape[:2]
                    
                    # Check for regular patterns that might indicate compression
                    block_variance = []
                    for y in range(0, height - 8, 8):
                        for x in range(0, width - 8, 8):
                            if len(img_array.shape) == 3:
                                block = img_array[y:y+8, x:x+8, 0]  # Use first channel
                            else:
                                block = img_array[y:y+8, x:x+8]
                            block_variance.append(np.var(block))
                    
                    if block_variance:
                        avg_variance = np.mean(block_variance)
                        if avg_variance < 10:  # Very low variance might indicate heavy compression
                            compression_indicators.append('Heavy compression artifacts detected')
            
            # Check for unusual compression patterns
            file_size = os.path.getsize(file_path)
            pixel_count = img_array.size
            
            if pixel_count > 0:
                compression_ratio = file_size / pixel_count
                
                if compression_ratio < 0.1:  # Very high compression
                    compression_indicators.append('Unusually high compression ratio')
                elif compression_ratio > 3:  # Very low compression
                    compression_indicators.append('Unusually low compression ratio')
            
            compression_score = max(0, 100 - len(compression_indicators) * 25)
            
            return {
                'compression_analysis': {
                    'compression_indicators': compression_indicators,
                    'compression_score': compression_score,
                    'file_size': file_size,
                    'compression_ratio': compression_ratio if 'compression_ratio' in locals() else 0
                }
            }
            
        except Exception as e:
            logger.warning(f"Compression analysis failed: {e}")
            return {
                'compression_analysis': {
                    'error': str(e),
                    'compression_score': 50
                }
            }
    
    def _analyze_pixel_patterns(self, file_path: str) -> Dict[str, Any]:
        """Analyze pixel patterns for signs of manipulation"""
        try:
            from PIL import Image
            import numpy as np
            
            image = Image.open(file_path)
            img_array = np.array(image)
            
            pattern_indicators = []
            
            # Check for cloning/copy-paste patterns
            if len(img_array.shape) >= 2:
                # Simple duplicate region detection
                height, width = img_array.shape[:2]
                
                # Sample small regions and look for exact duplicates
                sample_size = min(32, height // 4, width // 4)
                samples = []
                
                for y in range(0, height - sample_size, sample_size):
                    for x in range(0, width - sample_size, sample_size):
                        if len(img_array.shape) == 3:
                            sample = img_array[y:y+sample_size, x:x+sample_size, :]
                        else:
                            sample = img_array[y:y+sample_size, x:x+sample_size]
                        
                        # Convert to hashable format for comparison
                        sample_hash = hash(sample.tobytes())
                        samples.append(sample_hash)
                
                # Check for duplicate samples
                unique_samples = len(set(samples))
                total_samples = len(samples)
                
                if total_samples > 0:
                    uniqueness_ratio = unique_samples / total_samples
                    if uniqueness_ratio < 0.8:  # Less than 80% unique samples
                        pattern_indicators.append('Potential cloning/duplication detected')
            
            # Check for unnatural uniformity
            if len(img_array.shape) >= 2:
                # Calculate local variance
                if len(img_array.shape) == 3:
                    gray = np.mean(img_array, axis=2)
                else:
                    gray = img_array
                
                local_variance = np.var(gray)
                
                if local_variance < 100:  # Very low variance
                    pattern_indicators.append('Unnaturally uniform regions detected')
            
            pattern_score = max(0, 100 - len(pattern_indicators) * 30)
            
            return {
                'pixel_analysis': {
                    'pattern_indicators': pattern_indicators,
                    'pattern_score': pattern_score,
                    'local_variance': local_variance if 'local_variance' in locals() else 0
                }
            }
            
        except Exception as e:
            logger.warning(f"Pixel pattern analysis failed: {e}")
            return {
                'pixel_analysis': {
                    'error': str(e),
                    'pattern_score': 50
                }
            }
    
    def _analyze_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Analyze PDF metadata for authenticity indicators"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                suspicious_indicators = []
                
                if metadata:
                    # Check creation and modification dates
                    creation_date = metadata.get('/CreationDate')
                    mod_date = metadata.get('/ModDate')
                    
                    if creation_date and mod_date:
                        if creation_date != mod_date:
                            suspicious_indicators.append('Document has been modified after creation')
                    
                    # Check for suspicious creator/producer
                    creator = str(metadata.get('/Creator', '')).lower()
                    producer = str(metadata.get('/Producer', '')).lower()
                    
                    suspicious_creators = ['fake', 'forge', 'generator', 'template']
                    if any(term in creator for term in suspicious_creators):
                        suspicious_indicators.append('Suspicious creator software detected')
                    
                    if any(term in producer for term in suspicious_creators):
                        suspicious_indicators.append('Suspicious producer software detected')
                
                metadata_score = max(0, 100 - len(suspicious_indicators) * 25)
                
                return {
                    'pdf_metadata_analysis': {
                        'suspicious_indicators': suspicious_indicators,
                        'metadata_score': metadata_score,
                        'has_metadata': metadata is not None,
                        'metadata_fields': len(metadata) if metadata else 0
                    }
                }
                
        except Exception as e:
            logger.warning(f"PDF metadata analysis failed: {e}")
            return {
                'pdf_metadata_analysis': {
                    'error': str(e),
                    'metadata_score': 50
                }
            }
    
    def _analyze_pdf_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze PDF structure for signs of manipulation"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                structure_indicators = []
                
                # Check number of pages
                num_pages = len(pdf_reader.pages)
                if num_pages > 10:  # Unusually long for typical ID documents
                    structure_indicators.append('Unusually high page count for document type')
                
                # Check for form fields (might indicate template usage)
                if hasattr(pdf_reader, 'get_form_text_fields'):
                    try:
                        form_fields = pdf_reader.get_form_text_fields()
                        if form_fields:
                            structure_indicators.append('Form fields detected - possible template')
                    except:
                        pass
                
                # Check for annotations
                for page in pdf_reader.pages:
                    if '/Annots' in page:
                        structure_indicators.append('Annotations detected - possible modifications')
                        break
                
                structure_score = max(0, 100 - len(structure_indicators) * 20)
                
                return {
                    'pdf_structure_analysis': {
                        'structure_indicators': structure_indicators,
                        'structure_score': structure_score,
                        'page_count': num_pages
                    }
                }
                
        except Exception as e:
            logger.warning(f"PDF structure analysis failed: {e}")
            return {
                'pdf_structure_analysis': {
                    'error': str(e),
                    'structure_score': 50
                }
            }
    
    def _analyze_file_properties(self, file_path: str) -> Dict[str, Any]:
        """Analyze general file properties"""
        try:
            import os
            from datetime import datetime
            
            stat = os.stat(file_path)
            
            property_indicators = []
            
            # Check file timestamps
            creation_time = datetime.fromtimestamp(stat.st_ctime)
            modification_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Check if file was created and modified at exactly the same time
            time_diff = abs((creation_time - modification_time).total_seconds())
            if time_diff < 1:  # Less than 1 second difference
                property_indicators.append('Suspicious timestamp synchronization')
            
            # Check file size reasonableness
            file_size = stat.st_size
            if file_size < 1024:  # Very small file
                property_indicators.append('Unusually small file size')
            elif file_size > 50 * 1024 * 1024:  # Very large file (>50MB)
                property_indicators.append('Unusually large file size')
            
            property_score = max(0, 100 - len(property_indicators) * 25)
            
            return {
                'file_properties_analysis': {
                    'property_indicators': property_indicators,
                    'property_score': property_score,
                    'file_size': file_size,
                    'creation_time': creation_time.isoformat(),
                    'modification_time': modification_time.isoformat()
                }
            }
            
        except Exception as e:
            logger.warning(f"File properties analysis failed: {e}")
            return {
                'file_properties_analysis': {
                    'error': str(e),
                    'property_score': 50
                }
            }
    
    def _calculate_authenticity_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall authenticity score from analysis results"""
        scores = []
        
        # Extract individual scores
        for analysis_type, results in analysis_results.items():
            if isinstance(results, dict):
                for key, value in results.items():
                    if key.endswith('_score') and isinstance(value, (int, float)):
                        scores.append(value)
        
        if not scores:
            return 50.0  # Neutral score if no analysis completed
        
        # Calculate weighted average
        return sum(scores) / len(scores)
    
    def _identify_risk_indicators(self, analysis_results: Dict[str, Any]) -> list:
        """Identify all risk indicators from analysis results"""
        risk_indicators = []
        
        for analysis_type, results in analysis_results.items():
            if isinstance(results, dict):
                # Look for indicator lists
                for key, value in results.items():
                    if 'indicator' in key and isinstance(value, list):
                        risk_indicators.extend(value)
        
        return list(set(risk_indicators))  # Remove duplicates


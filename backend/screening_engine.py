"""
Global screening engine for CERES
Supports multiple international sanctions lists and PEP databases
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from fuzzywuzzy import fuzz, process
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

@dataclass
class ScreeningMatch:
    """Represents a screening match result"""
    source: str
    matched_name: str
    match_score: float
    entity_type: str
    list_type: str
    raw_data: Dict[str, Any]
    screening_date: datetime
    
class ScreeningSource(ABC):
    """Abstract base class for screening data sources"""
    
    @abstractmethod
    async def search(self, query: str, entity_type: str = 'individual') -> List[ScreeningMatch]:
        """Search for matches in this source"""
        pass
    
    @abstractmethod
    async def update_data(self) -> bool:
        """Update the local cache of this source's data"""
        pass
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the screening source"""
        pass

class OFACScreeningSource(ScreeningSource):
    """OFAC (Office of Foreign Assets Control) screening source"""
    
    def __init__(self):
        self.base_url = "https://www.treasury.gov/ofac/downloads/"
        self.data_cache = {}
        self.last_update = None
    
    @property
    def source_name(self) -> str:
        return "OFAC"
    
    async def search(self, query: str, entity_type: str = 'individual') -> List[ScreeningMatch]:
        """Search OFAC sanctions list"""
        matches = []
        
        # Simulate OFAC search with fuzzy matching
        # In production, this would query the actual OFAC API or local database
        test_entries = [
            {"name": "John Doe", "type": "individual", "list": "SDN"},
            {"name": "Jane Smith", "type": "individual", "list": "SDN"},
            {"name": "ACME Corporation", "type": "entity", "list": "SDN"},
        ]
        
        for entry in test_entries:
            if entity_type == 'individual' and entry['type'] != 'individual':
                continue
            if entity_type == 'entity' and entry['type'] != 'entity':
                continue
                
            score = fuzz.ratio(query.lower(), entry['name'].lower())
            if score >= 80:  # Threshold for potential match
                match = ScreeningMatch(
                    source=self.source_name,
                    matched_name=entry['name'],
                    match_score=score / 100.0,
                    entity_type=entry['type'],
                    list_type=entry['list'],
                    raw_data=entry,
                    screening_date=datetime.now()
                )
                matches.append(match)
        
        return matches
    
    async def update_data(self) -> bool:
        """Update OFAC data cache"""
        try:
            # In production, this would download and parse OFAC XML files
            self.last_update = datetime.now()
            logger.info(f"Updated {self.source_name} data cache")
            return True
        except Exception as e:
            logger.error(f"Failed to update {self.source_name} data: {e}")
            return False

class UNScreeningSource(ScreeningSource):
    """UN Consolidated List screening source"""
    
    def __init__(self):
        self.base_url = "https://scsanctions.un.org/resources/xml/"
        self.data_cache = {}
        self.last_update = None
    
    @property
    def source_name(self) -> str:
        return "UN_CONSOLIDATED"
    
    async def search(self, query: str, entity_type: str = 'individual') -> List[ScreeningMatch]:
        """Search UN Consolidated List"""
        matches = []
        
        # Simulate UN search
        test_entries = [
            {"name": "Ahmed Hassan", "type": "individual", "list": "Al-Qaida"},
            {"name": "Global Trading LLC", "type": "entity", "list": "Taliban"},
        ]
        
        for entry in test_entries:
            if entity_type == 'individual' and entry['type'] != 'individual':
                continue
            if entity_type == 'entity' and entry['type'] != 'entity':
                continue
                
            score = fuzz.ratio(query.lower(), entry['name'].lower())
            if score >= 80:
                match = ScreeningMatch(
                    source=self.source_name,
                    matched_name=entry['name'],
                    match_score=score / 100.0,
                    entity_type=entry['type'],
                    list_type=entry['list'],
                    raw_data=entry,
                    screening_date=datetime.now()
                )
                matches.append(match)
        
        return matches
    
    async def update_data(self) -> bool:
        """Update UN data cache"""
        try:
            self.last_update = datetime.now()
            logger.info(f"Updated {self.source_name} data cache")
            return True
        except Exception as e:
            logger.error(f"Failed to update {self.source_name} data: {e}")
            return False

class EUScreeningSource(ScreeningSource):
    """EU Financial Sanctions screening source"""
    
    def __init__(self):
        self.base_url = "https://webgate.ec.europa.eu/europeaid/fsd/fsf/"
        self.data_cache = {}
        self.last_update = None
    
    @property
    def source_name(self) -> str:
        return "EU_SANCTIONS"
    
    async def search(self, query: str, entity_type: str = 'individual') -> List[ScreeningMatch]:
        """Search EU sanctions list"""
        matches = []
        
        # Simulate EU search
        test_entries = [
            {"name": "Vladimir Petrov", "type": "individual", "list": "EU_SANCTIONS"},
            {"name": "Eastern Holdings", "type": "entity", "list": "EU_SANCTIONS"},
        ]
        
        for entry in test_entries:
            if entity_type == 'individual' and entry['type'] != 'individual':
                continue
            if entity_type == 'entity' and entry['type'] != 'entity':
                continue
                
            score = fuzz.ratio(query.lower(), entry['name'].lower())
            if score >= 80:
                match = ScreeningMatch(
                    source=self.source_name,
                    matched_name=entry['name'],
                    match_score=score / 100.0,
                    entity_type=entry['type'],
                    list_type=entry['list'],
                    raw_data=entry,
                    screening_date=datetime.now()
                )
                matches.append(match)
        
        return matches
    
    async def update_data(self) -> bool:
        """Update EU data cache"""
        try:
            self.last_update = datetime.now()
            logger.info(f"Updated {self.source_name} data cache")
            return True
        except Exception as e:
            logger.error(f"Failed to update {self.source_name} data: {e}")
            return False

class PEPScreeningSource(ScreeningSource):
    """Politically Exposed Persons screening source"""
    
    def __init__(self):
        self.base_url = "https://opensanctions.org/api/"
        self.data_cache = {}
        self.last_update = None
    
    @property
    def source_name(self) -> str:
        return "PEP_DATABASE"
    
    async def search(self, query: str, entity_type: str = 'individual') -> List[ScreeningMatch]:
        """Search PEP database"""
        matches = []
        
        # Only search for individuals in PEP database
        if entity_type != 'individual':
            return matches
        
        # Simulate PEP search
        test_entries = [
            {"name": "Maria Rodriguez", "type": "individual", "list": "PEP", "position": "Minister of Finance"},
            {"name": "Robert Johnson", "type": "individual", "list": "PEP", "position": "Central Bank Governor"},
        ]
        
        for entry in test_entries:
            score = fuzz.ratio(query.lower(), entry['name'].lower())
            if score >= 80:
                match = ScreeningMatch(
                    source=self.source_name,
                    matched_name=entry['name'],
                    match_score=score / 100.0,
                    entity_type=entry['type'],
                    list_type=entry['list'],
                    raw_data=entry,
                    screening_date=datetime.now()
                )
                matches.append(match)
        
        return matches
    
    async def update_data(self) -> bool:
        """Update PEP data cache"""
        try:
            self.last_update = datetime.now()
            logger.info(f"Updated {self.source_name} data cache")
            return True
        except Exception as e:
            logger.error(f"Failed to update {self.source_name} data: {e}")
            return False

class GlobalScreeningEngine:
    """
    Main screening engine that coordinates multiple sources
    """
    
    def __init__(self):
        self.sources = {
            'OFAC': OFACScreeningSource(),
            'UN': UNScreeningSource(),
            'EU': EUScreeningSource(),
            'PEP': PEPScreeningSource(),
        }
        self.enabled_sources = set(self.sources.keys())
        self.match_threshold = 0.8  # 80% similarity threshold
    
    def enable_source(self, source_name: str):
        """Enable a specific screening source"""
        if source_name in self.sources:
            self.enabled_sources.add(source_name)
    
    def disable_source(self, source_name: str):
        """Disable a specific screening source"""
        self.enabled_sources.discard(source_name)
    
    async def screen_individual(self, 
                              first_name: str, 
                              last_name: str, 
                              date_of_birth: Optional[str] = None,
                              nationality: Optional[str] = None) -> List[ScreeningMatch]:
        """
        Screen an individual against all enabled sources
        """
        full_name = f"{first_name} {last_name}".strip()
        all_matches = []
        
        # Search all enabled sources concurrently
        tasks = []
        for source_name in self.enabled_sources:
            source = self.sources[source_name]
            task = source.search(full_name, entity_type='individual')
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Screening error: {result}")
                    continue
                all_matches.extend(result)
        
        # Filter by threshold and deduplicate
        filtered_matches = [
            match for match in all_matches 
            if match.match_score >= self.match_threshold
        ]
        
        # Sort by match score (highest first)
        filtered_matches.sort(key=lambda x: x.match_score, reverse=True)
        
        return filtered_matches
    
    async def screen_entity(self, 
                           entity_name: str,
                           entity_type: str = 'corporation',
                           country: Optional[str] = None) -> List[ScreeningMatch]:
        """
        Screen a legal entity against all enabled sources
        """
        all_matches = []
        
        # Search all enabled sources concurrently
        tasks = []
        for source_name in self.enabled_sources:
            source = self.sources[source_name]
            task = source.search(entity_name, entity_type='entity')
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Screening error: {result}")
                    continue
                all_matches.extend(result)
        
        # Filter by threshold and deduplicate
        filtered_matches = [
            match for match in all_matches 
            if match.match_score >= self.match_threshold
        ]
        
        # Sort by match score (highest first)
        filtered_matches.sort(key=lambda x: x.match_score, reverse=True)
        
        return filtered_matches
    
    async def update_all_sources(self) -> Dict[str, bool]:
        """
        Update data for all sources
        """
        results = {}
        
        tasks = []
        source_names = []
        for source_name, source in self.sources.items():
            tasks.append(source.update_data())
            source_names.append(source_name)
        
        if tasks:
            update_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(update_results):
                source_name = source_names[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to update {source_name}: {result}")
                    results[source_name] = False
                else:
                    results[source_name] = result
        
        return results
    
    def get_source_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all sources
        """
        status = {}
        for source_name, source in self.sources.items():
            status[source_name] = {
                'enabled': source_name in self.enabled_sources,
                'last_update': getattr(source, 'last_update', None),
                'source_name': source.source_name
            }
        return status

# Global instance
screening_engine = GlobalScreeningEngine()


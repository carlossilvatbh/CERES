"""
OpenSanctions PEP Screening Source Implementation
Politically Exposed Persons database from OpenSanctions.org
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from fuzzywuzzy import fuzz
import asyncio
import aiohttp
import json

logger = logging.getLogger('ceres.screening.opensanctions')

@dataclass
class PEPEntity:
    """PEP entity data structure"""
    id: str
    name: str
    entity_type: str
    schema: str
    datasets: List[str]
    properties: Dict[str, Any]
    aliases: List[str]
    addresses: List[Dict[str, str]]
    identifiers: List[Dict[str, str]]
    nationalities: List[str]
    birth_date: str
    birth_place: str
    political_positions: List[str]
    family_relations: List[Dict[str, str]]

class OpenSanctionsSource:
    """
    OpenSanctions PEP Screening Source
    Uses OpenSanctions.org API for PEP and sanctions data
    """
    
    # OpenSanctions API URLs
    OPENSANCTIONS_API_BASE = "https://api.opensanctions.org"
    OPENSANCTIONS_SEARCH_URL = f"{OPENSANCTIONS_API_BASE}/search/default"
    OPENSANCTIONS_ENTITY_URL = f"{OPENSANCTIONS_API_BASE}/entities"
    
    # Dataset filters
    PEP_DATASETS = [
        'pep',
        'us_ofac_sdn',
        'un_sc_sanctions',
        'eu_fsf',
        'gb_hmt_sanctions',
        'ca_dfatd_sema_sanctions',
        'au_dfat_sanctions'
    ]
    
    def __init__(self, api_key: Optional[str] = None, cache_duration_hours: int = 24):
        self.api_key = api_key
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.entities: Dict[str, PEPEntity] = {}
        self.last_updated: Optional[datetime] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        headers = {'User-Agent': 'CERES-Compliance-System/1.0'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300),  # 5 minutes timeout
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def update_data(self, force_refresh: bool = False) -> bool:
        """
        Update PEP data from OpenSanctions
        Note: This is a search-based API, so we don't pre-load all data
        
        Args:
            force_refresh: Force refresh (not applicable for search API)
            
        Returns:
            bool: Always True for search-based API
        """
        try:
            # For search-based APIs, we don't pre-load data
            # Instead, we verify API connectivity
            test_response = await self._test_api_connectivity()
            
            if test_response:
                self.last_updated = datetime.now()
                logger.info("OpenSanctions API connectivity verified")
                return True
            else:
                logger.error("OpenSanctions API connectivity test failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify OpenSanctions API: {e}")
            return False
    
    async def _test_api_connectivity(self) -> bool:
        """Test API connectivity with a simple search"""
        try:
            params = {
                'q': 'test',
                'limit': 1,
                'datasets': 'pep'
            }
            
            async with self.session.get(self.OPENSANCTIONS_SEARCH_URL, params=params) as response:
                return response.status == 200
                
        except Exception as e:
            logger.warning(f"API connectivity test failed: {e}")
            return False
    
    async def search(self, query: str, threshold: int = 80) -> List[Dict[str, Any]]:
        """
        Search OpenSanctions for matches
        
        Args:
            query: Search query (name)
            threshold: Minimum fuzzy match score (0-100)
            
        Returns:
            List of matching entities with confidence scores
        """
        try:
            matches = []
            
            # Search across different datasets
            for dataset in self.PEP_DATASETS:
                dataset_matches = await self._search_dataset(query, dataset, threshold)
                matches.extend(dataset_matches)
            
            # Remove duplicates based on entity ID
            seen_ids = set()
            unique_matches = []
            
            for match in matches:
                entity_id = match.get('entity_id')
                if entity_id not in seen_ids:
                    seen_ids.add(entity_id)
                    unique_matches.append(match)
            
            # Sort by confidence score (highest first)
            unique_matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info(f"OpenSanctions search for '{query}' returned {len(unique_matches)} unique matches")
            return unique_matches
            
        except Exception as e:
            logger.error(f"OpenSanctions search failed: {e}")
            return []
    
    async def _search_dataset(self, query: str, dataset: str, threshold: int) -> List[Dict[str, Any]]:
        """Search specific dataset"""
        try:
            params = {
                'q': query,
                'limit': 50,  # Limit per dataset
                'datasets': dataset
            }
            
            async with self.session.get(self.OPENSANCTIONS_SEARCH_URL, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Search failed for dataset {dataset}: HTTP {response.status}")
                    return []
                
                data = await response.json()
                
            matches = []
            results = data.get('results', [])
            
            for result in results:
                match = await self._process_search_result(result, query, dataset, threshold)
                if match:
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.warning(f"Failed to search dataset {dataset}: {e}")
            return []
    
    async def _process_search_result(self, result: Dict, query: str, dataset: str, threshold: int) -> Optional[Dict[str, Any]]:
        """Process individual search result"""
        try:
            entity_id = result.get('id', '')
            if not entity_id:
                return None
            
            # Get entity details
            entity_details = await self._get_entity_details(entity_id)
            if not entity_details:
                return None
            
            # Calculate confidence score
            name = entity_details.get('properties', {}).get('name', [''])[0]
            if not name:
                return None
            
            confidence = fuzz.ratio(query.lower(), name.lower())
            
            # Check aliases for better match
            aliases = entity_details.get('properties', {}).get('alias', [])
            for alias in aliases:
                alias_score = fuzz.ratio(query.lower(), alias.lower())
                confidence = max(confidence, alias_score)
            
            if confidence < threshold:
                return None
            
            # Extract entity information
            properties = entity_details.get('properties', {})
            
            # Get addresses
            addresses = []
            address_data = properties.get('address', [])
            for addr in address_data:
                if isinstance(addr, str):
                    addresses.append({'full_address': addr})
                elif isinstance(addr, dict):
                    addresses.append(addr)
            
            # Get identifiers
            identifiers = []
            passport_numbers = properties.get('passportNumber', [])
            for passport in passport_numbers:
                identifiers.append({'type': 'passport', 'number': passport})
            
            national_ids = properties.get('nationalIdNumber', [])
            for national_id in national_ids:
                identifiers.append({'type': 'national_id', 'number': national_id})
            
            # Get political positions
            positions = properties.get('position', [])
            
            # Get family relations
            family_relations = []
            # This would require additional API calls to get related entities
            
            match = {
                'entity_id': entity_id,
                'name': name,
                'matched_name': name,  # Could be improved with alias matching
                'confidence': confidence,
                'entity_type': entity_details.get('schema', 'Person'),
                'programs': [dataset],
                'list_type': 'OPENSANCTIONS',
                'dataset': dataset,
                'addresses': addresses,
                'identifiers': identifiers,
                'aliases': aliases,
                'nationalities': properties.get('nationality', []),
                'birth_date': properties.get('birthDate', [''])[0],
                'birth_place': properties.get('birthPlace', [''])[0],
                'political_positions': positions,
                'family_relations': family_relations,
                'properties': properties,
                'match_type': 'fuzzy',
                'source': 'OpenSanctions'
            }
            
            return match
            
        except Exception as e:
            logger.warning(f"Failed to process search result: {e}")
            return None
    
    async def _get_entity_details(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed entity information"""
        try:
            url = f"{self.OPENSANCTIONS_ENTITY_URL}/{entity_id}"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                return await response.json()
                
        except Exception as e:
            logger.warning(f"Failed to get entity details for {entity_id}: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid (not applicable for search API)"""
        return True  # Search API doesn't use cache
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about OpenSanctions API"""
        return {
            'api_status': 'connected' if self.last_updated else 'disconnected',
            'last_verified': self.last_updated.isoformat() if self.last_updated else None,
            'supported_datasets': self.PEP_DATASETS,
            'api_key_configured': bool(self.api_key)
        }

# Example usage
async def test_opensanctions_source():
    """Test OpenSanctions screening source"""
    async with OpenSanctionsSource() as opensanctions:
        # Update/verify API
        verified = await opensanctions.update_data()
        print(f"API verified: {verified}")
        
        # Get statistics
        stats = opensanctions.get_statistics()
        print(f"Statistics: {stats}")
        
        # Search for matches
        matches = await opensanctions.search("Vladimir Putin")
        print(f"Matches for 'Vladimir Putin': {len(matches)}")
        
        for match in matches[:3]:  # Show top 3 matches
            print(f"- {match['name']} ({match['confidence']}%) - {match['dataset']}")

if __name__ == "__main__":
    asyncio.run(test_opensanctions_source())


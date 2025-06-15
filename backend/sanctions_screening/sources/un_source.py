"""
UN Consolidated Screening Source Implementation
United Nations Security Council Consolidated List
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

logger = logging.getLogger('ceres.screening.un')

@dataclass
class UNEntity:
    """UN entity data structure"""
    dataid: str
    name: str
    entity_type: str
    list_type: str
    un_list_type: str
    reference_number: str
    listed_on: str
    comments: str
    aliases: List[str]
    addresses: List[Dict[str, str]]
    identifiers: List[Dict[str, str]]
    nationalities: List[str]

class UNScreeningSource:
    """
    UN Consolidated Screening Source
    Uses UN Security Council Consolidated List API
    """
    
    # UN API URLs
    UN_API_BASE = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
    UN_API_JSON = "https://scsanctions.un.org/resources/xml/en/consolidated.json"
    
    def __init__(self, cache_duration_hours: int = 24):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.entities: Dict[str, UNEntity] = {}
        self.last_updated: Optional[datetime] = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300),  # 5 minutes timeout
            headers={'User-Agent': 'CERES-Compliance-System/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def update_data(self, force_refresh: bool = False) -> bool:
        """
        Update UN data from official API
        
        Args:
            force_refresh: Force download even if cache is valid
            
        Returns:
            bool: True if data was updated, False if using cached data
        """
        try:
            # Check if update is needed
            if not force_refresh and self._is_cache_valid():
                logger.info("UN data cache is valid, skipping update")
                return False
            
            logger.info("Updating UN data from official API")
            
            # Try JSON API first (faster), fallback to XML
            entities = await self._download_json_data()
            
            if not entities:
                logger.info("JSON API failed, trying XML API")
                entities = await self._download_xml_data()
            
            if entities:
                self.entities = entities
                self.last_updated = datetime.now()
                logger.info(f"UN data updated successfully: {len(self.entities)} entities")
                return True
            else:
                logger.error("No UN data could be loaded")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update UN data: {e}")
            return False
    
    async def _download_json_data(self) -> Dict[str, UNEntity]:
        """Download and parse UN JSON data"""
        try:
            async with self.session.get(self.UN_API_JSON) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status} for UN JSON API")
                
                data = await response.json()
                
            return self._parse_json_data(data)
            
        except Exception as e:
            logger.warning(f"Failed to download UN JSON data: {e}")
            return {}
    
    async def _download_xml_data(self) -> Dict[str, UNEntity]:
        """Download and parse UN XML data"""
        try:
            import xml.etree.ElementTree as ET
            
            async with self.session.get(self.UN_API_BASE) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status} for UN XML API")
                
                xml_content = await response.text()
                
            root = ET.fromstring(xml_content)
            return self._parse_xml_data(root)
            
        except Exception as e:
            logger.warning(f"Failed to download UN XML data: {e}")
            return {}
    
    def _parse_json_data(self, data: Dict) -> Dict[str, UNEntity]:
        """Parse UN JSON data"""
        entities = {}
        
        try:
            # Parse individuals
            individuals = data.get('CONSOLIDATED_LIST', {}).get('INDIVIDUALS', {}).get('INDIVIDUAL', [])
            if isinstance(individuals, dict):
                individuals = [individuals]
            
            for individual in individuals:
                entity = self._parse_individual_json(individual, 'Individual')
                if entity:
                    entities[entity.dataid] = entity
            
            # Parse entities
            entity_list = data.get('CONSOLIDATED_LIST', {}).get('ENTITIES', {}).get('ENTITY', [])
            if isinstance(entity_list, dict):
                entity_list = [entity_list]
            
            for entity_data in entity_list:
                entity = self._parse_entity_json(entity_data, 'Entity')
                if entity:
                    entities[entity.dataid] = entity
            
            logger.info(f"Parsed {len(entities)} UN entities from JSON")
            return entities
            
        except Exception as e:
            logger.error(f"Failed to parse UN JSON data: {e}")
            return {}
    
    def _parse_individual_json(self, data: Dict, entity_type: str) -> Optional[UNEntity]:
        """Parse individual from JSON data"""
        try:
            dataid = data.get('@dataid', '')
            if not dataid:
                return None
            
            # Build name
            first_name = data.get('FIRST_NAME', '')
            second_name = data.get('SECOND_NAME', '')
            third_name = data.get('THIRD_NAME', '')
            fourth_name = data.get('FOURTH_NAME', '')
            
            name_parts = [first_name, second_name, third_name, fourth_name]
            name = ' '.join([part for part in name_parts if part]).strip()
            
            # Get other fields
            un_list_type = data.get('UN_LIST_TYPE', '')
            reference_number = data.get('REFERENCE_NUMBER', '')
            listed_on = data.get('LISTED_ON', '')
            comments = data.get('COMMENTS1', '')
            
            # Parse aliases
            aliases = []
            individual_alias = data.get('INDIVIDUAL_ALIAS', [])
            if isinstance(individual_alias, dict):
                individual_alias = [individual_alias]
            
            for alias in individual_alias:
                alias_name = alias.get('ALIAS_NAME', '').strip()
                if alias_name:
                    aliases.append(alias_name)
            
            # Parse addresses
            addresses = []
            individual_address = data.get('INDIVIDUAL_ADDRESS', [])
            if isinstance(individual_address, dict):
                individual_address = [individual_address]
            
            for addr in individual_address:
                address = {
                    'street': addr.get('STREET', ''),
                    'city': addr.get('CITY', ''),
                    'state_province': addr.get('STATE_PROVINCE', ''),
                    'country': addr.get('COUNTRY', ''),
                    'note': addr.get('NOTE', '')
                }
                if any(address.values()):
                    addresses.append(address)
            
            # Parse identifiers
            identifiers = []
            individual_document = data.get('INDIVIDUAL_DOCUMENT', [])
            if isinstance(individual_document, dict):
                individual_document = [individual_document]
            
            for doc in individual_document:
                identifier = {
                    'type': doc.get('TYPE_OF_DOCUMENT', ''),
                    'number': doc.get('NUMBER', ''),
                    'issuing_country': doc.get('ISSUING_COUNTRY', ''),
                    'date_of_issue': doc.get('DATE_OF_ISSUE', ''),
                    'note': doc.get('NOTE', '')
                }
                if identifier['number']:
                    identifiers.append(identifier)
            
            # Parse nationalities
            nationalities = []
            nationality_data = data.get('NATIONALITY', [])
            if isinstance(nationality_data, dict):
                nationality_data = [nationality_data]
            
            for nat in nationality_data:
                nationality = nat.get('VALUE', '').strip()
                if nationality:
                    nationalities.append(nationality)
            
            return UNEntity(
                dataid=dataid,
                name=name,
                entity_type=entity_type,
                list_type='UN_CONSOLIDATED',
                un_list_type=un_list_type,
                reference_number=reference_number,
                listed_on=listed_on,
                comments=comments,
                aliases=aliases,
                addresses=addresses,
                identifiers=identifiers,
                nationalities=nationalities
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse UN individual: {e}")
            return None
    
    def _parse_entity_json(self, data: Dict, entity_type: str) -> Optional[UNEntity]:
        """Parse entity from JSON data"""
        try:
            dataid = data.get('@dataid', '')
            if not dataid:
                return None
            
            # Get entity name
            name = data.get('FIRST_NAME', '').strip()
            
            # Get other fields
            un_list_type = data.get('UN_LIST_TYPE', '')
            reference_number = data.get('REFERENCE_NUMBER', '')
            listed_on = data.get('LISTED_ON', '')
            comments = data.get('COMMENTS1', '')
            
            # Parse aliases
            aliases = []
            entity_alias = data.get('ENTITY_ALIAS', [])
            if isinstance(entity_alias, dict):
                entity_alias = [entity_alias]
            
            for alias in entity_alias:
                alias_name = alias.get('ALIAS_NAME', '').strip()
                if alias_name:
                    aliases.append(alias_name)
            
            # Parse addresses
            addresses = []
            entity_address = data.get('ENTITY_ADDRESS', [])
            if isinstance(entity_address, dict):
                entity_address = [entity_address]
            
            for addr in entity_address:
                address = {
                    'street': addr.get('STREET', ''),
                    'city': addr.get('CITY', ''),
                    'state_province': addr.get('STATE_PROVINCE', ''),
                    'country': addr.get('COUNTRY', ''),
                    'note': addr.get('NOTE', '')
                }
                if any(address.values()):
                    addresses.append(address)
            
            return UNEntity(
                dataid=dataid,
                name=name,
                entity_type=entity_type,
                list_type='UN_CONSOLIDATED',
                un_list_type=un_list_type,
                reference_number=reference_number,
                listed_on=listed_on,
                comments=comments,
                aliases=aliases,
                addresses=addresses,
                identifiers=[],  # Entities typically don't have personal documents
                nationalities=[]
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse UN entity: {e}")
            return None
    
    def _parse_xml_data(self, root) -> Dict[str, UNEntity]:
        """Parse UN XML data (fallback method)"""
        # XML parsing implementation would go here
        # For now, return empty dict
        logger.warning("XML parsing not implemented, use JSON API")
        return {}
    
    async def search(self, query: str, threshold: int = 80) -> List[Dict[str, Any]]:
        """
        Search UN entities for matches
        
        Args:
            query: Search query (name)
            threshold: Minimum fuzzy match score (0-100)
            
        Returns:
            List of matching entities with confidence scores
        """
        try:
            # Ensure data is loaded
            if not self.entities:
                await self.update_data()
            
            if not self.entities:
                logger.warning("No UN data available for searching")
                return []
            
            matches = []
            query_lower = query.lower().strip()
            
            for dataid, entity in self.entities.items():
                # Check primary name
                name_score = fuzz.ratio(query_lower, entity.name.lower())
                
                # Check aliases
                alias_scores = []
                for alias in entity.aliases:
                    alias_score = fuzz.ratio(query_lower, alias.lower())
                    alias_scores.append(alias_score)
                
                # Get best score
                best_score = max([name_score] + alias_scores) if alias_scores else name_score
                
                if best_score >= threshold:
                    match = {
                        'entity_id': dataid,
                        'name': entity.name,
                        'matched_name': entity.name if name_score == best_score else 
                                      max(entity.aliases, key=lambda x: fuzz.ratio(query_lower, x.lower())),
                        'confidence': best_score,
                        'entity_type': entity.entity_type,
                        'programs': [entity.un_list_type],
                        'list_type': entity.list_type,
                        'reference_number': entity.reference_number,
                        'listed_on': entity.listed_on,
                        'addresses': entity.addresses,
                        'identifiers': entity.identifiers,
                        'aliases': entity.aliases,
                        'nationalities': entity.nationalities,
                        'comments': entity.comments,
                        'match_type': 'fuzzy',
                        'source': 'UN'
                    }
                    matches.append(match)
            
            # Sort by confidence score (highest first)
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info(f"UN search for '{query}' returned {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"UN search failed: {e}")
            return []
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_updated or not self.entities:
            return False
        
        return datetime.now() - self.last_updated < self.cache_duration
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded UN data"""
        if not self.entities:
            return {'total_entities': 0, 'last_updated': None}
        
        stats = {
            'total_entities': len(self.entities),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'entity_types': {},
            'un_list_types': {},
            'nationalities': {}
        }
        
        for entity in self.entities.values():
            # Count entity types
            entity_type = entity.entity_type
            stats['entity_types'][entity_type] = stats['entity_types'].get(entity_type, 0) + 1
            
            # Count UN list types
            un_list_type = entity.un_list_type
            if un_list_type:
                stats['un_list_types'][un_list_type] = stats['un_list_types'].get(un_list_type, 0) + 1
            
            # Count nationalities
            for nationality in entity.nationalities:
                stats['nationalities'][nationality] = stats['nationalities'].get(nationality, 0) + 1
        
        return stats

# Example usage
async def test_un_source():
    """Test UN screening source"""
    async with UNScreeningSource() as un:
        # Update data
        updated = await un.update_data()
        print(f"Data updated: {updated}")
        
        # Get statistics
        stats = un.get_statistics()
        print(f"Statistics: {stats}")
        
        # Search for matches
        matches = await un.search("Osama bin Laden")
        print(f"Matches for 'Osama bin Laden': {len(matches)}")
        
        for match in matches[:3]:  # Show top 3 matches
            print(f"- {match['name']} ({match['confidence']}%)")

if __name__ == "__main__":
    asyncio.run(test_un_source())


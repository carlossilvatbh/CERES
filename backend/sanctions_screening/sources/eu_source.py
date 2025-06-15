"""
EU Sanctions Screening Source Implementation
European Union Consolidated Financial Sanctions List
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from fuzzywuzzy import fuzz
import asyncio
import aiohttp
import xml.etree.ElementTree as ET

logger = logging.getLogger('ceres.screening.eu')

@dataclass
class EUEntity:
    """EU entity data structure"""
    logical_id: str
    name: str
    entity_type: str
    regulation_type: str
    regulation_programme: str
    regulation_entry_into_force_date: str
    design_details: str
    aliases: List[str]
    addresses: List[Dict[str, str]]
    identifiers: List[Dict[str, str]]
    birth_dates: List[str]
    birth_places: List[str]
    citizenships: List[str]

class EUScreeningSource:
    """
    EU Sanctions Screening Source
    Downloads and parses EU Consolidated Financial Sanctions List
    """
    
    # EU Sanctions XML URL
    EU_SANCTIONS_URL = "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList/content?token=dG9rZW4tMjAxNw"
    EU_SANCTIONS_ALT_URL = "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw"
    
    def __init__(self, cache_duration_hours: int = 24):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.entities: Dict[str, EUEntity] = {}
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
        Update EU data from official sources
        
        Args:
            force_refresh: Force download even if cache is valid
            
        Returns:
            bool: True if data was updated, False if using cached data
        """
        try:
            # Check if update is needed
            if not force_refresh and self._is_cache_valid():
                logger.info("EU data cache is valid, skipping update")
                return False
            
            logger.info("Updating EU data from official sources")
            
            # Try primary URL first, then fallback
            entities = await self._download_and_parse_xml(self.EU_SANCTIONS_URL)
            
            if not entities:
                logger.info("Primary EU URL failed, trying alternative")
                entities = await self._download_and_parse_xml(self.EU_SANCTIONS_ALT_URL)
            
            if entities:
                self.entities = entities
                self.last_updated = datetime.now()
                logger.info(f"EU data updated successfully: {len(self.entities)} entities")
                return True
            else:
                logger.error("No EU data could be loaded")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update EU data: {e}")
            return False
    
    async def _download_and_parse_xml(self, url: str) -> Dict[str, EUEntity]:
        """Download and parse EU XML file"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status} for {url}")
                
                xml_content = await response.text()
                
            # Parse XML
            root = ET.fromstring(xml_content)
            return self._parse_eu_xml(root)
            
        except Exception as e:
            logger.error(f"Failed to download/parse EU XML: {e}")
            return {}
    
    def _parse_eu_xml(self, root: ET.Element) -> Dict[str, EUEntity]:
        """Parse EU sanctions XML"""
        entities = {}
        
        # Define namespace
        ns = {'': 'http://eu.europa.ec/fpi/fsd/export'}
        
        try:
            # Parse sanctioned entities
            for entity_elem in root.findall('.//sanctionEntity', ns):
                entity = self._parse_entity_element(entity_elem, ns)
                if entity:
                    entities[entity.logical_id] = entity
            
            logger.info(f"Parsed {len(entities)} EU entities")
            return entities
            
        except Exception as e:
            logger.error(f"Failed to parse EU XML: {e}")
            return {}
    
    def _parse_entity_element(self, entity_elem: ET.Element, ns: Dict[str, str]) -> Optional[EUEntity]:
        """Parse individual entity element"""
        try:
            # Get logical ID
            logical_id = entity_elem.get('logicalId', '')
            if not logical_id:
                return None
            
            # Get entity type
            entity_type = entity_elem.get('entityType', 'Unknown')
            
            # Get regulation info
            regulation_elem = entity_elem.find('regulation', ns)
            regulation_type = ''
            regulation_programme = ''
            regulation_entry_date = ''
            
            if regulation_elem is not None:
                regulation_type = regulation_elem.get('regulationType', '')
                regulation_programme = regulation_elem.get('programme', '')
                regulation_entry_date = regulation_elem.get('entryIntoForceDate', '')
            
            # Get names and aliases
            name = ''
            aliases = []
            
            for name_alias in entity_elem.findall('.//nameAlias', ns):
                whole_name = name_alias.get('wholeName', '').strip()
                is_primary = name_alias.get('strong', 'false').lower() == 'true'
                
                if whole_name:
                    if is_primary and not name:
                        name = whole_name
                    else:
                        aliases.append(whole_name)
            
            # If no primary name found, use first alias
            if not name and aliases:
                name = aliases.pop(0)
            
            # Get addresses
            addresses = []
            for address_elem in entity_elem.findall('.//address', ns):
                address = {}
                
                # Get address components
                for field in ['street', 'city', 'zipCode', 'region', 'countryIso2Code']:
                    value = address_elem.get(field, '').strip()
                    if value:
                        address[field] = value
                
                if address:
                    addresses.append(address)
            
            # Get identifiers
            identifiers = []
            for identification in entity_elem.findall('.//identification', ns):
                identifier = {
                    'type': identification.get('identificationTypeCode', ''),
                    'number': identification.get('number', ''),
                    'diplomatic': identification.get('diplomatic', ''),
                    'latin_script': identification.get('latinScript', '')
                }
                
                if identifier['number']:
                    identifiers.append(identifier)
            
            # Get birth information
            birth_dates = []
            birth_places = []
            
            for birth_date in entity_elem.findall('.//birthdate', ns):
                birth_date_value = birth_date.get('birthdate', '').strip()
                if birth_date_value:
                    birth_dates.append(birth_date_value)
            
            for birth_place in entity_elem.findall('.//birthplace', ns):
                birth_place_value = birth_place.get('place', '').strip()
                if birth_place_value:
                    birth_places.append(birth_place_value)
            
            # Get citizenships
            citizenships = []
            for citizenship in entity_elem.findall('.//citizenship', ns):
                citizenship_value = citizenship.get('countryIso2Code', '').strip()
                if citizenship_value:
                    citizenships.append(citizenship_value)
            
            # Get design details (reasons for listing)
            design_details = ''
            remark_elem = entity_elem.find('.//remark', ns)
            if remark_elem is not None:
                design_details = remark_elem.text or ''
            
            return EUEntity(
                logical_id=logical_id,
                name=name,
                entity_type=entity_type,
                regulation_type=regulation_type,
                regulation_programme=regulation_programme,
                regulation_entry_into_force_date=regulation_entry_date,
                design_details=design_details,
                aliases=aliases,
                addresses=addresses,
                identifiers=identifiers,
                birth_dates=birth_dates,
                birth_places=birth_places,
                citizenships=citizenships
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse EU entity: {e}")
            return None
    
    async def search(self, query: str, threshold: int = 80) -> List[Dict[str, Any]]:
        """
        Search EU entities for matches
        
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
                logger.warning("No EU data available for searching")
                return []
            
            matches = []
            query_lower = query.lower().strip()
            
            for logical_id, entity in self.entities.items():
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
                        'entity_id': logical_id,
                        'name': entity.name,
                        'matched_name': entity.name if name_score == best_score else 
                                      max(entity.aliases, key=lambda x: fuzz.ratio(query_lower, x.lower())),
                        'confidence': best_score,
                        'entity_type': entity.entity_type,
                        'programs': [entity.regulation_programme] if entity.regulation_programme else [],
                        'list_type': 'EU_SANCTIONS',
                        'regulation_type': entity.regulation_type,
                        'entry_into_force_date': entity.regulation_entry_into_force_date,
                        'addresses': entity.addresses,
                        'identifiers': entity.identifiers,
                        'aliases': entity.aliases,
                        'birth_dates': entity.birth_dates,
                        'birth_places': entity.birth_places,
                        'citizenships': entity.citizenships,
                        'design_details': entity.design_details,
                        'match_type': 'fuzzy',
                        'source': 'EU'
                    }
                    matches.append(match)
            
            # Sort by confidence score (highest first)
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info(f"EU search for '{query}' returned {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"EU search failed: {e}")
            return []
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_updated or not self.entities:
            return False
        
        return datetime.now() - self.last_updated < self.cache_duration
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded EU data"""
        if not self.entities:
            return {'total_entities': 0, 'last_updated': None}
        
        stats = {
            'total_entities': len(self.entities),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'entity_types': {},
            'regulation_types': {},
            'programmes': {},
            'citizenships': {}
        }
        
        for entity in self.entities.values():
            # Count entity types
            entity_type = entity.entity_type
            stats['entity_types'][entity_type] = stats['entity_types'].get(entity_type, 0) + 1
            
            # Count regulation types
            regulation_type = entity.regulation_type
            if regulation_type:
                stats['regulation_types'][regulation_type] = stats['regulation_types'].get(regulation_type, 0) + 1
            
            # Count programmes
            programme = entity.regulation_programme
            if programme:
                stats['programmes'][programme] = stats['programmes'].get(programme, 0) + 1
            
            # Count citizenships
            for citizenship in entity.citizenships:
                stats['citizenships'][citizenship] = stats['citizenships'].get(citizenship, 0) + 1
        
        return stats

# Example usage
async def test_eu_source():
    """Test EU screening source"""
    async with EUScreeningSource() as eu:
        # Update data
        updated = await eu.update_data()
        print(f"Data updated: {updated}")
        
        # Get statistics
        stats = eu.get_statistics()
        print(f"Statistics: {stats}")
        
        # Search for matches
        matches = await eu.search("Vladimir Putin")
        print(f"Matches for 'Vladimir Putin': {len(matches)}")
        
        for match in matches[:3]:  # Show top 3 matches
            print(f"- {match['name']} ({match['confidence']}%)")

if __name__ == "__main__":
    asyncio.run(test_eu_source())


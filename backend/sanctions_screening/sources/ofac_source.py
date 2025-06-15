"""
OFAC Consolidated Screening Source Implementation
Office of Foreign Assets Control - US Treasury Department
"""
import xml.etree.ElementTree as ET
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from fuzzywuzzy import fuzz
import asyncio
import aiohttp

logger = logging.getLogger('ceres.screening.ofac')

@dataclass
class OFACEntity:
    """OFAC entity data structure"""
    uid: str
    name: str
    entity_type: str
    programs: List[str]
    addresses: List[Dict[str, str]]
    identifiers: List[Dict[str, str]]
    aliases: List[str]
    remarks: str
    list_type: str

class OFACScreeningSource:
    """
    OFAC Consolidated Screening Source
    Downloads and parses OFAC XML data for sanctions screening
    """
    
    # OFAC XML URLs
    OFAC_URLS = {
        'consolidated': 'https://www.treasury.gov/ofac/downloads/sdn.xml',
        'consolidated_add': 'https://www.treasury.gov/ofac/downloads/add.xml',
        'consolidated_alt': 'https://www.treasury.gov/ofac/downloads/alt.xml',
        'sectoral': 'https://www.treasury.gov/ofac/downloads/ssi.xml',
        'non_sdn': 'https://www.treasury.gov/ofac/downloads/nonsdn.xml'
    }
    
    def __init__(self, cache_duration_hours: int = 24):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.entities: Dict[str, OFACEntity] = {}
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
        Update OFAC data from official sources
        
        Args:
            force_refresh: Force download even if cache is valid
            
        Returns:
            bool: True if data was updated, False if using cached data
        """
        try:
            # Check if update is needed
            if not force_refresh and self._is_cache_valid():
                logger.info("OFAC data cache is valid, skipping update")
                return False
            
            logger.info("Updating OFAC data from official sources")
            
            # Download and parse all OFAC lists
            all_entities = {}
            
            for list_name, url in self.OFAC_URLS.items():
                try:
                    entities = await self._download_and_parse_xml(url, list_name)
                    all_entities.update(entities)
                    logger.info(f"Loaded {len(entities)} entities from {list_name}")
                except Exception as e:
                    logger.error(f"Failed to load {list_name}: {e}")
                    continue
            
            if all_entities:
                self.entities = all_entities
                self.last_updated = datetime.now()
                logger.info(f"OFAC data updated successfully: {len(self.entities)} total entities")
                return True
            else:
                logger.error("No OFAC data could be loaded")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update OFAC data: {e}")
            return False
    
    async def _download_and_parse_xml(self, url: str, list_type: str) -> Dict[str, OFACEntity]:
        """Download and parse OFAC XML file"""
        entities = {}
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status} for {url}")
                
                xml_content = await response.text()
                
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Parse based on list type
            if list_type in ['consolidated', 'sectoral', 'non_sdn']:
                entities = self._parse_sdn_xml(root, list_type)
            elif list_type == 'consolidated_add':
                entities = self._parse_address_xml(root)
            elif list_type == 'consolidated_alt':
                entities = self._parse_alt_xml(root)
            
            return entities
            
        except Exception as e:
            logger.error(f"Failed to download/parse {url}: {e}")
            return {}
    
    def _parse_sdn_xml(self, root: ET.Element, list_type: str) -> Dict[str, OFACEntity]:
        """Parse SDN-style XML (main entity lists)"""
        entities = {}
        
        for entry in root.findall('.//sdnEntry'):
            try:
                uid = entry.get('uid', '')
                if not uid:
                    continue
                
                # Basic entity info
                first_name = entry.findtext('firstName', '').strip()
                last_name = entry.findtext('lastName', '').strip()
                full_name = f"{first_name} {last_name}".strip()
                
                if not full_name:
                    full_name = entry.findtext('title', '').strip()
                
                entity_type = entry.findtext('sdnType', 'Individual')
                
                # Programs
                programs = []
                for program in entry.findall('.//program'):
                    prog_text = program.text
                    if prog_text:
                        programs.append(prog_text.strip())
                
                # Addresses
                addresses = []
                for address in entry.findall('.//address'):
                    addr_dict = {}
                    for field in ['address1', 'address2', 'city', 'stateOrProvince', 'postalCode', 'country']:
                        value = address.findtext(field, '').strip()
                        if value:
                            addr_dict[field] = value
                    if addr_dict:
                        addresses.append(addr_dict)
                
                # Identifiers (IDs, passports, etc.)
                identifiers = []
                for id_elem in entry.findall('.//id'):
                    id_dict = {
                        'type': id_elem.get('idType', ''),
                        'number': id_elem.get('idNumber', ''),
                        'country': id_elem.get('idCountry', '')
                    }
                    if id_dict['number']:
                        identifiers.append(id_dict)
                
                # Aliases
                aliases = []
                for aka in entry.findall('.//aka'):
                    aka_type = aka.get('type', '')
                    aka_first = aka.findtext('firstName', '').strip()
                    aka_last = aka.findtext('lastName', '').strip()
                    aka_name = f"{aka_first} {aka_last}".strip()
                    
                    if not aka_name:
                        aka_name = aka.findtext('title', '').strip()
                    
                    if aka_name:
                        aliases.append(aka_name)
                
                # Remarks
                remarks = entry.findtext('remarks', '').strip()
                
                # Create entity
                entity = OFACEntity(
                    uid=uid,
                    name=full_name,
                    entity_type=entity_type,
                    programs=programs,
                    addresses=addresses,
                    identifiers=identifiers,
                    aliases=aliases,
                    remarks=remarks,
                    list_type=list_type
                )
                
                entities[uid] = entity
                
            except Exception as e:
                logger.warning(f"Failed to parse OFAC entry: {e}")
                continue
        
        return entities
    
    def _parse_address_xml(self, root: ET.Element) -> Dict[str, OFACEntity]:
        """Parse address XML (additional addresses)"""
        # This would update existing entities with additional addresses
        # For now, return empty dict as addresses are parsed in main XML
        return {}
    
    def _parse_alt_xml(self, root: ET.Element) -> Dict[str, OFACEntity]:
        """Parse alternate names XML"""
        # This would update existing entities with additional aliases
        # For now, return empty dict as aliases are parsed in main XML
        return {}
    
    async def search(self, query: str, threshold: int = 80) -> List[Dict[str, Any]]:
        """
        Search OFAC entities for matches
        
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
                logger.warning("No OFAC data available for searching")
                return []
            
            matches = []
            query_lower = query.lower().strip()
            
            for uid, entity in self.entities.items():
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
                        'entity_id': uid,
                        'name': entity.name,
                        'matched_name': entity.name if name_score == best_score else 
                                      max(entity.aliases, key=lambda x: fuzz.ratio(query_lower, x.lower())),
                        'confidence': best_score,
                        'entity_type': entity.entity_type,
                        'programs': entity.programs,
                        'list_type': entity.list_type,
                        'addresses': entity.addresses,
                        'identifiers': entity.identifiers,
                        'aliases': entity.aliases,
                        'remarks': entity.remarks,
                        'match_type': 'fuzzy',
                        'source': 'OFAC'
                    }
                    matches.append(match)
            
            # Sort by confidence score (highest first)
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info(f"OFAC search for '{query}' returned {len(matches)} matches")
            return matches
            
        except Exception as e:
            logger.error(f"OFAC search failed: {e}")
            return []
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_updated or not self.entities:
            return False
        
        return datetime.now() - self.last_updated < self.cache_duration
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded OFAC data"""
        if not self.entities:
            return {'total_entities': 0, 'last_updated': None}
        
        stats = {
            'total_entities': len(self.entities),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'entity_types': {},
            'programs': {},
            'list_types': {}
        }
        
        for entity in self.entities.values():
            # Count entity types
            entity_type = entity.entity_type
            stats['entity_types'][entity_type] = stats['entity_types'].get(entity_type, 0) + 1
            
            # Count programs
            for program in entity.programs:
                stats['programs'][program] = stats['programs'].get(program, 0) + 1
            
            # Count list types
            list_type = entity.list_type
            stats['list_types'][list_type] = stats['list_types'].get(list_type, 0) + 1
        
        return stats

# Example usage
async def test_ofac_source():
    """Test OFAC screening source"""
    async with OFACScreeningSource() as ofac:
        # Update data
        updated = await ofac.update_data()
        print(f"Data updated: {updated}")
        
        # Get statistics
        stats = ofac.get_statistics()
        print(f"Statistics: {stats}")
        
        # Search for matches
        matches = await ofac.search("Vladimir Putin")
        print(f"Matches for 'Vladimir Putin': {len(matches)}")
        
        for match in matches[:3]:  # Show top 3 matches
            print(f"- {match['name']} ({match['confidence']}%)")

if __name__ == "__main__":
    asyncio.run(test_ofac_source())


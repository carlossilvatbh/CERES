"""
Sanctions Screening Data Sources Integration
"""
import asyncio
import aiohttp
import logging
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus
import hashlib

logger = logging.getLogger('ceres')

class DataSourceManager:
    """
    Manager for all external data sources integration
    """
    
    def __init__(self):
        self.sources = {
            # Sanctions Lists
            'ofac_sdn': OFACSDNSource(),
            'ofac_consolidated': OFACConsolidatedSource(),
            'un_consolidated': UNConsolidatedSource(),
            'eu_sanctions': EUSanctionsSource(),
            'uk_ofsi': UKOFSISource(),
            'dfat_au': DFATAustraliaSource(),
            'seco_ch': SECOSwitzerlandSource(),
            'fintrac_ca': FINTRACCanadaSource(),
            'banco_central_br': BancoCentralBrazilSource(),
            
            # PEP Sources
            'opensanctions_pep': OpenSanctionsPEPSource(),
            'wikidata_pep': WikiDataPEPSource(),
            'ipu_parline': IPUParlineSource(),
            'parlgov': ParlGovSource(),
            'g20_officials': G20OfficialsSource(),
            'world_bank_soe': WorldBankSOESource(),
            'openownership': OpenOwnershipSource(),
            
            # Corporate Sources
            'opencorporates': OpenCorporatesSource(),
            'gleif_lei': GLEIFLEISource(),
            'sec_edgar': SECEdgarSource(),
            'companies_house_uk': CompaniesHouseUKSource(),
            'receita_cnpj': ReceitaCNPJSource(),
            
            # Media Sources
            'gdelt': GDELTSource(),
            'common_crawl_news': CommonCrawlNewsSource(),
            'newscatcher': NewscatcherSource(),
        }
        
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'CERES-Compliance-System/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_all_sources(self, query_name: str, source_types: List[str] = None) -> Dict[str, Any]:
        """
        Search across all configured sources
        """
        if source_types is None:
            source_types = ['sanctions', 'pep', 'corporate']
        
        results = {}
        tasks = []
        
        for source_code, source in self.sources.items():
            if any(st in source.source_type for st in source_types):
                if source.is_enabled:
                    task = self._search_source_safe(source_code, source, query_name)
                    tasks.append(task)
        
        # Execute all searches concurrently
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(search_results):
            source_code = list(self.sources.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Search failed for {source_code}: {result}")
                results[source_code] = {
                    'success': False,
                    'error': str(result),
                    'matches': []
                }
            else:
                results[source_code] = result
        
        return results
    
    async def _search_source_safe(self, source_code: str, source, query_name: str) -> Dict[str, Any]:
        """
        Safely search a single source with error handling
        """
        try:
            return await source.search(query_name, self.session)
        except Exception as e:
            logger.error(f"Error searching {source_code}: {e}")
            return {
                'success': False,
                'error': str(e),
                'matches': []
            }

class BaseDataSource:
    """
    Base class for all data sources
    """
    
    def __init__(self):
        self.source_type = 'unknown'
        self.name = 'Unknown Source'
        self.code = 'unknown'
        self.is_enabled = True
        self.base_url = ''
        self.rate_limit = 10  # requests per second
        self.cache_ttl = 3600  # 1 hour
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search for a name in this data source
        """
        raise NotImplementedError("Subclasses must implement search method")
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize name for searching
        """
        return name.strip().upper()
    
    def _calculate_confidence(self, query_name: str, matched_name: str) -> float:
        """
        Calculate confidence score for a match
        """
        from difflib import SequenceMatcher
        return SequenceMatcher(None, query_name.upper(), matched_name.upper()).ratio() * 100

# OFAC Sources
class OFACSDNSource(BaseDataSource):
    """
    OFAC Specially Designated Nationals (SDN) List
    """
    
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'OFAC SDN List'
        self.code = 'ofac_sdn'
        self.base_url = 'https://sanctionssearch.ofac.treas.gov/api'
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search OFAC SDN list
        """
        search_url = f"{self.base_url}/search"
        params = {
            'name': query_name,
            'type': 'individual',
            'maxResults': 50
        }
        
        async with session.get(search_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                matches = []
                
                for item in data.get('results', []):
                    confidence = self._calculate_confidence(query_name, item.get('name', ''))
                    
                    matches.append({
                        'name': item.get('name'),
                        'entity_id': item.get('id'),
                        'confidence': confidence,
                        'entity_type': item.get('type'),
                        'programs': item.get('programs', []),
                        'addresses': item.get('addresses', []),
                        'dates_of_birth': item.get('datesOfBirth', []),
                        'source_url': f"https://sanctionssearch.ofac.treas.gov/Details/{item.get('id')}"
                    })
                
                return {
                    'success': True,
                    'source': self.code,
                    'matches': matches,
                    'total_results': len(matches)
                }
            else:
                raise Exception(f"OFAC API returned status {response.status}")

class OFACConsolidatedSource(BaseDataSource):
    """
    OFAC Consolidated Sanctions List
    """
    
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'OFAC Consolidated List'
        self.code = 'ofac_consolidated'
        self.base_url = 'https://www.treasury.gov/ofac/downloads'
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search OFAC Consolidated list (requires downloading and parsing XML)
        """
        # This would typically involve downloading the consolidated XML file
        # and parsing it locally for better performance
        
        # For now, return a placeholder implementation
        return {
            'success': True,
            'source': self.code,
            'matches': [],
            'total_results': 0,
            'note': 'Consolidated list search requires local XML parsing'
        }

# UN Sources
class UNConsolidatedSource(BaseDataSource):
    """
    UN Security Council Consolidated List
    """
    
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'UN Consolidated List'
        self.code = 'un_consolidated'
        self.base_url = 'https://scsanctions.un.org/resources'
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search UN Consolidated list
        """
        # UN provides XML downloads that need to be parsed locally
        # This is a simplified implementation
        
        return {
            'success': True,
            'source': self.code,
            'matches': [],
            'total_results': 0,
            'note': 'UN list search requires XML download and parsing'
        }

# EU Sources
class EUSanctionsSource(BaseDataSource):
    """
    EU Financial Sanctions Database
    """
    
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'EU Financial Sanctions'
        self.code = 'eu_sanctions'
        self.base_url = 'https://webgate.ec.europa.eu/fsd/fsf'
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search EU sanctions database
        """
        return {
            'success': True,
            'source': self.code,
            'matches': [],
            'total_results': 0,
            'note': 'EU sanctions search requires specialized API integration'
        }

# UK Sources
class UKOFSISource(BaseDataSource):
    """
    UK Office of Financial Sanctions Implementation
    """
    
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'UK OFSI'
        self.code = 'uk_ofsi'
        self.base_url = 'https://ofsistorage.blob.core.windows.net/publishlive'
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search UK OFSI consolidated list
        """
        return {
            'success': True,
            'source': self.code,
            'matches': [],
            'total_results': 0,
            'note': 'UK OFSI search requires CSV/Excel file parsing'
        }

# Additional country sources (simplified implementations)
class DFATAustraliaSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'DFAT Australia'
        self.code = 'dfat_au'

class SECOSwitzerlandSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'SECO Switzerland'
        self.code = 'seco_ch'

class FINTRACCanadaSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'FINTRAC Canada'
        self.code = 'fintrac_ca'

class BancoCentralBrazilSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'sanctions'
        self.name = 'Banco Central Brasil'
        self.code = 'banco_central_br'

# PEP Sources
class OpenSanctionsPEPSource(BaseDataSource):
    """
    OpenSanctions PEP Database
    """
    
    def __init__(self):
        super().__init__()
        self.source_type = 'pep'
        self.name = 'OpenSanctions PEP'
        self.code = 'opensanctions_pep'
        self.base_url = 'https://api.opensanctions.org'
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search OpenSanctions PEP database
        """
        search_url = f"{self.base_url}/search/default"
        params = {
            'q': query_name,
            'schema': 'Person',
            'topics': 'role.pep',
            'limit': 50
        }
        
        try:
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    matches = []
                    
                    for item in data.get('results', []):
                        properties = item.get('properties', {})
                        name = properties.get('name', [''])[0] if properties.get('name') else ''
                        
                        confidence = self._calculate_confidence(query_name, name)
                        
                        matches.append({
                            'name': name,
                            'entity_id': item.get('id'),
                            'confidence': confidence,
                            'entity_type': 'pep',
                            'country': properties.get('country', []),
                            'position': properties.get('position', []),
                            'topics': item.get('topics', []),
                            'source_url': f"https://opensanctions.org/entities/{item.get('id')}"
                        })
                    
                    return {
                        'success': True,
                        'source': self.code,
                        'matches': matches,
                        'total_results': len(matches)
                    }
                else:
                    raise Exception(f"OpenSanctions API returned status {response.status}")
        except Exception as e:
            logger.error(f"OpenSanctions PEP search failed: {e}")
            return {
                'success': False,
                'source': self.code,
                'error': str(e),
                'matches': []
            }

class WikiDataPEPSource(BaseDataSource):
    """
    WikiData SPARQL for PEP information
    """
    
    def __init__(self):
        super().__init__()
        self.source_type = 'pep'
        self.name = 'WikiData PEP'
        self.code = 'wikidata_pep'
        self.base_url = 'https://query.wikidata.org/sparql'
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search WikiData for politicians and officials
        """
        # SPARQL query to find politicians
        sparql_query = f"""
        SELECT ?person ?personLabel ?positionLabel ?countryLabel WHERE {{
          ?person wdt:P31 wd:Q5 .
          ?person wdt:P39 ?position .
          ?position wdt:P279* wd:Q4164871 .
          ?person rdfs:label ?personLabel .
          FILTER(CONTAINS(LCASE(?personLabel), LCASE("{query_name}")))
          OPTIONAL {{ ?person wdt:P27 ?country }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
        }}
        LIMIT 20
        """
        
        params = {
            'query': sparql_query,
            'format': 'json'
        }
        
        try:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    matches = []
                    
                    for binding in data.get('results', {}).get('bindings', []):
                        name = binding.get('personLabel', {}).get('value', '')
                        confidence = self._calculate_confidence(query_name, name)
                        
                        matches.append({
                            'name': name,
                            'entity_id': binding.get('person', {}).get('value', ''),
                            'confidence': confidence,
                            'entity_type': 'pep',
                            'position': binding.get('positionLabel', {}).get('value', ''),
                            'country': binding.get('countryLabel', {}).get('value', ''),
                            'source_url': binding.get('person', {}).get('value', '')
                        })
                    
                    return {
                        'success': True,
                        'source': self.code,
                        'matches': matches,
                        'total_results': len(matches)
                    }
                else:
                    raise Exception(f"WikiData SPARQL returned status {response.status}")
        except Exception as e:
            logger.error(f"WikiData PEP search failed: {e}")
            return {
                'success': False,
                'source': self.code,
                'error': str(e),
                'matches': []
            }

# Additional PEP sources (simplified)
class IPUParlineSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'pep'
        self.name = 'IPU Parline'
        self.code = 'ipu_parline'

class ParlGovSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'pep'
        self.name = 'ParlGov'
        self.code = 'parlgov'

class G20OfficialsSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'pep'
        self.name = 'G20 Officials'
        self.code = 'g20_officials'

class WorldBankSOESource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'pep'
        self.name = 'World Bank SOE'
        self.code = 'world_bank_soe'

class OpenOwnershipSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'corporate'
        self.name = 'OpenOwnership'
        self.code = 'openownership'

# Corporate Sources
class OpenCorporatesSource(BaseDataSource):
    """
    OpenCorporates API
    """
    
    def __init__(self):
        super().__init__()
        self.source_type = 'corporate'
        self.name = 'OpenCorporates'
        self.code = 'opencorporates'
        self.base_url = 'https://api.opencorporates.com/v0.4'
    
    async def search(self, query_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """
        Search OpenCorporates for companies and officers
        """
        # Search for companies
        search_url = f"{self.base_url}/companies/search"
        params = {
            'q': query_name,
            'format': 'json',
            'per_page': 20
        }
        
        try:
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    matches = []
                    
                    for company in data.get('results', {}).get('companies', []):
                        company_data = company.get('company', {})
                        name = company_data.get('name', '')
                        confidence = self._calculate_confidence(query_name, name)
                        
                        matches.append({
                            'name': name,
                            'entity_id': company_data.get('company_number'),
                            'confidence': confidence,
                            'entity_type': 'company',
                            'jurisdiction': company_data.get('jurisdiction_code'),
                            'status': company_data.get('company_type'),
                            'incorporation_date': company_data.get('incorporation_date'),
                            'source_url': company_data.get('opencorporates_url')
                        })
                    
                    return {
                        'success': True,
                        'source': self.code,
                        'matches': matches,
                        'total_results': len(matches)
                    }
                else:
                    raise Exception(f"OpenCorporates API returned status {response.status}")
        except Exception as e:
            logger.error(f"OpenCorporates search failed: {e}")
            return {
                'success': False,
                'source': self.code,
                'error': str(e),
                'matches': []
            }

# Additional corporate sources (simplified)
class GLEIFLEISource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'corporate'
        self.name = 'GLEIF LEI'
        self.code = 'gleif_lei'

class SECEdgarSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'corporate'
        self.name = 'SEC EDGAR'
        self.code = 'sec_edgar'

class CompaniesHouseUKSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'corporate'
        self.name = 'Companies House UK'
        self.code = 'companies_house_uk'

class ReceitaCNPJSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'corporate'
        self.name = 'Receita CNPJ'
        self.code = 'receita_cnpj'

# Media Sources
class GDELTSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'media'
        self.name = 'GDELT 2.0'
        self.code = 'gdelt'

class CommonCrawlNewsSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'media'
        self.name = 'Common Crawl News'
        self.code = 'common_crawl_news'

class NewscatcherSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.source_type = 'media'
        self.name = 'Newscatcher Free'
        self.code = 'newscatcher'


"""
Unified Data Source Manager for CERES Screening
Manages all screening sources and provides unified search interface
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .ofac_source import OFACScreeningSource
from .un_source import UNScreeningSource
from .eu_source import EUScreeningSource
from .opensanctions_source import OpenSanctionsSource

logger = logging.getLogger('ceres.screening.manager')

class DataSourceManager:
    """
    Unified manager for all screening data sources
    Provides consolidated search across multiple sources
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sources = {}
        self.source_status = {}
    
    async def __aenter__(self):
        """Initialize all data sources"""
        try:
            # Initialize OFAC source
            self.sources['ofac'] = OFACScreeningSource(
                cache_duration_hours=self.config.get('ofac_cache_hours', 24)
            )
            await self.sources['ofac'].__aenter__()
            
            # Initialize UN source
            self.sources['un'] = UNScreeningSource(
                cache_duration_hours=self.config.get('un_cache_hours', 24)
            )
            await self.sources['un'].__aenter__()
            
            # Initialize EU source
            self.sources['eu'] = EUScreeningSource(
                cache_duration_hours=self.config.get('eu_cache_hours', 24)
            )
            await self.sources['eu'].__aenter__()
            
            # Initialize OpenSanctions source
            opensanctions_api_key = self.config.get('opensanctions_api_key')
            self.sources['opensanctions'] = OpenSanctionsSource(
                api_key=opensanctions_api_key,
                cache_duration_hours=self.config.get('opensanctions_cache_hours', 24)
            )
            await self.sources['opensanctions'].__aenter__()
            
            logger.info("All screening sources initialized")
            return self
            
        except Exception as e:
            logger.error(f"Failed to initialize data sources: {e}")
            await self._cleanup_sources()
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup all data sources"""
        await self._cleanup_sources()
    
    async def _cleanup_sources(self):
        """Cleanup all initialized sources"""
        for source_name, source in self.sources.items():
            try:
                if hasattr(source, '__aexit__'):
                    await source.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Failed to cleanup source {source_name}: {e}")
    
    async def update_all_sources(self, force_refresh: bool = False) -> Dict[str, bool]:
        """
        Update all data sources
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Dict mapping source names to update success status
        """
        results = {}
        
        for source_name, source in self.sources.items():
            try:
                logger.info(f"Updating {source_name} source...")
                success = await source.update_data(force_refresh=force_refresh)
                results[source_name] = success
                self.source_status[source_name] = {
                    'status': 'active' if success else 'error',
                    'last_update': datetime.now().isoformat(),
                    'error': None if success else 'Update failed'
                }
                logger.info(f"{source_name} update: {'success' if success else 'failed'}")
                
            except Exception as e:
                logger.error(f"Failed to update {source_name}: {e}")
                results[source_name] = False
                self.source_status[source_name] = {
                    'status': 'error',
                    'last_update': datetime.now().isoformat(),
                    'error': str(e)
                }
        
        return results
    
    async def search_all_sources(self, query: str, source_types: Optional[List[str]] = None, 
                                threshold: int = 80) -> Dict[str, Dict[str, Any]]:
        """
        Search across all or specified sources
        
        Args:
            query: Search query (name)
            source_types: List of source types to search (None for all)
            threshold: Minimum confidence threshold
            
        Returns:
            Dict mapping source names to search results
        """
        results = {}
        
        # Determine which sources to search
        sources_to_search = self.sources.keys()
        if source_types:
            # Map source types to actual sources
            type_mapping = {
                'sanctions': ['ofac', 'un', 'eu'],
                'pep': ['opensanctions'],
                'corporate': ['opensanctions']
            }
            
            sources_to_search = set()
            for source_type in source_types:
                sources_to_search.update(type_mapping.get(source_type, []))
        
        # Search each source
        search_tasks = []
        for source_name in sources_to_search:
            if source_name in self.sources:
                task = self._search_source_with_error_handling(
                    source_name, self.sources[source_name], query, threshold
                )
                search_tasks.append(task)
        
        # Execute searches concurrently
        if search_tasks:
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Process results
            for i, (source_name, result) in enumerate(zip(sources_to_search, search_results)):
                if isinstance(result, Exception):
                    logger.error(f"Search failed for {source_name}: {result}")
                    results[source_name] = {
                        'success': False,
                        'error': str(result),
                        'matches': [],
                        'processing_time': 0
                    }
                else:
                    results[source_name] = result
        
        return results
    
    async def _search_source_with_error_handling(self, source_name: str, source: Any, 
                                               query: str, threshold: int) -> Dict[str, Any]:
        """Search individual source with error handling and timing"""
        start_time = datetime.now()
        
        try:
            matches = await source.search(query, threshold=threshold)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'matches': matches,
                'processing_time': processing_time,
                'source': source_name
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Search failed for {source_name}: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'matches': [],
                'processing_time': processing_time,
                'source': source_name
            }
    
    async def search_specific_source(self, source_name: str, query: str, 
                                   threshold: int = 80) -> Dict[str, Any]:
        """
        Search specific source
        
        Args:
            source_name: Name of source to search
            query: Search query
            threshold: Minimum confidence threshold
            
        Returns:
            Search results from specified source
        """
        if source_name not in self.sources:
            return {
                'success': False,
                'error': f'Source {source_name} not available',
                'matches': [],
                'processing_time': 0
            }
        
        return await self._search_source_with_error_handling(
            source_name, self.sources[source_name], query, threshold
        )
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """Get statistics for all sources"""
        stats = {
            'sources': {},
            'total_sources': len(self.sources),
            'active_sources': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        for source_name, source in self.sources.items():
            try:
                source_stats = source.get_statistics()
                source_stats['status'] = self.source_status.get(source_name, {})
                stats['sources'][source_name] = source_stats
                
                # Count active sources
                if self.source_status.get(source_name, {}).get('status') == 'active':
                    stats['active_sources'] += 1
                    
            except Exception as e:
                logger.warning(f"Failed to get statistics for {source_name}: {e}")
                stats['sources'][source_name] = {
                    'error': str(e),
                    'status': self.source_status.get(source_name, {})
                }
        
        return stats
    
    def get_available_sources(self) -> List[str]:
        """Get list of available source names"""
        return list(self.sources.keys())
    
    def is_source_active(self, source_name: str) -> bool:
        """Check if specific source is active"""
        return (source_name in self.sources and 
                self.source_status.get(source_name, {}).get('status') == 'active')

# Example usage and testing
async def test_data_source_manager():
    """Test the unified data source manager"""
    config = {
        'ofac_cache_hours': 24,
        'un_cache_hours': 24,
        'eu_cache_hours': 24,
        'opensanctions_cache_hours': 24,
        # 'opensanctions_api_key': 'your-api-key-here'  # Optional
    }
    
    async with DataSourceManager(config) as manager:
        # Update all sources
        print("Updating all sources...")
        update_results = await manager.update_all_sources()
        print(f"Update results: {update_results}")
        
        # Get statistics
        stats = manager.get_source_statistics()
        print(f"Source statistics: {stats}")
        
        # Search all sources
        print("\nSearching all sources for 'Vladimir Putin'...")
        search_results = await manager.search_all_sources("Vladimir Putin")
        
        for source_name, result in search_results.items():
            if result['success']:
                print(f"{source_name}: {len(result['matches'])} matches in {result['processing_time']:.2f}s")
                for match in result['matches'][:2]:  # Show top 2 matches
                    print(f"  - {match['name']} ({match['confidence']}%)")
            else:
                print(f"{source_name}: Error - {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_data_source_manager())


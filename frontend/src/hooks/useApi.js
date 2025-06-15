/**
 * Custom hook for API calls with proper dependency management
 * Prevents infinite re-renders and provides loading states
 */
import { useState, useEffect, useCallback, useRef } from 'react'

export const useApi = (url, options = {}) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // Use ref to track if component is mounted
  const isMountedRef = useRef(true)
  
  // Memoize the fetch function to prevent infinite re-renders
  const fetchData = useCallback(async () => {
    if (!url || loading) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      // Only update state if component is still mounted
      if (isMountedRef.current) {
        setData(result)
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err.message)
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false)
      }
    }
  }, [url, loading, options.headers, options.method, options.body])
  
  // Effect with proper dependencies
  useEffect(() => {
    if (options.immediate !== false) {
      fetchData()
    }
    
    // Cleanup function
    return () => {
      isMountedRef.current = false
    }
  }, [fetchData, options.immediate])
  
  // Manual refetch function
  const refetch = useCallback(() => {
    fetchData()
  }, [fetchData])
  
  return { data, loading, error, refetch }
}

export const useApiMutation = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const mutate = useCallback(async (url, options = {}) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])
  
  return { mutate, loading, error }
}

export default useApi


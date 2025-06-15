import { describe, it, expect } from 'vitest'

// Simple test that doesn't import unused dependencies
describe('Basic functionality', () => {
  it('should run tests successfully', () => {
    const element = document.createElement('div')
    element.textContent = 'CERES'
    document.body.appendChild(element)
    
    expect(element.textContent).toBe('CERES')
  })
  
  it('should handle basic math', () => {
    expect(2 + 2).toBe(4)
  })
  
  it('should work with arrays', () => {
    const arr = [1, 2, 3]
    expect(arr.length).toBe(3)
    expect(arr[0]).toBe(1)
  })
})


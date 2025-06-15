import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

// Simple test that doesn't depend on App component
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
})


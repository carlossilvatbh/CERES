import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from './App'
import { describe, it, expect } from 'vitest'

describe('App', () => {
  it('renders login page by default', () => {
    render(<App />)
    expect(screen.getByText(/Entrar no Sistema/i)).toBeInTheDocument()
  })
})

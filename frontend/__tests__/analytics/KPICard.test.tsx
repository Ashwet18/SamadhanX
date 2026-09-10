/**
 * Tests for KPICard component
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { KPICard } from '@/components/analytics/KPICard'
import { FileText } from 'lucide-react'

describe('KPICard', () => {
  test('should render title and value', () => {
    render(
      <KPICard
        title="Total Challenges"
        value={150}
      />
    )

    expect(screen.getByText('Total Challenges')).toBeInTheDocument()
    expect(screen.getByText('150')).toBeInTheDocument()
  })

  test('should render subtitle when provided', () => {
    render(
      <KPICard
        title="Total Challenges"
        value={150}
        subtitle="45 validated"
      />
    )

    expect(screen.getByText('45 validated')).toBeInTheDocument()
  })

  test('should render icon when provided', () => {
    const { container } = render(
      <KPICard
        title="Total Challenges"
        value={150}
        icon={FileText}
      />
    )

    // Icon is rendered via lucide-react
    const icon = container.querySelector('svg')
    expect(icon).toBeInTheDocument()
  })

  test('should handle string values', () => {
    render(
      <KPICard
        title="Verified Beneficiaries"
        value="12,000"
      />
    )

    expect(screen.getByText('12,000')).toBeInTheDocument()
  })

  test('should handle large numbers', () => {
    render(
      <KPICard
        title="Total Beneficiaries"
        value={1234567}
      />
    )

    expect(screen.getByText('1234567')).toBeInTheDocument()
  })

  test('should apply custom icon colors', () => {
    const { container } = render(
      <KPICard
        title="Total Challenges"
        value={150}
        icon={FileText}
        iconBgColor="bg-red-100"
        iconColor="text-red-600"
      />
    )

    const iconContainer = container.querySelector('.bg-red-100')
    expect(iconContainer).toBeInTheDocument()
  })
})

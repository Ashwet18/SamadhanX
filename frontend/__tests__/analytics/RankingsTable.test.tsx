/**
 * Tests for RankingsTable component
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { RankingsTable } from '@/components/analytics/RankingsTable'

describe('RankingsTable', () => {
  const mockItems = [
    { name: 'University A', value: 15, subtitle: '5 completed' },
    { name: 'University B', value: 12, subtitle: '3 completed' },
    { name: 'University C', value: 10, subtitle: '2 completed' },
  ]

  test('should render table title', () => {
    render(
      <RankingsTable
        title="Top Universities"
        items={mockItems}
      />
    )

    expect(screen.getByText('Top Universities')).toBeInTheDocument()
  })

  test('should render description when provided', () => {
    render(
      <RankingsTable
        title="Top Universities"
        description="Most active universities by project count"
        items={mockItems}
      />
    )

    expect(screen.getByText('Most active universities by project count')).toBeInTheDocument()
  })

  test('should render all items with ranks', () => {
    render(
      <RankingsTable
        title="Top Universities"
        items={mockItems}
      />
    )

    expect(screen.getByText('#1')).toBeInTheDocument()
    expect(screen.getByText('#2')).toBeInTheDocument()
    expect(screen.getByText('#3')).toBeInTheDocument()

    expect(screen.getByText('University A')).toBeInTheDocument()
    expect(screen.getByText('University B')).toBeInTheDocument()
    expect(screen.getByText('University C')).toBeInTheDocument()
  })

  test('should render values correctly', () => {
    render(
      <RankingsTable
        title="Top Universities"
        items={mockItems}
      />
    )

    expect(screen.getByText('15')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
  })

  test('should render subtitles when provided', () => {
    render(
      <RankingsTable
        title="Top Universities"
        items={mockItems}
      />
    )

    expect(screen.getByText('5 completed')).toBeInTheDocument()
    expect(screen.getByText('3 completed')).toBeInTheDocument()
    expect(screen.getByText('2 completed')).toBeInTheDocument()
  })

  test('should show empty message when no items', () => {
    render(
      <RankingsTable
        title="Top Universities"
        items={[]}
        emptyMessage="No universities found"
      />
    )

    expect(screen.getByText('No universities found')).toBeInTheDocument()
  })

  test('should use custom value label', () => {
    render(
      <RankingsTable
        title="Top Partners"
        items={mockItems}
        valueLabel="Partnerships"
      />
    )

    expect(screen.getByText('Partnerships')).toBeInTheDocument()
  })

  test('should render badges when provided', () => {
    const itemsWithBadges = [
      { name: 'Project A', value: 100, badge: 'PRJ-001' },
    ]

    render(
      <RankingsTable
        title="High Impact Projects"
        items={itemsWithBadges}
      />
    )

    expect(screen.getByText('PRJ-001')).toBeInTheDocument()
  })

  test('should format large numbers with commas', () => {
    const itemsWithLargeNumbers = [
      { name: 'Project A', value: 1000 },
      { name: 'Project B', value: 10000 },
    ]

    render(
      <RankingsTable
        title="Impact Projects"
        items={itemsWithLargeNumbers}
      />
    )

    expect(screen.getByText('1,000')).toBeInTheDocument()
    expect(screen.getByText('10,000')).toBeInTheDocument()
  })
})

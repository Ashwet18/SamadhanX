/**
 * Tests for Challenge Form Component
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import { ChallengeForm } from '@/components/challenges/ChallengeForm'
import { challengeApi } from '@/lib/api/challenges'
import { UserRole } from '@/types/api'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('@/lib/api/challenges', () => ({
  challengeApi: {
    createChallenge: jest.fn(),
    updateChallenge: jest.fn(),
    uploadChallengeMedia: jest.fn(),
    getCategories: jest.fn(),
  },
}))

jest.mock('lucide-react', () => ({
  Upload: () => <div data-testid="upload-icon">Upload</div>,
  X: () => <div data-testid="x-icon">X</div>,
  MapPin: () => <div data-testid="mappin-icon">MapPin</div>,
  Loader2: () => <div data-testid="loader-icon">Loader2</div>,
  CheckCircle: () => <div data-testid="check-circle">CheckCircle</div>,
  AlertCircle: () => <div data-testid="alert-circle">AlertCircle</div>,
  Image: () => <div data-testid="image-icon">Image</div>,
  Video: () => <div data-testid="video-icon">Video</div>,
  Music: () => <div data-testid="music-icon">Music</div>,
  FileIcon: () => <div data-testid="file-icon">FileIcon</div>,
  FileText: () => <div data-testid="file-text-icon">FileText</div>,
  Info: () => <div data-testid="info-icon">Info</div>,
  AlertTriangle: () => <div data-testid="alert-triangle">AlertTriangle</div>,
}))

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
}

const mockCategories = [
  { id: 'cat-1', name: 'Education', description: 'Education issues', parent_id: null },
  { id: 'cat-2', name: 'Healthcare', description: 'Healthcare issues', parent_id: null },
]

describe('ChallengeForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(challengeApi.getCategories as jest.Mock).mockResolvedValue(mockCategories)
    // Mock window.scrollTo which is not implemented in jsdom
    window.scrollTo = jest.fn()
  })

  describe('Create Mode', () => {
    it('should render all form fields', async () => {
      render(<ChallengeForm mode="create" />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toBeInTheDocument()
      })

      expect(screen.getByLabelText(/detailed description/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/district/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/block/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/village/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /submit challenge/i })).toBeInTheDocument()
    })

    it('should validate required fields', async () => {
      const user = userEvent.setup()
      render(<ChallengeForm mode="create" />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toBeInTheDocument()
      })

      const submitButton = screen.getByRole('button', { name: /submit challenge/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument()
      })
      expect(screen.getByText(/description is required/i)).toBeInTheDocument()
      expect(screen.getByText(/district is required/i)).toBeInTheDocument()
    })

    it('should validate title length', async () => {
      const user = userEvent.setup()
      render(<ChallengeForm mode="create" />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toBeInTheDocument()
      })

      const titleInput = screen.getByLabelText(/challenge title/i)
      
      // Too short
      await user.type(titleInput, 'Short')
      const submitButton = screen.getByRole('button', { name: /submit challenge/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/title must be at least 10 characters/i)).toBeInTheDocument()
      })
    })

    it('should validate description length', async () => {
      const user = userEvent.setup()
      render(<ChallengeForm mode="create" />)

      await waitFor(() => {
        expect(screen.getByLabelText(/detailed description/i)).toBeInTheDocument()
      })

      const descriptionInput = screen.getByLabelText(/detailed description/i)
      
      // Too short
      await user.type(descriptionInput, 'Too short')
      const submitButton = screen.getByRole('button', { name: /submit challenge/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/description must be at least 30 characters/i)).toBeInTheDocument()
      })
    })

    it('should validate category selection', async () => {
      const user = userEvent.setup()
      render(<ChallengeForm mode="create" />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toBeInTheDocument()
      })

      // Fill required fields but don't select category
      await user.type(screen.getByLabelText(/challenge title/i), 'Valid Challenge Title')
      await user.type(
        screen.getByLabelText(/detailed description/i),
        'This is a valid description with more than thirty characters to pass validation'
      )

      const submitButton = screen.getByRole('button', { name: /submit challenge/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/at least one category is required/i)).toBeInTheDocument()
      })
    })

    it('should validate coordinate pairing', async () => {
      const user = userEvent.setup()
      render(<ChallengeForm mode="create" />)

      await waitFor(() => {
        expect(screen.getByLabelText(/latitude/i)).toBeInTheDocument()
      })

      // Enter only latitude
      await user.type(screen.getByLabelText(/latitude/i), '23.5')
      
      const submitButton = screen.getByRole('button', { name: /submit challenge/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/longitude is required when latitude is provided/i)).toBeInTheDocument()
      })
    })

    it('should create challenge successfully', async () => {
      const user = userEvent.setup()
      const mockChallenge = {
        id: 'challenge-1',
        challenge_code: 'CH-JH-2026-00001',
        title: 'Test Challenge',
        description: 'Test description',
        status: 'SUBMITTED',
        district: 'Ranchi',
        categories: [],
        media: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      ;(challengeApi.createChallenge as jest.Mock).mockResolvedValue(mockChallenge)

      const onSuccess = jest.fn()
      render(<ChallengeForm mode="create" onSuccess={onSuccess} />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toBeInTheDocument()
      })

      // Fill form
      await user.type(screen.getByLabelText(/challenge title/i), 'Valid Challenge Title')
      await user.type(
        screen.getByLabelText(/detailed description/i),
        'This is a valid description with more than thirty characters to pass validation'
      )
      
      // Select district
      const districtSelect = screen.getByLabelText(/district/i)
      await user.selectOptions(districtSelect, 'Ranchi')

      // Select category
      await waitFor(() => {
        expect(screen.getByText('Education')).toBeInTheDocument()
      })
      const eduCheckbox = screen.getByLabelText(/select education/i)
      await user.click(eduCheckbox)

      // Submit
      const submitButton = screen.getByRole('button', { name: /submit challenge/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(challengeApi.createChallenge).toHaveBeenCalled()
      })

      // Should show success message
      await waitFor(() => {
        expect(screen.getByText(/challenge submitted successfully/i)).toBeInTheDocument()
      })
    })

    it('should handle API errors', async () => {
      const user = userEvent.setup()
      ;(challengeApi.createChallenge as jest.Mock).mockRejectedValue({
        response: { data: { detail: 'Server error' } },
      })

      render(<ChallengeForm mode="create" />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toBeInTheDocument()
      })

      // Fill required fields
      await user.type(screen.getByLabelText(/challenge title/i), 'Valid Challenge Title')
      await user.type(
        screen.getByLabelText(/detailed description/i),
        'This is a valid description with more than thirty characters'
      )
      
      const districtSelect = screen.getByLabelText(/district/i)
      await user.selectOptions(districtSelect, 'Ranchi')

      // Select category
      await waitFor(() => {
        expect(screen.getByText('Education')).toBeInTheDocument()
      })
      await user.click(screen.getByLabelText(/select education/i))

      const submitButton = screen.getByRole('button', { name: /submit challenge/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/server error/i)).toBeInTheDocument()
      })
    })

    it('should prevent duplicate submission while submitting', async () => {
      const user = userEvent.setup()
      let resolveCreate: (value: any) => void
      const createPromise = new Promise((resolve) => {
        resolveCreate = resolve
      })
      ;(challengeApi.createChallenge as jest.Mock).mockReturnValue(createPromise)

      render(<ChallengeForm mode="create" />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toBeInTheDocument()
      })

      // Fill form
      await user.type(screen.getByLabelText(/challenge title/i), 'Valid Challenge Title')
      await user.type(
        screen.getByLabelText(/detailed description/i),
        'This is a valid description with more than thirty characters'
      )
      const districtSelect = screen.getByLabelText(/district/i)
      await user.selectOptions(districtSelect, 'Ranchi')

      await waitFor(() => {
        expect(screen.getByText('Education')).toBeInTheDocument()
      })
      await user.click(screen.getByLabelText(/select education/i))

      // Click submit
      const submitButton = screen.getByRole('button', { name: /submit challenge/i })
      await user.click(submitButton)

      // Button should be disabled
      await waitFor(() => {
        expect(submitButton).toBeDisabled()
      })

      // Resolve promise and wait for state update
      await waitFor(async () => {
        resolveCreate!({
          id: 'test',
          challenge_code: 'CH-JH-2026-00001',
          status: 'SUBMITTED',
        })
      })
    })
  })

  describe('Edit Mode', () => {
    const mockChallenge = {
      id: 'challenge-1',
      challenge_code: 'CH-JH-2026-00001',
      title: 'Existing Challenge',
      description: 'Existing description that is long enough to pass validation requirements',
      status: 'SUBMITTED' as const,
      district: 'Ranchi',
      block: 'Test Block',
      village: 'Test Village',
      latitude: 23.5,
      longitude: 85.5,
      affected_population: 1000,
      categories: [{ id: 'cat-1', name: 'Education', description: '', parent_id: null }],
      media: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    it('should pre-fill form with existing data', async () => {
      render(<ChallengeForm mode="edit" challenge={mockChallenge} />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toHaveValue('Existing Challenge')
      })

      expect(screen.getByLabelText(/detailed description/i)).toHaveValue(mockChallenge.description)
      expect(screen.getByLabelText(/district/i)).toHaveValue('Ranchi')
      expect(screen.getByLabelText(/block/i)).toHaveValue('Test Block')
      expect(screen.getByLabelText(/village/i)).toHaveValue('Test Village')
    })

    it('should update challenge successfully', async () => {
      const user = userEvent.setup()
      const updatedChallenge = { ...mockChallenge, title: 'Updated Title' }
      ;(challengeApi.updateChallenge as jest.Mock).mockResolvedValue(updatedChallenge)

      const onSuccess = jest.fn()
      render(<ChallengeForm mode="edit" challenge={mockChallenge} onSuccess={onSuccess} />)

      await waitFor(() => {
        expect(screen.getByLabelText(/challenge title/i)).toBeInTheDocument()
      })

      // Modify title
      const titleInput = screen.getByLabelText(/challenge title/i)
      await user.clear(titleInput)
      await user.type(titleInput, 'Updated Title Here')

      // Submit
      const submitButton = screen.getByRole('button', { name: /save changes/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(challengeApi.updateChallenge).toHaveBeenCalled()
      })
    })
  })
})

/**
 * Challenge validation utilities
 * Matches backend validation constraints exactly
 */

export interface ChallengeValidationErrors {
  title?: string
  description?: string
  district?: string
  block?: string
  village?: string
  latitude?: string
  longitude?: string
  affected_population?: string
  category_ids?: string
}

/**
 * Validate challenge title
 * Backend: min 10, max 500 characters, cannot be blank/whitespace
 */
export function validateTitle(title: string): string | undefined {
  const trimmed = title.trim()
  
  if (!trimmed) {
    return 'Title is required'
  }
  
  if (trimmed.length < 10) {
    return 'Title must be at least 10 characters'
  }
  
  if (trimmed.length > 500) {
    return 'Title must not exceed 500 characters'
  }
  
  return undefined
}

/**
 * Validate challenge description
 * Backend: min 30, max 5000 characters, cannot be blank/whitespace
 */
export function validateDescription(description: string): string | undefined {
  const trimmed = description.trim()
  
  if (!trimmed) {
    return 'Description is required'
  }
  
  if (trimmed.length < 30) {
    return 'Description must be at least 30 characters'
  }
  
  if (trimmed.length > 5000) {
    return 'Description must not exceed 5000 characters'
  }
  
  return undefined
}

/**
 * Validate district name
 * Backend: min 2, max 100 characters, cannot be blank/whitespace
 */
export function validateDistrict(district: string): string | undefined {
  const trimmed = district.trim()
  
  if (!trimmed) {
    return 'District is required'
  }
  
  if (trimmed.length < 2) {
    return 'District must be at least 2 characters'
  }
  
  if (trimmed.length > 100) {
    return 'District must not exceed 100 characters'
  }
  
  return undefined
}

/**
 * Validate block name (optional)
 * Backend: max 100 characters, cannot be whitespace-only
 */
export function validateBlock(block: string | undefined): string | undefined {
  if (!block) return undefined
  
  const trimmed = block.trim()
  if (!trimmed) {
    return 'Block cannot be whitespace only'
  }
  
  if (trimmed.length > 100) {
    return 'Block must not exceed 100 characters'
  }
  
  return undefined
}

/**
 * Validate village name (optional)
 * Backend: max 100 characters, cannot be whitespace-only
 */
export function validateVillage(village: string | undefined): string | undefined {
  if (!village) return undefined
  
  const trimmed = village.trim()
  if (!trimmed) {
    return 'Village cannot be whitespace only'
  }
  
  if (trimmed.length > 100) {
    return 'Village must not exceed 100 characters'
  }
  
  return undefined
}

/**
 * Validate GPS coordinates
 * Backend: latitude -90 to 90, longitude -180 to 180
 * Both must be provided together
 */
export function validateCoordinates(
  latitude: number | null,
  longitude: number | null
): { latitude?: string; longitude?: string } {
  const errors: { latitude?: string; longitude?: string } = {}
  
  // If one is provided, both must be provided
  if (latitude !== null && longitude === null) {
    errors.longitude = 'Longitude is required when latitude is provided'
  }
  
  if (longitude !== null && latitude === null) {
    errors.latitude = 'Latitude is required when longitude is provided'
  }
  
  // Validate ranges
  if (latitude !== null) {
    if (latitude < -90 || latitude > 90) {
      errors.latitude = 'Latitude must be between -90 and 90'
    }
  }
  
  if (longitude !== null) {
    if (longitude < -180 || longitude > 180) {
      errors.longitude = 'Longitude must be between -180 and 180'
    }
  }
  
  return errors
}

/**
 * Validate affected population (optional)
 * Backend: 0 to 10,000,000
 */
export function validateAffectedPopulation(
  population: number | undefined
): string | undefined {
  if (population === undefined || population === null) return undefined
  
  if (population < 0) {
    return 'Affected population cannot be negative'
  }
  
  if (population > 10000000) {
    return 'Affected population must not exceed 10,000,000'
  }
  
  return undefined
}

/**
 * Validate category selection
 * Backend: at least one category required
 */
export function validateCategories(categoryIds: string[]): string | undefined {
  if (!categoryIds || categoryIds.length === 0) {
    return 'At least one category is required'
  }
  
  return undefined
}

/**
 * Validate entire challenge form
 * Returns all validation errors
 */
export function validateChallengeForm(data: {
  title: string
  description: string
  district: string
  block?: string
  village?: string
  latitude?: number | null
  longitude?: number | null
  affected_population?: number
  category_ids: string[]
}): ChallengeValidationErrors {
  const errors: ChallengeValidationErrors = {}
  
  const titleError = validateTitle(data.title)
  if (titleError) errors.title = titleError
  
  const descriptionError = validateDescription(data.description)
  if (descriptionError) errors.description = descriptionError
  
  const districtError = validateDistrict(data.district)
  if (districtError) errors.district = districtError
  
  const blockError = validateBlock(data.block)
  if (blockError) errors.block = blockError
  
  const villageError = validateVillage(data.village)
  if (villageError) errors.village = villageError
  
  const coordErrors = validateCoordinates(
    data.latitude ?? null,
    data.longitude ?? null
  )
  if (coordErrors.latitude) errors.latitude = coordErrors.latitude
  if (coordErrors.longitude) errors.longitude = coordErrors.longitude
  
  const populationError = validateAffectedPopulation(data.affected_population)
  if (populationError) errors.affected_population = populationError
  
  const categoryError = validateCategories(data.category_ids)
  if (categoryError) errors.category_ids = categoryError
  
  return errors
}

/**
 * Check if there are any validation errors
 */
export function hasValidationErrors(errors: ChallengeValidationErrors): boolean {
  return Object.keys(errors).length > 0
}

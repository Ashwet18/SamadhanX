/**
 * TypeScript type definitions for SamadhanX API
 * 
 * These types define the structure of data exchanged between
 * the frontend and backend API.
 */

// Base types
export type UUID = string
export type ISODateTime = string
export type Email = string
export type PhoneNumber = string
export type URL = string

// User roles enum
export enum UserRole {
  CITIZEN = 'CITIZEN',
  GOVERNMENT_OFFICER = 'GOVERNMENT_OFFICER',
  UNIVERSITY_ADMIN = 'UNIVERSITY_ADMIN',
  FACULTY = 'FACULTY',
  STUDENT = 'STUDENT',
  INDUSTRY = 'INDUSTRY',
  MENTOR = 'MENTOR',
  CSR = 'CSR',
  RESEARCHER = 'RESEARCHER',
  PLATFORM_ADMIN = 'PLATFORM_ADMIN'
}

// Challenge status enum
export enum ChallengeStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  AI_ANALYSIS = 'AI_ANALYSIS',
  PENDING_REVIEW = 'PENDING_REVIEW',
  VALIDATED = 'VALIDATED',
  MATCHING = 'MATCHING',
  UNIVERSITY_INVITED = 'UNIVERSITY_INVITED',
  ACCEPTED = 'ACCEPTED',
  PROJECT_CREATED = 'PROJECT_CREATED',
  REJECTED = 'REJECTED',
  DUPLICATE = 'DUPLICATE',
  ON_HOLD = 'ON_HOLD',
  CANCELLED = 'CANCELLED'
}

// Project status enum
export enum ProjectStatus {
  DRAFT = 'DRAFT',
  TEAM_FORMED = 'TEAM_FORMED',
  PROPOSAL_SUBMITTED = 'PROPOSAL_SUBMITTED',
  APPROVED = 'APPROVED',
  PROTOTYPE = 'PROTOTYPE',
  TESTING = 'TESTING',
  PILOT = 'PILOT',
  DEPLOYED = 'DEPLOYED',
  IMPACT_MEASURED = 'IMPACT_MEASURED',
  COMPLETED = 'COMPLETED',
  SUSPENDED = 'SUSPENDED',
  CANCELLED = 'CANCELLED'
}

// Priority levels
export enum Priority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

// Account status enum (matches backend)
export enum AccountStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  SUSPENDED = 'SUSPENDED',
  PENDING = 'PENDING'
}

// Media type enum (matches backend)
export enum MediaType {
  IMAGE = 'IMAGE',
  VIDEO = 'VIDEO',
  AUDIO = 'AUDIO',
  DOCUMENT = 'DOCUMENT'
}

// User related types (matches backend auth schemas)
export interface User {
  id: UUID
  name: string  // Backend uses single 'name' field, not first_name/last_name
  email: Email
  phone?: PhoneNumber
  account_status: AccountStatus
  roles: string[]  // Array of role names
  created_at: ISODateTime
  updated_at: ISODateTime
  // Profile indicators
  is_citizen: boolean
  is_government_officer: boolean
  is_faculty: boolean
  is_student: boolean
  // Government officer details (if applicable)
  government_employee_id?: string
  government_department?: string
  government_designation?: string
}

export interface AuthTokens {
  access_token: string
  token_type: string
}

export interface LoginCredentials {
  email: Email
  password: string
}

export interface RegisterData {
  name: string  // Backend requires single 'name' field
  email: Email
  phone?: PhoneNumber
  password: string
  role: UserRole
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// Challenge related types (matches backend schemas)
export interface Challenge {
  id: UUID
  challenge_code: string  // Format: CH-JH-YYYY-XXXXX
  title: string
  description: string
  status: ChallengeStatus
  priority_score?: number
  priority_level?: Priority
  // Location fields (Jharkhand-specific)
  district: string
  block?: string
  village?: string
  latitude?: number
  longitude?: number
  affected_population?: number
  categories: Category[]
  media: MediaFile[]
  submitted_by?: UUID
  submitter_name?: string
  created_at: ISODateTime
  updated_at: ISODateTime
}

export interface ChallengeCreate {
  title: string  // Min 10, max 500 chars
  description: string  // Min 30, max 5000 chars
  district: string  // Min 2, max 100 chars
  block?: string  // Max 100 chars
  village?: string  // Max 100 chars
  latitude?: number  // -90 to 90
  longitude?: number  // -180 to 180
  affected_population?: number  // 0 to 10,000,000
  category_ids: UUID[]  // At least 1 required
}

export interface ChallengeUpdate {
  title?: string
  description?: string
  status?: ChallengeStatus
  priority?: Priority
  location?: string
  category_ids?: UUID[]
}

export interface ChallengeAIAnalysis {
  id: UUID
  challenge_id: UUID
  classification: string[]
  severity_score: number
  urgency_score: number
  complexity_score: number
  required_skills: string[]
  estimated_timeline: string
  potential_impact: string
  similar_challenges: UUID[]
  university_matches: UniversityMatch[]
  analysis_confidence: number
  created_at: ISODateTime
}

export interface Category {
  id: UUID
  name: string
  description: string
  parent_id?: UUID
  color_code?: string
  icon?: string
  is_active: boolean
}

// University related types
export interface University {
  id: UUID
  name: string
  short_name: string
  description?: string
  address: string
  city: string
  state: string
  pincode: string
  website?: URL
  logo_url?: URL
  is_active: boolean
  established_year?: number
  type: 'PUBLIC' | 'PRIVATE' | 'DEEMED'
  accreditation?: string[]
  created_at: ISODateTime
}

export interface Department {
  id: UUID
  university_id: UUID
  name: string
  short_name: string
  description?: string
  head_of_department?: UUID
  is_active: boolean
}

export interface Faculty {
  id: UUID
  user_id: UUID
  university_id: UUID
  department_id: UUID
  designation: string
  qualification: string[]
  expertise_areas: string[]
  research_interests: string[]
  publications?: string[]
  is_available: boolean
}

export interface Student {
  id: UUID
  user_id: UUID
  university_id: UUID
  department_id: UUID
  student_id: string
  program: string
  year: number
  cgpa?: number
  skills: string[]
  interests: string[]
  is_available: boolean
}

export interface UniversityMatch {
  university_id: UUID
  university_name: string
  match_score: number
  reasons: string[]
  matching_faculty: UUID[]
  matching_departments: UUID[]
  available_resources: string[]
}

// Project related types
export interface Project {
  id: UUID
  title: string
  description: string
  challenge_id: UUID
  university_id: UUID
  status: ProjectStatus
  start_date: ISODateTime
  end_date?: ISODateTime
  budget?: number
  funding_source?: string
  team_members: ProjectMember[]
  milestones: ProjectMilestone[]
  deliverables: ProjectDeliverable[]
  created_at: ISODateTime
  updated_at: ISODateTime
}

export interface ProjectMember {
  id: UUID
  project_id: UUID
  user_id: UUID
  role: 'LEAD' | 'MEMBER' | 'ADVISOR'
  joined_at: ISODateTime
  is_active: boolean
}

export interface ProjectMilestone {
  id: UUID
  project_id: UUID
  title: string
  description: string
  due_date: ISODateTime
  completion_date?: ISODateTime
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'OVERDUE'
  deliverables?: string[]
}

export interface ProjectDeliverable {
  id: UUID
  project_id: UUID
  milestone_id?: UUID
  title: string
  description: string
  file_url?: URL
  submitted_by: UUID
  submitted_at: ISODateTime
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED'
}

// Industry related types
export interface IndustryPartner {
  id: UUID
  name: string
  description?: string
  industry_type: string
  website?: URL
  logo_url?: URL
  contact_person: string
  contact_email: Email
  contact_phone: PhoneNumber
  expertise_areas: string[]
  csr_focus: string[]
  is_active: boolean
}

export interface Partnership {
  id: UUID
  project_id: UUID
  industry_partner_id: UUID
  type: 'FUNDING' | 'MENTORSHIP' | 'RESOURCES' | 'DEPLOYMENT'
  description: string
  start_date: ISODateTime
  end_date?: ISODateTime
  value?: number
  status: 'PROPOSED' | 'ACTIVE' | 'COMPLETED' | 'TERMINATED'
}

// Notification types
export interface Notification {
  id: UUID
  user_id: UUID
  title: string
  message: string
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR'
  is_read: boolean
  action_url?: URL
  metadata?: Record<string, any>
  created_at: ISODateTime
}

// Analytics types
export interface DashboardMetrics {
  total_challenges: number
  active_projects: number
  participating_universities: number
  industry_partnerships: number
  challenges_by_status: Record<ChallengeStatus, number>
  projects_by_status: Record<ProjectStatus, number>
  monthly_submissions: Array<{
    month: string
    challenges: number
    projects: number
  }>
  top_categories: Array<{
    category: string
    count: number
  }>
  geographic_distribution: Array<{
    location: string
    count: number
    coordinates: [number, number]
  }>
}

// API response wrappers
export interface ApiResponse<T> {
  data?: T
  message: string
  success: boolean
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface ApiError {
  message: string
  error_code?: string
  details?: Record<string, any>
  success: false
}

// Form types
export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface FilterParams {
  search?: string
  status?: string
  category?: string
  location?: string
  date_from?: string
  date_to?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface ChallengeFilters extends FilterParams {
  status?: ChallengeStatus
  priority?: Priority
  category_id?: UUID
  submitted_by?: UUID
  assigned_to?: UUID
}

export interface ProjectFilters extends FilterParams {
  status?: ProjectStatus
  university_id?: UUID
  challenge_id?: UUID
  team_member?: UUID
}

// File upload types
export interface FileUpload {
  file: File
  progress?: number
  status?: 'pending' | 'uploading' | 'completed' | 'error'
  url?: string
  error?: string
}

export interface MediaFile {
  id: UUID
  filename: string
  original_name: string
  file_size: number
  mime_type: string
  url: URL
  thumbnail_url?: URL
  uploaded_by: UUID
  created_at: ISODateTime
}
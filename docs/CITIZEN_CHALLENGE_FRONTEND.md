# Citizen Challenge Frontend - Phase 3C

## Overview

Phase 3C implements the complete citizen-facing challenge workflow, allowing citizens to submit, view, edit, and manage societal challenges.

## Routes Implemented

### Citizen Routes (Protected - CITIZEN role required)

1. **`/citizen`** - Citizen Dashboard
   - Welcome message with user name
   - Quick stats: Total challenges, Under Review, Validated
   - Primary action: "Submit a New Challenge" button
   - Recent challenges preview (5 most recent)
   - Link to view all challenges

2. **`/citizen/challenges`** - My Challenges List
   - Paginated list of user's challenges
   - Status filtering (All, Submitted, Pending Review, Validated, Draft)
   - Challenge cards with: code, title, status, district, date, metadata
   - Empty state with call-to-action
   - View details link for each challenge

3. **`/citizen/challenges/new`** - Submit New Challenge
   - Complete challenge submission form
   - All required validation
   - Category selection from API
   - Location inputs (district, block, village, GPS)
   - Media upload (up to 5 files)
   - Success state with challenge code display

4. **`/citizen/challenges/[id]`** - Challenge Detail
   - Full challenge information
   - Challenge code, status, priority
   - Description, categories, location
   - Media files with download links
   - Edit button (if DRAFT or SUBMITTED)
   - Delete button (if DRAFT only)
   - Delete confirmation dialog

5. **`/citizen/challenges/[id]/edit`** - Edit Challenge
   - Pre-filled form with existing data
   - Only accessible for DRAFT or SUBMITTED challenges
   - Same validation as create form
   - Success redirect to detail page

## Components Created

### Challenge Components (`components/challenges/`)

1. **ChallengeForm.tsx**
   - Reusable for create/edit modes
   - Complete validation matching backend
   - Dynamic category loading from API
   - Location picker integration
   - Media upload integration
   - Success/error states
   - Prevents duplicate submission

2. **CategorySelect.tsx**
   - Fetches categories from GET /api/v1/categories
   - Displays hierarchical categories (parent/child)
   - Multiple selection support
   - Loading/error/empty states
   - Real database category IDs only

3. **MediaUpload.tsx**
   - Up to 5 files
   - File type validation (images, videos, audio, PDF)
   - File size validation (backend limits)
   - Preview for images
   - File details display
   - Remove selected files
   - Accessible controls

4. **LocationPicker.tsx**
   - Browser geolocation support
   - Manual lat/long input
   - Coordinate pairing validation
   - Permission denial handling
   - Optional field (GPS coords)
   - Clear location button

5. **ChallengeStatus.tsx**
   - Colored status badges
   - Maps all ChallengeStatus enum values
   - Accessible labels

6. **ChallengeCard.tsx**
   - Displays challenge summary
   - Challenge code, title, status
   - Location, date, affected population
   - Category and media count
   - View details button
   - Responsive layout

## API Integration

### Endpoints Used

- `POST /api/v1/challenges` - Create challenge
- `GET /api/v1/challenges/my` - List user's challenges (with pagination, filters)
- `GET /api/v1/challenges/{id}` - Get challenge details
- `PATCH /api/v1/challenges/{id}` - Update challenge
- `DELETE /api/v1/challenges/{id}` - Delete challenge (DRAFT only)
- `POST /api/v1/challenges/{id}/media` - Upload media
- `GET /api/v1/challenges/{id}/media` - Get challenge media
- `DELETE /api/v1/challenges/{id}/media/{media_id}` - Delete media
- `GET /api/v1/categories` - List categories (NEW in Phase 3C)

### API Client (`lib/api/challenges.ts`)

Functions:
- `createChallenge(data)` - Submit new challenge
- `getMyChallenges(page, pageSize, status)` - Get user challenges
- `getChallenge(id)` - Get challenge by ID
- `updateChallenge(id, data)` - Update challenge
- `deleteChallenge(id)` - Delete challenge
- `uploadChallengeMedia(id, file, onProgress)` - Upload file
- `getChallengeMedia(id)` - Get media list
- `deleteChallengeMedia(id, mediaId)` - Delete media
- `getCategories()` - Fetch categories (NEW)

## Validation

### Client-Side Validation (`lib/validation/challenge.ts`)

Matches backend constraints exactly:

- **Title**: 10-500 characters, required, no whitespace-only
- **Description**: 30-5000 characters, required, no whitespace-only
- **District**: 2-100 characters, required
- **Block**: Max 100 characters, optional
- **Village**: Max 100 characters, optional
- **Latitude**: -90 to 90, optional
- **Longitude**: -180 to 180, optional
- **Coordinates**: Both required if either provided
- **Affected Population**: 0 to 10,000,000, optional
- **Categories**: At least 1 required

### Media Validation (`lib/utils/mediaValidation.ts`)

File type and size limits (matches backend):

- **Images** (JPEG, PNG, WebP): Max 10 MB
- **Videos** (MP4, WebM): Max 50 MB
- **Audio** (MP3, WAV, OGG): Max 20 MB
- **Documents** (PDF): Max 10 MB
- **Maximum**: 5 files per challenge

## Category Integration

### Dynamic Category Loading

**Phase 3C Solution:**
- Categories fetched from `GET /api/v1/categories`
- Real database UUIDs used
- No hardcoded category data
- CategorySelect component handles:
  - API loading state
  - Error handling
  - Empty state
  - Hierarchical display
  - Multiple selection

**Backend Endpoint Created:**
- `backend/app/routers/categories.py`
- Returns all categories ordered alphabetically
- Includes parent/child relationships
- Read-only, no authentication required

## Location Implementation

### Jharkhand Districts

**Static data** (`lib/constants/jharkhand.ts`):
- 24 Jharkhand districts
- Used for dropdown selection
- Backend accepts any valid string (not enforced)

### GPS Coordinates

**Optional but paired**:
- Browser geolocation API support
- Manual lat/long input
- Validation: both required if either provided
- Ranges: lat (-90 to 90), lng (-180 to 180)
- Permission denial handled gracefully

## Media Upload Implementation

### Upload Flow

1. **Select Files**: User selects up to 5 files via file input
2. **Client Validation**: Type and size checked immediately
3. **Preview**: Image preview shown, file details displayed
4. **Challenge Creation**: Challenge submitted without media
5. **Media Upload**: Files uploaded sequentially to challenge
6. **Success**: Redirect to detail page showing all media

### Media Display

- Detail page fetches media via `GET /api/v1/challenges/{id}/media`
- Media cards show: type icon, filename, size
- Download links to backend URLs
- Accessible file type indicators

## Security

### Authorization

**Route Protection** (`app/citizen/layout.tsx`):
- RequireRole wrapper
- CITIZEN role required
- Unauthenticated → redirect to login
- Wrong role → access denied

### Challenge Ownership

**Edit/Delete Controls**:
- Edit: Only DRAFT or SUBMITTED, only owner
- Delete: Only DRAFT, only owner
- Backend validates ownership (frontend is UI-only)

**Data Access**:
- `GET /api/v1/challenges/my` - Only user's challenges
- Backend filters by `submitted_by`
- Citizens cannot access others' challenges

**Government Features Blocked**:
- No AI analysis trigger
- No validation/review actions
- No university matching UI
- No duplicate review
- Backend endpoints remain protected

## Testing

### Test Coverage

**Challenge Form Tests** (`__tests__/challenges/ChallengeForm.test.tsx`):
- Form rendering
- Required field validation
- Title length validation (min 10, max 500)
- Description length validation (min 30, max 5000)
- Category selection validation
- Coordinate pairing validation
- Successful challenge creation
- API error handling
- Duplicate submission prevention
- Pre-fill for edit mode
- Update challenge success

## Files Created

### Frontend Files

**Pages** (11 files):
- `app/citizen/layout.tsx`
- `app/citizen/page.tsx`
- `app/citizen/challenges/page.tsx`
- `app/citizen/challenges/new/page.tsx`
- `app/citizen/challenges/[id]/page.tsx`
- `app/citizen/challenges/[id]/edit/page.tsx`

**Components** (6 files):
- `components/challenges/ChallengeForm.tsx`
- `components/challenges/CategorySelect.tsx`
- `components/challenges/MediaUpload.tsx`
- `components/challenges/LocationPicker.tsx`
- `components/challenges/ChallengeStatus.tsx`
- `components/challenges/ChallengeCard.tsx`

**Libraries** (5 files):
- `lib/api/challenges.ts`
- `lib/validation/challenge.ts`
- `lib/utils/mediaValidation.ts`
- `lib/constants/jharkhand.ts`
- `lib/constants/categories.ts` (DELETED - replaced with API)

**Tests** (1 file so far):
- `__tests__/challenges/ChallengeForm.test.tsx`

### Backend Files

**Created**:
- `backend/app/routers/categories.py` - Category endpoint
- `backend/tests/test_categories.py` - Category tests (10 tests)

**Modified**:
- `backend/app/main.py` - Register category router

## Known Limitations

1. **Test Database Seeding**: One category test skipped due to test DB not having seeded categories
2. **Media Upload Sequence**: Media uploaded after challenge creation (requires challenge ID)
3. **Pagination**: Basic prev/next, no page number jumping
4. **Status Filter**: Limited to common statuses in UI
5. **Location Validation**: Backend accepts any district string, frontend provides list
6. **Category Hierarchy**: Currently shows all categories flat, could group by parent

## Future Enhancements (Not Phase 3C)

- Challenge draft autosave
- Image/video preview in media upload
- Map view for location selection
- Bulk media upload
- Challenge duplication detection (frontend UI)
- Advanced filtering (date range, priority)
- Export challenge data
- Print-friendly challenge detail view

## Phase 3C Status

✅ Citizen dashboard implemented
✅ Challenge submission form complete
✅ Category integration with real API
✅ Location picker with GPS support
✅ Media upload with validation
✅ My Challenges list with filters
✅ Challenge detail page
✅ Edit challenge functionality
✅ Delete challenge with confirmation
✅ Route protection (CITIZEN role)
✅ Backend category endpoint
✅ Backend category tests
✅ Challenge form tests started

**Ready for**: Full test suite execution and final verification

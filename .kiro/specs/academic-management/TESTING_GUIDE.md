# Curriculum Management - Manual Testing Guide

## Prerequisites
- Django server running
- Test users created for different roles (super_admin, subject_teacher, student)
- Sample subjects and school classes created
- Sample terms created

## Test Scenarios

### 1. Curriculum Management (Super Admin/Teacher)

#### Test 1.1: Create New Curriculum
**Steps:**
1. Login as super_admin or subject_teacher
2. Navigate to `/academic/curriculum/`
3. Click "Create Curriculum" button
4. Fill in the form:
   - Title: "Grade 10 Science Curriculum 2024-2025"
   - Description: "Comprehensive science curriculum for grade 10"
   - Academic Year: "2024-2025"
   - Select subjects (e.g., Biology, Chemistry, Physics)
   - Leave "Published" unchecked for now
5. Add Learning Objectives:
   - Click "Add Objective"
   - Title: "Understand cell structure"
   - Description: "Students will learn about cell organelles and their functions"
   - Subject: Biology
   - Grade Level: "Grade 10"
   - Order: 1
6. Add Syllabus Content:
   - Click "Add Content"
   - Subject: Biology
   - Content: "Introduction to Cell Biology..."
   - Order: 1
7. Click "Create Curriculum"

**Expected Result:**
- Curriculum created successfully
- Redirected to curriculum detail page
- All information displayed correctly
- Status shows "Draft"

#### Test 1.2: Edit Curriculum
**Steps:**
1. From curriculum detail page, click "Edit"
2. Modify title to "Grade 10 Science Curriculum 2024-2025 (Updated)"
3. Add another learning objective
4. Check "Published" checkbox
5. Click "Edit Curriculum"

**Expected Result:**
- Curriculum updated successfully
- Status changes to "Published"
- New learning objective appears in the list

#### Test 1.3: View Curriculum List
**Steps:**
1. Navigate to `/academic/curriculum/`
2. Test search functionality:
   - Enter "Science" in search box
   - Click "Filter"
3. Test academic year filter:
   - Select "2024-2025"
   - Click "Filter"
4. Test subject filter:
   - Select "Biology"
   - Click "Filter"

**Expected Result:**
- Search returns relevant curricula
- Filters work correctly
- Pagination works if more than 10 curricula

### 2. Lesson Planning (Teacher)

#### Test 2.1: Create Lesson Plan
**Steps:**
1. Login as subject_teacher
2. Navigate to `/academic/lesson-plans/`
3. Click "Create Lesson Plan"
4. Fill in the form:
   - Title: "Introduction to Cell Biology"
   - Curriculum: Select the published curriculum
   - Subject: Biology
   - School Class: Select a class
   - Learning Objectives: Check relevant objectives
   - Content: "Today we will learn about..."
   - Resources: "Textbook pages 45-50, Microscope"
   - Estimated Duration: "01:30:00"
   - Leave "Completed" unchecked
5. Click "Create Lesson Plan"

**Expected Result:**
- Lesson plan created successfully
- Redirected to lesson plan detail page
- All information displayed correctly

#### Test 2.2: Mark Lesson as Completed
**Steps:**
1. From lesson plan detail page
2. Click "Mark as Completed" button

**Expected Result:**
- Status changes to "Completed"
- Completion date is set
- Coverage tracking is updated automatically

#### Test 2.3: View Lesson Plan List
**Steps:**
1. Navigate to `/academic/lesson-plans/`
2. Test filters:
   - Filter by curriculum
   - Filter by subject
   - Filter by class
   - Filter by completion status

**Expected Result:**
- All filters work correctly
- Lesson plans are displayed with correct information
- Completion status is visible

### 3. Coverage Tracking

#### Test 3.1: View Coverage Report
**Steps:**
1. Login as subject_teacher or super_admin
2. Navigate to `/academic/coverage-report/`
3. Select a curriculum
4. Select a class
5. Click "Generate Report"

**Expected Result:**
- Coverage report is displayed
- Shows percentage completion for each learning objective
- Highlights at-risk objectives (< 50% completion)
- Shows total coverage percentage
- Lists remaining objectives

#### Test 3.2: Verify Coverage Updates
**Steps:**
1. Create a lesson plan with specific learning objectives
2. Mark the lesson as completed
3. View coverage report for that curriculum and class

**Expected Result:**
- Coverage percentage increases for the associated objectives
- Completed lessons count increases
- Completion percentage is calculated correctly

### 4. Role-Based Access Control

#### Test 4.1: Super Admin Access
**Steps:**
1. Login as super_admin
2. Try to access all curriculum management features

**Expected Result:**
- Can view all curricula
- Can create new curricula
- Can edit any curriculum
- Can view all lesson plans
- Can view all coverage reports

#### Test 4.2: Subject Teacher Access
**Steps:**
1. Login as subject_teacher
2. Try to access curriculum management features

**Expected Result:**
- Can view curricula for their subjects only
- Can create curricula for their subjects
- Can edit only their own curricula
- Can create lesson plans for their subjects and classes
- Can view only their own lesson plans
- Can view coverage reports for their subjects and classes

#### Test 4.3: Student Access
**Steps:**
1. Login as student
2. Try to access curriculum management URLs directly

**Expected Result:**
- Cannot access curriculum list
- Cannot create curricula
- Cannot create lesson plans
- Redirected to dashboard with error message

### 5. Data Validation

#### Test 5.1: Curriculum Validation
**Steps:**
1. Try to create a curriculum without a title
2. Try to publish a curriculum without learning objectives
3. Try to create a curriculum with invalid academic year format

**Expected Result:**
- Form validation errors are displayed
- Cannot save invalid data
- Helpful error messages are shown

#### Test 5.2: Lesson Plan Validation
**Steps:**
1. Try to create a lesson plan without selecting a curriculum
2. Try to create a lesson plan with a subject not in the curriculum
3. Try to create a lesson plan with a class the teacher doesn't teach

**Expected Result:**
- Form validation errors are displayed
- Cannot save invalid data
- Helpful error messages are shown

### 6. Integration Tests

#### Test 6.1: Complete Workflow
**Steps:**
1. Create a curriculum with learning objectives
2. Publish the curriculum
3. Create multiple lesson plans for different objectives
4. Mark some lessons as completed
5. View coverage report

**Expected Result:**
- All steps complete successfully
- Coverage report shows accurate data
- Completed lessons are reflected in coverage percentages

#### Test 6.2: Multi-Subject Curriculum
**Steps:**
1. Create a curriculum with multiple subjects
2. Add learning objectives for each subject
3. Add syllabus content for each subject
4. Create lesson plans for different subjects
5. View coverage report

**Expected Result:**
- All subjects are handled correctly
- Learning objectives are grouped by subject
- Syllabus content is grouped by subject
- Coverage is tracked separately for each subject

### 7. UI/UX Tests

#### Test 7.1: Responsive Design
**Steps:**
1. Access curriculum management on different devices:
   - Desktop (1920x1080)
   - Tablet (768x1024)
   - Mobile (375x667)

**Expected Result:**
- All pages are responsive
- Forms are usable on all devices
- Tables adapt to smaller screens
- Navigation works on all devices

#### Test 7.2: User Experience
**Steps:**
1. Navigate through the curriculum management workflow
2. Check for:
   - Clear navigation
   - Helpful error messages
   - Confirmation messages
   - Loading indicators
   - Intuitive form layouts

**Expected Result:**
- User experience is smooth and intuitive
- No confusing elements
- Clear feedback for all actions

## Common Issues and Solutions

### Issue 1: "Cannot publish curriculum without learning objectives"
**Solution:** Add at least one learning objective before publishing

### Issue 2: "Teacher not authorized to teach this subject"
**Solution:** Ensure the teacher is assigned to the subject in the admin panel

### Issue 3: "Coverage not updating"
**Solution:** Ensure lesson plans are marked as completed, not just saved

### Issue 4: "Cannot see curriculum in list"
**Solution:** Check if curriculum is published and if user has permission to view it

## Performance Tests

### Test P.1: Large Dataset
**Steps:**
1. Create 100+ curricula
2. Create 1000+ lesson plans
3. Test list views with pagination
4. Test search and filter performance

**Expected Result:**
- Pages load within 2 seconds
- Pagination works smoothly
- Search and filters are responsive

### Test P.2: Coverage Calculation
**Steps:**
1. Create a curriculum with 50+ learning objectives
2. Create 200+ lesson plans
3. Generate coverage report

**Expected Result:**
- Report generates within 3 seconds
- Calculations are accurate
- No timeout errors

## Conclusion

After completing all tests, verify:
- ✅ All CRUD operations work correctly
- ✅ Role-based access control is functioning
- ✅ Data validation is working
- ✅ Coverage tracking is accurate
- ✅ UI is responsive and user-friendly
- ✅ Performance is acceptable

If all tests pass, the Curriculum Management system is ready for production use.

# Accessing Curriculum Management

## Navigation Links Added

I've added navigation links to access the Curriculum Management system from the dashboards.

### For Subject Teachers

After logging in as a subject teacher, you'll see these new buttons in the "Quick Actions" section:

1. **📚 Curriculum Management** - Access the curriculum list
2. **📝 Lesson Plans** - View and create lesson plans
3. **📈 Coverage Reports** - Track curriculum coverage

**Direct URLs:**
- Curriculum List: `/academic/curriculum/`
- Lesson Plans: `/academic/lesson-plans/`
- Coverage Reports: `/academic/coverage-report/`
- Assignments: `/academic/assignments/`

### For Super Admins

After logging in as super admin, you'll see these new buttons in the "Academic Management" section:

1. **Curriculum Management** - Manage all curricula
2. **Lesson Plans** - View all lesson plans
3. **Coverage Reports** - View all coverage reports
4. **Assignments** - Manage all assignments

**Direct URLs:**
- Same as above

## How to Access

### Method 1: Dashboard Buttons (Recommended)
1. Log in to the system
2. You'll be redirected to your dashboard
3. Look for the "Quick Actions" section (teachers) or "Academic Management" section (admins)
4. Click on the relevant button

### Method 2: Direct URL
1. Log in to the system
2. Type the URL directly in your browser:
   - For curriculum list: `http://your-domain/academic/curriculum/`
   - For lesson plans: `http://your-domain/academic/lesson-plans/`
   - For coverage reports: `http://your-domain/academic/coverage-report/`

### Method 3: Bookmark
1. Navigate to the curriculum management page
2. Bookmark it in your browser for quick access

## What You'll See

### Subject Teachers
- **Curriculum List**: Only curricula for subjects you teach
- **Lesson Plans**: Only your lesson plans
- **Coverage Reports**: Reports for your subjects and classes
- **Create Buttons**: Available for creating new curricula and lesson plans

### Super Admins
- **Curriculum List**: All curricula in the system
- **Lesson Plans**: All lesson plans from all teachers
- **Coverage Reports**: Reports for all curricula and classes
- **Full Access**: Can edit any curriculum or lesson plan

## Quick Start Guide

1. **First Time Setup**:
   - Log in as super admin or subject teacher
   - Click "📚 Curriculum Management" button
   - Click "Create Curriculum" to create your first curriculum

2. **Creating a Curriculum**:
   - Fill in title, description, and academic year
   - Select subjects
   - Add learning objectives
   - Add syllabus content
   - Click "Create Curriculum"

3. **Creating Lesson Plans**:
   - Click "📝 Lesson Plans" button
   - Click "Create Lesson Plan"
   - Select curriculum and subject
   - Add content and resources
   - Click "Create Lesson Plan"

4. **Tracking Coverage**:
   - Click "📈 Coverage Reports" button
   - Select curriculum and class
   - Click "Generate Report"
   - View coverage percentages

## Troubleshooting

### "I don't see the buttons"
- Make sure you're logged in as a subject teacher or super admin
- Students and other roles don't have access to curriculum management
- Refresh the page if you just logged in

### "I get a permission error"
- Check your user role in the system
- Contact your administrator if you should have access

### "The page is blank"
- Make sure the Django server is running
- Check the browser console for errors
- Try clearing your browser cache

### "I can't create a curriculum"
- Make sure you're assigned to at least one subject
- Contact your administrator to assign subjects to your account

## Support

If you need help:
1. Check the User Guide: `.kiro/specs/academic-management/USER_GUIDE.md`
2. Check the Testing Guide: `.kiro/specs/academic-management/TESTING_GUIDE.md`
3. Contact your system administrator

## Summary

✅ Navigation links added to both dashboards
✅ Subject teachers can access curriculum management
✅ Super admins have full access
✅ Direct URLs available for bookmarking
✅ Role-based access control working

You can now access the Curriculum Management system from your dashboard!

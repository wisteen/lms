# Curriculum Management - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Managing Curricula](#managing-curricula)
4. [Lesson Planning](#lesson-planning)
5. [Coverage Tracking](#coverage-tracking)
6. [Best Practices](#best-practices)
7. [FAQs](#faqs)

## Introduction

The Curriculum Management system helps schools organize and track their academic curricula, lesson plans, and learning objectives. It provides tools for:

- Creating and managing curricula
- Defining learning objectives
- Planning lessons
- Tracking curriculum coverage
- Generating reports

### Who Can Use This System?

- **Super Administrators**: Full access to all features
- **Subject Teachers**: Can create curricula for their subjects and manage lesson plans
- **Class Teachers**: Can view curricula and lesson plans for their classes

## Getting Started

### Accessing the System

1. Log in to the school management system
2. Navigate to **Academic** > **Curriculum Management** from the main menu
3. You'll see the curriculum list page

### Understanding the Interface

The curriculum management interface consists of:
- **Curriculum List**: View all available curricula
- **Curriculum Details**: View detailed information about a curriculum
- **Lesson Plans**: Create and manage lesson plans
- **Coverage Reports**: Track curriculum implementation

## Managing Curricula

### Creating a New Curriculum

1. Click the **"Create Curriculum"** button on the curriculum list page
2. Fill in the basic information:
   - **Title**: Give your curriculum a descriptive name (e.g., "Grade 10 Science Curriculum 2024-2025")
   - **Description**: Provide a brief overview of the curriculum
   - **Academic Year**: Select the academic year (format: YYYY-YYYY)
   - **Subjects**: Select all subjects covered by this curriculum
   - **Published**: Check this box when the curriculum is ready to use

3. Add Learning Objectives:
   - Click **"Add Objective"** to add a new learning objective
   - For each objective, provide:
     - **Title**: A concise statement of what students will learn
     - **Description**: Detailed explanation of the objective
     - **Subject**: The subject this objective belongs to
     - **Grade Level**: The target grade level
     - **Order**: The sequence number for organizing objectives

4. Add Syllabus Content:
   - Click **"Add Content"** to add syllabus content
   - For each content section:
     - **Subject**: The subject this content belongs to
     - **Content**: Detailed syllabus content (supports rich text formatting)
     - **Order**: The sequence number for organizing content

5. Click **"Create Curriculum"** to save

### Editing a Curriculum

1. Navigate to the curriculum detail page
2. Click the **"Edit"** button
3. Make your changes
4. Click **"Edit Curriculum"** to save

**Note**: You can only edit curricula you created (unless you're a super admin)

### Publishing a Curriculum

A curriculum must be published before teachers can use it for lesson planning:

1. Edit the curriculum
2. Ensure it has at least one learning objective
3. Check the **"Published"** checkbox
4. Save the curriculum

### Viewing Curriculum Details

1. Click on a curriculum title in the list
2. The detail page shows:
   - Basic information (title, description, academic year)
   - List of subjects
   - Learning objectives (grouped by subject)
   - Syllabus content (grouped by subject)

### Searching and Filtering Curricula

Use the search and filter options on the curriculum list page:

- **Search**: Enter keywords to search in titles and descriptions
- **Academic Year**: Filter by academic year
- **Subject**: Filter by subject

## Lesson Planning

### Creating a Lesson Plan

1. Navigate to **Academic** > **Lesson Plans**
2. Click **"Create Lesson Plan"**
3. Fill in the form:
   - **Title**: Name of the lesson
   - **Curriculum**: Select the curriculum this lesson implements
   - **Subject**: Select the subject
   - **School Class**: Select the class
   - **Learning Objectives**: Check all objectives this lesson addresses
   - **Content**: Detailed lesson content (supports rich text)
   - **Resources**: List of required materials and resources
   - **Estimated Duration**: How long the lesson will take (format: HH:MM:SS)
   - **Completed**: Check this when the lesson has been taught

4. Click **"Create Lesson Plan"** to save

### Marking a Lesson as Completed

1. Open the lesson plan detail page
2. Click **"Mark as Completed"**
3. The system automatically:
   - Sets the completion date
   - Updates coverage tracking for associated learning objectives

### Viewing Your Lesson Plans

The lesson plan list shows all your lesson plans with:
- Title and subject
- Associated class
- Completion status
- Creation date

Use the filters to find specific lesson plans:
- **Curriculum**: Filter by curriculum
- **Subject**: Filter by subject
- **Class**: Filter by class
- **Completion Status**: Show only completed or pending lessons

## Coverage Tracking

### Generating a Coverage Report

1. Navigate to **Academic** > **Coverage Report**
2. Select a curriculum from the dropdown
3. Select a class from the dropdown
4. Click **"Generate Report"**

### Understanding the Coverage Report

The report shows:

- **Overall Coverage**: Total percentage of curriculum covered
- **Objectives by Subject**: Coverage for each learning objective
  - Green progress bar: Good progress (≥ 50%)
  - Yellow progress bar: At risk (< 50%)
  - Red progress bar: Not started (0%)
- **Completed Lessons**: Number of lessons completed for each objective
- **Total Planned Lessons**: Total lessons planned for each objective
- **Remaining Objectives**: List of objectives not yet covered

### Interpreting Coverage Percentages

- **100%**: Objective fully covered
- **50-99%**: Objective partially covered
- **1-49%**: Objective started but needs more attention
- **0%**: Objective not yet addressed

## Best Practices

### Creating Effective Curricula

1. **Be Specific**: Write clear, measurable learning objectives
2. **Organize Logically**: Order objectives from simple to complex
3. **Align with Standards**: Ensure objectives align with educational standards
4. **Include All Subjects**: Don't forget to add objectives for all subjects
5. **Review Regularly**: Update curricula based on feedback and results

### Planning Effective Lessons

1. **Link to Objectives**: Always associate lessons with specific learning objectives
2. **Be Realistic**: Set achievable duration estimates
3. **List Resources**: Document all required materials
4. **Update Status**: Mark lessons as completed promptly to keep coverage tracking accurate
5. **Review Coverage**: Regularly check coverage reports to identify gaps

### Tracking Coverage Effectively

1. **Regular Monitoring**: Check coverage reports weekly
2. **Address Gaps**: Prioritize objectives with low coverage
3. **Balance Coverage**: Ensure all objectives receive adequate attention
4. **Document Progress**: Use lesson completion to track progress
5. **Adjust Plans**: Modify lesson plans based on coverage data

## FAQs

### Q: Why can't I publish my curriculum?
**A**: Curricula must have at least one learning objective before they can be published. Add learning objectives and try again.

### Q: Why don't I see a curriculum in the list?
**A**: You can only see curricula for subjects you teach. If you're a super admin, you should see all curricula. Check with your administrator if you think you should have access.

### Q: How do I delete a curriculum?
**A**: Currently, curricula can only be deleted by super administrators through the admin panel. Contact your administrator if you need to delete a curriculum.

### Q: Why isn't my coverage updating?
**A**: Coverage only updates when lesson plans are marked as completed. Make sure you're clicking "Mark as Completed" after teaching each lesson.

### Q: Can I create lesson plans for unpublished curricula?
**A**: No, curricula must be published before they can be used for lesson planning. This ensures that only finalized curricula are used for teaching.

### Q: How do I add more learning objectives to an existing curriculum?
**A**: Edit the curriculum and use the "Add Objective" button to add more objectives. You can add as many as needed.

### Q: Can I reorder learning objectives?
**A**: Yes, use the "Order" field when creating or editing objectives. Lower numbers appear first.

### Q: What happens if I delete a lesson plan?
**A**: Deleting a lesson plan will update the coverage tracking automatically. The coverage percentage for associated objectives will be recalculated.

### Q: Can multiple teachers work on the same curriculum?
**A**: Yes, but only the creator (or super admin) can edit the curriculum. Other teachers can create lesson plans using the curriculum.

### Q: How do I export a curriculum?
**A**: Currently, curricula can be viewed and printed from the detail page. Export functionality may be added in future updates.

## Getting Help

If you encounter issues or have questions:

1. Check this user guide
2. Review the FAQs section
3. Contact your school's system administrator
4. Submit a support ticket through the help desk

## Tips for Success

1. **Start Small**: Begin with one curriculum and expand gradually
2. **Collaborate**: Work with other teachers to create comprehensive curricula
3. **Be Consistent**: Update lesson plans and coverage regularly
4. **Use Reports**: Leverage coverage reports to improve teaching
5. **Provide Feedback**: Share suggestions for system improvements

---

**Last Updated**: January 2025
**Version**: 1.0

# IMPORTANT

- S3 Cleanup
    - Store all the created s3 object keys, urls and their statuses
    - Keep track of Each S3 object upload status (optional)
    - Create a scheduled task to mark all as expired and delete all the unused objects

- Maintain a dedicated table for keeping track of each item uploaded by each instructor ( This is different from keeping track of each s3 open as mentioned above. The purpose here is to keep track of instructor's storage usage )



# To-Dos

## Dashboard APIs

### MVP 1
- [X] Refresh Token Rotation Fix
- [X] Dashboard Logout
- [X] Check & Test Refresh and access tokens on dashboard
- [X] Dashboard KPIs
- [X] Enrollments Tracking API
- [] Account Details Update Security

### MVP 2
- [] Media and Storage Management Library
- [] Permission's on individual courses and lessons
- [] Improve account details update security

## Headless APIs

### MVP 1
- [X] Student details update security
- [X] Student Logout API
- [X] Refresh Token Rotation
- [X] Update the Check student exists api to POST Request
- [] KPIs (Students, Courses, Enrollments)
- [] Total Count of Lessons and Courses in lesson and course list
- [X] Organise extras and paginated response properly

### MVP 2
- [] Permission's on individual courses and lessons
- [] Instructor Payment Module
- [] Course Trailers
- [] Course Tags
- [] List of featured courses


## Architectural Updates
- [] Apply Rate Limiting
- [] Apply Anon Throttle
- [] API Key Caching
- [] Data Caching (maybe)
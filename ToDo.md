# Config

- Setup Docker Compose

# Dashboard Services

- Need to ensure that an instructor is only able to access only his related data (courses, lessons, students etc.)
- Generate Unique API Key for Instructor

# Fixes

- Store lesson video size as well
- Store more precise lesson video duration
- Look for API bottlenecks and slow api process
- Apply caching and cache invalidation where-ever its required

# IMPORTANT

- S3 Cleanup
    - Store all the created s3 object keys, urls and their statuses
    - Keep track of Each S3 object upload status (optional)
    - Create a scheduled task to mark all as expired and delete all the unused objects

- Maintain a dedicated table for keeping track of each item uploaded by each instructor ( This is different from keeping track of each s3 open as mentioned above. The purpose here is to keep track of instructor's storage usage )


# Headless APIs:

- [x] Instructor Profile
- [x] Student Signup Auth
- [x] Student Login Auth
- [x] Student Refresh Token
- [x] Student Profile
- [x] Student Identifier Exists Lookup
- [x] List Course
- [x] Retrieve Course
- [x] Enroll into Course
- [x] List Course Lessons
- [x] Retrive Course Lesson Details
- [X] Student Enrolled Courses List
- [X] Fetch Lesson Resources
- [X] Student update details
- [X] Dynamic Selection for lesson resources
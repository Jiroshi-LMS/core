# Config

- Setup Docker Compose

# Dashboard Services

- Need to ensure that an instructor is only able to access only his related data (courses, lessons, students etc.)
- Generate Unique API Key for Instructor

# Fixes

- Store lesson video size as well
- Store more precise lesson video duration

# IMPORTANT

- S3 Cleanup
    - Store all the created s3 object keys, urls and their statuses
    - Keep track of Each S3 object upload status (optional)
    - Create a scheduled task to mark all as expired and delete all the unused objects

- Maintain a dedicated table for keeping track of each item uploaded by each instructor ( This is different from keeping track of each s3 open as mentioned above. The purpose here is to keep track of instructor's storage usage )
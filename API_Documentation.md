# API Documentation

## Overview

This API provides endpoints for managing users, levels, videos, questions, exams, and reports for an educational platform. It supports authentication, role-based access control, and multilingual responses (English and Arabic).

## Base URL

`http://localhost:5000`

## Authentication

- **JWT-based authentication** is required for most endpoints.
- Use `/register` and `/login` to obtain a JWT token.
- Include the token in the `Authorization` header as `Bearer <token>` for protected routes.

## Endpoints

### Welcome Video Management

- **POST /welcome_video**
  - **Description**: Set the welcome video (Admin only).
  - **Request Body**: `{ "video_url": "string" }`
  - **Response**: `200` (Success), `400` (Missing video URL), `403` (Unauthorized)
- **GET /welcome_video**
  - **Description**: Get the welcome video.
  - **Response**: `200` (Success with video URL), `404` (Not found)

### Authentication

- **POST /register**
  - **Description**: Register a new user.
  - **Request Body**: `{ "name": "string", "email": "string", "password": "string", "role": "string (optional)", "picture": "string (optional)" }`
  - **Response**: `201` (User created with token), `400` (User already exists)
- **POST /login**
  - **Description**: Log in a user.
  - **Request Body**: `{ "email": "string", "password": "string", "google": boolean (optional) }`
  - **Response**: `200` (Success with token), `401` (Invalid credentials), `404` (User not found)

### User Management

- **GET /users/<user_id>**
  - **Description**: Get user details (Admin or self).
  - **Response**: `200` (User data), `403` (Access denied), `404` (User not found)
- **PUT /users/<user_id>**
  - **Description**: Update user details (Admin or self).
  - **Request Body**: `{ "name": "string (optional)", "picture": "string (optional)", "role": "string (optional, admin only)" }`
  - **Response**: `200` (User updated), `403` (Access denied), `404` (User not found)
- **GET /admin/users**
  - **Description**: Get all users (Admin only).
  - **Response**: `200` (List of users)
- **DELETE /admin/users/<user_id>**
  - **Description**: Delete a user (Admin only).
  - **Response**: `200` (User deleted), `404` (User not found)
- **POST /admin/users/<user_id>/reset_password**
  - **Description**: Reset user password (Admin only).
  - **Request Body**: `{ "new_password": "string" }`
  - **Response**: `200` (Password reset), `400` (Missing password), `404` (User not found)
- **POST /admin/users/<user_id>/assign_level/<level_id>**
  - **Description**: Assign a level to a user (Admin only).
  - **Response**: `201` (Level assigned), `400` (Level already assigned), `404` (User or level not found)

### Level Management

- **POST /levels**
  - **Description**: Create a new level (Admin only).
  - **Request Body (multipart/form-data)**: `{ "name": "string", "description": "string (optional)", "level_number": "integer", "welcome_video_url": "string (optional)", "price": "float", "initial_exam_question": "string (optional)", "final_exam_question": "string (optional)", "file": file }`
  - **Response**: `201` (Level created), `400` (Validation errors)
- **PUT /levels/<level_id>**
  - **Description**: Update a level (Admin only).
  - **Request Body (multipart/form-data)**: `{ "name": "string (optional)", "description": "string (optional)", "level_number": "integer (optional)", "welcome_video_url": "string (optional)", "price": "float (optional)", "initial_exam_question": "string (optional)", "final_exam_question": "string (optional)", "file": file (optional) }`
  - **Response**: `200` (Level updated), `404` (Level not found)
- **DELETE /levels/<level_id>**
  - **Description**: Delete a level (Admin only).
  - **Response**: `200` (Level deleted), `404` (Level not found)
- **GET /levels**
  - **Description**: Get all levels (Admin or client).
  - **Query Parameters**: `min_price`, `max_price`, `level_number`, `name`
  - **Response**: `200` (List of levels)
- **GET /admin/levels**
  - **Description**: Get all levels with admin details (Admin only).
  - **Query Parameters**: `min_price`, `max_price`, `level_number`, `name`
  - **Response**: `200` (List of levels with user count)
- **GET /levels/<level_id>**
  - **Description**: Get a specific level (Client).
  - **Response**: `200` (Level details), `404` (Level not found)
- **POST /users/<user_id>/levels/<level_id>/purchase**
  - **Description**: Purchase a level (Admin or self).
  - **Response**: `201` (Level purchased), `400` (Level already purchased), `403` (Access denied), `404` (Level not found)
- **PATCH /users/<user_id>/levels/<level_id>/update_progress**
  - **Description**: Update level progress (Admin or self).
  - **Response**: `200` (Progress updated), `400` (Level not purchased), `403` (Access denied)

### Video Management

- **POST /levels/<level_id>/videos**
  - **Description**: Add a video to a level (Admin only).
  - **Request Body**: `{ "youtube_link": "string" }`
  - **Response**: `201` (Video created), `404` (Level not found)
- **PUT /videos/<video_id>**
  - **Description**: Update a video (Admin only).
  - **Request Body**: `{ "youtube_link": "string (optional)" }`
  - **Response**: `200` (Video updated), `404` (Video not found)
- **DELETE /videos/<video_id>**
  - **Description**: Delete a video (Admin only).
  - **Response**: `200` (Video deleted), `404` (Video not found)
- **GET /admin/videos**
  - **Description**: Get all videos (Admin only).
  - **Response**: `200` (List of videos)
- **PATCH /users/<user_id>/levels/<level_id>/videos/<video_id>/complete**
  - **Description**: Mark a video as completed (Admin or self).
  - **Response**: `200` (Video completed), `400` (Level not purchased or video not accessible), `403` (Access denied)

### Question Management

- **POST /videos/<video_id>/questions**
  - **Description**: Create a question for a video (Admin only).
  - **Request Body**: `{ "text": "string", "order": "integer (optional)" }`
  - **Response**: `201` (Question created), `404` (Video not found)
- **PUT /questions/<question_id>**
  - **Description**: Update a question (Admin only).
  - **Request Body**: `{ "text": "string (optional)", "order": "integer (optional)" }`
  - **Response**: `200` (Question updated), `404` (Question not found)
- **DELETE /questions/<question_id>**
  - **Description**: Delete a question (Admin only).
  - **Response**: `200` (Question deleted), `404` (Question not found)
- **GET /admin/questions**
  - **Description**: Get all questions (Admin only).
  - **Response**: `200` (List of questions)
- **GET /videos/<video_id>/questions**
  - **Description**: Get questions for a video (Admin or client).
  - **Response**: `200` (List of questions), `404` (Video not found)

### Question Answer Submission

- **POST /questions/<question_id>/submit**
  - **Description**: Submit an answer to a question (Client).
  - **Request Body**: `{ "correct_words": integer, "wrong_words": integer, "correct_words_list": array (optional), "wrong_words_list": array (optional) }`
  - **Response**: `200` (Answer submitted), `400` (Validation errors or video not opened), `403` (Level not purchased), `404` (Question not found)
- **GET /users/<user_id>/questions/<question_id>/answer**
  - **Description**: Get a user's answer to a question (Admin or self).
  - **Response**: `200` (Answer details), `403` (Access denied), `404` (Answer or question not found)
- **GET /admin/questions/<question_id>/answers**
  - **Description**: Get all answers for a question (Admin only).
  - **Response**: `200` (List of answers), `404` (Question not found)

### Exam Routes

- **POST /exams/<level_id>/initial**
  - **Description**: Submit initial exam for a level (Client).
  - **Request Body**: `{ "correct_words": integer, "wrong_words": integer, "correct_words_list": array (optional), "wrong_words_list": array (optional) }`
  - **Response**: `201` (Exam submitted), `400` (Level not purchased)
- **POST /exams/<level_id>/final**
  - **Description**: Submit final exam for a level (Client).
  - **Request Body**: `{ "correct_words": integer, "wrong_words": integer, "correct_words_list": array (optional), "wrong_words_list": array (optional) }`
  - **Response**: `201` (Exam submitted), `400` (Level not purchased or exam not available)
- **GET /exams/<level_id>/user/<user_id>**
  - **Description**: Get exam results for a user and level (Admin or self).
  - **Response**: `200` (List of exam results), `403` (Access denied)
- **GET /admin/exams**
  - **Description**: Get all exam results (Admin only).
  - **Response**: `200` (List of exam results)

### Report and Statistics

- **GET /report**
  - **Description**: Get user progress report (Client).
  - **Query Parameters**: `format` (json or markdown)
  - **Response**: `200` (Report in requested format), `404` (User not found)
- **GET /admin/statistics**
  - **Description**: Get platform statistics (Admin only).
  - **Response**: `200` (Statistics data)
- **GET /admin/users/<user_id>/statistics**
  - **Description**: Get user-specific statistics (Admin only).
  - **Response**: `200` (User statistics), `404` (User not found)

### File Serving

- **GET /Uploads/levels/<filename>**
  - **Description**: Serve uploaded level images.
  - **Response**: File content or `404` (File not found)

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "message": "Localized error message",
  "message_key": "error_key",
  "lang": "en or ar"
}
```

## Success Responses

Success responses follow this format:

```json
{
  "success": true,
  "message": "Localized success message",
  "message_key": "success_key",
  "lang": "en or ar",
  "data": { ... } // Optional data
}
```

## Localization

- Supports English (`en`) and Arabic (`ar`).
- Language can be specified via:
  - Query parameter: `?lang=en`
  - Form data: `lang=en`
  - Header: `Accept-Language: en`
  - JSON body: `{ "lang": "en" }`
- Defaults to English if no valid language is provided.

## Notes

- Admin routes require `role: admin`.
- Client routes require authentication and `role: client`.
- File uploads (e.g., level images) use `multipart/form-data`.
- Database operations are atomic with proper error handling.

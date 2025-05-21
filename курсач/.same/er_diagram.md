# ER-диаграмма базы данных

```mermaid
erDiagram
    USERS {
        int id PK
        string name
        string email
        string password_hash
        string role
    }

    COURSES {
        int id PK
        string title
        text description
    }

    MODULES {
        int id PK
        int course_id FK
        string title
        text content
    }

    ENROLLMENTS {
        int id PK
        int user_id FK
        int course_id FK
        float progress
    }

    ASSESSMENTS {
        int id PK
        int module_id FK
        int user_id FK
        float grade
    }

    FEEDBACKS {
        int id PK
        int course_id FK
        int user_id FK
        text comment
        int rating
    }

    USERS ||--o{ ENROLLMENTS : "enrolls"
    USERS ||--o{ ASSESSMENTS : "receives"
    USERS ||--o{ FEEDBACKS : "provides"

    COURSES ||--o{ MODULES : "contains"
    COURSES ||--o{ ENROLLMENTS : "has"
    COURSES ||--o{ FEEDBACKS : "receives"

    MODULES ||--o{ ASSESSMENTS : "has"

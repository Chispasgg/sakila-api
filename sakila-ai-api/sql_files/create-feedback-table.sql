-- Crear tabla feedback para el sistema de recomendaciones
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL,
    feedback_text TEXT,
    is_positive BOOLEAN NOT NULL,
    created_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_user_id FOREIGN KEY (user_id) REFERENCES customer(customer_id)
);

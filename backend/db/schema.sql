CREATE TABLE IF NOT EXISTS employee_info (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    address TEXT,
    contact_number VARCHAR(15),
    pan_number VARCHAR(10),
    aadhar_number VARCHAR(12),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_documents (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employee_info(id) ON DELETE CASCADE,
    resume TEXT,
    educational_certificates TEXT,
    offer_letters TEXT,
    pan_card TEXT,
    aadhar_card TEXT,
    form_16_or_it_returns TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

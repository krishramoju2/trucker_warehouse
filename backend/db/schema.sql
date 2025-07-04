CREATE TABLE employee_info (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    address TEXT NOT NULL,
    contact_number VARCHAR(15),
    pan_number VARCHAR(10) UNIQUE,
    aadhar_number VARCHAR(12) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee_documents (
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
 

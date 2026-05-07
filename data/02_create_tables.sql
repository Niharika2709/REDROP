USE blood_donation;

CREATE TABLE Blood_Group (
    blood_group_id INT PRIMARY KEY,
    blood_type VARCHAR(3) NOT NULL UNIQUE
);

CREATE TABLE donor (
    donor_id INT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INT NOT NULL CHECK (age >= 18),
    gender ENUM('M','F','O'),
    contact VARCHAR(15) NOT NULL UNIQUE,
    blood_group_id INT NOT NULL,
    last_donation DATE,

    FOREIGN KEY (blood_group_id)
    REFERENCES Blood_Group(blood_group_id)
);

CREATE TABLE Donation_Record (
    donation_id INT PRIMARY KEY,
    donor_id INT NOT NULL,
    donation_date DATE NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),

    FOREIGN KEY (donor_id)
    REFERENCES donor(donor_id)
);

CREATE TABLE Emergency_Request (
    request_id INT PRIMARY KEY,
    hospital_name VARCHAR(50) NOT NULL,
    blood_group_id INT NOT NULL,
    required_units INT NOT NULL CHECK (required_units > 0),
    request_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',

    FOREIGN KEY (blood_group_id)
    REFERENCES Blood_Group(blood_group_id)
);

CREATE TABLE Blood_Availability (
    blood_group_id INT PRIMARY KEY,
    available_units INT NOT NULL CHECK (available_units >= 0),

    FOREIGN KEY (blood_group_id)
    REFERENCES Blood_Group(blood_group_id)
);

CREATE TABLE Donor_Notification (
    notification_id INT PRIMARY KEY,
    donor_id INT NOT NULL,
    request_id INT NOT NULL,
    notification_status VARCHAR(20) DEFAULT 'Pending',

    FOREIGN KEY (donor_id)
    REFERENCES donor(donor_id),

    FOREIGN KEY (request_id)
    REFERENCES Emergency_Request(request_id)
);
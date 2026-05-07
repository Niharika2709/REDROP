USE blood_donation;

INSERT INTO Blood_Group VALUES
(1,'A+'),
(2,'A-'),
(3,'B+'),
(4,'B-'),
(5,'AB+'),
(6,'AB-'),
(7,'O+'),
(8,'O-');

INSERT INTO donor VALUES
(101,'Rahul',22,'M','9876543210',1,'2025-12-01'),
(102,'Aman',25,'M','9876543211',2,'2025-11-15'),
(103,'Riya',21,'F','9876543212',1,'2025-10-10');

INSERT INTO Emergency_Request VALUES
(201,'City Hospital',1,2,'2026-04-10','Pending');

INSERT INTO Blood_Availability VALUES
(1,5),
(2,3),
(3,4),
(4,2);

INSERT INTO Donation_Record VALUES
(301,101,'2026-04-20',1);

INSERT INTO Donor_Notification VALUES
(401,101,201,'Sent');
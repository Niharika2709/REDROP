USE blood_donation;

DELIMITER $$

CREATE TRIGGER update_blood_after_donation

AFTER INSERT ON Donation_Record

FOR EACH ROW

BEGIN

    UPDATE Blood_Availability
    SET available_units = available_units + NEW.quantity

    WHERE blood_group_id = (
        SELECT blood_group_id
        FROM donor
        WHERE donor_id = NEW.donor_id
    );

END $$

DELIMITER ;
USE blood_donation;

DELIMITER $$

CREATE PROCEDURE find_matching_donors(
    IN bg_id INT
)

BEGIN

    SELECT donor_id,
           name,
           contact
    FROM donor
    WHERE blood_group_id = bg_id
    AND last_donation < CURDATE() - INTERVAL 3 MONTH;

END $$

DELIMITER ;
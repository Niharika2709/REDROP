USE blood_donation;

DELIMITER $$

CREATE FUNCTION check_donor_eligibility(
    last_date DATE
)
RETURNS VARCHAR(20)

DETERMINISTIC

BEGIN

    DECLARE result VARCHAR(20);

    IF last_date < CURDATE() - INTERVAL 3 MONTH THEN
        SET result = 'Eligible';
    ELSE
        SET result = 'Not Eligible';
    END IF;

    RETURN result;

END $$

DELIMITER ;
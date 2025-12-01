-- Add image_data column to business_cards table
ALTER TABLE business_cards ADD COLUMN image_data LONGTEXT COMMENT 'Base64 encoded image data';
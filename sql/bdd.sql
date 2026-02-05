-- =====================================================
-- FAKE DATA SEED - CENDRES_VAPEUR
-- =====================================================

START TRANSACTION;

-- Categories
INSERT INTO apps_category (id, name, description, created_at) VALUES
(1, 'Rituels', 'Objets utilisés lors des rituels coloniaux', NOW()),
(2, 'Reliques', 'Artefacts anciens retrouvés dans les cendres', NOW()),
(3, 'Consommables', 'Produits à usage unique', NOW());

-- Products
INSERT INTO apps_product
(id, name, description, image, stock, base_price, current_price, popularity_score, category_id)
VALUES
(1, 'Encens Noir', 'Encens utilisé pour les invocations mineures', 'encens_noir.jpg', 120, 5.00, 6.50, 8.2, 3),
(2, 'Masque de Cendre', 'Masque rituel ancestral', 'masque_cendre.jpg', 15, 45.00, 59.90, 9.4, 2),
(3, 'Bougie Runique', 'Bougie gravée de symboles anciens', 'bougie_runique.jpg', 60, 12.00, 14.00, 7.1, 1);

-- Users
INSERT INTO apps_customuser
(id, username, email, password, role, avatar_url, biography)
VALUES
(1, 'admin', 'admin@cendres.test', 'hashed_password_admin', 'ADMIN', NULL, 'Gardien des archives.'),
(2, 'elyra', 'elyra@cendres.test', 'hashed_password_user', 'USER', NULL, 'Adepte des rituels anciens.'),
(3, 'morth', 'morth@cendres.test', 'hashed_password_user', 'USER', NULL, 'Chercheur de reliques.');

-- Orders
INSERT INTO apps_order
(id, status, total_amount, created_at, invoice_file, user_id)
VALUES
(1, 'PAID', 73.90, NOW(), 'invoice_001.pdf', 2),
(2, 'PENDING', 14.00, NOW(), NULL, 3);

-- Order Items
INSERT INTO apps_orderitem
(id, quantity, unit_price_frozen, order_id, product_id)
VALUES
(1, 1, 59.90, 1, 2),
(2, 2, 6.50, 1, 1),
(3, 1, 14.00, 2, 3);

-- Shift Notes
INSERT INTO apps_shiftnote
(id, date, shift_type, content, order_id)
VALUES
(1, CURDATE(), 'NIGHT', 'Commande traitée durant le cycle nocturne.', 1);

-- Colony Events
INSERT INTO apps_colonyevent
(id, title, date, severity)
VALUES
(1, 'Chute de cendres excessive', '2026-01-12', 'HIGH'),
(2, 'Extinction partielle des flammes', '2026-02-01', 'LOW');

-- Votes
INSERT INTO apps_vote (id, product_id, user_id) VALUES
(1, 2, 2),
(2, 2, 3),
(3, 1, 2);

-- Two-factor codes
INSERT INTO apps_twofactorcode
(id, code, created_at, expires_at, user_id)
VALUES
(1, '483920', NOW(), DATE_ADD(NOW(), INTERVAL 10 MINUTE), 2);

COMMIT;
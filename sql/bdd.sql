DELETE FROM OrderItem; DELETE FROM Order; DELETE FROM Vote; 
DELETE FROM TwoFactorCode; DELETE FROM ShiftNote; DELETE FROM ColonyEvent; 
DELETE FROM Product; DELETE FROM CustomUser;

INSERT INTO CustomUser (id, username, email, password, role, biography) VALUES
(1, 'Valerian_Admin', 'valerian@guilde.fr', 'hash_secure_99', 'Administrateur', 'Grand Conseil - Secteur Nord'),
(2, 'Mathias_Pourpre', 'mathias@zonefranche.fr', 'hash_secure_01', 'Administrateur', 'Élite de la sécurité cryptée'),
(3, 'Troc_Vendeur', 'vendeur@vapeur.com', 'hash_secure_02', 'Éditeur', 'Gestionnaire du stock de cuivre'),
(4, 'Citoyen_Lambda', 'survivant@cendres.fr', 'hash_secure_03', 'Utilisateur', 'Ouvrier de la chaudière centrale'),
(5, 'Espion_Anonyme', 'invit@exterieur.net', 'hash_secure_04', 'Invité', 'Visiteur de passage');

INSERT INTO TwoFactorCode (user_id, code, created_at, expires_at) VALUES
(1, '8829', datetime('now'), datetime('now', '+10 minutes')),
(2, '4412', datetime('now'), datetime('now', '+10 minutes'));

INSERT INTO Product (id, name, description, category, stock, base_price, current_price, popularity_score) VALUES
(1, 'Engrenage en Bronze', 'Pièce d occasion pour turbine à vapeur', 'MÉCANIQUE', 150, 12.50, 14.20, 85),
(2, 'Filtre à Charbon Actif', 'Indispensable pour respirer dans le Secteur Cendre', 'SURVIE', 45, 50.00, 75.00, 120),
(3, 'Seringue d Adrénaline', 'Stimulant chimique pour double quart', 'MÉDICAL', 10, 100.00, 95.50, 30),
(4, 'Tuyau de Cuivre Brossé', 'Matériau de construction noble', 'MATÉRIAUX', 500, 5.00, 8.40, 200);

INSERT INTO ColonyEvent (title, date, severity) VALUES
('Fuite de Vapeur Secteur 4', '2026-02-05', 'ÉLEVÉE'),
('Arrivée du convoi de ravitaillement', '2026-02-07', 'NORMALE');

INSERT INTO ShiftNote (user_id, date, shift_type, content) VALUES
(2, '2026-02-04', 'MATIN', 'Pression de la chaudière stable. Pas d intrusion réseau détectée.'),
(4, '2026-02-04', 'SOIR', 'Surchauffe signalée sur le piston n°3.');

INSERT INTO Vote (user_id, product_id) VALUES (4, 1), (4, 2), (1, 2), (2, 4);

INSERT INTO "Order" (id, user_id, status, total_amount, created_at) VALUES
(1, 4, 'COMPLÉTÉ', 89.20, '2026-02-03 14:30:00');

INSERT INTO OrderItem (order_id, product_id, quantity, unit_price_frozen) VALUES
(1, 1, 1, 14.20),
(1, 2, 1, 75.00);
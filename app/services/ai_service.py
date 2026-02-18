# AI service - Demo mode (no OpenAI API)

from app.models.ai_itinerary import create_ai_itinerary


# Real places with coordinates for popular destinations
# Each place: (name, address, lat, lng, category)
# Categories: morning, lunch, afternoon, evening
DESTINATION_PLACES = {
    'paris': [
        ('Eiffel Tower', 'Champ de Mars, 5 Av. Anatole France, 75007', 48.8584, 2.2945, 'morning'),
        ('Louvre Museum', 'Rue de Rivoli, 75001', 48.8606, 2.3376, 'morning'),
        ('Sacré-Cœur Basilica', '35 Rue du Chevalier de la Barre, 75018', 48.8867, 2.3431, 'morning'),
        ('Arc de Triomphe', 'Place Charles de Gaulle, 75008', 48.8738, 2.2950, 'morning'),
        ('Musée d\'Orsay', '1 Rue de la Légion d\'Honneur, 75007', 48.8600, 2.3266, 'morning'),
        ('Café de Flore', '172 Bd Saint-Germain, 75006', 48.8541, 2.3326, 'lunch'),
        ('Le Bouillon Chartier', '7 Rue du Faubourg Montmartre, 75009', 48.8745, 2.3444, 'lunch'),
        ('Breizh Café', '109 Rue Vieille du Temple, 75003', 48.8631, 2.3620, 'lunch'),
        ('Pink Mamma', '20bis Rue de Douai, 75009', 48.8818, 2.3370, 'lunch'),
        ('Notre-Dame Cathedral', '6 Parvis Notre-Dame, 75004', 48.8530, 2.3499, 'afternoon'),
        ('Luxembourg Gardens', 'Rue de Médicis, 75006', 48.8462, 2.3372, 'afternoon'),
        ('Sainte-Chapelle', '10 Bd du Palais, 75001', 48.8554, 2.3450, 'afternoon'),
        ('Palace of Versailles', 'Place d\'Armes, 78000 Versailles', 48.8049, 2.1204, 'afternoon'),
        ('Moulin Rouge', '82 Bd de Clichy, 75018', 48.8841, 2.3323, 'evening'),
        ('Seine River Cruise', 'Port de la Bourdonnais, 75007', 48.8600, 2.2900, 'evening'),
        ('Le Marais District', 'Le Marais, 75004', 48.8593, 2.3622, 'evening'),
        ('Montmartre Walk', 'Place du Tertre, 75018', 48.8865, 2.3408, 'evening'),
    ],
    'rome': [
        ('Colosseum', 'Piazza del Colosseo, 00184', 41.8902, 12.4922, 'morning'),
        ('Vatican Museums', 'Viale Vaticano, 00165', 41.9065, 12.4536, 'morning'),
        ('Pantheon', 'Piazza della Rotonda, 00186', 41.8986, 12.4769, 'morning'),
        ('Roman Forum', 'Via della Salara Vecchia, 00186', 41.8925, 12.4853, 'morning'),
        ('Trattoria Da Enzo', 'Via dei Vascellari 29, 00153', 41.8882, 12.4742, 'lunch'),
        ('Roscioli', 'Via dei Giubbonari 21, 00186', 41.8946, 12.4731, 'lunch'),
        ('Pizzarium', 'Via della Meloria 43, 00136', 41.9073, 12.4405, 'lunch'),
        ('Trevi Fountain', 'Piazza di Trevi, 00187', 41.9009, 12.4833, 'afternoon'),
        ('Spanish Steps', 'Piazza di Spagna, 00187', 41.9060, 12.4828, 'afternoon'),
        ('Borghese Gallery', 'Piazzale Scipione Borghese 5, 00197', 41.9142, 12.4921, 'afternoon'),
        ('Trastevere District', 'Trastevere, 00153', 41.8869, 12.4700, 'evening'),
        ('Piazza Navona', 'Piazza Navona, 00186', 41.8992, 12.4731, 'evening'),
        ('Castel Sant\'Angelo', 'Lungotevere Castello 50, 00193', 41.9031, 12.4663, 'evening'),
    ],
    'barcelona': [
        ('Sagrada Família', 'C/ de Mallorca 401, 08013', 41.4036, 2.1744, 'morning'),
        ('Park Güell', 'Carrer d\'Olot, 08024', 41.4145, 2.1527, 'morning'),
        ('Casa Batlló', 'Passeig de Gràcia 43, 08007', 41.3916, 2.1650, 'morning'),
        ('La Boqueria Market', 'La Rambla 91, 08001', 41.3816, 2.1719, 'morning'),
        ('Can Culleretes', 'Carrer d\'en Quintana 5, 08002', 41.3815, 2.1743, 'lunch'),
        ('El Xampanyet', 'Carrer de Montcada 22, 08003', 41.3847, 2.1815, 'lunch'),
        ('La Pepita', 'Carrer de Còrsega 343, 08037', 41.3986, 2.1572, 'lunch'),
        ('Gothic Quarter', 'Barri Gòtic, 08002', 41.3833, 2.1761, 'afternoon'),
        ('Barcelona Cathedral', 'Pla de la Seu, 08002', 41.3841, 2.1763, 'afternoon'),
        ('Barceloneta Beach', 'Passeig Marítim, 08003', 41.3784, 2.1925, 'afternoon'),
        ('Magic Fountain of Montjuïc', 'Plaça de Carles Buïgas, 08038', 41.3714, 2.1519, 'evening'),
        ('Las Ramblas Walk', 'La Rambla, 08002', 41.3809, 2.1734, 'evening'),
        ('Flamenco Show at Tablao Cordobes', 'La Rambla 35, 08002', 41.3802, 2.1739, 'evening'),
    ],
    'bali': [
        ('Tanah Lot Temple', 'Beraban, Kediri, Tabanan', -8.6213, 115.0868, 'morning'),
        ('Tegallalang Rice Terraces', 'Tegallalang, Gianyar', -8.4312, 115.2793, 'morning'),
        ('Uluwatu Temple', 'Pecatu, South Kuta, Badung', -8.8291, 115.0849, 'morning'),
        ('Tirta Empul Temple', 'Tampaksiring, Gianyar', -8.4153, 115.3153, 'morning'),
        ('Warung Babi Guling Ibu Oka', 'Jl. Tegal Sari No.2, Ubud', -8.5069, 115.2625, 'lunch'),
        ('Locavore', 'Jl. Dewi Sita, Ubud', -8.5075, 115.2646, 'lunch'),
        ('La Laguna Bali', 'Jl. Pantai Kayu Putih, Canggu', -8.6577, 115.1307, 'lunch'),
        ('Ubud Monkey Forest', 'Jl. Monkey Forest, Ubud', -8.5183, 115.2588, 'afternoon'),
        ('Ubud Art Market', 'Jl. Raya Ubud, Ubud', -8.5067, 115.2628, 'afternoon'),
        ('Seminyak Beach', 'Seminyak, Kuta, Badung', -8.6897, 115.1577, 'afternoon'),
        ('Kecak Fire Dance at Uluwatu', 'Uluwatu Temple, Pecatu', -8.8291, 115.0849, 'evening'),
        ('Jimbaran Bay Seafood', 'Jl. Bukit Permai, Jimbaran', -8.7904, 115.1601, 'evening'),
        ('Potato Head Beach Club', 'Jl. Petitenget 51B, Seminyak', -8.6802, 115.1551, 'evening'),
    ],
    'tokyo': [
        ('Senso-ji Temple', '2 Chome-3-1 Asakusa, Taito', 35.7148, 139.7967, 'morning'),
        ('Meiji Shrine', '1-1 Yoyogikamizonocho, Shibuya', 35.6764, 139.6993, 'morning'),
        ('Tokyo Tower', '4 Chome-2-8 Shibakoen, Minato', 35.6586, 139.7454, 'morning'),
        ('Imperial Palace Gardens', '1-1 Chiyoda, Chiyoda', 35.6852, 139.7528, 'morning'),
        ('Tsukiji Outer Market', '4 Chome-16 Tsukiji, Chuo', 35.6654, 139.7707, 'morning'),
        ('Ichiran Ramen Shibuya', '1 Chome-22-7 Jinnan, Shibuya', 35.6619, 139.6998, 'lunch'),
        ('Sushi Dai at Toyosu', '6 Chome-6-2 Toyosu, Koto', 35.6456, 139.7810, 'lunch'),
        ('Gonpachi Nishi-Azabu', '1 Chome-13-11 Nishiazabu, Minato', 35.6568, 139.7260, 'lunch'),
        ('Afuri Ramen', '1 Chome-1-7 Ebisuminami, Shibuya', 35.6465, 139.7103, 'lunch'),
        ('Shibuya Crossing', '2 Chome-2-1 Dogenzaka, Shibuya', 35.6595, 139.7004, 'afternoon'),
        ('Akihabara Electronics District', 'Sotokanda, Chiyoda', 35.7023, 139.7745, 'afternoon'),
        ('Ueno Park & Museums', '5-20 Uenokoen, Taito', 35.7146, 139.7732, 'afternoon'),
        ('TeamLab Borderless', '1-3-8 Aomi, Koto', 35.6265, 139.7837, 'afternoon'),
        ('Shinjuku Omoide Yokocho', '1 Chome-2 Nishishinjuku, Shinjuku', 35.6938, 139.6993, 'evening'),
        ('Golden Gai', '1 Chome-1 Kabukicho, Shinjuku', 35.6941, 139.7036, 'evening'),
        ('Roppongi Hills', '6 Chome-10-1 Roppongi, Minato', 35.6604, 139.7292, 'evening'),
        ('Odaiba Night View', '1 Chome Daiba, Minato', 35.6267, 139.7753, 'evening'),
    ],
    'kyoto': [
        ('Fushimi Inari Shrine', '68 Fukakusa Yabunouchicho, Fushimi', 34.9671, 135.7727, 'morning'),
        ('Kinkaku-ji (Golden Pavilion)', '1 Kinkakujicho, Kita', 35.0394, 135.7292, 'morning'),
        ('Arashiyama Bamboo Grove', 'Sagaogurayama Tabuchiyamacho, Ukyo', 35.0173, 135.6711, 'morning'),
        ('Kiyomizu-dera Temple', '1-294 Kiyomizu, Higashiyama', 34.9949, 135.7850, 'morning'),
        ('Nishiki Market', 'Nishikikoji-dori, Nakagyo', 35.0050, 135.7649, 'lunch'),
        ('Omen Noodle Shop', '74 Jodoji Ishibashicho, Sakyo', 35.0254, 135.7944, 'lunch'),
        ('Gion Kappa Restaurant', '297 Kitagawa, Gionmachi Minamigawa, Higashiyama', 35.0037, 135.7751, 'lunch'),
        ('Philosopher\'s Path', 'Shishigatani Honenin Nishimachi, Sakyo', 35.0212, 135.7940, 'afternoon'),
        ('Gion District', 'Gionmachi, Higashiyama', 35.0037, 135.7756, 'afternoon'),
        ('Nijo Castle', '541 Nijojocho, Nakagyo', 35.0142, 135.7481, 'afternoon'),
        ('Pontocho Alley', 'Pontocho, Nakagyo', 35.0042, 135.7705, 'evening'),
        ('Gion Corner Cultural Show', '570-2 Gionmachi Minamigawa, Higashiyama', 35.0019, 135.7754, 'evening'),
        ('Kamogawa Riverside Walk', 'Kamogawa River, Kyoto', 35.0063, 135.7694, 'evening'),
    ],
    'london': [
        ('Tower of London', 'London EC3N 4AB', 51.5081, -0.0759, 'morning'),
        ('British Museum', 'Great Russell St, London WC1B 3DG', 51.5194, -0.1270, 'morning'),
        ('Buckingham Palace', 'London SW1A 1AA', 51.5014, -0.1419, 'morning'),
        ('Westminster Abbey', '20 Deans Yd, London SW1P 3PA', 51.4993, -0.1273, 'morning'),
        ('Borough Market', '8 Southwark St, London SE1 1TL', 51.5055, -0.0910, 'lunch'),
        ('Dishoom Kings Cross', '5 Stable St, London N1C 4AB', 51.5359, -0.1249, 'lunch'),
        ('Padella', '6 Southwark St, London SE1 1TQ', 51.5054, -0.0912, 'lunch'),
        ('Tower Bridge', 'Tower Bridge Rd, London SE1 2UP', 51.5055, -0.0754, 'afternoon'),
        ('Hyde Park', 'London W2 2UH', 51.5073, -0.1657, 'afternoon'),
        ('St Paul\'s Cathedral', 'St Paul\'s Churchyard, London EC4M 8AD', 51.5138, -0.0984, 'afternoon'),
        ('Big Ben & Parliament', 'London SW1A 0AA', 51.5007, -0.1246, 'afternoon'),
        ('West End Theatre District', 'Shaftesbury Ave, London W1D', 51.5129, -0.1303, 'evening'),
        ('Sky Garden', '20 Fenchurch St, London EC3M 8AF', 51.5113, -0.0836, 'evening'),
        ('Camden Town', 'Camden Town, London NW1', 51.5392, -0.1426, 'evening'),
    ],
    'new york': [
        ('Statue of Liberty', 'Liberty Island, New York, NY 10004', 40.6892, -74.0445, 'morning'),
        ('Central Park', 'New York, NY 10024', 40.7829, -73.9654, 'morning'),
        ('Empire State Building', '20 W 34th St, New York, NY 10001', 40.7484, -73.9857, 'morning'),
        ('Metropolitan Museum of Art', '1000 5th Ave, New York, NY 10028', 40.7794, -73.9632, 'morning'),
        ('Times Square', 'Manhattan, NY 10036', 40.7580, -73.9855, 'morning'),
        ('Joe\'s Pizza', '7 Carmine St, New York, NY 10014', 40.7306, -74.0021, 'lunch'),
        ('Katz\'s Delicatessen', '205 E Houston St, New York, NY 10002', 40.7223, -73.9874, 'lunch'),
        ('Chelsea Market', '75 9th Ave, New York, NY 10011', 40.7425, -74.0060, 'lunch'),
        ('Los Tacos No. 1', '75 9th Ave, New York, NY 10011', 40.7425, -74.0060, 'lunch'),
        ('Brooklyn Bridge Walk', 'Brooklyn Bridge, New York, NY 10038', 40.7061, -73.9969, 'afternoon'),
        ('Top of the Rock', '30 Rockefeller Plaza, New York, NY 10112', 40.7587, -73.9787, 'afternoon'),
        ('High Line Park', 'New York, NY 10011', 40.7480, -74.0048, 'afternoon'),
        ('9/11 Memorial', '180 Greenwich St, New York, NY 10007', 40.7115, -74.0134, 'afternoon'),
        ('Broadway Show', 'Theatre District, Manhattan', 40.7590, -73.9845, 'evening'),
        ('Rooftop Bar at 230 Fifth', '230 5th Ave, New York, NY 10001', 40.7441, -73.9880, 'evening'),
        ('DUMBO Brooklyn', 'DUMBO, Brooklyn, NY 11201', 40.7033, -73.9894, 'evening'),
    ],
    'dubai': [
        ('Burj Khalifa', '1 Sheikh Mohammed bin Rashid Blvd', 25.1972, 55.2744, 'morning'),
        ('Dubai Mall', 'Financial Center Rd, Downtown Dubai', 25.1985, 55.2796, 'morning'),
        ('Palm Jumeirah', 'Palm Jumeirah, Dubai', 25.1124, 55.1390, 'morning'),
        ('Dubai Museum', 'Al Fahidi St, Bur Dubai', 25.2636, 55.2972, 'morning'),
        ('Al Mahara', 'Burj Al Arab, Jumeirah St', 25.1413, 55.1853, 'lunch'),
        ('Arabian Tea House', 'Al Fahidi Historical Neighbourhood', 25.2635, 55.2963, 'lunch'),
        ('Pierchic', 'Al Qasr Hotel, Madinat Jumeirah', 25.1319, 55.1825, 'lunch'),
        ('Dubai Marina Walk', 'Dubai Marina, Dubai', 25.0763, 55.1391, 'afternoon'),
        ('Gold Souk', 'Deira, Dubai', 25.2867, 55.2994, 'afternoon'),
        ('Jumeirah Mosque', 'Jumeirah Beach Rd, Dubai', 25.2340, 55.2533, 'afternoon'),
        ('Dubai Fountain Show', 'Downtown Dubai', 25.1953, 55.2750, 'evening'),
        ('Madinat Jumeirah', 'King Salman Bin Abdulaziz Al Saud St', 25.1333, 55.1842, 'evening'),
        ('Desert Safari', 'Dubai Desert Conservation Reserve', 25.0500, 55.4000, 'evening'),
    ],
    'bangkok': [
        ('Grand Palace', 'Na Phra Lan Rd, Phra Borom Maha Ratchawang', 13.7500, 100.4914, 'morning'),
        ('Wat Pho', '2 Sanam Chai Rd, Phra Borom Maha Ratchawang', 13.7465, 100.4930, 'morning'),
        ('Wat Arun', '158 Wang Doem Rd, Bangkok Yai', 13.7437, 100.4888, 'morning'),
        ('Chatuchak Weekend Market', 'Kamphaeng Phet 2 Rd, Chatuchak', 13.7999, 100.5504, 'morning'),
        ('Jay Fai', '327 Maha Chai Rd, Samran Rat', 13.7538, 100.5037, 'lunch'),
        ('Som Tam Nua', '392/14 Siam Square Soi 5', 13.7454, 100.5348, 'lunch'),
        ('Thipsamai Pad Thai', '313 Maha Chai Rd, Samran Rat', 13.7525, 100.5035, 'lunch'),
        ('Jim Thompson House', '6 Rama I Rd, Wang Mai', 13.7497, 100.5292, 'afternoon'),
        ('Chinatown (Yaowarat)', 'Yaowarat Rd, Samphanthawong', 13.7407, 100.5097, 'afternoon'),
        ('Lumphini Park', 'Rama IV Rd, Pathumwan', 13.7311, 100.5418, 'afternoon'),
        ('Khao San Road', 'Khao San Rd, Phra Nakhon', 13.7589, 100.4971, 'evening'),
        ('Asiatique The Riverfront', '2194 Charoen Krung Rd, Wat Phraya Krai', 13.7064, 100.5014, 'evening'),
        ('Rooftop Bar at Lebua', '1055 Si Lom Rd, Bang Rak', 13.7222, 100.5148, 'evening'),
    ],
    'istanbul': [
        ('Hagia Sophia', 'Sultan Ahmet, Ayasofya Meydanı, 34122', 41.0086, 28.9802, 'morning'),
        ('Blue Mosque', 'Sultan Ahmet, At Meydanı No:7, 34122', 41.0054, 28.9768, 'morning'),
        ('Topkapi Palace', 'Cankurtaran, 34122 Fatih', 41.0115, 28.9833, 'morning'),
        ('Grand Bazaar', 'Beyazıt, Kalpakçılar Cd. No:22, 34126', 41.0107, 28.9680, 'morning'),
        ('Hafiz Mustafa 1864', 'Hobyar, Hamidiye Cd. No:84, 34112', 41.0161, 28.9719, 'lunch'),
        ('Karaköy Lokantası', 'Kemankeş Karamustafa Paşa, Kemankeş Cd. No:37', 41.0225, 28.9780, 'lunch'),
        ('Nusr-Et Steakhouse', 'Etiler, Nispetiye Cd. No:87', 41.0806, 29.0340, 'lunch'),
        ('Basilica Cistern', 'Alemdar, Yerebatan Cd. 1/3, 34110', 41.0084, 28.9779, 'afternoon'),
        ('Galata Tower', 'Bereketzade, Galata Kulesi, 34421', 41.0256, 28.9741, 'afternoon'),
        ('Spice Bazaar', 'Rüstem Paşa, Erzak Ambarı Sok. No:92, 34116', 41.0164, 28.9706, 'afternoon'),
        ('Bosphorus Cruise', 'Eminönü Pier, Fatih', 41.0177, 28.9735, 'evening'),
        ('Istiklal Street', 'Beyoğlu, İstiklal Cd., 34433', 41.0334, 28.9769, 'evening'),
        ('Ortaköy District', 'Ortaköy, Beşiktaş', 41.0478, 29.0275, 'evening'),
    ],
    'sydney': [
        ('Sydney Opera House', 'Bennelong Point, Sydney NSW 2000', -33.8568, 151.2153, 'morning'),
        ('Sydney Harbour Bridge', 'Sydney Harbour Bridge, Sydney NSW 2060', -33.8523, 151.2108, 'morning'),
        ('Bondi Beach', 'Bondi Beach, NSW 2026', -33.8915, 151.2767, 'morning'),
        ('Royal Botanic Garden', 'Mrs Macquaries Rd, Sydney NSW 2000', -33.8642, 151.2166, 'morning'),
        ('The Grounds of Alexandria', '7A/2 Huntley St, Alexandria NSW 2015', -33.9057, 151.1956, 'lunch'),
        ('Quay Restaurant', 'Upper Level, Overseas Passenger Terminal', -33.8569, 151.2100, 'lunch'),
        ('Bourke Street Bakery', '633 Bourke St, Surry Hills NSW 2010', -33.8844, 151.2122, 'lunch'),
        ('Taronga Zoo', 'Bradleys Head Rd, Mosman NSW 2088', -33.8437, 151.2412, 'afternoon'),
        ('The Rocks District', 'The Rocks, Sydney NSW 2000', -33.8597, 151.2085, 'afternoon'),
        ('Darling Harbour', 'Darling Harbour, Sydney NSW 2000', -33.8724, 151.1992, 'afternoon'),
        ('Vivid Sydney Walk', 'Circular Quay, Sydney NSW 2000', -33.8610, 151.2110, 'evening'),
        ('Barangaroo Reserve', 'Barangaroo NSW 2000', -33.8570, 151.2017, 'evening'),
        ('Manly Beach Sunset', 'Manly Beach, Manly NSW 2095', -33.7970, 151.2870, 'evening'),
    ],
    'singapore': [
        ('Marina Bay Sands', '10 Bayfront Ave, 018956', 1.2834, 103.8607, 'morning'),
        ('Gardens by the Bay', '18 Marina Gardens Dr, 018953', 1.2816, 103.8636, 'morning'),
        ('Merlion Park', '1 Fullerton Rd, 049213', 1.2868, 103.8545, 'morning'),
        ('Sentosa Island', 'Sentosa, Singapore', 1.2494, 103.8303, 'morning'),
        ('Maxwell Food Centre', '1 Kadayanallur St, 069184', 1.2804, 103.8448, 'lunch'),
        ('Jumbo Seafood', '20 Upper Circular Road, 058416', 1.2873, 103.8470, 'lunch'),
        ('Lau Pa Sat', '18 Raffles Quay, 048582', 1.2806, 103.8504, 'lunch'),
        ('Chinatown Heritage Centre', '48 Pagoda St, 059207', 1.2836, 103.8443, 'afternoon'),
        ('Little India', 'Little India, Singapore', 1.3066, 103.8518, 'afternoon'),
        ('Orchard Road Shopping', 'Orchard Rd, Singapore', 1.3048, 103.8318, 'afternoon'),
        ('Clarke Quay', '3 River Valley Rd, 179024', 1.2906, 103.8465, 'evening'),
        ('Gardens by the Bay Light Show', '18 Marina Gardens Dr, 018953', 1.2816, 103.8636, 'evening'),
        ('Night Safari', '80 Mandai Lake Rd, 729826', 1.4043, 103.7891, 'evening'),
    ],
    'maldives': [
        ('Malé Friday Mosque', 'Medhuziyaaraiy Magu, Malé', 4.1755, 73.5093, 'morning'),
        ('National Museum', 'Chaandhanee Magu, Malé', 4.1752, 73.5094, 'morning'),
        ('Banana Reef', 'North Malé Atoll', 4.2622, 73.5333, 'morning'),
        ('Artificial Beach', 'Boduthakurufaanu Magu, Malé', 4.1714, 73.5188, 'morning'),
        ('Sea House', 'JA Manafaru, Haa Alif Atoll', 6.7500, 72.9333, 'lunch'),
        ('Ithaa Undersea Restaurant', 'Conrad Maldives, Rangali Island', 3.5597, 72.5897, 'lunch'),
        ('Fish Market Malé', 'Boduthakurufaanu Magu, Malé', 4.1741, 73.5141, 'lunch'),
        ('Snorkeling at Maafushi', 'Maafushi Island, Kaafu Atoll', 3.9439, 73.4908, 'afternoon'),
        ('Hulhumalé Beach', 'Hulhumalé, Kaafu Atoll', 4.2110, 73.5400, 'afternoon'),
        ('Vaadhoo Island Bioluminescence', 'Vaadhoo Island, Raa Atoll', 5.3833, 72.8833, 'afternoon'),
        ('Sunset Dolphin Cruise', 'South Malé Atoll', 4.0000, 73.5000, 'evening'),
        ('Overwater Villa Dinner', 'Baa Atoll', 5.2000, 73.0000, 'evening'),
        ('Stargazing Sandbank', 'Ari Atoll', 3.8833, 72.8333, 'evening'),
    ],
    'switzerland': [
        ('Jungfraujoch', 'Jungfraujoch, 3801 Fieschertal', 46.5474, 7.9623, 'morning'),
        ('Lake Lucerne', 'Lake Lucerne, Lucerne', 47.0159, 8.3378, 'morning'),
        ('Matterhorn Viewpoint', 'Zermatt, 3920', 45.9766, 7.6585, 'morning'),
        ('Chapel Bridge Lucerne', 'Kapellbrücke, 6002 Luzern', 47.0516, 8.3078, 'morning'),
        ('Zeughauskeller Zürich', 'Bahnhofstrasse 28a, 8001 Zürich', 47.3716, 8.5392, 'lunch'),
        ('Chäsalp', 'Blüemlisalpstrasse 17, 3600 Thun', 46.7581, 7.6300, 'lunch'),
        ('Restaurant Whymper-Stube', 'Bahnhofstrasse 80, 3920 Zermatt', 46.0207, 7.7491, 'lunch'),
        ('Rhine Falls', 'Rheinfallquai, 8212 Neuhausen am Rheinfall', 47.6779, 8.6150, 'afternoon'),
        ('Old Town Bern', 'Altstadt, 3011 Bern', 46.9480, 7.4474, 'afternoon'),
        ('Château de Chillon', 'Avenue de Chillon 21, 1820 Veytaux', 46.4142, 6.9273, 'afternoon'),
        ('Zurich Lake Cruise', 'Zürichsee, Zürich', 47.3505, 8.5599, 'evening'),
        ('Grindelwald Village Walk', 'Grindelwald, 3818', 46.6244, 8.0413, 'evening'),
        ('Fondue Night in Zermatt', 'Zermatt Village, 3920', 46.0207, 7.7491, 'evening'),
    ],
}

# Category to time-slot mapping
CATEGORY_TIMES = {
    'morning': '09:00 AM',
    'lunch': '12:00 PM',
    'afternoon': '02:00 PM',
    'evening': '06:00 PM',
}


def _normalize_destination(dest_str):
    """Match user input to a known destination key."""
    lower = dest_str.lower().strip()
    for key in DESTINATION_PLACES:
        if key in lower or lower in key:
            return key
    return None


def _build_day_activities(places_by_cat, day_index, budget, duration):
    """Pick one place per category for a given day, cycling through the pool."""
    activities = []
    cost_fractions = {'morning': 0.05, 'lunch': 0.03, 'afternoon': 0.04, 'evening': 0.06}

    for cat in ['morning', 'lunch', 'afternoon', 'evening']:
        pool = places_by_cat.get(cat, [])
        if not pool:
            continue
        place = pool[day_index % len(pool)]
        name, address, lat, lng, _ = place
        activities.append({
            'time': CATEGORY_TIMES[cat],
            'activity': name,
            'location': address,
            'lat': lat,
            'lng': lng,
            'cost': round(budget * cost_fractions[cat]),
        })
    return activities


def generate_itinerary(user_id, data):
    """Demo: return a pre-built itinerary with real places and coordinates."""
    destinations = data.get('destinations', ['Paris'])
    duration = int(data.get('duration', 3))
    budget = float(data.get('budget', 1000))
    travelers = int(data.get('travelers', 1))
    preferences = data.get('preferences', [])
    start_date = data.get('startDate', '')

    dest_str = ', '.join(destinations) if isinstance(destinations, list) else destinations

    # Try to match the first destination to our database
    first_dest = destinations[0] if isinstance(destinations, list) else destinations
    matched_key = _normalize_destination(first_dest)

    days = []
    if matched_key:
        # Group places by category
        all_places = DESTINATION_PLACES[matched_key]
        places_by_cat = {}
        for place in all_places:
            cat = place[4]
            places_by_cat.setdefault(cat, []).append(place)

        for d in range(1, duration + 1):
            activities = _build_day_activities(places_by_cat, d - 1, budget, duration)
            days.append({
                'day': d,
                'activities': activities,
                'totalCost': round(budget / duration),
                'tips': [
                    'Book tickets in advance for popular attractions.',
                    'Try local street food for an authentic experience.',
                    'Use public transport to save money.',
                ],
            })
    else:
        # Fallback: generic activities without coordinates
        for d in range(1, duration + 1):
            days.append({
                'day': d,
                'activities': [
                    {'time': '09:00 AM', 'activity': f'Morning exploration of {dest_str}', 'location': f'{dest_str} City Center', 'cost': round(budget * 0.05)},
                    {'time': '12:00 PM', 'activity': 'Local cuisine lunch experience', 'location': f'Local Restaurant in {dest_str}', 'cost': round(budget * 0.03)},
                    {'time': '02:00 PM', 'activity': f'Visit famous landmarks - Day {d}', 'location': f'{dest_str} Landmark', 'cost': round(budget * 0.04)},
                    {'time': '06:00 PM', 'activity': 'Evening cultural experience', 'location': f'{dest_str} Cultural District', 'cost': round(budget * 0.06)},
                ],
                'totalCost': round(budget / duration),
                'tips': [
                    'Book tickets in advance for popular attractions.',
                    'Try local street food for an authentic experience.',
                    'Use public transport to save money.',
                ],
            })

    generated = {
        'title': f'{duration}-Day Adventure in {dest_str}',
        'days': days,
        'totalBudget': budget,
        'recommendations': [
            f'Best time to visit {dest_str} is during shoulder season for fewer crowds.',
            'Consider purchasing a city pass for discounted attraction entry.',
            'Learn a few basic phrases in the local language.',
            'Always carry some local currency for small vendors.',
            'Book accommodations near public transport for convenience.',
        ],
    }

    itinerary_data = {
        'userId': user_id,
        'input': {
            'destinations': destinations,
            'duration': duration,
            'budget': budget,
            'travelers': travelers,
            'preferences': preferences,
            'startDate': start_date,
        },
        'generatedItinerary': generated,
    }
    saved = create_ai_itinerary(itinerary_data)
    return saved, None


def get_suggestions(data):
    """Demo: return mock travel suggestions."""
    suggestions = [
        {
            'destination': 'Bali',
            'country': 'Indonesia',
            'description': 'Tropical paradise with stunning temples, rice terraces, and vibrant culture.',
            'estimatedCost': 1200,
            'bestTimeToVisit': 'April - October',
        },
        {
            'destination': 'Kyoto',
            'country': 'Japan',
            'description': 'Ancient capital with thousands of temples, traditional gardens, and geisha districts.',
            'estimatedCost': 2000,
            'bestTimeToVisit': 'March - May, October - November',
        },
        {
            'destination': 'Santorini',
            'country': 'Greece',
            'description': 'Iconic white-washed buildings, stunning sunsets, and crystal-clear waters.',
            'estimatedCost': 1800,
            'bestTimeToVisit': 'May - October',
        },
        {
            'destination': 'Marrakech',
            'country': 'Morocco',
            'description': 'Exotic markets, stunning palaces, and the gateway to the Sahara Desert.',
            'estimatedCost': 800,
            'bestTimeToVisit': 'March - May, September - November',
        },
        {
            'destination': 'Reykjavik',
            'country': 'Iceland',
            'description': 'Northern lights, geysers, waterfalls, and dramatic volcanic landscapes.',
            'estimatedCost': 2500,
            'bestTimeToVisit': 'June - August (summer), October - March (northern lights)',
        },
    ]
    return suggestions, None

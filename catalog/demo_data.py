"""Demo ma'lumotlar — haqiqiy narx reestri emas, namunaviy ma'lumot."""

# (category_icon, category_name_uz, [(name_inn, name_uz)])
CATEGORIES = [
    ("thermometer", "Og'riq qoldiruvchi va isitma tushiruvchi", [
        ("Paracetamol", "Paratsetamol"), ("Ibuprofen", "Ibuprofen"),
        ("Metamizole sodium", "Metamizol natriy"), ("Diclofenac", "Diklofenak"),
        ("Ketorolac", "Ketorolak"), ("Nimesulide", "Nimesulid"),
    ]),
    ("shield", "Antibiotiklar", [
        ("Amoxicillin", "Amoksitsillin"), ("Amoxicillin+Clavulanate", "Amoksitsillin+Klavulanat"),
        ("Azithromycin", "Azitromitsin"), ("Ciprofloxacin", "Siprofloksatsin"),
        ("Cefixime", "Tsefiksim"), ("Doxycycline", "Doksitsiklin"),
        ("Clarithromycin", "Klaritromitsin"), ("Metronidazole", "Metronidazol"),
    ]),
    ("virus", "Shamollash va gripp", [
        ("Oseltamivir", "Oseltamivir"), ("Bromhexine", "Bromgeksin"),
        ("Ambroxol", "Ambroksol"), ("Acetylcysteine", "Atsetilsistein"),
    ]),
    ("flower", "Allergiya", [
        ("Loratadine", "Loratadin"), ("Cetirizine", "Setirizin"),
        ("Desloratadine", "Desloratadin"), ("Chlorpheniramine", "Xlorfeniramin"),
    ]),
    ("stomach", "Oshqozon-ichak", [
        ("Omeprazole", "Omeprazol"), ("Pantoprazole", "Pantoprazol"),
        ("Drotaverine", "Drotaverin"), ("Domperidone", "Domperidon"),
        ("Loperamide", "Loperamid"), ("Simethicone", "Simetikon"),
        ("Diosmectite", "Diosmektit"), ("Nifuroxazide", "Nifuroksazid"),
        ("Probiotic complex", "Probiotik kompleks"),
    ]),
    ("heart-solid", "Yurak va qon tomir", [
        ("Amlodipine", "Amlodipin"), ("Enalapril", "Enalapril"),
        ("Lisinopril", "Lizinopril"), ("Losartan", "Lozartan"),
        ("Bisoprolol", "Bisoprolol"), ("Atorvastatin", "Atorvastatin"),
        ("Captopril", "Kaptopril"),
    ]),
    ("droplet", "Diabet", [("Metformin", "Metformin"), ("Gliclazide", "Glikazid")]),
    ("pill", "Vitamin va minerallar", [
        ("Ascorbic acid", "Askorbin kislotasi"), ("Cholecalciferol", "Vitamin D3"),
        ("Calcium+D3", "Kaltsiy+D3"), ("Magnesium+B6", "Magniy+B6"),
        ("Multivitamin complex", "Multivitamin kompleksi"),
    ]),
    ("lungs", "Nafas yo'llari", [("Salbutamol", "Salbutamol"), ("Montelukast", "Montelukast")]),
    ("bottle", "Teri va tashqi ishlatish", [
        ("Betamethasone", "Betametazon"), ("Hydrocortisone", "Gidrokortizon"),
        ("Clotrimazole", "Klotrimazol"), ("Ketoprofen", "Ketoprofen (gel)"),
    ]),
]

# substance_inn -> [(trade_name, manufacturer, dosage_form, dosage_strength, reference_price, [aliases])]
DRUGS = {
    "Paracetamol": [
        ("Panadol", "GSK", "tabletka", "500mg", 12000, ["панадол"]),
        ("Efferalgan", "UPSA", "eff. tabletka", "500mg", 18000, ["эфералган"]),
        ("Paracetamol-Farmak", "Farmak", "tabletka", "500mg", 4000, ["парацетамол"]),
    ],
    "Ibuprofen": [
        ("Nurofen", "Reckitt Benckiser", "tabletka", "400mg", 22000, ["нурофен"]),
        ("Ibuprom", "US Pharmacia", "tabletka", "400mg", 16000, ["ибупром"]),
    ],
    "Metamizole sodium": [
        ("Analgin", "Nobel", "tabletka", "500mg", 3500, ["анальгин"]),
        ("Baralgin M", "Sanofi", "tabletka", "500mg", 21000, ["баралгин"]),
    ],
    "Diclofenac": [
        ("Voltaren", "Novartis", "gel", "1%", 34000, ["вольтарен"]),
        ("Diclofenac-Nobel", "Nobel", "tabletka", "50mg", 5000, ["диклофенак"]),
    ],
    "Ketorolac": [("Ketorol", "Dr. Reddy's", "tabletka", "10mg", 13000, ["кеторол"])],
    "Nimesulide": [
        ("Nise", "Dr. Reddy's", "tabletka", "100mg", 17000, ["найз"]),
        ("Nimesil", "Guidotti", "granula", "100mg", 32000, ["нимесил"]),
    ],
    "Amoxicillin": [("Flemoxin Solutab", "Astellas", "tabletka", "500mg", 26000, ["флемоксин солютаб"])],
    "Amoxicillin+Clavulanate": [
        ("Amoksiklav", "Sandoz", "tabletka", "625mg", 42000, ["амоксиклав", "amoxiclav"]),
        ("Augmentin", "GSK", "tabletka", "625mg", 55000, ["аугментин"]),
        ("Flemoklav Solutab", "Astellas", "tabletka", "625mg", 48000, ["флемоклав солютаб"]),
    ],
    "Azithromycin": [
        ("Sumamed", "Teva/Pliva", "kapsula", "500mg", 45000, ["сумамед"]),
        ("Azitral", "Shreya Life", "kapsula", "500mg", 30000, ["азитрал"]),
    ],
    "Ciprofloxacin": [("Ciprobay", "Bayer", "tabletka", "500mg", 25000, ["ципробай"])],
    "Cefixime": [("Suprax", "Sanofi", "kapsula", "400mg", 52000, ["супракс"])],
    "Doxycycline": [("Unidox Solutab", "Astellas", "tabletka", "100mg", 21000, ["юнидокс солютаб"])],
    "Clarithromycin": [("Klacid", "Abbott", "tabletka", "500mg", 58000, ["клацид"])],
    "Metronidazole": [("Trichopolum", "Polpharma", "tabletka", "250mg", 6000, ["трихопол"])],
    "Oseltamivir": [("Tamiflu", "Roche", "kapsula", "75mg", 175000, ["тамифлю"])],
    "Bromhexine": [("Bromhexine-Nobel", "Nobel", "tabletka", "8mg", 4000, ["бромгексин"])],
    "Ambroxol": [
        ("Lazolvan", "Sanofi", "sirop", "30mg/5ml", 32000, ["лазолван"]),
        ("Ambroxol-Nobel", "Nobel", "sirop", "30mg/5ml", 12000, ["амброксол"]),
    ],
    "Acetylcysteine": [("ACC", "Sandoz", "eff. tabletka", "200mg", 27000, ["ацц"])],
    "Loratadine": [
        ("Claritin", "Bayer", "tabletka", "10mg", 19000, ["кларитин"]),
        ("Loratadine-Farmak", "Farmak", "tabletka", "10mg", 6000, ["лоратадин"]),
    ],
    "Cetirizine": [
        ("Zyrtec", "UCB", "tomchi", "10mg/ml", 32000, ["зиртек"]),
        ("Cetrin", "Dr. Reddy's", "tabletka", "10mg", 14000, ["цетрин"]),
    ],
    "Desloratadine": [("Erius", "Bayer", "tabletka", "5mg", 38000, ["эриус"])],
    "Chlorpheniramine": [("Chlorfeniramin-Nobel", "Nobel", "tabletka", "4mg", 3500, ["хлорфенирамин"])],
    "Omeprazole": [
        ("Omez", "Dr. Reddy's", "kapsula", "20mg", 17000, ["омез"]),
        ("Omeprazole-Nobel", "Nobel", "kapsula", "20mg", 6500, ["омепразол"]),
    ],
    "Pantoprazole": [("Nolpaza", "KRKA", "tabletka", "40mg", 26000, ["нольпаза"])],
    "Drotaverine": [
        ("No-shpa", "Sanofi", "tabletka", "40mg", 16000, ["но-шпа", "noshpa"]),
        ("Drotaverine-Farmak", "Farmak", "tabletka", "40mg", 4000, ["дротаверин"]),
    ],
    "Domperidone": [("Motilium", "Janssen", "tabletka", "10mg", 27000, ["мотилиум"])],
    "Loperamide": [("Imodium", "Janssen", "kapsula", "2mg", 21000, ["имодиум"])],
    "Simethicone": [("Espumisan", "Berlin-Chemie", "kapsula", "40mg", 34000, ["эспумизан"])],
    "Diosmectite": [("Smecta", "Ipsen", "poroshok", "3g", 26000, ["смекта"])],
    "Nifuroxazide": [("Enterofuril", "Bosnalijek", "kapsula", "200mg", 33000, ["энтерофурил"])],
    "Probiotic complex": [
        ("Linex", "Sandoz", "kapsula", "—", 34000, ["линекс"]),
        ("Bifiform", "Pfizer", "kapsula", "—", 38000, ["бифиформ"]),
    ],
    "Amlodipine": [
        ("Norvasc", "Pfizer", "tabletka", "5mg", 23000, ["норваск"]),
        ("Amlodipine-Nobel", "Nobel", "tabletka", "5mg", 6000, ["амлодипин"]),
    ],
    "Enalapril": [("Enap", "KRKA", "tabletka", "10mg", 11000, ["энап"])],
    "Lisinopril": [("Diroton", "Gedeon Richter", "tabletka", "10mg", 24000, ["диротон"])],
    "Losartan": [("Lozap", "Zentiva", "tabletka", "50mg", 28000, ["лозап"])],
    "Bisoprolol": [("Concor", "Merck", "tabletka", "5mg", 32000, ["конкор"])],
    "Atorvastatin": [("Atoris", "KRKA", "tabletka", "20mg", 29000, ["аторис"])],
    "Captopril": [("Capoten", "Bristol-Myers Squibb", "tabletka", "25mg", 15000, ["капотен"])],
    "Metformin": [
        ("Glucophage", "Merck", "tabletka", "850mg", 26000, ["глюкофаж"]),
        ("Siofor", "Berlin-Chemie", "tabletka", "850mg", 21000, ["сиофор"]),
    ],
    "Gliclazide": [("Diabeton MR", "Servier", "tabletka", "60mg", 38000, ["диабетон"])],
    "Ascorbic acid": [("Celaskon", "Zentiva", "tabletka", "500mg", 16000, ["целаскон", "витамин с"])],
    "Cholecalciferol": [("Aquadetrim", "Medana", "tomchi", "15000 IU/ml", 24000, ["аквадетрим"])],
    "Calcium+D3": [("Calcium-D3 Nycomed", "Takeda", "tabletka", "500mg+200IU", 33000, ["кальций д3 никомед"])],
    "Magnesium+B6": [
        ("Magne B6", "Sanofi", "tabletka", "470mg", 42000, ["магне б6"]),
        ("Magnelis B6", "Ozon", "tabletka", "470mg", 22000, ["магнелис б6"]),
    ],
    "Multivitamin complex": [
        ("Supradyn", "Bayer", "tabletka", "—", 55000, ["супрадин"]),
        ("Vitrum", "Unipharm", "tabletka", "—", 62000, ["витрум"]),
    ],
    "Salbutamol": [("Ventolin", "GSK", "aerozol", "100mcg", 29000, ["вентолин"])],
    "Montelukast": [("Singulair", "MSD", "tabletka", "10mg", 48000, ["сингуляр"])],
    "Betamethasone": [("Celestoderm", "MSD", "krem", "0.1%", 25000, ["целестодерм"])],
    "Hydrocortisone": [("Hydrocortisone-Nobel", "Nobel", "malham", "1%", 6000, ["гидрокортизон"])],
    "Clotrimazole": [("Kandid", "Glenmark", "krem", "1%", 15000, ["кандид"])],
    "Ketoprofen": [("Fastum gel", "Menarini", "gel", "2.5%", 31000, ["фастум гель"])],
}

# (name, address, lat, lng, phone)
PHARMACIES = [
    ("Dorixona 24/7 — Chilonzor", "Chilonzor tumani, Bunyodkor shoh ko'chasi 12", 41.2856, 69.2034, "+998712001001"),
    ("Apteka Plus — Yunusobod", "Yunusobod tumani, Amir Temur ko'chasi 45", 41.3457, 69.2874, "+998712001002"),
    ("Salomatlik Dorixonasi — Mirzo Ulug'bek", "Mirzo Ulug'bek tumani, Buyuk Ipak Yo'li 78", 41.3300, 69.3197, "+998712001003"),
    ("Oq Dorixona — Shayxontohur", "Shayxontohur tumani, Navoi ko'chasi 23", 41.3266, 69.2306, "+998712001004"),
    ("Zamin Farm — Sergeli", "Sergeli tumani, Qatortol ko'chasi 5", 41.2214, 69.2286, "+998712001005"),
    ("Doctor Apteka — Yashnobod", "Yashnobod tumani, Farg'ona yo'li 34", 41.3072, 69.3406, "+998712001006"),
    ("Med Servis — Olmazor", "Olmazor tumani, Kichik Halqa yo'li 9", 41.3608, 69.2185, "+998712001007"),
    ("Sog'lom Hayot — Bektemir", "Bektemir tumani, Qorasuv ko'chasi 15", 41.2437, 69.3459, "+998712001008"),
    ("Apteka Nur — Uchtepa", "Uchtepa tumani, Guliston ko'chasi 8", 41.2941, 69.1975, "+998712001009"),
    ("Farovon Dorixona — Yakkasaroy", "Yakkasaroy tumani, Mustaqillik shoh ko'chasi 61", 41.2965, 69.2578, "+998712001010"),
    ("Ideal Apteka — Shayxontohur 2", "Shayxontohur tumani, Beruniy ko'chasi 102", 41.3197, 69.2364, "+998712001011"),
    ("Vita Dorixona — Chilonzor 2", "Chilonzor tumani, Qatortol ko'chasi 40", 41.2789, 69.2011, "+998712001012"),
    ("Shifo Apteka — Yunusobod 2", "Yunusobod tumani, Shifokorlar ko'chasi 3", 41.3521, 69.2790, "+998712001013"),
    ("Rohat Dorixonasi — Mirobod", "Mirobod tumani, Taras Shevchenko ko'chasi 14", 41.3005, 69.2916, "+998712001014"),
    ("Barakat Apteka — Mirzo Ulug'bek 2", "Mirzo Ulug'bek tumani, Xurshid ko'chasi 22", 41.3378, 69.3355, "+998712001015"),
    ("Umid Dorixonasi — Sergeli 2", "Sergeli tumani, Qo'yliq ko'chasi 11", 41.2158, 69.2412, "+998712001016"),
    ("Najot Apteka — Bektemir 2", "Bektemir tumani, Sirdaryo ko'chasi 6", 41.2352, 69.3520, "+998712001017"),
    ("Ishonch Dorixona — Yashnobod 2", "Yashnobod tumani, Beshqayrag'och ko'chasi 19", 41.3129, 69.3512, "+998712001018"),
    ("Tinchlik Apteka — Uchtepa 2", "Uchtepa tumani, Nurafshon ko'chasi 27", 41.2887, 69.1889, "+998712001019"),
    ("Bahor Dorixonasi — Olmazor 2", "Olmazor tumani, Chorsu ko'chasi 4", 41.3654, 69.2251, "+998712001020"),
]

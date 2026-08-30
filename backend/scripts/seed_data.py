"""Demo seed ma'lumotlari (README'da ko'rsatilganidek — bular haqiqiy narx
reestri emas, taxminiy/namuna ma'lumotlar). TZ 6-bo'limiga mos:
~60 ta ta'sir moddasi, ~250 ta savdo nomi, ~25 ta Toshkent dorixonasi.
"""

# (name_inn, name_uz, name_ru)
SUBSTANCES = [
    ("Paracetamol", "Paratsetamol", "Парацетамол"),
    ("Ibuprofen", "Ibuprofen", "Ибупрофен"),
    ("Metamizole sodium", "Metamizol natriy", "Метамизол натрия"),
    ("Acetylsalicylic acid", "Atsetilsalitsil kislotasi", "Ацетилсалициловая кислота"),
    ("Nimesulide", "Nimesulid", "Нимесулид"),
    ("Diclofenac", "Diklofenak", "Диклофенак"),
    ("Ketorolac", "Ketorolak", "Кеторолак"),
    ("Amoxicillin", "Amoksitsillin", "Амоксициллин"),
    ("Amoxicillin+Clavulanate", "Amoksitsillin+Klavulanat", "Амоксициллин+Клавуланат"),
    ("Azithromycin", "Azitromitsin", "Азитромицин"),
    ("Ciprofloxacin", "Siprofloksatsin", "Ципрофлоксацин"),
    ("Cefixime", "Tsefiksim", "Цефиксим"),
    ("Ceftriaxone", "Tseftriakson", "Цефтриаксон"),
    ("Doxycycline", "Doksitsiklin", "Доксициклин"),
    ("Clarithromycin", "Klaritromitsin", "Кларитромицин"),
    ("Levofloxacin", "Levofloksatsin", "Левофлоксацин"),
    ("Metronidazole", "Metronidazol", "Метронидазол"),
    ("Oseltamivir", "Oseltamivir", "Осельтамивир"),
    ("Acyclovir", "Atsiklovir", "Ацикловир"),
    ("Loratadine", "Loratadin", "Лоратадин"),
    ("Cetirizine", "Setirizin", "Цетиризин"),
    ("Chlorpheniramine", "Xlorfeniramin", "Хлорфенирамин"),
    ("Diphenhydramine", "Difengidramin", "Дифенгидрамин"),
    ("Desloratadine", "Desloratadin", "Дезлоратадин"),
    ("Omeprazole", "Omeprazol", "Омепразол"),
    ("Pantoprazole", "Pantoprazol", "Пантопразол"),
    ("Ranitidine", "Ranitidin", "Ранитидин"),
    ("Drotaverine", "Drotaverin", "Дротаверин"),
    ("Domperidone", "Domperidon", "Домперидон"),
    ("Loperamide", "Loperamid", "Лоперамид"),
    ("Simethicone", "Simetikon", "Симетикон"),
    ("Mebeverine", "Meberin", "Мебеверин"),
    ("Amlodipine", "Amlodipin", "Амлодипин"),
    ("Enalapril", "Enalapril", "Эналаприл"),
    ("Lisinopril", "Lizinopril", "Лизиноприл"),
    ("Losartan", "Lozartan", "Лозартан"),
    ("Bisoprolol", "Bisoprolol", "Бисопролол"),
    ("Atorvastatin", "Atorvastatin", "Аторвастатин"),
    ("Captopril", "Kaptopril", "Каптоприл"),
    ("Metformin", "Metformin", "Метформин"),
    ("Gliclazide", "Glikazid", "Гликлазид"),
    ("Ascorbic acid", "Askorbin kislotasi", "Аскорбиновая кислота"),
    ("Cholecalciferol", "Xoletsiferol (Vitamin D3)", "Холекальциферол"),
    ("Calcium+D3", "Kaltsiy+D3", "Кальций+Д3"),
    ("Magnesium+B6", "Magniy+B6", "Магний+Б6"),
    ("Multivitamin complex", "Multivitamin kompleksi", "Мультивитаминный комплекс"),
    ("Salbutamol", "Salbutamol", "Сальбутамол"),
    ("Bromhexine", "Bromgeksin", "Бромгексин"),
    ("Ambroxol", "Ambroksol", "Амброксол"),
    ("Acetylcysteine", "Atsetilsistein", "Ацетилцистеин"),
    ("Montelukast", "Montelukast", "Монтелукаст"),
    ("Ketoprofen", "Ketoprofen", "Кетопрофен"),
    ("Meloxicam", "Meloksikam", "Мелоксикам"),
    ("Betamethasone", "Betametazon", "Бетаметазон"),
    ("Hydrocortisone", "Gidrokortizon", "Гидрокортизон"),
    ("Clotrimazole", "Klotrimazol", "Клотримазол"),
    ("Oral rehydration salts", "Og'iz orqali reгidratatsiya tuzlari", "Регидратационные соли"),
    ("Activated charcoal", "Faollashtirilgan ko'mir", "Активированный уголь"),
    ("Diosmectite", "Diosmektit", "Диосмектит"),
    ("Nifuroxazide", "Nifuroksazid", "Нифуроксазид"),
    ("Probiotic complex", "Probiotik kompleks", "Пробиотический комплекс"),
]

# substance_inn -> list of (trade_name, manufacturer, dosage_form, dosage_strength, reference_price, [aliases])
DRUGS: dict[str, list[tuple[str, str, str, str, int, list[str]]]] = {
    "Paracetamol": [
        ("Panadol", "GSK", "tabletka", "500mg", 12000, ["панадол", "panadol 500"]),
        ("Efferalgan", "UPSA", "eff. tabletka", "500mg", 18000, ["эфералган"]),
        ("Paracetamol-Farmak", "Farmak", "tabletka", "500mg", 4000, ["парацетамол"]),
        ("Paracetamol sirop", "Nobel", "sirop", "120mg/5ml", 15000, ["парацетамол сироп"]),
    ],
    "Ibuprofen": [
        ("Nurofen", "Reckitt Benckiser", "tabletka", "400mg", 22000, ["нурофен"]),
        ("Ibuprom", "US Pharmacia", "tabletka", "400mg", 16000, ["ибупром"]),
        ("Ibuprofen-Nika", "Nika Pharm", "tabletka", "200mg", 6000, ["ибупрофен"]),
    ],
    "Metamizole sodium": [
        ("Analgin", "Nobel", "tabletka", "500mg", 3500, ["анальгин", "анальгін"]),
        ("Baralgin M", "Sanofi", "tabletka", "500mg", 21000, ["баралгин"]),
    ],
    "Acetylsalicylic acid": [
        ("Aspirin", "Bayer", "tabletka", "500mg", 9000, ["аспирин"]),
        ("Cardiomagnyl", "Takeda", "tabletka", "75mg", 28000, ["кардиомагнил"]),
    ],
    "Nimesulide": [
        ("Nise", "Dr. Reddy's", "tabletka", "100mg", 17000, ["найз", "nise 100"]),
        ("Nimesil", "Laboratori Guidotti", "granula", "100mg", 32000, ["нимесил"]),
    ],
    "Diclofenac": [
        ("Voltaren", "Novartis", "gel", "1%", 34000, ["вольтарен"]),
        ("Diclofenac-Nobel", "Nobel", "tabletka", "50mg", 5000, ["диклофенак"]),
        ("Olfen", "Mepha", "kapsula", "75mg", 24000, ["олфен"]),
    ],
    "Ketorolac": [
        ("Ketorol", "Dr. Reddy's", "tabletka", "10mg", 13000, ["кеторол"]),
        ("Ketanov", "Ranbaxy", "tabletka", "10mg", 12000, ["кетанов"]),
    ],
    "Amoxicillin": [
        ("Amoxicillin-Farmak", "Farmak", "kapsula", "500mg", 8000, ["амоксициллин"]),
        ("Flemoxin Solutab", "Astellas", "tabletka", "500mg", 26000, ["флемоксин солютаб"]),
    ],
    "Amoxicillin+Clavulanate": [
        ("Amoksiklav", "Sandoz", "tabletka", "625mg", 42000, ["амоксиклав", "amoxiclav", "amoksiklav 625"]),
        ("Augmentin", "GSK", "tabletka", "625mg", 55000, ["аугментин"]),
        ("Flemoklav Solutab", "Astellas", "tabletka", "625mg", 48000, ["флемоклав солютаб"]),
    ],
    "Azithromycin": [
        ("Sumamed", "Teva/Pliva", "kapsula", "500mg", 45000, ["сумамед"]),
        ("Azitral", "Shreya Life", "kapsula", "500mg", 30000, ["азитрал"]),
        ("AzitroSandoz", "Sandoz", "tabletka", "500mg", 27000, ["азитро сандоз"]),
    ],
    "Ciprofloxacin": [
        ("Ciprobay", "Bayer", "tabletka", "500mg", 25000, ["ципробай"]),
        ("Ciprofloxacin-Nobel", "Nobel", "tabletka", "500mg", 9000, ["ципрофлоксацин"]),
    ],
    "Cefixime": [
        ("Suprax", "Sanofi", "kapsula", "400mg", 52000, ["супракс"]),
        ("Cefspan", "Zodiac", "kapsula", "400mg", 34000, ["цефспан"]),
    ],
    "Ceftriaxone": [
        ("Ceftriaxone-Farmak", "Farmak", "in'yeksiya", "1g", 7000, ["цефтриаксон"]),
        ("Rocephin", "Roche", "in'yeksiya", "1g", 48000, ["роцефин"]),
    ],
    "Doxycycline": [
        ("Doxycycline-Nobel", "Nobel", "kapsula", "100mg", 4500, ["доксициклин"]),
        ("Unidox Solutab", "Astellas", "tabletka", "100mg", 21000, ["юнидокс солютаб"]),
    ],
    "Clarithromycin": [
        ("Klacid", "Abbott", "tabletka", "500mg", 58000, ["клацид"]),
        ("Fromilid", "KRKA", "tabletka", "500mg", 41000, ["фромилид"]),
    ],
    "Levofloxacin": [
        ("Tavanic", "Sanofi", "tabletka", "500mg", 47000, ["таваник"]),
        ("Levofloxacin-Teva", "Teva", "tabletka", "500mg", 19000, ["левофлоксацин"]),
    ],
    "Metronidazole": [
        ("Trichopolum", "Polpharma", "tabletka", "250mg", 6000, ["трихопол"]),
        ("Metronidazole-Nobel", "Nobel", "tabletka", "250mg", 3000, ["метронидазол"]),
    ],
    "Oseltamivir": [
        ("Tamiflu", "Roche", "kapsula", "75mg", 175000, ["тамифлю"]),
    ],
    "Acyclovir": [
        ("Zovirax", "GSK", "krem", "5%", 28000, ["зовиракс"]),
        ("Acyclovir-Nobel", "Nobel", "tabletka", "400mg", 8000, ["ацикловир"]),
    ],
    "Loratadine": [
        ("Claritin", "Bayer", "tabletka", "10mg", 19000, ["кларитин"]),
        ("Loratadine-Farmak", "Farmak", "tabletka", "10mg", 6000, ["лоратадин"]),
    ],
    "Cetirizine": [
        ("Zyrtec", "UCB", "tomchi", "10mg/ml", 32000, ["зиртек"]),
        ("Cetrin", "Dr. Reddy's", "tabletka", "10mg", 14000, ["цетрин"]),
        ("Allertec", "Nobel", "tabletka", "10mg", 11000, ["аллертек"]),
    ],
    "Chlorpheniramine": [
        ("Chlorfeniramin-Nobel", "Nobel", "tabletka", "4mg", 3500, ["хлорфенирамин"]),
    ],
    "Diphenhydramine": [
        ("Dimedrol", "Darnitsa", "in'yeksiya", "1%", 4000, ["димедрол"]),
    ],
    "Desloratadine": [
        ("Erius", "Bayer", "tabletka", "5mg", 38000, ["эриус"]),
        ("Desal", "KRKA", "tabletka", "5mg", 24000, ["десал"]),
    ],
    "Omeprazole": [
        ("Omez", "Dr. Reddy's", "kapsula", "20mg", 17000, ["омез"]),
        ("Losec", "AstraZeneca", "kapsula", "20mg", 39000, ["лосек"]),
        ("Omeprazole-Nobel", "Nobel", "kapsula", "20mg", 6500, ["омепразол"]),
    ],
    "Pantoprazole": [
        ("Nolpaza", "KRKA", "tabletka", "40mg", 26000, ["нольпаза"]),
        ("Controloc", "Takeda", "tabletka", "40mg", 44000, ["контролок"]),
    ],
    "Ranitidine": [
        ("Ranisan", "KRKA", "tabletka", "150mg", 9000, ["ранисан"]),
    ],
    "Drotaverine": [
        ("No-shpa", "Chinoin/Sanofi", "tabletka", "40mg", 16000, ["но-шпа", "noshpa"]),
        ("Drotaverine-Farmak", "Farmak", "tabletka", "40mg", 4000, ["дротаверин"]),
        ("Spazmalgon", "KRKA", "tabletka", "40mg", 14000, ["спазмалгон"]),
    ],
    "Domperidone": [
        ("Motilium", "Janssen", "tabletka", "10mg", 27000, ["мотилиум"]),
        ("Domet", "Sun Pharma", "tabletka", "10mg", 13000, ["домет"]),
    ],
    "Loperamide": [
        ("Imodium", "Janssen", "kapsula", "2mg", 21000, ["имодиум"]),
        ("Loperamide-Nobel", "Nobel", "tabletka", "2mg", 3000, ["лоперамид"]),
    ],
    "Simethicone": [
        ("Espumisan", "Berlin-Chemie", "kapsula", "40mg", 34000, ["эспумизан"]),
        ("Bebinos", "Kern Pharma", "tomchi", "—", 29000, ["бебинос"]),
    ],
    "Mebeverine": [
        ("Duspatalin", "Abbott", "kapsula", "200mg", 45000, ["дюспаталин"]),
    ],
    "Amlodipine": [
        ("Norvasc", "Pfizer", "tabletka", "5mg", 23000, ["норваск"]),
        ("Amlodipine-Nobel", "Nobel", "tabletka", "5mg", 6000, ["амлодипин"]),
        ("Tenox", "KRKA", "tabletka", "5mg", 18000, ["тенокс"]),
    ],
    "Enalapril": [
        ("Enap", "KRKA", "tabletka", "10mg", 11000, ["энап"]),
        ("Enalapril-Nobel", "Nobel", "tabletka", "10mg", 3500, ["эналаприл"]),
    ],
    "Lisinopril": [
        ("Diroton", "Gedeon Richter", "tabletka", "10mg", 24000, ["диротон"]),
        ("Lisinopril-Teva", "Teva", "tabletka", "10mg", 9000, ["лизиноприл"]),
    ],
    "Losartan": [
        ("Lozap", "Zentiva", "tabletka", "50mg", 28000, ["лозап"]),
        ("Lorista", "KRKA", "tabletka", "50mg", 22000, ["лориста"]),
    ],
    "Bisoprolol": [
        ("Concor", "Merck", "tabletka", "5mg", 32000, ["конкор"]),
        ("Bisoprolol-Nobel", "Nobel", "tabletka", "5mg", 8000, ["бисопролол"]),
    ],
    "Atorvastatin": [
        ("Lipitor", "Pfizer", "tabletka", "20mg", 47000, ["липитор"]),
        ("Atoris", "KRKA", "tabletka", "20mg", 29000, ["аторис"]),
    ],
    "Captopril": [
        ("Capoten", "Bristol-Myers Squibb", "tabletka", "25mg", 15000, ["капотен"]),
        ("Captopril-Nobel", "Nobel", "tabletka", "25mg", 3000, ["каптоприл"]),
    ],
    "Metformin": [
        ("Glucophage", "Merck", "tabletka", "850mg", 26000, ["глюкофаж"]),
        ("Siofor", "Berlin-Chemie", "tabletka", "850mg", 21000, ["сиофор"]),
        ("Metformin-Nobel", "Nobel", "tabletka", "850mg", 7000, ["метформин"]),
    ],
    "Gliclazide": [
        ("Diabeton MR", "Servier", "tabletka", "60mg", 38000, ["диабетон"]),
    ],
    "Ascorbic acid": [
        ("Vitamin C-Nobel", "Nobel", "tabletka", "500mg", 5000, ["витамин с", "аскорбинка"]),
        ("Celaskon", "Zentiva", "tabletka", "500mg", 16000, ["целаскон"]),
    ],
    "Cholecalciferol": [
        ("Aquadetrim", "Medana", "tomchi", "15000 IU/ml", 24000, ["аквадетрим"]),
        ("Vigantol", "Merck", "tomchi", "20000 IU/ml", 27000, ["вигантол"]),
    ],
    "Calcium+D3": [
        ("Calcium-D3 Nycomed", "Takeda", "tabletka", "500mg+200IU", 33000, ["кальций д3 никомед"]),
    ],
    "Magnesium+B6": [
        ("Magne B6", "Sanofi", "tabletka", "470mg", 42000, ["магне б6"]),
        ("Magnelis B6", "Ozon", "tabletka", "470mg", 22000, ["магнелис б6"]),
    ],
    "Multivitamin complex": [
        ("Supradyn", "Bayer", "tabletka", "—", 55000, ["супрадин"]),
        ("Vitrum", "Unipharm", "tabletka", "—", 62000, ["витрум"]),
        ("Complivit", "Pharmstandard", "tabletka", "—", 24000, ["компливит"]),
    ],
    "Salbutamol": [
        ("Ventolin", "GSK", "aerozol", "100mcg", 29000, ["вентолин"]),
    ],
    "Bromhexine": [
        ("Bromhexine-Nobel", "Nobel", "tabletka", "8mg", 4000, ["бромгексин"]),
    ],
    "Ambroxol": [
        ("Lazolvan", "Sanofi/Boehringer", "sirop", "30mg/5ml", 32000, ["лазолван"]),
        ("Ambroxol-Nobel", "Nobel", "sirop", "30mg/5ml", 12000, ["амброксол"]),
        ("Flavamed", "Berlin-Chemie", "tabletka", "30mg", 19000, ["флавамед"]),
    ],
    "Acetylcysteine": [
        ("ACC", "Sandoz", "eff. tabletka", "200mg", 27000, ["ацц"]),
        ("Fluimucil", "Zambon", "granula", "200mg", 24000, ["флуимуцил"]),
    ],
    "Montelukast": [
        ("Singulair", "MSD", "tabletka", "10mg", 48000, ["сингуляр"]),
    ],
    "Ketoprofen": [
        ("Ketonal", "Sandoz", "kapsula", "50mg", 22000, ["кетонал"]),
        ("Fastum gel", "Menarini", "gel", "2.5%", 31000, ["фастум гель"]),
    ],
    "Meloxicam": [
        ("Movalis", "Boehringer Ingelheim", "tabletka", "15mg", 34000, ["мовалис"]),
        ("Meloxicam-Nobel", "Nobel", "tabletka", "15mg", 9000, ["мелоксикам"]),
    ],
    "Betamethasone": [
        ("Diprospan", "MSD", "in'yeksiya", "7mg/ml", 36000, ["дипроспан"]),
        ("Celestoderm", "MSD", "krem", "0.1%", 25000, ["целестодерм"]),
    ],
    "Hydrocortisone": [
        ("Hydrocortisone-Nobel", "Nobel", "malham", "1%", 6000, ["гидрокортизон"]),
    ],
    "Clotrimazole": [
        ("Kandid", "Glenmark", "krem", "1%", 15000, ["кандид"]),
        ("Clotrimazole-Nobel", "Nobel", "vagin. tabletka", "100mg", 8000, ["клотримазол"]),
    ],
    "Oral rehydration salts": [
        ("Regidron", "Orion Pharma", "poroshok", "—", 8000, ["регидрон"]),
        ("Hydrovit", "Zdrave", "poroshok", "—", 6500, ["гидровит"]),
    ],
    "Activated charcoal": [
        ("Faol ko'mir", "Farmak", "tabletka", "250mg", 2000, ["активированный уголь", "активка"]),
    ],
    "Diosmectite": [
        ("Smecta", "Ipsen", "poroshok", "3g", 26000, ["смекта"]),
        ("Neosmectin", "Bosnalijek", "poroshok", "3g", 19000, ["неосмектин"]),
    ],
    "Nifuroxazide": [
        ("Enterofuril", "Bosnalijek", "kapsula", "200mg", 33000, ["энтерофурил"]),
        ("Stopdiar", "Sandoz", "kapsula", "200mg", 27000, ["стопдиар"]),
    ],
    "Probiotic complex": [
        ("Linex", "Sandoz", "kapsula", "—", 34000, ["линекс"]),
        ("Bifiform", "Pfizer", "kapsula", "—", 38000, ["бифиформ"]),
        ("Lactofiltrum", "Avva Rus", "tabletka", "—", 29000, ["лактофильтрум"]),
    ],
}

# (name, address, lat, lng, phone) — Toshkent shahri, taxminiy koordinatalar.
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
    ("Rasadxona Apteka — Mirzo Ulug'bek 3", "Mirzo Ulug'bek tumani, Astronomik ko'cha 2", 41.3243, 69.3298, "+998712001021"),
    ("Gulbog' Dorixonasi — Yakkasaroy 2", "Yakkasaroy tumani, Gulbog' ko'chasi 17", 41.2903, 69.2649, "+998712001022"),
    ("Osiyo Apteka — Chilonzor 3", "Chilonzor tumani, Osiyo ko'chasi 31", 41.2812, 69.2145, "+998712001023"),
    ("Nihol Dorixona — Yunusobod 3", "Yunusobod tumani, Nihol ko'chasi 8", 41.3489, 69.2955, "+998712001024"),
    ("Marjon Apteka — Shayxontohur 3", "Shayxontohur tumani, Marjon ko'chasi 12", 41.3231, 69.2432, "+998712001025"),
]

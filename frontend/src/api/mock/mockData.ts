import type { Pharmacy } from '../../types/api'

export interface MockSubstance {
  id: number
  name_inn: string
  name_uz: string
}

export interface MockDrug {
  id: number
  trade_name: string
  substance_id: number
  manufacturer: string
  dosage_form: string
  dosage_strength: string
  reference_price: number
  aliases: string[]
}

export interface MockPrice {
  pharmacy_id: number
  drug_id: number
  price: number
  in_stock: boolean
  updated_at: string
}

export const substances: MockSubstance[] = [
  { id: 1, name_inn: 'Amoxicillin + Clavulanic acid', name_uz: 'Amoksitsillin + Klavulanat kislota' },
  { id: 2, name_inn: 'Paracetamol', name_uz: 'Parasetamol' },
  { id: 3, name_inn: 'Ibuprofen', name_uz: 'Ibuprofen' },
  { id: 4, name_inn: 'Omeprazole', name_uz: 'Omeprazol' },
  { id: 5, name_inn: 'Loratadine', name_uz: 'Loratadin' },
  { id: 6, name_inn: 'Metformin', name_uz: 'Metformin' },
  { id: 7, name_inn: 'Azithromycin', name_uz: 'Azitromitsin' },
]

export const drugs: MockDrug[] = [
  { id: 1, trade_name: 'Amoksiklav 625mg', substance_id: 1, manufacturer: 'Sandoz', dosage_form: 'tabletka', dosage_strength: '625mg', reference_price: 45000, aliases: ['амоксиклав', 'amoxiclav', 'амоксиклав 625'] },
  { id: 2, trade_name: 'Augmentin 625mg', substance_id: 1, manufacturer: 'GSK', dosage_form: 'tabletka', dosage_strength: '625mg', reference_price: 52000, aliases: ['аугментин', 'augmentin'] },
  { id: 3, trade_name: 'Panadol 500mg', substance_id: 2, manufacturer: 'GSK', dosage_form: 'tabletka', dosage_strength: '500mg', reference_price: 12000, aliases: ['панадол'] },
  { id: 4, trade_name: 'Paracetamol-Darmon 500mg', substance_id: 2, manufacturer: 'Darmon', dosage_form: 'tabletka', dosage_strength: '500mg', reference_price: 6000, aliases: ['парацетамол', 'paracetamol'] },
  { id: 5, trade_name: 'Nurofen 400mg', substance_id: 3, manufacturer: 'Reckitt', dosage_form: 'tabletka', dosage_strength: '400mg', reference_price: 22000, aliases: ['нурофен'] },
  { id: 6, trade_name: 'Ibuprom 400mg', substance_id: 3, manufacturer: 'US Pharmacia', dosage_form: 'tabletka', dosage_strength: '400mg', reference_price: 15000, aliases: ['ибупром', 'ибупрофен', 'ibuprofen'] },
  { id: 7, trade_name: 'Omez 20mg', substance_id: 4, manufacturer: "Dr. Reddy's", dosage_form: 'kapsula', dosage_strength: '20mg', reference_price: 28000, aliases: ['омез'] },
  { id: 8, trade_name: 'Ultop 20mg', substance_id: 4, manufacturer: 'KRKA', dosage_form: 'kapsula', dosage_strength: '20mg', reference_price: 31000, aliases: ['ультоп'] },
  { id: 9, trade_name: 'Claritin 10mg', substance_id: 5, manufacturer: 'Bayer', dosage_form: 'tabletka', dosage_strength: '10mg', reference_price: 26000, aliases: ['кларитин'] },
  { id: 10, trade_name: 'Lorano 10mg', substance_id: 5, manufacturer: 'Sandoz', dosage_form: 'tabletka', dosage_strength: '10mg', reference_price: 14000, aliases: ['лорано'] },
  { id: 11, trade_name: 'Glucophage 500mg', substance_id: 6, manufacturer: 'Merck', dosage_form: 'tabletka', dosage_strength: '500mg', reference_price: 32000, aliases: ['глюкофаж'] },
  { id: 12, trade_name: 'Siofor 500mg', substance_id: 6, manufacturer: 'Berlin-Chemie', dosage_form: 'tabletka', dosage_strength: '500mg', reference_price: 27000, aliases: ['сиофор'] },
  { id: 13, trade_name: 'Sumamed 500mg', substance_id: 7, manufacturer: 'Pliva', dosage_form: 'tabletka', dosage_strength: '500mg', reference_price: 48000, aliases: ['сумамед'] },
  { id: 14, trade_name: 'Azimed 500mg', substance_id: 7, manufacturer: 'Nobel', dosage_form: 'tabletka', dosage_strength: '500mg', reference_price: 36000, aliases: ['азимед'] },
]

export const pharmacies: Pharmacy[] = [
  { id: 1, name: "Oq Ipak Dorixona", address: "Chilonzor tumani, Bunyodkor shoh ko'chasi 12", lat: 41.2856, lng: 69.2034, phone: '+998 71 200 10 10' },
  { id: 2, name: "Sog'lom Hayot", address: 'Yunusobod tumani, Amir Temur ko\'chasi 45', lat: 41.3399, lng: 69.2879, phone: '+998 71 200 20 20' },
  { id: 3, name: 'Shifo Dorixonasi', address: "Mirzo Ulug'bek tumani, Buyuk Ipak Yo'li 5", lat: 41.3275, lng: 69.3193, phone: '+998 71 200 30 30' },
  { id: 4, name: 'Salomatlik Plus', address: "Sergeli tumani, Qatortol ko'chasi 78", lat: 41.2273, lng: 69.2308, phone: '+998 71 200 40 40' },
  { id: 5, name: 'Doristor', address: "Yakkasaroy tumani, Shota Rustaveli ko'chasi 3", lat: 41.2996, lng: 69.2626, phone: '+998 71 200 50 50' },
  { id: 6, name: 'Apteka №1', address: "Mirobod tumani, Nukus ko'chasi 21", lat: 41.3006, lng: 69.2879, phone: '+998 71 200 60 60' },
]

function seededRandom(seed: number) {
  let value = seed % 2147483647
  if (value <= 0) value += 2147483646
  return () => {
    value = (value * 16807) % 2147483647
    return (value - 1) / 2147483646
  }
}

export const prices: MockPrice[] = (() => {
  const rows: MockPrice[] = []
  for (const pharmacy of pharmacies) {
    const rand = seededRandom(pharmacy.id * 97 + 13)
    for (const drug of drugs) {
      if (rand() < 0.15) continue
      const variance = 0.85 + rand() * 0.4
      const isOverpriced = rand() < 0.25
      const multiplier = isOverpriced ? variance + 0.3 : variance
      const price = Math.round((drug.reference_price * multiplier) / 500) * 500
      const daysAgo = Math.floor(rand() * 6)
      rows.push({
        pharmacy_id: pharmacy.id,
        drug_id: drug.id,
        price,
        in_stock: rand() > 0.12,
        updated_at: new Date(Date.now() - daysAgo * 86400000).toISOString(),
      })
    }
  }
  return rows
})()

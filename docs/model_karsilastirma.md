# Chat modeli karşılaştırması

Aynı 7 soruyu, aynı retrieval sonuçlarıyla (top-4 parça) üç modele sordum. Hepsi Foundry Local
kataloğundaki GPU varyantları, M3 Pro / 18 GB bir MacBook'ta çalıştı. Süreler embedding ve
arama dahil değil, sadece modelin cevap üretme süresi.

| Model | Boyut | Ort. süre | Türkçe cevap kalitesi | Not |
|---|---|---|---|---|
| phi-4-mini | 3,7 GB | ~5 sn | Zayıf | Aynı ifadeyi döngü hâlinde tekrar etti ("hem normal hem hem fazla ders yükünü..."), bağlamda cevap varken bile "bulamadım" dedi, "iki derstir alabilirsiniz" gibi bozuk cümleler kurdu. `frequency_penalty` döngüyü kesiyor ama içerik yine karışık. |
| qwen3-1.7b | 1,4 GB | ~4 sn | Zayıf | En hızlısı ama bağlamı olduğu gibi kopyalıyor ("Parça 1 (Staj Yönergesi...)"), soruyu cevabın içine yapıştırıyor, maddeleri karıştırıyor. |
| **qwen3-4b** | 2,9 GB | ~6 sn | İyi | Sayıları ve koşulları doğru aktarıyor, Türkçesi düzgün. Kusurları: bazen aynı cümleyi iki kere yazıyor, istenmese de liste yapıyor; ikisi de temizleme adımıyla büyük ölçüde çözüldü. |

## qwen3-4b ile ilgili iki ayar

**Düşünme modu.** Qwen3 varsayılan olarak cevaptan önce `<think>` bloğunda İngilizce akıl yürütüyor;
bu 300-400 token tutuyor ve cevap 15 saniyeyi buluyordu. Kullanıcı mesajının sonuna `/no_think`
ekleyince blok boş geliyor ve süre 6 saniyeye iniyor. (OpenAI uyumlu API üzerinden
`enable_thinking=False` gönderme denemesi işe yaramadı.)

**Kaynak satırı.** Önce modelden "Kaynak: belge, madde" satırı yazmasını istedim. Örnek verince
örneği aynen kopyaladı (alakasız soruda "Kaynak: Staj Yönergesi, Madde 5" yazdı), örnek vermeyip
"parçanın başındaki etiketi yaz" deyince bu sefer parçaların tamamını kopyalamaya başladı. Küçük
modeller prompt'taki biçim örneklerine fazla takılıyor. Sonunda kaynak satırını modele hiç
bırakmadım: cevabın altına, eşiği geçen ilk iki parçanın etiketini uygulama ekliyor.

## Örnek: "Yaz okulunda en fazla kaç ders alabilirim?"

- phi-4-mini: *"Yaz öğretiminde en fazla iki derstir alabilirsiniz."*
- qwen3-1.7b: *"(1) Yaz öğretiminin süresi final dönemi hariç yedi haftadır. Soru: Yaz okulunda en fazla kaç ders alabilirim?"* (bağlamı ve soruyu geri yazdı)
- qwen3-4b: *"Yaz öğretiminde en fazla iki ders alabilirim. Mezuniyet durumundaki öğrenciler, danışman onayı ile üç ders alabilirler."*

Sonuç: varsayılan model `qwen3-4b`. Daha hızlı bir makinede `qwen3-8b` ya da `phi-4` denenebilir;
`ayarlar.py` içindeki `CHAT_MODELI` değerini değiştirmek yeterli.

# CMP-02 — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — PergolaTerrace, отдельная виньетка для общей сетки и источник ракурсов деталей. Store files built from it — `12_Compositions, 07_Closeups`.
Reference image: `planning/CottageGardenDecor/scenes/CMP-02.png`

## Prompt (Codex, Sol 6.2)

```
Edit only plants on the pergola in first image. Preserve every other prop, framing and matching models. Four separate fitted wisteria hangings under the beam, each with grouped small faceted leaf clumps and SEVERAL segmented tapered lavender pendant clusters underneath as in reference 2. All four wisteria hangings identical, violet and pale lilac mixed, each mounted directly under beam with no visible rod ends, no gap, no oversized single hanging cone. Pink rose garland like third reference with pink flowers instead of red, short and narrow 1.6 m total, resting ON TOP of centre of front wooden beam with the rest of beam clear. No other changes.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Каркас | STR-04 ×1, STR-05 ×1, PLT-05 ×4, PLT-03_Pink ×1 | Два пролёта с общей парой стоек. Глициния снизу балок на 2,24 м, одна розовая гирлянда над передней балкой на 2,46 м. |
| Под перголой | FUR-03 ×1, FUR-04 ×2 | Тёмное кованое бистро, стол 0,75 м и два стула 0,85 м. |
| Задняя граница | MOD-01 ×2, MOD-02 ×3 | Два пролёта белой ширмы по 2 м с общим средним столбом. |
| Передние углы | ORN-03_Planted ×2 | Каменные урны с цветами на квадратных пьедесталах, по 1,384 м. |

## Camera and light

- Ракурс, высота и FOV. Наклон 40° вниз, азимут 30° к фронту площадки, слабая перспектива близкая к ортографической, квадрат 1:1. Единая ориентация камеры для всех шести виньеток, высота и дистанция под габарит площадки, поля около 10%.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Сплошной тёплый светлый фон #F5F1E9, как у виньеток Farm Processing, и небольшой остров с ровным газоном.
- Свободная область. Поля по периметру, подписи размещаются отдельно при сборке сетки.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Видны два пролёта и четырёхкратный подвес глицинии. Виньетка передаёт состав, конструкцию стыка сверить по Modules и размерам каталога. Розовую гирлянду ставить поверх балки по монтажной высоте.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. Глициния висит с зазором, у стола прямые ноги, гирлянда на всю балку. |
| 2 | Отклонена. Стол и урны уточнены, глициния из одиночных кистей вместо групп. |
| 3 | Выбрана. Четыре группы кистей под балкой, одна короткая розовая гирлянда, кованое бистро и две урны читаются. |

## Fixes

<!-- The render reviewer appends fix sections. -->

# Hero_Lite — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5): Hero / полевая работа Lite · Store files built from it: 05_Hero (Lite)
Reference image: `planning/FarmMachinery/scenes/Hero_Lite.png`

Кадрирование: 16:9, 1672 × 941 px.
Референс постановки для Unity (MKT-01). Опорные изображения моделей из `art/FarmMachinery/Previews/`: TRC-01, IMP-01, TRC-02, TRL-01, лист принятых превью lite-implements.

## Prompt (Codex, Sol 6.2)

```
Wide 16:9 landscape single-panel staged Unity scene reference, 40-degree downward front-oblique three-quarter camera with weak perspective, one leading focal point. Foreground left and centre: one compact red cab tractor with smaller front tyres correctly hauling one gray four-share plough from its rear. Model the exact first two input models, tractor nose down-left and plough visible behind toward the right, grounded on a textureless muted brown soil colour plane. Middle right: one larger BLUE tractor with four equal large cream-rimmed tyres from reference 3 (approved blue body atlas) towing one tall RED two-axle tipper from reference 4, with a low straw-gold grain load inside the trailer. Attach its drawbar to the tractor's rear; this group is smaller in composition by depth. One parked seed drill red box (reference 5), one parked red single-axle folded-boom sprayer (reference 6) and one small gray cultivator with red hitch (reference 7) are separate in one distant lane with room between each. Do not duplicate. Broad flat soil and muted beige stubble bands and a small muted cool-sage parking patch on one single level plane. Light neutral sky high in background; clean spaces between main silhouettes and outer edges. No building, silo, tall plant, trees, fence, animals, bales, people, labels, logos, borders, scene-set or decorative items. All assets match exact simple low-poly shapes and proportions shown by the supplied modeling previews.

Use only the catalog models specified, treat individual input images as exact geometry and colour references, never reuse their isolated backgrounds. Actual Blender preview proportions and construction must win over stylized interpretations. Muted red #C8473B, opaque blue-grey windows, dark tread blocks and cream solid rims, simple hard-edged geometry; limited cool gray-blue sky gradient if visible, texture-free ground in two or three calm flat tones, soft daylight from upper left, subtle contact shadows only, wheels and implements seated on the same plane. Pure concept stage reference for Unity scene placement, no type or poster graphics. Return the requested landscape ratio with full silhouettes.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Передний левый план | TRC-01 Red ×1, IMP-01 ×1 | Главный акцент. Плуг на Link3P_Rear, лапы выставить к плоскости. |
| Средний правый план | TRC-02 Blue ×1, TRL-01 Grain ×1 | Сцепить на Hitch_Rear, ход параллельно границе двух плоскостей. Зерно только в TRL-01. |
| Дальний угол двора | IMP-02 ×1, IMP-03 Transport ×1, IMP-06 ×1 | Припарковать раздельно, беречь силуэты и не перекрывать главную связку. |

## Camera and light

- Angle / height / FOV: 40° вниз, около 35° к продольной оси тягачей, высота 17 м над плоскостью, вертикальный FOV 36°. Визир между пахотой и линией перевозки.
- Light: мягкий дневной ключ сверху слева, холодное рассеянное заполнение, короткие мягкие контактные тени.
- Background: одна ровная плоскость с двумя или тремя плоскими цветами — почва, стерня, короткая трава. Светлый серо-голубой фон, если виден горизонт.
- Free area for plates: Плашка не предусмотрена. Оставить края свободными на 5%.

## Not in pack — remove

- Посторонних объектов в выбранном кадре не обнаружено.

## Поправки для постановки в Unity

- Убрать мелкую шумовую фактуру светлых полос, использовать сплошные цвета.

## Generations

| # | Settings | Result |
|---|---|---|
| 1 | ImageGen, session model gpt-6.2-sol | Выбрано: читается основной трактор с плугом, зерновоз и три припаркованных орудия. Первый вызов с семью входами отклонён инструментом до генерации, затем орудия сведены в один лист. |

## Fixes

<!-- The render reviewer appends "## Fix N (<date>)" sections. -->

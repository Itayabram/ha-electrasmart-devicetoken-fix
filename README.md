# תיקון ל-Electra Smart Integration — שגיאת `KeyError: 'deviceToken'`

## הבעיה

החל מסוף ספטמבר 2026, משתמשים רבים של אינטגרציית **Electra Smart** ב-Home Assistant מדווחים שכל המזגנים נעלמים (`unavailable`) ולא נטענים מחדש, עם השגיאה הבאה בלוג:

```
KeyError: 'deviceToken'
File ".../electrasmart/device/__init__.py", line 20, in __init__
    self.token: str = data["deviceToken"]
```

**הסיבה:** ה-API הציבורי של אלקטרה (`GET_DEVICES`) הפסיק להחזיר שדה `deviceToken` עבור חלק מהמכשירים. ספריית `pyElectra` שה-integration משתמשת בה לא מתמודדת עם זה בחן ומתרסקת — וקריסה אחת כזו מפילה את **כל** החשבון (כל המזגנים, לא רק את הבעייתי).

דווח גם בקהילה הישראלית ([פוסט פייסבוק](https://www.facebook.com/groups/homeassistant.co.il)) ובגיטהאב הרשמי:
- https://github.com/home-assistant/core/issues/183846
- https://github.com/home-assistant/core/issues/183829

## הפתרון

זהו עותק מקומי (`custom_components`) של האינטגרציה הרשמית, זהה לחלוטין לקוד המקור (גרסת Home Assistant 2026.9.4) — **מלבד שינוי אחד ממוקד**: ב-`__init__.py` יש monkey-patch שהופך את `deviceToken` לשדה אופציונלי במקום לקרוס. אם מכשיר חסר טוקן, הוא נרשם עם אזהרה בלוג וממשיך לפעול (קריאת סטטוס ובדרך כלל גם שליחת פקודות ימשיכו לעבוד); שאר המכשירים בחשבון לא נפגעים כלל.

## התקנה

### אפשרות א': דרך HACS (מומלץ)
1. ב-HACS → שלוש נקודות למעלה → **Custom repositories**
2. הדבק את כתובת הריפו הזה, קטגוריה **Integration**
3. חפש "Electra Smart (deviceToken fix)" והתקן
4. **הפעל מחדש את Home Assistant** (custom_components לא נטענים ב-hot reload)

### אפשרות ב': ידני
1. העתק את התיקייה `custom_components/electrasmart` מהריפו הזה אל `/config/custom_components/electrasmart` בשרת ה-HA שלך
2. הפעל מחדש את Home Assistant

### אם האינטגרציה כבר מוגדרת אצלך
אין צורך להגדיר מחדש — פשוט שים את הקבצים במקום והפעל מחדש. ה-config entry הקיים ימשיך לעבוד כרגיל.

## חשוב לדעת

- זה **תיקון זמני בצד הלקוח**, לא תיקון רשמי. ברגע ש-Home Assistant/Electra יתקנו את הבעיה בגרסת הליבה הרשמית, **ה-custom_components הזה ימשיך "לנצח" ולהסתיר את התיקון הרשמי** עד שתסיר אותו ידנית:
  ```
  rm -rf /config/custom_components/electrasmart
  ```
  ואז restart נוסף.
- מומלץ לעקוב אחרי ה-issues למעלה ולהסיר את התיקון הזה כשהם ייסגרו.

## קרדיט

התיקון המקורי ב-`__init__.py` הוא שלי (Itay); כל שאר הקוד הוא עותק ללא שינוי של האינטגרציה הרשמית, codeowners: [@jafar-atili](https://github.com/jafar-atili).

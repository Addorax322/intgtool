# Гайд: как запустить AI Integration Tool

## Два способа запуска

---

## 1. Запуск с промптом из сообщения (командная строка)

Сразу передаёте текст запроса в кавычках:

```bash
python main.py "Объясни простыми словами, что такое машинное обучение"
```

**Windows (PowerShell):**
```powershell
python main.py "Объясни простыми словами, что такое машинное обучение"
```

Ответ выводится в консоль и сохраняется в `output/output_1.txt`.

---

## 2. Запуск с файлом (запрос из файла)

Запрос берётся из текстового файла, результат пишется в другой файл:

```bash
python main.py --input request.txt --output result.txt
```

Короткие опции:

```bash
python main.py -i request.txt -o result.txt
```

**Если `--output` не указан**, результат сохранится в файл рядом с входным, например `request_response.txt`:

```bash
python main.py -i request.txt
# Результат: request_response.txt в той же папке
```

---

## Дополнительные опции

| Опция | Описание | Пример |
|-------|----------|--------|
| `--stream`, `-s` | Стриминг ответа в консоль | `python main.py --stream "Напиши стих"` |
| `--model`, `-m` | Другая модель | `python main.py -m deepseek/deepseek-r1 "вопрос"` |
| `--no-save` | Не сохранять в output_N.txt | `python main.py --no-save "вопрос"` |
| `--file`, `-f` | То же, что `--input` | `python main.py -f input.txt -o out.txt` |

---

## Примеры

**Промпт из сообщения:**
```bash
python main.py "Переведи на английский: Привет, мир!"
```

**Промпт из файла:**
```bash
python main.py -i input.txt -o result.txt
```

**Стриминг (по мере генерации):**
```bash
python main.py --stream "Напиши короткое стихотворение про код"
```

**Интерактивный режим (без аргументов):**
```bash
python main.py
```
Вводите запросы по очереди, выходите через `exit` или `quit`.
